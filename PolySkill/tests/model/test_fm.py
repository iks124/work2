import os, pytest
from polyskill.model import FoundationModel

def test_construct_from_kwargs():
    fm = FoundationModel(provider="openai", name="gpt-4.1", temperature=0.1, max_tokens=64)
    assert fm.provider == "openai" and fm.name == "gpt-4.1"

def test_resolve_litellm_model_string():
    assert FoundationModel(provider="openai", name="gpt-4.1")._model_string() == "gpt-4.1"
    assert FoundationModel(provider="anthropic", name="claude-3-7-sonnet-20250219")._model_string() == "anthropic/claude-3-7-sonnet-20250219"
    fm = FoundationModel(provider="local", name="qwen3-coder-480b-a35b")
    assert fm._model_string().startswith("openai/")  # OpenAI-compatible base_url path

def test_messages_from_prompt_and_images(tmp_path):
    fm = FoundationModel(provider="openai", name="gpt-4.1")
    msgs = fm._build_messages(prompt="hi", images=None)
    assert msgs[-1]["role"] == "user"

def test_local_structured_calls_disable_thinking_by_default(monkeypatch):
    monkeypatch.delenv("POLYSKILL_OSS_ENABLE_THINKING", raising=False)
    fm = FoundationModel(provider="local", name="Qwen3.5-9B")
    assert fm._provider_kwargs()["extra_body"] == {
        "chat_template_kwargs": {"enable_thinking": False}
    }

def test_local_thinking_can_be_reenabled(monkeypatch):
    monkeypatch.setenv("POLYSKILL_OSS_ENABLE_THINKING", "1")
    fm = FoundationModel(provider="local", name="Qwen3.5-9B")
    assert "extra_body" not in fm._provider_kwargs()

def test_local_model_can_override_endpoint_per_instance(monkeypatch):
    monkeypatch.setenv("POLYSKILL_OSS_API_BASE", "http://fallback.invalid/v1")
    fm = FoundationModel(
        provider="local", name="Qwen3.5-9B",
        base_url="http://127.0.0.1:8003/v1", api_key="EMPTY",
    )
    kwargs = fm._provider_kwargs()
    assert kwargs["api_base"] == "http://127.0.0.1:8003/v1"
    assert kwargs["api_key"] == "EMPTY"

@pytest.mark.llm
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs OPENAI_API_KEY")
def test_generate_openai_real():
    fm = FoundationModel(provider="openai", name="gpt-4.1", max_tokens=8, temperature=0)
    out = fm.generate(prompt="Reply with the single word: pong")
    assert isinstance(out, str) and len(out) > 0
