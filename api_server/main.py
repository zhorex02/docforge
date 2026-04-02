"""DocForge REST API — FastAPI application."""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_server.routes import documents, health

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

app = FastAPI(
    title="DocForge API",
    version="1.0.0",
    description="Generate professional business documents (invoices, receipts, quotes, proposals, SOWs) as PDF via API.",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(documents.router)
app.include_router(health.router)


@app.get("/")
async def root():
    return {
        "name": "DocForge API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "POST /v1/{doc_type} — Generate PDF (invoice, receipt, quote, proposal, sow, delivery_note, credit_note)",
            "POST /v1/{doc_type}/preview — HTML preview",
            "GET /v1/templates — List available templates",
            "GET /v1/health — Health check",
        ],
    }
