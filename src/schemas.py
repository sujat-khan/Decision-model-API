"""Pydantic schemas for OpenRouter System One decision models."""
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field

class NoulQuestion(BaseModel):
    """Boolean / Yes-No decision question returning probability of True."""
    type: Literal["noul"] = "noul"
    instructions: str = Field(..., description="Prompt or condition to evaluate")
    criteria: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional descriptions for 'true' and 'false' conditions"
    )

class ChoiceQuestion(BaseModel):
    """Multiple choice categorical decision question."""
    type: Literal["choice"] = "choice"
    instructions: str = Field(..., description="Prompt or classification query")
    criteria: Dict[str, str] = Field(
        ...,
        description="Mapping of choice keys to their definitions/rubric"
    )

class ScoreQuestion(BaseModel):
    """Ordered scale decision question returning weighted score."""
    type: Literal["score"] = "score"
    instructions: str = Field(..., description="Prompt or evaluation query")
    criteria: List[str] = Field(
        ...,
        description="Ordered list of criteria from lowest (0) to highest"
    )

class NoulAnswer(BaseModel):
    """Answer for a noul question."""
    type: Literal["noul"] = "noul"
    noul: float = Field(..., ge=0.0, le=1.0, description="Probability of True (0.0 to 1.0)")

class ChoiceAnswer(BaseModel):
    """Answer for a choice question."""
    type: Literal["choice"] = "choice"
    choice: str = Field(..., description="Selected choice option")
    confidence: Optional[float] = Field(None, description="Confidence in chosen option")
    probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Probability distribution across all options"
    )

class ScoreAnswer(BaseModel):
    """Answer for a score question."""
    type: Literal["score"] = "score"
    score: float = Field(..., description="Probability-weighted position on scale")
    confidence: Optional[float] = Field(None, description="Confidence in score")
    probabilities: Optional[Dict[str, float]] = Field(
        default=None,
        description="Probabilities across ordinal buckets"
    )
    legend: Optional[Dict[str, str]] = Field(
        default=None,
        description="Ordinal bucket index to criteria mapping"
    )

class UsageInfo(BaseModel):
    """Token and cost usage information."""
    input_tokens: Optional[int] = 0
    output_tokens: Optional[int] = 0
    cost: Optional[float] = 0.0

class SystemOneRequest(BaseModel):
    """Payload for OpenRouter System One API."""
    model: str = Field(..., description="Model ID, e.g. inception/mercury-decide:free")
    state: Union[str, Dict[str, Any]] = Field(
        ...,
        description="State to evaluate: plain text string or JSON object"
    )
    questions: Dict[str, Any] = Field(
        ...,
        description="Map of question IDs to question definitions"
    )

class SystemOneResponse(BaseModel):
    """Response returned from OpenRouter System One API."""
    id: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    answers: Dict[str, Any] = Field(default_factory=dict)
    usage: Optional[UsageInfo] = None
    latency_ms: Optional[float] = None
    raw: Optional[Dict[str, Any]] = None
