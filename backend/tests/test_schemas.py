import pytest
from pydantic import ValidationError

from backend.models.schemas import ChatRequest, Scheme


def test_flat_fields_are_mapped_into_eligibility_rules():
    s = Scheme(
        scheme_id="x", title="X", description="d",
        min_age=18, max_age=35, max_income=300000, documents_required=["Aadhaar"],
    )
    assert s.eligibility_rules == {"min_age": 18, "max_age": 35, "max_income": 300000}
    assert s.required_documents == ["Aadhaar"]


def test_funding_amount_none_becomes_zero():
    assert Scheme(scheme_id="x", title="X", description="d", funding_amount=None).funding_amount == 0


def test_chat_request_rejects_too_short_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="hi")
