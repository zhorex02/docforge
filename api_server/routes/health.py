"""Health and info endpoints."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter
from core.engine import DocForgeEngine

router = APIRouter(tags=["health"])
engine = DocForgeEngine()


@router.get("/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@router.get("/v1/templates")
async def templates():
    return engine.list_templates()
