from backend.agents.profile_extractor import ProfileExtractorAgent


class _NoLLM:
    """Stand-in for LLMService when no API key is set."""

    def generate_json(self, *_args, **_kwargs):
        return None


def test_rule_based_fallback_extracts_core_fields():
    agent = ProfileExtractorAgent(llm_service=_NoLLM())
    profile = agent.run("I am a 24 year old woman from Karnataka, I want to start a business")
    assert profile.age == 24
    assert profile.gender == "female"
    assert profile.state and "karnataka" in profile.state.lower()


def test_hindi_input_detects_gender():
    agent = ProfileExtractorAgent(llm_service=_NoLLM())
    assert agent.run("मैं एक महिला हूँ, उम्र 30").gender == "female"
