def test_agents_import_and_construct(tmp_path, monkeypatch):
    from polyskill.model import fm

    monkeypatch.setattr(
        fm.FoundationModel, "generate", lambda self, **kw: "<action>noop()</action>"
    )
    from polyskill.agents.agent import VLMAgent, LLMAgent

    a = VLMAgent(
        model_configs={"main": {"provider": "openai", "name": "gpt-4.1"}},
        enable_skill_induction=True,
        skill_storage_path=str(tmp_path / "skills"),
    )
    assert isinstance(a.get_skill_statistics(), dict)
    out = a.complete_task(success=True)  # must not raise
    assert out is None or isinstance(out, dict)

    # LLMAgent should at least be importable / constructible.
    assert LLMAgent is not None
