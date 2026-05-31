from pydantic import BaseModel, Field


class AssistantQuestionRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class AssistantSource(BaseModel):
    source_type: str
    title: str
    reference: str
    snippet: str


class AssistantAnswerResponse(BaseModel):
    answer: str
    confidence: float
    requires_expert_review: bool
    sources: list[AssistantSource]
    safety_notice: str | None = None