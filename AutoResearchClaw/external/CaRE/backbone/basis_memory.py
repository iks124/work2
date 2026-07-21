import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class SharedAdapter(nn.Module):
    """CaRE-compatible shared adapter used to isolate structural asymmetry."""

    def __init__(self, dim, bottleneck=64, dropout=0.1):
        super().__init__()
        self.norm = nn.LayerNorm(dim)
        self.down_proj = nn.Linear(dim, bottleneck)
        self.up_proj = nn.Linear(bottleneck, dim)
        self.dropout = nn.Dropout(dropout)
        self.scale = nn.Parameter(torch.zeros(dim))
        self.reset_parameters()

    def reset_parameters(self):
        for module in (self.down_proj, self.up_proj):
            nn.init.kaiming_uniform_(module.weight, a=math.sqrt(5))
            nn.init.zeros_(module.bias)

    def forward(self, x):
        x = self.down_proj(self.norm(x))
        x = self.dropout(F.relu(x))
        return self.up_proj(x) * self.scale


class BasisMemoryAdapter(nn.Module):
    """Fixed-capacity low-rank adapter memory with interchangeable readers."""

    SUPPORTED_MODES = {"signed_top2", "hard_top2", "fixed_top2", "dense_softmax"}

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.dim = int(config.d_model)
        self.basis_count = int(config.get("basis_count", 8))
        self.rank = int(config.get("basis_rank", 16))
        self.key_dim = int(config.get("basis_key_dim", self.dim))
        self.temperature = float(config.get("router_temperature", 0.2))
        self.balance_temperature = float(
            config.get("balance_temperature", self.temperature)
        )
        self.init_scale = float(config.get("basis_init_scale", 1e-3))
        self.use_shared_adapter = bool(config.get("use_shared_adapter", False))
        self.basis_enabled = bool(config.get("basis_enabled", True))
        self.mode = str(config.get("memory_mode", "signed_top2"))
        if self.mode not in self.SUPPORTED_MODES:
            raise ValueError(f"Unsupported basis-memory mode: {self.mode}")
        if self.basis_count < 2:
            raise ValueError("basis_count must be at least 2")
        if self.temperature <= 0:
            raise ValueError("router_temperature must be positive")

        self.input_norm = nn.LayerNorm(self.dim)
        self.query = nn.Linear(self.dim, self.key_dim, bias=False)
        self.keys = nn.Parameter(torch.empty(self.basis_count, self.key_dim))
        self.down = nn.Parameter(torch.empty(self.basis_count, self.dim, self.rank))
        self.up = nn.Parameter(torch.empty(self.basis_count, self.rank, self.dim))
        self.scale = nn.Parameter(torch.full((self.dim,), self.init_scale))
        self.shared_adapter = None
        if self.use_shared_adapter:
            # Preserve the global RNG stream so enabling the shared branch does
            # not silently change basis/latent-head initialization in a paired
            # ablation. The branch still receives a deterministic initialization
            # from the current RNG state inside the fork.
            with torch.random.fork_rng(devices=[]):
                self.shared_adapter = SharedAdapter(
                    self.dim,
                    bottleneck=int(config.get("adapter_dim", 64)),
                    dropout=0.1,
                )
        self.latent_head = nn.ModuleList()
        self.last_route = None
        self.last_balance_loss = None
        self.register_buffer("_route_load", torch.zeros(self.basis_count), persistent=False)
        self.register_buffer("_route_entropy_sum", torch.zeros(()), persistent=False)
        self.register_buffer("_route_samples", torch.zeros((), dtype=torch.long), persistent=False)
        self.register_buffer("_negative_weights", torch.zeros((), dtype=torch.long), persistent=False)
        self.register_buffer("_active_weights", torch.zeros((), dtype=torch.long), persistent=False)
        self._reset_parameters()
        self._update_adapters()

    def _reset_parameters(self):
        nn.init.trunc_normal_(self.query.weight, std=0.02)
        nn.init.normal_(self.keys, std=1.0 / math.sqrt(self.key_dim))
        nn.init.kaiming_uniform_(self.down, a=math.sqrt(5))
        nn.init.kaiming_uniform_(self.up, a=math.sqrt(5))

    def _update_adapters(self, num_classes=None):
        for parameter in self.latent_head.parameters():
            parameter.requires_grad = False
        num_classes = self.config.init_cls if num_classes is None else num_classes
        head = nn.Sequential(
            nn.LayerNorm(self.dim),
            nn.Linear(self.dim, int(num_classes)),
        ).to(self.config._device)
        nn.init.ones_(head[0].weight)
        nn.init.zeros_(head[0].bias)
        nn.init.trunc_normal_(head[1].weight, std=0.02)
        nn.init.zeros_(head[1].bias)
        self.latent_head.append(head)
        self.requires_grad_(True)
        for old_head in self.latent_head[:-1]:
            old_head.requires_grad_(False)

    def _load_shared_adapter(self, use_ema=False):
        self.requires_grad_(True)
        for old_head in self.latent_head[:-1]:
            old_head.requires_grad_(False)

    def route(self, cls_token):
        query = F.normalize(self.query(self.input_norm(cls_token)), dim=-1)
        keys = F.normalize(self.keys, dim=-1)
        scores = query @ keys.transpose(0, 1)
        soft_importance = torch.softmax(scores / self.balance_temperature, dim=-1)
        mean_importance = soft_importance.mean(dim=0)
        self.last_balance_loss = (
            self.basis_count * mean_importance.square().sum() - 1.0
        )

        if self.mode == "signed_top2":
            indices = scores.abs().topk(2, dim=-1).indices
            selected = scores.gather(-1, indices)
            weights = selected / selected.abs().sum(dim=-1, keepdim=True).clamp_min(1e-6)
            weights = weights.to(dtype=scores.dtype)
            route = torch.zeros_like(scores).scatter(-1, indices, weights)
        elif self.mode == "hard_top2":
            indices = scores.topk(2, dim=-1).indices
            selected = scores.gather(-1, indices) / self.temperature
            weights = torch.softmax(selected, dim=-1).to(dtype=scores.dtype)
            route = torch.zeros_like(scores).scatter(-1, indices, weights)
        elif self.mode == "fixed_top2":
            route = torch.zeros_like(scores)
            route[:, :2] = 0.5
        else:
            route = torch.softmax(scores / self.temperature, dim=-1)

        self.last_route = route.detach()
        with torch.no_grad():
            probabilities = route.abs()
            probabilities = probabilities / probabilities.sum(dim=-1, keepdim=True).clamp_min(1e-12)
            self._route_load.add_((route != 0).sum(dim=0))
            self._route_entropy_sum.add_(
                -(probabilities * probabilities.clamp_min(1e-12).log()).sum()
            )
            self._route_samples.add_(route.shape[0])
            self._negative_weights.add_((route < 0).sum())
            self._active_weights.add_((route != 0).sum())
        return route

    def reset_diagnostics(self):
        self._route_load.zero_()
        self._route_entropy_sum.zero_()
        self._route_samples.zero_()
        self._negative_weights.zero_()
        self._active_weights.zero_()

    def diagnostics(self):
        samples = max(1, int(self._route_samples.item()))
        active = max(1, int(self._active_weights.item()))
        load = self._route_load.float() / samples
        return {
            "route_entropy": float(self._route_entropy_sum.item() / samples),
            "slot_load": load.cpu().tolist(),
            "dead_slots": int((self._route_load == 0).sum().item()),
            "negative_weight_fraction": float(self._negative_weights.item() / active),
        }

    def forward(self, x, add_residual=True, residual=None, task_id=0, with_task_id=False):
        residual = x if residual is None else residual
        normalized = self.input_norm(x)
        route = self.route(x[:, 0])
        if not self.basis_enabled:
            update = torch.zeros_like(x)
        elif self.mode == "dense_softmax":
            down = torch.einsum("bnd,edr->benr", normalized, self.down)
            down = F.relu(down)
            basis_outputs = torch.einsum("benr,erd->bend", down, self.up)
            update = torch.einsum("be,bend->bnd", route, basis_outputs)
        else:
            indices = route.abs().topk(2, dim=-1).indices
            weights = route.gather(-1, indices)
            selected_down = self.down[indices]
            selected_up = self.up[indices]
            down = torch.einsum("bnd,bkdr->bknr", normalized, selected_down)
            down = F.relu(down)
            basis_outputs = torch.einsum("bknr,bkrd->bknd", down, selected_up)
            update = torch.einsum("bk,bknd->bnd", weights, basis_outputs)
        update = update * self.scale
        if self.shared_adapter is not None:
            update = update + self.shared_adapter(x)
        output = update + residual if add_residual else update

        cls = None
        if with_task_id:
            if task_id < 0 or task_id >= len(self.latent_head):
                raise IndexError(
                    f"task_id {task_id} is invalid for {len(self.latent_head)} heads"
                )
            cls = self.latent_head[task_id](output[:, 0])
        return output, cls

    def stored_parameter_count(self):
        names = ("keys", "down", "up")
        return sum(getattr(self, name).numel() for name in names)

    def active_adapter_flops(self, batch_size, token_count):
        active = self.basis_count if self.mode == "dense_softmax" else 2
        projections = 4 * batch_size * token_count * self.dim * self.rank * active
        routing = 2 * batch_size * self.key_dim * self.basis_count
        return projections + routing
