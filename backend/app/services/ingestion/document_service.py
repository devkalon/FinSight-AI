import os
import re
import uuid
from decimal import Decimal
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.config import settings
from backend.app.models.document import FinancialDocument
from backend.app.models.transaction import Transaction
from backend.app.models.category import Category
from backend.app.schemas.document import CandidateTransaction
from backend.app.services.ingestion.ocr_engine import ocr_engine
from backend.app.services.ingestion.pdf_parser import pdf_parser
from backend.app.services.ingestion.csv_parser import csv_parser
from backend.app.services.ingestion.indian_normalization import indian_normalizer

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".pdf"}
ALLOWED_STATEMENT_EXTENSIONS = {".pdf", ".csv"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

class DocumentService:
    """
    Service managing secure multi-source Indian document ingestion, MIME validation,
    OCR/PDF/CSV parsing with bank adapter routing, duplicate detection, and candidate confirmation.
    """

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        base = os.path.basename(filename)
        clean = re.sub(r'[^A-Za-z0-9_.-]', '_', base)
        return clean or f"file_{uuid.uuid4().hex[:8]}"

    async def _detect_duplicates(
        self,
        candidates: List[Dict[str, Any]],
        user_id: str,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Scans existing user transactions to detect and flag duplicates.
        """
        if not candidates:
            return candidates

        # Fetch recent user transactions for duplicate checking
        res = await db.execute(
            select(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.is_deleted == False
            )
        )
        existing_txs = res.scalars().all()
        
        # Build set of existing fingerprints and date+amount keys
        existing_keys = set()
        for tx in existing_txs:
            amt_str = f"{float(tx.amount):.2f}"
            m_str = (tx.merchant_name or "").strip().lower()
            d_str = tx.transaction_date.isoformat() if hasattr(tx.transaction_date, 'isoformat') else str(tx.transaction_date)
            existing_keys.add(f"{d_str}:{amt_str}:{m_str}")
            existing_keys.add(f"{d_str}:{amt_str}")

        # Mark duplicates on candidates
        for cand in candidates:
            cand_d = cand.get("transaction_date")
            cand_amt = f"{float(cand.get('amount', 0.0)):.2f}"
            cand_m = (cand.get("merchant_name") or "").strip().lower()

            key_full = f"{cand_d}:{cand_amt}:{cand_m}"
            key_short = f"{cand_d}:{cand_amt}"

            if key_full in existing_keys or key_short in existing_keys:
                cand["is_duplicate"] = True
                cand["duplicate_reason"] = f"Potential duplicate: existing transaction on {cand_d} for ₹{cand_amt}"
            else:
                cand["is_duplicate"] = False
                cand["duplicate_reason"] = None

        return candidates

    @staticmethod
    def validate_magic_bytes(content: bytes, ext: str) -> bool:
        if not content:
            return False
        if ext == ".pdf":
            return content.startswith(b"%PDF")
        elif ext == ".png":
            return content.startswith(b"\x89PNG")
        elif ext in {".jpg", ".jpeg"}:
            return content.startswith(b"\xff\xd8\xff")
        elif ext == ".webp":
            return len(content) > 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"
        elif ext == ".bmp":
            return content.startswith(b"BM")
        elif ext == ".csv":
            try:
                content[:1024].decode("utf-8")
                return True
            except UnicodeDecodeError:
                return False
        return True

    async def process_receipt_or_screenshot(
        self,
        file: UploadFile,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Validates, saves, and extracts candidate transactions from a receipt or payment screenshot.
        """
        safe_name = self.sanitize_filename(file.filename or "receipt.png")
        ext = os.path.splitext(safe_name)[1].lower()

        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )

        if not self.validate_magic_bytes(content, ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File validation failed: Content magic bytes do not match specified file extension '{ext}'."
            )

        saved_filename = f"{uuid.uuid4()}_{safe_name}"
        save_path = os.path.join(settings.UPLOAD_DIR, "receipts", saved_filename)
        with open(save_path, "wb") as f:
            f.write(content)

        if ext == ".pdf":
            # PDF Receipt Parsing
            pdf_res = pdf_parser.parse_bank_statement(save_path)
            candidates = pdf_res.get("candidates", [])
            avg_conf = pdf_res.get("confidence_avg", 0.93)
            ocr_result = {
                "raw_text": f"PDF Receipt parsed from {safe_name}",
                "confidence_score": avg_conf,
                "candidates": candidates,
                "redaction_stats": {}
            }
        else:
            # Process through OCR Engine
            ocr_result = ocr_engine.extract_from_image(save_path, filename=safe_name)
            candidates = ocr_result.get("candidates", [])
            avg_conf = ocr_result.get("confidence_score", 0.90)

        # Check for duplicates
        candidates = await self._detect_duplicates(candidates, user_id, db)

        # Record document in DB
        doc = FinancialDocument(
            user_id=user_id,
            filename=safe_name,
            file_type="receipt",
            file_size_bytes=len(content),
            storage_path=save_path,
            processing_status="pending_verification",
            parsed_metadata={
                "ocr_result": ocr_result,
                "candidates": candidates,
                "confidence_score": avg_conf
            }
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "file_type": "receipt",
            "processing_status": doc.processing_status,
            "total_extracted_transactions": len(candidates),
            "confidence_avg": avg_conf,
            "candidates": candidates,
            "redaction_stats": ocr_result.get("redaction_stats", {}),
            "extracted_transaction": {
                "merchant_name": ocr_result.get("merchant_name"),
                "amount": ocr_result.get("amount", 0.0),
                "currency": ocr_result.get("currency", "INR"),
                "transaction_date": ocr_result.get("transaction_date"),
                "category_suggestion": ocr_result.get("category_suggestion"),
                "subcategory": ocr_result.get("subcategory"),
                "payment_method": ocr_result.get("payment_method"),
                "raw_text": ocr_result.get("raw_text"),
                "confidence_score": avg_conf,
                "redaction_stats": ocr_result.get("redaction_stats", {})
            }
        }

    async def process_bank_statement(
        self,
        file: UploadFile,
        user_id: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Validates, saves, and parses a PDF or CSV bank statement / UPI export using Indian Bank Adapters.
        """
        safe_name = self.sanitize_filename(file.filename or "statement.pdf")
        ext = os.path.splitext(safe_name)[1].lower()

        if ext not in ALLOWED_STATEMENT_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported statement format '{ext}'. Allowed: PDF, CSV"
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )

        if not self.validate_magic_bytes(content, ext):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Statement file validation failed: Content magic bytes do not match specified file format '{ext}'."
            )

        saved_filename = f"{uuid.uuid4()}_{safe_name}"
        save_path = os.path.join(settings.UPLOAD_DIR, "statements", saved_filename)
        with open(save_path, "wb") as f:
            f.write(content)

        if ext == ".csv":
            candidates, summary = csv_parser.parse_csv_with_summary(content, filename=safe_name)
            file_type = "bank_statement_csv"
            avg_conf = 0.95
        else:
            pdf_res = pdf_parser.parse_bank_statement(save_path)
            candidates = pdf_res.get("candidates", [])
            summary = pdf_res.get("account_summary", {})
            file_type = "bank_statement_pdf"
            avg_conf = pdf_res.get("confidence_avg", 0.94)

        # Detect duplicates against user's transaction ledger
        candidates = await self._detect_duplicates(candidates, user_id, db)

        doc = FinancialDocument(
            user_id=user_id,
            filename=safe_name,
            file_type=file_type,
            file_size_bytes=len(content),
            storage_path=save_path,
            processing_status="pending_verification",
            parsed_metadata={
                "parsed_count": len(candidates),
                "summary": summary,
                "candidates": candidates,
                "confidence_score": avg_conf
            }
        )
        db.add(doc)
        await db.commit()
        await db.refresh(doc)

        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "file_type": file_type,
            "processing_status": doc.processing_status,
            "total_parsed_transactions": len(candidates),
            "total_extracted_transactions": len(candidates),
            "confidence_avg": avg_conf,
            "candidates": candidates,
            "transactions": candidates,
            "account_summary": summary
        }

    async def confirm_and_commit_candidates(
        self,
        doc_id: str,
        user_id: str,
        candidates: List[CandidateTransaction],
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Commits verified candidate transactions directly to the transactions ledger.
        """
        res = await db.execute(
            select(FinancialDocument).filter(
                FinancialDocument.id == doc_id,
                FinancialDocument.user_id == user_id
            )
        )
        doc = res.scalars().first()
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )

        cat_res = await db.execute(
            select(Category).filter(
                (Category.user_id == user_id) | (Category.user_id == None) | (Category.is_custom == False)
            )
        )
        available_categories = {c.name.lower(): c.id for c in cat_res.scalars().all()}

        created_tx_ids = []
        for cand in candidates:
            # Parse Date
            try:
                tx_date = datetime.strptime(cand.transaction_date, "%Y-%m-%d").date()
            except Exception:
                tx_date = indian_normalizer.parse_indian_date(cand.transaction_date)

            # Resolve Category ID
            cat_id = None
            if cand.category_suggestion:
                cat_id = available_categories.get(cand.category_suggestion.lower())

            # Create Transaction Entity with exact Decimal money precision
            tx = Transaction(
                user_id=user_id,
                amount=Decimal(str(round(cand.amount, 2))),
                currency=cand.currency or "INR",
                transaction_type=cand.transaction_type or "debit",
                transaction_date=tx_date,
                description=cand.description,
                merchant_name=cand.merchant_name,
                category_id=cat_id,
                subcategory=cand.subcategory,
                payment_method=cand.payment_method or "UPI",
                source=cand.source or ("ocr_receipt" if doc.file_type == "receipt" else doc.file_type),
                confidence_score=float(cand.confidence_score or 0.95),
                notes=f"Ingested from {doc.filename}",
                is_subscription=False
            )
            db.add(tx)
            await db.flush()
            created_tx_ids.append(tx.id)

        # Update document status
        doc.processing_status = "confirmed"
        if doc.parsed_metadata:
            metadata = dict(doc.parsed_metadata)
            metadata["committed_tx_ids"] = created_tx_ids
            metadata["confirmed_at"] = datetime.utcnow().isoformat()
            doc.parsed_metadata = metadata

        await db.commit()

        return {
            "document_id": doc.id,
            "committed_count": len(created_tx_ids),
            "transaction_ids": created_tx_ids,
            "message": f"Successfully committed {len(created_tx_ids)} transactions to your financial ledger."
        }

document_service = DocumentService()
