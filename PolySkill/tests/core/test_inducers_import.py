def test_inducer_imports_and_litellm_enum():
    from polyskill.core.inducers import LLMBasedInducer, ASIInducer, LLMProvider
    from polyskill.core.inducers.llm_inducer import LLMInducerConfig, LLMConfig
    assert hasattr(LLMProvider, "LITELLM")
    cfg = LLMInducerConfig(llm_config=LLMConfig(provider=LLMProvider.LITELLM, model_name="gpt-4.1"))
    LLMBasedInducer(cfg)  # must not raise
