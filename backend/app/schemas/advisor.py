from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ChatMessageCreate(BaseModel):
    session_id: Optional[str] = None
    message: str
    persona: Optional[str] = "balanced" # 'buffett', 'kiyosaki', 'sethi', 'indian_expert', 'balanced'

class Citation(BaseModel):
    source_title: str
    author: Optional[str] = None
    relevant_quote: str
    relevance_score: float

class ToolExecutionResult(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    output: Any

class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    sender: str
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionOut(BaseModel):
    id: str
    title: str
    persona: str
    created_at: datetime
    messages: Optional[List[ChatMessageOut]] = []

    class Config:
        from_attributes = True

class PhilosophyComparisonRequest(BaseModel):
    question: str
    context_amount: Optional[float] = None

class GuruOpinion(BaseModel):
    guru_name: str
    persona_title: str
    core_philosophy: str
    recommendation: str
    action_steps: List[str]
    pros: List[str]
    cons: List[str]

class PhilosophyComparisonResponse(BaseModel):
    topic: str
    opinions: Dict[str, GuruOpinion]
    synthesized_verdict: str

class PhilosophyProfile(BaseModel):
    id: str
    name: str
    documented_foundation: str
    core_axiom: str
    primary_focus: str
    dimensions: Dict[str, str]

class PhilosophyPerspective(BaseModel):
    philosophy_id: str
    name: str
    documented_foundation: str
    core_axiom: str
    perspective: str
    actionable_steps: List[str]
    advantages: List[str]
    limitations: List[str]

class KeyDifference(BaseModel):
    dimension: str
    philosophies_comparison: Dict[str, str]
    summary: str

class PhilosophyComparisonDetailRequest(BaseModel):
    question: str
    philosophies: Optional[List[str]] = ["value_compounding", "cashflow_assets", "conscious_spending"]
    dimension: Optional[str] = "all"
    context_amount: Optional[float] = None

class PhilosophyComparisonDetailResponse(BaseModel):
    topic: str
    detected_dimension: str
    perspectives: List[PhilosophyPerspective]
    key_differences: List[KeyDifference]
    areas_of_agreement: List[str]
    balanced_synthesis: str
    educational_disclaimer: str
