from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.chat import ChatSession, ChatMessage
from backend.app.schemas.advisor import (
    ChatMessageCreate, ChatMessageOut, ChatSessionOut,
    PhilosophyComparisonRequest, PhilosophyComparisonResponse
)
from backend.app.services.ai.agent import financial_advisor_agent
from backend.app.services.ai.gurus import guru_engine
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/sessions", response_model=List[ChatSessionOut])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(ChatSession).options(selectinload(ChatSession.messages)).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc())
    )
    return res.scalars().all()

@router.post("/chat", response_model=ChatMessageOut)
async def chat_with_advisor(
    chat_in: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Retrieve or create session
    session_id = chat_in.session_id
    if session_id:
        s_res = await db.execute(
            select(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        )
        session = s_res.scalars().first()
        if not session:
            session_id = None

    if not session_id:
        # Generate new session title from query
        title = chat_in.message[:40] + ("..." if len(chat_in.message) > 40 else "")
        session = ChatSession(
            user_id=current_user.id,
            title=title,
            persona=chat_in.persona or current_user.preferred_guru or "balanced"
        )
        db.add(session)
        await db.flush()
        session_id = session.id

    # Record user message
    user_msg = ChatMessage(
        session_id=session_id,
        sender="user",
        content=chat_in.message
    )
    db.add(user_msg)

    # Process AI Agent response via LangGraph StateGraph
    user_context = {
        "monthly_income": current_user.monthly_income,
        "currency": current_user.preferred_currency,
        "full_name": current_user.full_name
    }

    agent_result = await financial_advisor_agent.process_query(
        db=db,
        user_id=current_user.id,
        user_query=chat_in.message,
        persona=chat_in.persona or session.persona or "balanced",
        user_context=user_context
    )

    # Record assistant message
    ai_msg = ChatMessage(
        session_id=session_id,
        sender="assistant",
        content=agent_result["response"],
        tool_calls=agent_result.get("tool_calls"),
        citations=agent_result.get("citations")
    )
    db.add(ai_msg)
    await db.commit()
    await db.refresh(ai_msg)

    return ai_msg

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageOut])
async def get_session_messages(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    s_res = await db.execute(select(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id))
    session = s_res.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    res = await db.execute(
        select(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc())
    )
    return res.scalars().all()

from backend.app.schemas.advisor import (
    ChatMessageCreate, ChatMessageOut, ChatSessionOut,
    PhilosophyComparisonRequest, PhilosophyComparisonResponse,
    PhilosophyProfile, PhilosophyComparisonDetailRequest, PhilosophyComparisonDetailResponse
)

@router.get("/philosophies", response_model=List[PhilosophyProfile])
async def list_financial_philosophies(
    current_user: User = Depends(get_current_user)
):
    """
    Returns structured knowledge profiles for documented financial philosophies.
    """
    return guru_engine.list_philosophies()

@router.post("/compare", response_model=PhilosophyComparisonDetailResponse)
async def compare_financial_philosophies(
    req: PhilosophyComparisonDetailRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a structured side-by-side comparison across financial philosophies:
    - Perspectives A, B, C
    - Key differences
    - Areas of agreement
    - Balanced synthesis
    - Educational disclaimer
    """
    return guru_engine.compare_philosophies(
        question=req.question,
        philosophy_ids=req.philosophies,
        dimension=req.dimension,
        context_amount=req.context_amount
    )

@router.post("/compare-philosophies", response_model=PhilosophyComparisonResponse)
async def compare_philosophies(
    req: PhilosophyComparisonRequest,
    current_user: User = Depends(get_current_user)
):
    return guru_engine.get_guru_comparison(
        question=req.question,
        amount=req.context_amount or 0.0
    )
