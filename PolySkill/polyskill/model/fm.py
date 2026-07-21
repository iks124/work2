"""Unified litellm-backed foundation-model client for PolySkill.

Routes all four supported models through litellm:
  - provider="openai"     -> "<name>"            (OPENAI_API_KEY)
  - provider="anthropic"  -> "anthropic/<name>"  (ANTHROPIC_API_KEY)
  - provider in {"local","oss","openai-compatible"} ->
        "openai/<served-name>" with api_base/api_key from env
        (POLYSKILL_OSS_API_BASE / POLYSKILL_OSS_API_KEY) — SGLang or OpenRouter.
"""
from __future__ import annotations
import os, base64
from typing import Any, Optional, Union, List
from io import BytesIO

import litellm

# Map paper model names -> the name your OSS endpoint actually serves. Override via env if needed.
_OSS_NAME_MAP = {
    "qwen3-coder-480b-a35b": os.getenv("POLYSKILL_QWEN_SERVED_NAME", "qwen3-coder-480b-a35b"),
    "glm-4.5": os.getenv("POLYSKILL_GLM_SERVED_NAME", "glm-4.5"),
}
_OSS_PROVIDERS = {"local", "oss", "openai-compatible", "sglang", "vllm", "openrouter"}


def _image_to_data_url(img) -> str:
    if isinstance(img, str) and os.path.exists(img):
        with open(img, "rb") as f:
            raw = f.read()
        return "data:image/png;base64," + base64.b64encode(raw).decode()
    # PIL.Image
    buf = BytesIO(); img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


class FoundationModel:
    def __init__(self, provider: str, name: str, temperature: float = 0.0,
                 max_tokens: int = 512, timeout: int = 120, num_responses: int = 1,
                 base_url: Optional[str] = None, api_key: Optional[str] = None,
                 **kwargs: Any):
        self.provider = provider
        self.name = name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.num_responses = num_responses
        self.base_url = base_url
        self.api_key = api_key
        self.extra = kwargs

    def _model_string(self) -> str:
        p = self.provider.lower()
        if p == "openai":
            return self.name
        if p == "anthropic":
            return self.name if self.name.startswith("anthropic/") else f"anthropic/{self.name}"
        if p in _OSS_PROVIDERS:
            served = _OSS_NAME_MAP.get(self.name, self.name)
            return f"openai/{served}"
        # default: pass through (lets litellm route, e.g. "openrouter/...")
        return self.name

    def _provider_kwargs(self) -> dict:
        p = self.provider.lower()
        if p in _OSS_PROVIDERS:
            # Per-model values are required when the agent/judge and inducer are
            # served by different OpenAI-compatible endpoints.
            base = self.base_url or os.getenv("POLYSKILL_OSS_API_BASE")
            key = self.api_key or os.getenv("POLYSKILL_OSS_API_KEY", "EMPTY")
            kw = {"api_key": key}
            if base:
                kw["api_base"] = base
            # Qwen reasoning text is emitted in message.content and can consume
            # the entire output budget before structured actions / judge labels /
            # induced code appear.  Structured web-agent calls should therefore
            # use the model's non-thinking chat template by default.
            if os.getenv("POLYSKILL_OSS_ENABLE_THINKING", "0").lower() not in {
                "1", "true", "yes", "on"
            }:
                kw["extra_body"] = {
                    "chat_template_kwargs": {"enable_thinking": False}
                }
            return kw
        return {}

    def _build_messages(self, messages=None, prompt=None, images=None) -> List[dict]:
        if messages is not None:
            return messages
        content: Union[str, list]
        if images:
            content = [{"type": "text", "text": prompt or ""}]
            for im in images:
                content.append({"type": "image_url", "image_url": {"url": _image_to_data_url(im)}})
        else:
            content = prompt or ""
        return [{"role": "user", "content": content}]

    def generate(self, messages: Optional[List[dict]] = None, prompt: Optional[str] = None,
                 images: Optional[list] = None, max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None, n: Optional[int] = None,
                 return_raw: bool = False, **kwargs) -> Union[str, tuple, Any]:
        msgs = self._build_messages(messages=messages, prompt=prompt, images=images)
        call = dict(model=self._model_string(), messages=msgs,
                    temperature=self.temperature if temperature is None else temperature,
                    max_tokens=self.max_tokens if max_tokens is None else max_tokens,
                    timeout=self.timeout, **self._provider_kwargs(), **kwargs)
        n = n if n is not None else self.num_responses
        if n and n > 1:
            call["n"] = n
        resp = litellm.completion(**call)
        if return_raw:
            return resp
        texts = [c.message.content for c in resp.choices]
        if n and n > 1:
            return texts
        return texts[0]

    # Back-compat helper used by inducers expecting a `.completion(...)` object.
    def completion(self, **kwargs):
        kwargs.setdefault("model", self._model_string())
        for k, v in self._provider_kwargs().items():
            kwargs.setdefault(k, v)
        return litellm.completion(**kwargs)
