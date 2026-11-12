from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=3)
    language: str = "en"
    session_id: str | None = None
    stream: bool = True


class AgentStep(BaseModel):
    agent: str
    status: str
    message: str
    data: dict[str, Any] | None = None


class UserProfile(BaseModel):
    age: int | None = None
    gender: str | None = None
    state: str | None = None
    district: str | None = None
    income_annual: int | None = None
    caste_category: str | None = None
    occupation: str | None = None
    education: str | None = None
    business_intent: str | None = None
    existing_business: bool | None = None
    has_bank_account: bool | None = None
    disabilities: bool | None = None
    minority: bool | None = None


class Scheme(BaseModel):
    scheme_id: str
    title: str
    description: str
    category: list[str] = Field(default_factory=list)
    eligibility_rules: dict[str, Any] = Field(default_factory=dict)
    funding_amount: int = 0
    deadline: str | None = None
    required_documents: list[str] = Field(default_factory=list)
    application_url: str | None = None

    # Flat fields from the new JSON format — ignored after mapping
    ministry: str | None = None
    state: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    max_income: int | None = None
    documents_required: list[str] = Field(default_factory=list)
    target_group: list[str] = Field(default_factory=list)

    model_config = {"extra": "ignore"}

    @field_validator("funding_amount", mode="before")
    @classmethod
    def coerce_funding_amount(cls, v: Any) -> int:
        if v is None:
            return 0
        return int(v)

    @model_validator(mode="after")
    def _map_flat_fields(self) -> Scheme:
        if not self.eligibility_rules:
            rules: dict[str, Any] = {}
            if self.min_age is not None:
                rules["min_age"] = self.min_age
            if self.max_age is not None:
                rules["max_age"] = self.max_age
            if self.max_income is not None:
                rules["max_income"] = self.max_income
            self.eligibility_rules = rules
        if not self.required_documents and self.documents_required:
            self.required_documents = self.documents_required
        return self


class SchemeResult(BaseModel):
    scheme_id: str
    title: str
    funding_amount: int
    eligibility: str
    confidence: int
    reasoning: str
    category: list[str] = Field(default_factory=list)
    deadline: str | None = None


class ChatResponse(BaseModel):
    profile: UserProfile
    results: list[SchemeResult]
    steps: list[AgentStep] = Field(default_factory=list)
    language: str = "en"


class ApplicationRequest(BaseModel):
    user_id: str
    scheme_id: str
    form_data: dict[str, Any]
    notify_phone: str | None = None
    user_profile: dict[str, Any] | None = None


class ApplicationResponse(BaseModel):
    application_id: str
    status: str
    message: str
    whatsapp_sent: bool
    persisted: bool = False
    next_steps: str | None = None


class ProfileFormRequest(BaseModel):
    scheme_id: str
    user_profile: dict[str, Any]
