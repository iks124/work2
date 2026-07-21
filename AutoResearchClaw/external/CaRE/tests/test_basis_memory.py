import unittest

import torch
from easydict import EasyDict

from backbone.basis_memory import BasisMemoryAdapter


def make_config(mode):
    return EasyDict(
        d_model=64,
        basis_count=8,
        basis_rank=4,
        basis_key_dim=16,
        router_temperature=0.2,
        basis_init_scale=1e-3,
        use_shared_adapter=False,
        basis_enabled=True,
        adapter_dim=8,
        memory_mode=mode,
        init_cls=10,
        _device=torch.device("cpu"),
    )


class BasisMemoryAdapterTest(unittest.TestCase):
    def _run_mode(self, mode):
        torch.manual_seed(7)
        module = BasisMemoryAdapter(make_config(mode))
        tokens = torch.randn(4, 17, 64, requires_grad=True)
        output, aux = module(tokens, task_id=0, with_task_id=True)
        self.assertEqual(output.shape, tokens.shape)
        self.assertEqual(aux.shape, (4, 10))
        loss = output.square().mean() + aux.square().mean()
        loss.backward()
        for name in ("keys", "down", "up"):
            gradient = getattr(module, name).grad
            self.assertIsNotNone(gradient, name)
            self.assertTrue(torch.isfinite(gradient).all(), name)
            self.assertGreater(gradient.abs().sum().item(), 0.0, name)
        self.assertTrue(torch.isfinite(tokens.grad).all())
        return module

    def test_signed_top2_gradient_and_sparsity(self):
        module = self._run_mode("signed_top2")
        nonzero = (module.last_route != 0).sum(dim=-1)
        self.assertTrue(torch.equal(nonzero, torch.full_like(nonzero, 2)))
        absolute_sums = module.last_route.abs().sum(dim=-1)
        self.assertTrue(torch.allclose(absolute_sums, torch.ones_like(absolute_sums)))

    def test_hard_top2_gradient_and_sparsity(self):
        module = self._run_mode("hard_top2")
        nonzero = (module.last_route != 0).sum(dim=-1)
        self.assertTrue(torch.equal(nonzero, torch.full_like(nonzero, 2)))
        self.assertTrue(
            torch.allclose(module.last_route.sum(dim=-1), torch.ones(4))
        )

    def test_fixed_top2_is_content_independent(self):
        module = BasisMemoryAdapter(make_config("fixed_top2"))
        module(torch.randn(4, 17, 64))
        expected = torch.zeros(4, 8)
        expected[:, :2] = 0.5
        self.assertTrue(torch.equal(module.last_route, expected))

    def test_dense_gradient_and_budget(self):
        dense = self._run_mode("dense_softmax")
        sparse = BasisMemoryAdapter(make_config("signed_top2"))
        self.assertTrue((dense.last_route > 0).all())
        self.assertEqual(dense.stored_parameter_count(), sparse.stored_parameter_count())
        dense_flops = dense.active_adapter_flops(4, 17)
        sparse_flops = sparse.active_adapter_flops(4, 17)
        self.assertGreater(dense_flops, sparse_flops)

    def test_capacity_does_not_grow_across_tasks(self):
        module = BasisMemoryAdapter(make_config("signed_top2"))
        stored_before = module.stored_parameter_count()
        basis_shapes = (module.keys.shape, module.down.shape, module.up.shape)
        module._update_adapters(num_classes=10)
        self.assertEqual(module.stored_parameter_count(), stored_before)
        self.assertEqual(
            (module.keys.shape, module.down.shape, module.up.shape), basis_shapes
        )
        self.assertEqual(len(module.latent_head), 2)

    def test_configurable_scale_and_shared_adapter(self):
        config = make_config("hard_top2")
        config.basis_init_scale = 0.1
        config.use_shared_adapter = True
        module = BasisMemoryAdapter(config)
        self.assertTrue(torch.allclose(module.scale, torch.full_like(module.scale, 0.1)))
        self.assertIsNotNone(module.shared_adapter)
        tokens = torch.randn(2, 5, 64)
        output, _ = module(tokens)
        output.square().mean().backward()
        self.assertIsNotNone(module.shared_adapter.scale.grad)
        self.assertGreater(module.shared_adapter.scale.grad.abs().sum().item(), 0.0)

    def test_shared_toggle_preserves_paired_initialization(self):
        torch.manual_seed(11)
        control = BasisMemoryAdapter(make_config("hard_top2"))
        torch.manual_seed(11)
        config = make_config("hard_top2")
        config.use_shared_adapter = True
        treatment = BasisMemoryAdapter(config)
        for name in ("keys", "down", "up"):
            self.assertTrue(
                torch.equal(getattr(control, name), getattr(treatment, name)), name
            )
        self.assertTrue(
            torch.equal(
                control.latent_head[0][1].weight,
                treatment.latent_head[0][1].weight,
            )
        )

    def test_shared_only_disables_basis_update(self):
        config = make_config("hard_top2")
        config.use_shared_adapter = True
        config.basis_enabled = False
        module = BasisMemoryAdapter(config)
        tokens = torch.randn(2, 5, 64)
        output, _ = module(tokens)
        expected = tokens + module.shared_adapter(tokens)
        self.assertTrue(torch.allclose(output, expected))

    def test_balance_loss_is_finite_and_differentiable(self):
        module = BasisMemoryAdapter(make_config("hard_top2"))
        module(torch.randn(8, 5, 64))
        self.assertTrue(torch.isfinite(module.last_balance_loss))
        self.assertGreaterEqual(module.last_balance_loss.item(), -1e-6)
        module.last_balance_loss.backward()
        self.assertGreater(module.keys.grad.abs().sum().item(), 0.0)
        self.assertGreater(module.query.weight.grad.abs().sum().item(), 0.0)


if __name__ == "__main__":
    unittest.main()
