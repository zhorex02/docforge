"""DocForge MCP Server — Professional Document Generator."""

import sys
import os
import base64

# Add parent dir to path so core/ is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from core.engine import DocForgeEngine
from core.models import DOCUMENT_TYPES

mcp = FastMCP("DocForge")
engine = DocForgeEngine()


# ── FREE TOOLS ────────────────────────────────────────────────────────────

@mcp.tool()
def generate_invoice(
    company_name: str,
    company_address: str,
    client_name: str,
    client_address: str,
    invoice_number: str,
    invoice_date: str,
    items: list[dict],
    currency: str = "EUR",
    tax_rate: float = 21.0,
    discount_percent: float = 0.0,
    due_date: str = "",
    company_tax_id: str = "",
    company_email: str = "",
    client_tax_id: str = "",
    client_email: str = "",
    notes: str = "",
    payment_terms: str = "",
    bank_details: str = "",
    language: str = "en",
) -> str:
    """Generate a professional invoice PDF. Returns base64-encoded PDF.

    Args:
        company_name: Your company name
        company_address: Your company address
        client_name: Client's name
        client_address: Client's address
        invoice_number: Invoice number (e.g., INV-2026-001)
        invoice_date: Invoice date (YYYY-MM-DD)
        items: List of items, each with 'description', 'quantity', 'unit_price'
        currency: Currency code (EUR, USD, GBP, etc.)
        tax_rate: Tax rate percentage (default 21%)
        discount_percent: Discount percentage (0-100)
        due_date: Payment due date
        company_tax_id: Company tax ID (NIF/CIF/VAT)
        company_email: Company email
        client_tax_id: Client tax ID
        client_email: Client email
        notes: Additional notes
        payment_terms: Payment terms text
        bank_details: Bank details for payment
        language: 'en' for English, 'es' for Spanish
    """
    data = {
        "company": {"name": company_name, "address": company_address, "tax_id": company_tax_id, "email": company_email},
        "client": {"name": client_name, "address": client_address, "tax_id": client_tax_id, "email": client_email},
        "invoice_number": invoice_number, "invoice_date": invoice_date, "due_date": due_date,
        "items": items, "currency": currency, "tax_rate": tax_rate, "discount_percent": discount_percent,
        "notes": notes, "payment_terms": payment_terms, "bank_details": bank_details, "language": language,
    }
    pdf_bytes = engine.generate("invoice", data)
    return f"PDF generated successfully ({len(pdf_bytes):,} bytes). Base64 data:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def generate_receipt(
    company_name: str,
    client_name: str,
    receipt_number: str,
    receipt_date: str,
    items: list[dict],
    payment_method: str = "Bank Transfer",
    currency: str = "EUR",
    tax_rate: float = 21.0,
    company_address: str = "",
    client_address: str = "",
    notes: str = "",
    language: str = "en",
) -> str:
    """Generate a payment receipt PDF marked as PAID. Returns base64-encoded PDF.

    Args:
        company_name: Your company name
        client_name: Client's name
        receipt_number: Receipt number
        receipt_date: Receipt date (YYYY-MM-DD)
        items: List of items with 'description', 'quantity', 'unit_price'
        payment_method: How payment was made (Bank Transfer, Credit Card, etc.)
        currency: Currency code
        tax_rate: Tax percentage
        company_address: Company address
        client_address: Client address
        notes: Additional notes
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "receipt_number": receipt_number, "receipt_date": receipt_date,
        "payment_method": payment_method, "items": items,
        "currency": currency, "tax_rate": tax_rate, "notes": notes, "language": language,
    }
    pdf_bytes = engine.generate("receipt", data)
    return f"Receipt PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def generate_quote(
    company_name: str,
    client_name: str,
    quote_number: str,
    quote_date: str,
    valid_until: str,
    items: list[dict],
    currency: str = "EUR",
    tax_rate: float = 21.0,
    discount_percent: float = 0.0,
    company_address: str = "",
    client_address: str = "",
    notes: str = "",
    language: str = "en",
) -> str:
    """Generate a quote/estimate PDF with validity date. Returns base64-encoded PDF.

    Args:
        company_name: Your company name
        client_name: Client's name
        quote_number: Quote number
        quote_date: Quote date
        valid_until: Expiry date for the quote
        items: List of items with 'description', 'quantity', 'unit_price'
        currency: Currency code
        tax_rate: Tax percentage
        discount_percent: Discount percentage
        company_address: Company address
        client_address: Client address
        notes: Additional notes
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "quote_number": quote_number, "quote_date": quote_date, "valid_until": valid_until,
        "items": items, "currency": currency, "tax_rate": tax_rate,
        "discount_percent": discount_percent, "notes": notes, "language": language,
    }
    pdf_bytes = engine.generate("quote", data)
    return f"Quote PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def list_templates() -> str:
    """List all available document templates and their required fields."""
    templates = engine.list_templates()
    result = "Available Document Templates:\n\n"
    for t in templates:
        result += f"- **{t['label_en']}** ({t['label_es']}) — type: `{t['type']}`\n"
    return result


@mcp.tool()
def preview_document(doc_type: str, data: dict) -> str:
    """Preview a document as HTML without generating PDF.

    Args:
        doc_type: Document type (invoice, receipt, quote, proposal, sow, delivery_note, credit_note)
        data: Document data matching the template's required fields
    """
    return engine.preview(doc_type, data)


# ── PRO TOOLS ─────────────────────────────────────────────────────────────

@mcp.tool()
def generate_proposal(
    company_name: str,
    client_name: str,
    project_title: str,
    proposal_date: str,
    summary: str,
    scope: str,
    timeline: str,
    investment: str,
    company_address: str = "",
    client_address: str = "",
    conditions: str = "",
    language: str = "en",
) -> str:
    """Generate a project proposal PDF. Returns base64-encoded PDF. PRO feature.

    Args:
        company_name: Your company name
        client_name: Client's name
        project_title: Title of the project
        proposal_date: Date of proposal
        summary: Executive summary of the project
        scope: Scope of work description
        timeline: Project timeline
        investment: Price/investment amount
        company_address: Company address
        client_address: Client address
        conditions: Terms and conditions
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "project_title": project_title, "proposal_date": proposal_date,
        "summary": summary, "scope": scope, "timeline": timeline,
        "investment": investment, "conditions": conditions, "language": language,
    }
    pdf_bytes = engine.generate("proposal", data)
    return f"Proposal PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def generate_sow(
    company_name: str,
    client_name: str,
    project_title: str,
    sow_date: str,
    description: str,
    deliverables: list[str],
    milestones: list[dict] = [],
    company_address: str = "",
    client_address: str = "",
    acceptance_criteria: str = "",
    currency: str = "EUR",
    language: str = "en",
) -> str:
    """Generate a Statement of Work PDF with milestones. Returns base64-encoded PDF. PRO feature.

    Args:
        company_name: Your company name
        client_name: Client's name
        project_title: Project title
        sow_date: SOW date
        description: Project description
        deliverables: List of deliverable descriptions
        milestones: List of milestones with 'name', 'due_date', 'amount'
        company_address: Company address
        client_address: Client address
        acceptance_criteria: Acceptance criteria text
        currency: Currency code
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "project_title": project_title, "sow_date": sow_date,
        "description": description, "deliverables": deliverables,
        "milestones": milestones, "acceptance_criteria": acceptance_criteria,
        "currency": currency, "language": language,
    }
    pdf_bytes = engine.generate("sow", data)
    return f"SOW PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def generate_delivery_note(
    company_name: str,
    client_name: str,
    delivery_number: str,
    delivery_date: str,
    items: list[dict],
    company_address: str = "",
    client_address: str = "",
    invoice_reference: str = "",
    notes: str = "",
    language: str = "en",
) -> str:
    """Generate a delivery note/packing slip PDF. Returns base64-encoded PDF. PRO feature.

    Args:
        company_name: Your company name
        client_name: Client's name
        delivery_number: Delivery note number
        delivery_date: Delivery date
        items: List of items with 'description', 'quantity', 'unit' (e.g., pcs, kg, boxes)
        company_address: Company address
        client_address: Client address
        invoice_reference: Related invoice number
        notes: Additional notes
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "delivery_number": delivery_number, "delivery_date": delivery_date,
        "invoice_reference": invoice_reference, "items": items,
        "notes": notes, "language": language,
    }
    pdf_bytes = engine.generate("delivery_note", data)
    return f"Delivery Note PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


@mcp.tool()
def generate_credit_note(
    company_name: str,
    client_name: str,
    credit_note_number: str,
    credit_note_date: str,
    original_invoice: str,
    reason: str,
    items: list[dict],
    currency: str = "EUR",
    tax_rate: float = 21.0,
    company_address: str = "",
    client_address: str = "",
    language: str = "en",
) -> str:
    """Generate a credit note PDF referencing an original invoice. Returns base64-encoded PDF. PRO feature.

    Args:
        company_name: Your company name
        client_name: Client's name
        credit_note_number: Credit note number
        credit_note_date: Credit note date
        original_invoice: Original invoice number being credited
        reason: Reason for the credit
        items: Items being credited with 'description', 'quantity', 'unit_price'
        currency: Currency code
        tax_rate: Tax percentage
        company_address: Company address
        client_address: Client address
        language: 'en' or 'es'
    """
    data = {
        "company": {"name": company_name, "address": company_address},
        "client": {"name": client_name, "address": client_address},
        "credit_note_number": credit_note_number, "credit_note_date": credit_note_date,
        "original_invoice": original_invoice, "reason": reason,
        "items": items, "currency": currency, "tax_rate": tax_rate, "language": language,
    }
    pdf_bytes = engine.generate("credit_note", data)
    return f"Credit Note PDF generated ({len(pdf_bytes):,} bytes). Base64:\n{base64.b64encode(pdf_bytes).decode()}"


if __name__ == "__main__":
    mcp.run()
