from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, StringConstraints


class Lead(BaseModel):
    name: str
    message: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]
    source: str
    email: Optional[str] = None
    phone: Optional[str] = None


class Extracted(BaseModel):
    service_needed: Optional[str] = None
    budget: Optional[str] = None
    timeline: Optional[str] = None
    location: Optional[str] = None


class QualifyResult(BaseModel):
    intent: Literal["hot", "warm", "cold"]
    confidence: float = Field(ge=0, le=1)
    reason: str
    extracted: Extracted = Field(default_factory=Extracted)
    sms_draft: str = Field(max_length=320)


class LeadResponse(BaseModel):
    lead_id: str
    status: Literal["ok", "failed"]
    attempts: int
    result: Optional[QualifyResult] = None
    error: Optional[str] = None
