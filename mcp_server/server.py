"""DocForge MCP Server — Professional Document Generator."""

import sys
import os
import uuid
import json
import time
import hashlib
import threading

# Add parent dir to path so core/ is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import BaseModel, Field
from fastmcp import FastMCP
from core.engine import DocForgeEngine

mcp = FastMCP("DocForge")
engine = DocForgeEngine()


# ── File storage for generated PDFs ───────────────────────────────────────

_STORAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".generated")
os.makedirs(_STORAGE_DIR, exist_ok=True)

# Track files for cleanup (remove after 1 hour)
_FILE_REGISTRY: dict[str, float] = {}
_CLEANUP_INTERVAL = 3600  # 1 hour


def _store_pdf(pdf_bytes: bytes, filename: str) -> str:
    """Store PDF to disk, return the file ID."""
    file_id = hashlib.sha256(f"{filename}{time.time()}{uuid.uuid4()}".encode()).hexdigest()[:16]
    safe_name = filename.replace(" ", "_").replace("/", "-")
    stored_name = f"{file_id}_{safe_name}"
    filepath = os.path.join(_STORAGE_DIR, stored_name)

    with open(filepath, "wb") as f:
        f.write(pdf_bytes)

    _FILE_REGISTRY[stored_name] = time.time()
    return file_id, stored_name, len(pdf_bytes)


def _cleanup_old_files():
    """Remove files older than 1 hour."""
    now = time.time()
    to_remove = []
    for name, created_at in _FILE_REGISTRY.items():
        if now - created_at > _CLEANUP_INTERVAL:
            filepath = os.path.join(_STORAGE_DIR, name)
            try:
                os.remove(filepath)
            except OSError:
                pass
            to_remove.append(name)
    for name in to_remove:
        del _FILE_REGISTRY[name]


def _build_response(doc_type: str, doc_id: str, filename: str, stored_name: str, size: int, pdf_bytes: bytes) -> str:
    """Build a clean JSON response for the AI client."""
    _cleanup_old_files()

    import base64
    b64_data = base64.b64encode(pdf_bytes).decode()
    data_uri = f"data:application/pdf;base64,{b64_data}"

    response = {
        "success": True,
        "document_type": doc_type,
        "file_name": filename,
        "mime_type": "application/pdf",
        "size_bytes": size,
        "download_link": data_uri,
        "message": f"{doc_type.replace('_', ' ').title()} generated successfully ({size:,} bytes). Open the download_link to view the PDF.",
    }
    return json.dumps(response)


# ── Typed models for MCP tool parameters ──────────────────────────────────

class InvoiceItem(BaseModel):
    """A single line item on an invoice, receipt, quote, or credit note."""
    description: str = Field(..., description="What was sold or delivered, e.g. 'Web Development - Frontend'")
    quantity: float = Field(1.0, description="Number of units, e.g. 10")
    unit_price: float = Field(..., description="Price per unit in the document currency, e.g. 150.00")


class DeliveryItem(BaseModel):
    """A single item on a delivery note."""
    description: str = Field(..., description="Item being delivered, e.g. 'Server Equipment'")
    quantity: float = Field(1.0, description="Number of units delivered, e.g. 2")
    unit: str = Field("pcs", description="Unit of measurement: pcs, kg, boxes, pallets, etc.")


class Milestone(BaseModel):
    """A project milestone with payment amount."""
    name: str = Field(..., description="Milestone name, e.g. 'Phase 1 - Design'")
    description: str = Field("", description="Optional details about the milestone")
    due_date: str = Field("", description="Due date in YYYY-MM-DD format")
    amount: float = Field(0.0, description="Payment amount for this milestone")


# ── Safe value helpers (Field defaults may not resolve in direct calls) ────

def _s(val, default="") -> str:
    return val if isinstance(val, str) else default

def _f(val, default=0.0) -> float:
    return float(val) if isinstance(val, (int, float)) else default

def _items(items_list) -> list[dict]:
    return [i.model_dump() if hasattr(i, "model_dump") else i for i in items_list]


# ── Helper to generate + store + respond ──────────────────────────────────

def _generate_and_respond(doc_type: str, data: dict, filename: str) -> str:
    """Generate PDF, store it, return clean JSON response with data URI."""
    pdf_bytes = engine.generate(doc_type, data)
    doc_id, stored_name, size = _store_pdf(pdf_bytes, filename)
    return _build_response(doc_type, doc_id, filename, stored_name, size, pdf_bytes)


# ── FREE TOOLS ────────────────────────────────────────────────────────────

@mcp.tool()
def generate_invoice(
    company_name: str = Field(..., description="Your company or business name"),
    company_address: str = Field(..., description="Your company full address"),
    client_name: str = Field(..., description="Client or customer name"),
    client_address: str = Field(..., description="Client full address"),
    invoice_number: str = Field(..., description="Unique invoice number, e.g. INV-2026-001"),
    invoice_date: str = Field(..., description="Invoice date in YYYY-MM-DD format, e.g. 2026-04-03"),
    items: list[InvoiceItem] = Field(..., description="List of line items. Each item MUST have 'description' (str), 'quantity' (number), and 'unit_price' (number)."),
    currency: str = Field("EUR", description="Currency code: EUR, USD, GBP, CHF, CAD, AUD, JPY, or MXN"),
    tax_rate: float = Field(21.0, description="Tax rate as percentage, e.g. 21.0 for 21% VAT"),
    discount_percent: float = Field(0.0, description="Discount percentage applied to subtotal, 0-100"),
    due_date: str = Field("", description="Payment due date in YYYY-MM-DD format"),
    company_tax_id: str = Field("", description="Your tax ID (NIF/CIF/VAT number)"),
    company_email: str = Field("", description="Your company email"),
    client_tax_id: str = Field("", description="Client tax ID"),
    client_email: str = Field("", description="Client email"),
    notes: str = Field("", description="Additional notes shown at bottom of invoice"),
    payment_terms: str = Field("", description="Payment terms, e.g. 'Net 30'"),
    bank_details: str = Field("", description="Bank details for payment (IBAN, BIC, bank name)"),
    language: str = Field("en", description="Document language: 'en' for English, 'es' for Spanish"),
) -> str:
    """Generate a professional invoice as PDF. Returns a download URL for the PDF file.

    Example items: [{"description": "Web Development", "quantity": 10, "unit_price": 150.00}]
    """
    data = {
        "company": {"name": company_name, "address": company_address, "tax_id": _s(company_tax_id), "email": _s(company_email)},
        "client": {"name": client_name, "address": client_address, "tax_id": _s(client_tax_id), "email": _s(client_email)},
        "invoice_number": invoice_number, "invoice_date": invoice_date, "due_date": _s(due_date),
        "items": _items(items), "currency": _s(currency, "EUR"), "tax_rate": _f(tax_rate, 21.0),
        "discount_percent": _f(discount_percent), "notes": _s(notes),
        "payment_terms": _s(payment_terms), "bank_details": _s(bank_details), "language": _s(language, "en"),
    }
    return _generate_and_respond("invoice", data, f"invoice-{invoice_number}.pdf")


@mcp.tool()
def generate_receipt(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    receipt_number: str = Field(..., description="Receipt number, e.g. REC-2026-001"),
    receipt_date: str = Field(..., description="Receipt date YYYY-MM-DD"),
    items: list[InvoiceItem] = Field(..., description="Items paid for. Each MUST have 'description', 'quantity', 'unit_price'."),
    payment_method: str = Field("Bank Transfer", description="Payment method: Bank Transfer, Credit Card, PayPal, Cash, etc."),
    currency: str = Field("EUR", description="Currency code: EUR, USD, GBP"),
    tax_rate: float = Field(21.0, description="Tax rate percentage"),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    notes: str = Field("", description="Additional notes"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a payment receipt PDF marked as PAID. Returns a download URL.

    Example items: [{"description": "Consulting Services", "quantity": 1, "unit_price": 500.00}]
    """
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "receipt_number": receipt_number, "receipt_date": receipt_date,
        "payment_method": _s(payment_method, "Bank Transfer"),
        "items": _items(items), "currency": _s(currency, "EUR"),
        "tax_rate": _f(tax_rate, 21.0), "notes": _s(notes), "language": _s(language, "en"),
    }
    return _generate_and_respond("receipt", data, f"receipt-{receipt_number}.pdf")


@mcp.tool()
def generate_quote(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    quote_number: str = Field(..., description="Quote number, e.g. QT-2026-001"),
    quote_date: str = Field(..., description="Quote date YYYY-MM-DD"),
    valid_until: str = Field(..., description="Quote expiry date YYYY-MM-DD"),
    items: list[InvoiceItem] = Field(..., description="Quoted items. Each MUST have 'description', 'quantity', 'unit_price'."),
    currency: str = Field("EUR", description="Currency code"),
    tax_rate: float = Field(21.0, description="Tax rate percentage"),
    discount_percent: float = Field(0.0, description="Discount percentage 0-100"),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    notes: str = Field("", description="Additional notes"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a quote/estimate PDF with validity date. Returns a download URL.

    Example items: [{"description": "Website Redesign", "quantity": 1, "unit_price": 5000.00}]
    """
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "quote_number": quote_number, "quote_date": quote_date, "valid_until": valid_until,
        "items": _items(items), "currency": _s(currency, "EUR"), "tax_rate": _f(tax_rate, 21.0),
        "discount_percent": _f(discount_percent), "notes": _s(notes), "language": _s(language, "en"),
    }
    return _generate_and_respond("quote", data, f"quote-{quote_number}.pdf")


@mcp.tool()
def list_templates() -> str:
    """List all available document templates and their required fields."""
    return """Available Document Templates:

1. **Invoice** (Factura) — generate_invoice
   Required: company_name, company_address, client_name, client_address, invoice_number, invoice_date, items
   Items format: [{"description": "...", "quantity": 10, "unit_price": 100.00}]

2. **Receipt** (Recibo) — generate_receipt
   Required: company_name, client_name, receipt_number, receipt_date, items
   Items format: same as invoice

3. **Quote** (Presupuesto) — generate_quote
   Required: company_name, client_name, quote_number, quote_date, valid_until, items
   Items format: same as invoice

4. **Proposal** (Propuesta) — generate_proposal
   Required: company_name, client_name, project_title, proposal_date, summary, scope, timeline, investment

5. **Statement of Work** (SOW) — generate_sow
   Required: company_name, client_name, project_title, sow_date, description, deliverables
   Deliverables: ["Deliverable 1", "Deliverable 2"]
   Milestones: [{"name": "Phase 1", "due_date": "2026-05-01", "amount": 5000}]

6. **Delivery Note** (Albarán) — generate_delivery_note
   Required: company_name, client_name, delivery_number, delivery_date, items
   Items: [{"description": "Item", "quantity": 2, "unit": "boxes"}]

7. **Credit Note** (Nota de Crédito) — generate_credit_note
   Required: company_name, client_name, credit_note_number, credit_note_date, original_invoice, reason, items
   Items format: same as invoice"""


@mcp.tool()
def preview_document(doc_type: str = Field(..., description="Document type: invoice, receipt, quote, proposal, sow, delivery_note, or credit_note"), data: dict = Field(..., description="Document data matching the template fields. Use list_templates to see required fields.")) -> str:
    """Preview a document as HTML without generating PDF. Use list_templates first to see required fields."""
    return engine.preview(doc_type, data)


# ── PRO TOOLS ─────────────────────────────────────────────────────────────

@mcp.tool()
def generate_proposal(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    project_title: str = Field(..., description="Title of the proposed project"),
    proposal_date: str = Field(..., description="Proposal date YYYY-MM-DD"),
    summary: str = Field(..., description="Executive summary of the project (1-3 paragraphs)"),
    scope: str = Field(..., description="Detailed scope of work description"),
    timeline: str = Field(..., description="Project timeline, e.g. '8 weeks' or detailed phases"),
    investment: str = Field(..., description="Total price/investment, e.g. '15,000 EUR'"),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    conditions: str = Field("", description="Terms and conditions text"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a project proposal PDF. Returns a download URL. PRO feature."""
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "project_title": project_title, "proposal_date": proposal_date,
        "summary": summary, "scope": scope, "timeline": timeline,
        "investment": investment, "conditions": _s(conditions), "language": _s(language, "en"),
    }
    safe_title = project_title.replace(" ", "-")[:30]
    return _generate_and_respond("proposal", data, f"proposal-{safe_title}.pdf")


@mcp.tool()
def generate_sow(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    project_title: str = Field(..., description="Project title"),
    sow_date: str = Field(..., description="SOW date YYYY-MM-DD"),
    description: str = Field(..., description="Full project description"),
    deliverables: list[str] = Field(..., description="List of deliverable descriptions, e.g. ['API endpoints', 'Documentation', 'Tests']"),
    milestones: list[Milestone] = Field(default_factory=list, description="Optional milestones. Each has 'name' (str), 'due_date' (str), 'amount' (number)."),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    acceptance_criteria: str = Field("", description="Criteria for accepting deliverables"),
    currency: str = Field("EUR", description="Currency code"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a Statement of Work PDF with deliverables and milestones. Returns a download URL. PRO feature.

    Example milestones: [{"name": "Phase 1", "due_date": "2026-05-01", "amount": 5000}]
    """
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "project_title": project_title, "sow_date": sow_date,
        "description": description, "deliverables": deliverables,
        "milestones": [m.model_dump() if hasattr(m, "model_dump") else m for m in (milestones or [])],
        "acceptance_criteria": _s(acceptance_criteria),
        "currency": _s(currency, "EUR"), "language": _s(language, "en"),
    }
    safe_title = project_title.replace(" ", "-")[:30]
    return _generate_and_respond("sow", data, f"sow-{safe_title}.pdf")


@mcp.tool()
def generate_delivery_note(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    delivery_number: str = Field(..., description="Delivery note number, e.g. DN-2026-001"),
    delivery_date: str = Field(..., description="Delivery date YYYY-MM-DD"),
    items: list[DeliveryItem] = Field(..., description="Items delivered. Each MUST have 'description' (str), 'quantity' (number), 'unit' (str like 'pcs', 'kg', 'boxes')."),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    invoice_reference: str = Field("", description="Related invoice number"),
    notes: str = Field("", description="Additional notes"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a delivery note/packing slip PDF with signature field. Returns a download URL. PRO feature.

    Example items: [{"description": "Server Equipment", "quantity": 2, "unit": "pcs"}]
    """
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "delivery_number": delivery_number, "delivery_date": delivery_date,
        "invoice_reference": _s(invoice_reference),
        "items": _items(items), "notes": _s(notes), "language": _s(language, "en"),
    }
    return _generate_and_respond("delivery_note", data, f"delivery-note-{delivery_number}.pdf")


@mcp.tool()
def generate_credit_note(
    company_name: str = Field(..., description="Your company name"),
    client_name: str = Field(..., description="Client name"),
    credit_note_number: str = Field(..., description="Credit note number, e.g. CN-2026-001"),
    credit_note_date: str = Field(..., description="Credit note date YYYY-MM-DD"),
    original_invoice: str = Field(..., description="Original invoice number being credited, e.g. INV-2026-001"),
    reason: str = Field(..., description="Reason for the credit, e.g. 'Overcharge on consulting hours'"),
    items: list[InvoiceItem] = Field(..., description="Items being credited. Each MUST have 'description', 'quantity', 'unit_price'."),
    currency: str = Field("EUR", description="Currency code"),
    tax_rate: float = Field(21.0, description="Tax rate percentage"),
    company_address: str = Field("", description="Company address"),
    client_address: str = Field("", description="Client address"),
    language: str = Field("en", description="'en' or 'es'"),
) -> str:
    """Generate a credit note PDF referencing an original invoice. Returns a download URL. PRO feature.

    Example items: [{"description": "Overcharged hours", "quantity": 5, "unit_price": 100.00}]
    """
    data = {
        "company": {"name": company_name, "address": _s(company_address)},
        "client": {"name": client_name, "address": _s(client_address)},
        "credit_note_number": credit_note_number, "credit_note_date": credit_note_date,
        "original_invoice": original_invoice, "reason": reason,
        "items": _items(items), "currency": _s(currency, "EUR"),
        "tax_rate": _f(tax_rate, 21.0), "language": _s(language, "en"),
    }
    return _generate_and_respond("credit_note", data, f"credit-note-{credit_note_number}.pdf")


# ── File serving (for download URLs) ─────────────────────────────────────

@mcp.custom_route("/files/{filename}", methods=["GET"])
async def serve_file(request):
    """Serve generated PDF files for download."""
    from starlette.responses import Response as StarletteResponse

    filename = request.path_params.get("filename", "")
    filepath = os.path.join(_STORAGE_DIR, filename)

    if not os.path.exists(filepath) or ".." in filename:
        return StarletteResponse(
            content=json.dumps({"error": "file_not_found", "message": "File not found or expired."}),
            status_code=404,
            media_type="application/json",
        )

    with open(filepath, "rb") as f:
        pdf_data = f.read()

    return StarletteResponse(
        content=pdf_data,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename.split("_", 1)[-1] if "_" in filename else filename}"',
            "Content-Length": str(len(pdf_data)),
        },
    )


if __name__ == "__main__":
    import os as _os
    transport = _os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "streamable-http":
        mcp.run(transport="streamable-http", host="0.0.0.0", port=int(_os.getenv("PORT", "8080")))
    elif transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=int(_os.getenv("PORT", "8080")))
    else:
        mcp.run()
