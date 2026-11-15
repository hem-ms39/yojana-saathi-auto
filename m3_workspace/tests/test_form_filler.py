from backend.agents.form_filler import generate_prefilled_form, list_available_forms


def test_templates_available():
    forms = list_available_forms()
    assert "pm-mudra-shishu" in forms
    assert len(forms) >= 5


def test_prefill_uses_profile_values_and_normalizes_gender():
    form = generate_prefilled_form("pm-mudra-shishu", {"name": "Asha", "gender": "F"})
    values = {f["key"]: f["value"] for f in form["fields"]}
    assert form["total_fields"] > 0
    assert form["auto_filled_count"] >= 1
    if "gender" in values:
        assert values["gender"] == "Female"


def test_unknown_scheme_returns_error_payload():
    form = generate_prefilled_form("no-such-scheme", {})
    assert form["fields"] == []
    assert "error" in form
