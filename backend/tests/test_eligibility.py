from backend.agents.eligibility import EligibilityAgent
from backend.models.schemas import Scheme, UserProfile


def _scheme(**kw) -> Scheme:
    base = dict(scheme_id="s1", title="Test Scheme", description="d", funding_amount=50000)
    base.update(kw)
    return Scheme(**base)


def test_age_outside_range_scores_lower_than_inside():
    agent = EligibilityAgent()
    scheme = _scheme(min_age=18, max_age=35)
    inside = agent.run(UserProfile(age=25), [scheme])[0]
    outside = agent.run(UserProfile(age=60), [scheme])[0]
    assert inside.confidence > outside.confidence
    assert "above max age" in outside.reasoning


def test_results_sorted_by_confidence_desc():
    agent = EligibilityAgent()
    good = _scheme(scheme_id="good", min_age=18, max_age=40)
    bad = _scheme(scheme_id="bad", min_age=50, max_age=60)
    results = agent.run(UserProfile(age=22), [bad, good])
    assert [r.scheme_id for r in results] == ["good", "bad"]


def test_eligibility_label_is_valid():
    result = EligibilityAgent().run(UserProfile(age=22), [_scheme()])[0]
    assert result.eligibility in {"yes", "likely", "no"}
    assert isinstance(result.confidence, int)
