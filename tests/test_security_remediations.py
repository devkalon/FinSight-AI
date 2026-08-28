import pytest
import os
import tempfile
from io import BytesIO
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import Settings
from backend.app.core.security import revoke_token, is_token_revoked, clear_revoked_tokens_for_testing
from backend.app.services.ingestion.document_service import document_service

client = TestClient(app)

def test_sec01_production_secret_validation():
    """
    SEC-01: Verify that Settings enforces secure SECRET_KEY in production.
    """
    s = Settings(ENVIRONMENT="production", SECRET_KEY="custom-secure-key-302948204820984029")
    assert s.ENVIRONMENT == "production"
    
    with pytest.raises(ValueError, match="CRITICAL SECURITY ERROR"):
        bad_settings = Settings(ENVIRONMENT="production", SECRET_KEY="super-secret-finsight-ai-jwt-key-2026-secure-token-vault")
        bad_settings.validate_security()

def test_sec02_cors_wildcard_remover():
    """
    SEC-02: Verify CORS origins do not include wildcard '*' when credentials allowed.
    """
    from backend.app.core.config import settings
    assert "*" not in settings.BACKEND_CORS_ORIGINS
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS

def test_sec03_rate_limiting_middleware():
    """
    SEC-03: Verify rate limiting headers / 429 response when exceeding rate limit.
    """
    from backend.app.main import _RATE_LIMIT_STORE
    _RATE_LIMIT_STORE.clear()
    
    # Trigger repeated requests on a rate-limited path using custom headers or client
    responses = [client.get("/api/v1/health", headers={"X-Forwarded-For": "198.51.100.1"}) for _ in range(350)]
    assert any(r.status_code == 429 for r in responses)
    _RATE_LIMIT_STORE.clear()

def test_sec04_thread_safe_token_revocation():
    """
    SEC-04: Verify token revocation tracking and revocation clearance.
    """
    clear_revoked_tokens_for_testing()
    test_token = "eyTestTokenRevocation123"
    assert not is_token_revoked(test_token)
    revoke_token(test_token)
    assert is_token_revoked(test_token)

def test_sec06_magic_bytes_file_upload_validation():
    """
    SEC-06: Verify file upload rejects spoofed files failing magic byte signatures.
    """
    # Fake PNG content (plain text instead of PNG header)
    bad_png_content = b"This is plain text pretending to be a PNG image."
    valid_png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    assert not document_service.validate_magic_bytes(bad_png_content, ".png")
    assert document_service.validate_magic_bytes(valid_png_content, ".png")

    # Fake PDF content
    bad_pdf_content = b"NOT_A_PDF_HEADER"
    valid_pdf_content = b"%PDF-1.4 Header content"
    assert not document_service.validate_magic_bytes(bad_pdf_content, ".pdf")
    assert document_service.validate_magic_bytes(valid_pdf_content, ".pdf")

def test_sec08_security_response_headers():
    """
    SEC-08: Verify security headers are returned on API responses.
    """
    res = client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in res.headers
    assert "Content-Security-Policy" in res.headers
