from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.assistant import AssistantAnswerResponse, AssistantQuestionRequest
from app.services.assistant_service import build_grounded_answer


router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/ask", response_model=AssistantAnswerResponse)
def ask_assistant(
    payload: AssistantQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssistantAnswerResponse:
    result = build_grounded_answer(
        question=payload.question,
        db=db,
    )

    return AssistantAnswerResponse(**result)