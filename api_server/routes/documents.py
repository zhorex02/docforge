"""Document generation REST endpoints."""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from core.engine import DocForgeEngine
from api_server.middleware.auth import verify_api_key, increment_usage

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["documents"])
engine = DocForgeEngine()

DOC_TYPES = ["invoice", "receipt", "quote", "proposal", "sow", "delivery_note", "credit_note"]


@router.post("/{doc_type}")
async def generate_document(doc_type: str, data: dict, auth: dict = Depends(verify_api_key)):
    if doc_type not in DOC_TYPES:
        return JSONResponse(status_code=400, content={"error": "invalid_type", "message": f"Unknown type: {doc_type}. Available: {DOC_TYPES}"})
    try:
        pdf_bytes = engine.generate(doc_type, data)
        increment_usage(auth["key"])
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={doc_type}.pdf", "X-PDF-Size": str(len(pdf_bytes))},
        )
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": "validation_error", "message": str(e)})
    except Exception as e:
        logger.error("Generation failed for %s: %s", doc_type, e)
        return JSONResponse(status_code=500, content={"error": "generation_failed", "message": str(e)})


@router.post("/{doc_type}/preview")
async def preview_document(doc_type: str, data: dict, auth: dict = Depends(verify_api_key)):
    if doc_type not in DOC_TYPES:
        return JSONResponse(status_code=400, content={"error": "invalid_type", "message": f"Unknown type: {doc_type}."})
    try:
        html = engine.preview(doc_type, data)
        return Response(content=html, media_type="text/html")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": "validation_error", "message": str(e)})
