import os
import shutil
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.document import FinancialDocument, DocumentChunk
from backend.app.schemas.document import (
    DocumentOut,
    OCRUploadResponse,
    BankStatementParseResponse,
    DocumentIngestionResponse,
    ConfirmCandidatesRequest,
    ConfirmCandidatesResponse
)
from backend.app.services.ingestion.document_service import document_service
from backend.app.api.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialDocument)
        .filter(FinancialDocument.user_id == current_user.id)
        .order_by(FinancialDocument.created_at.desc())
    )
    return res.scalars().all()

@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialDocument).filter(
            FinancialDocument.id == doc_id,
            FinancialDocument.user_id == current_user.id
        )
    )
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    return doc

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialDocument).filter(
            FinancialDocument.id == doc_id,
            FinancialDocument.user_id == current_user.id
        )
    )
    doc = res.scalars().first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or access denied"
        )
    if doc.storage_path and os.path.exists(doc.storage_path):
        try:
            os.remove(doc.storage_path)
        except Exception as e:
            pass

    await db.delete(doc)
    await db.commit()
    return {"message": "Document deleted successfully"}

@router.post("/upload/receipt", response_model=OCRUploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest receipt or payment screenshot (PNG, JPG, WebP) with OCR and confidence scoring.
    """
    res = await document_service.process_receipt_or_screenshot(file, current_user.id, db)
    return res

@router.post("/upload/bank-statement", response_model=BankStatementParseResponse)
async def upload_bank_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest PDF or CSV bank statement with tabular extraction and candidate generation.
    """
    res = await document_service.process_bank_statement(file, current_user.id, db)
    return res

@router.post("/{doc_id}/confirm", response_model=ConfirmCandidatesResponse)
async def confirm_document_candidates(
    doc_id: str,
    payload: ConfirmCandidatesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Confirm and commit reviewed/edited candidate transactions into the primary financial ledger.
    """
    res = await document_service.confirm_and_commit_candidates(
        doc_id=doc_id,
        user_id=current_user.id,
        candidates=payload.transactions,
        db=db
    )
    return res

from backend.app.services.ai.rag_engine import rag_engine
from backend.app.schemas.document import (
    KnowledgeDocumentOut,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeChunkOut
)

@router.post("/knowledge/upload")
async def upload_knowledge_document(
    file: UploadFile = File(...),
    source_title: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    safe_name = document_service.sanitize_filename(file.filename or "financial_guide.pdf")
    file_bytes = await file.read()
    
    doc = await rag_engine.ingest_knowledge_file(
        db=db,
        user_id=current_user.id,
        filename=safe_name,
        file_bytes=file_bytes,
        source_title=source_title,
        author=author
    )
    meta = doc.parsed_metadata or {}
    return {
        "message": f"Successfully ingested and indexed '{meta.get('source_title', safe_name)}' into your personal RAG knowledge base.",
        "document_id": doc.id,
        "source_title": meta.get("source_title", safe_name),
        "author": meta.get("author", "User Upload"),
        "total_pages": meta.get("total_pages", 1),
        "total_chunks": meta.get("total_chunks", 0)
    }

@router.get("/knowledge/list")
async def list_knowledge_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        select(FinancialDocument).filter(
            FinancialDocument.user_id == current_user.id,
            FinancialDocument.file_type == "financial_knowledge",
            FinancialDocument.is_deleted == False
        ).order_by(FinancialDocument.created_at.desc())
    )
    docs = res.scalars().all()
    results = []
    for d in docs:
        meta = d.parsed_metadata or {}
        results.append({
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size_bytes": d.file_size_bytes,
            "total_chunks": meta.get("total_chunks", 0),
            "source_title": meta.get("source_title", d.filename),
            "author": meta.get("author", "User Upload"),
            "created_at": d.created_at
        })
    return results

@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    req: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await rag_engine.retrieve_user_knowledge(
        db=db,
        user_id=current_user.id,
        query=req.query,
        top_k=req.top_k or 3,
        relevance_threshold=req.relevance_threshold or 0.20
    )
    return {
        "query": res["query"],
        "results_count": res["results_count"],
        "chunks": res["chunks"],
        "answer_supported": res["answer_supported"],
        "grounded_summary": res["message"]
    }

@router.post("/upload/book")
async def upload_financial_book(
    file: UploadFile = File(...),
    title: str = Form("Financial Guide"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    safe_name = document_service.sanitize_filename(file.filename or f"{title}.pdf")
    file_bytes = await file.read()
    doc = await rag_engine.ingest_knowledge_file(
        db=db,
        user_id=current_user.id,
        filename=safe_name,
        file_bytes=file_bytes,
        source_title=title,
        author="User Library"
    )
    return {"message": f"'{title}' successfully uploaded and indexed into knowledge base for AI RAG.", "document_id": doc.id}
