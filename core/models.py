"""Pydantic models for all document types."""

from pydantic import BaseModel, Field


# ── Shared ────────────────────────────────────────────────────────────────

class CompanyInfo(BaseModel):
    name: str
    address: str = ""
    tax_id: str = ""
    email: str = ""
    phone: str = ""
    logo_url: str = ""


class ClientInfo(BaseModel):
    name: str
    address: str = ""
    tax_id: str = ""
    email: str = ""


class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float
    tax_rate: float | None = None  # per-item override


# ── Invoice ───────────────────────────────────────────────────────────────

class InvoiceData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    invoice_number: str
    invoice_date: str
    due_date: str = ""
    items: list[LineItem]
    currency: str = Field("EUR", pattern="^(EUR|USD|GBP|CHF|CAD|AUD|JPY|MXN)$")
    tax_rate: float = 21.0
    discount_percent: float = Field(0.0, ge=0, le=100)
    notes: str = ""
    payment_terms: str = ""
    bank_details: str = ""
    language: str = Field("en", pattern="^(en|es)$")


# ── Receipt ───────────────────────────────────────────────────────────────

class ReceiptData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    receipt_number: str
    receipt_date: str
    payment_method: str = "Bank Transfer"
    items: list[LineItem]
    currency: str = Field("EUR", pattern="^(EUR|USD|GBP|CHF|CAD|AUD|JPY|MXN)$")
    tax_rate: float = 21.0
    notes: str = ""
    language: str = Field("en", pattern="^(en|es)$")


# ── Quote ─────────────────────────────────────────────────────────────────

class QuoteData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    quote_number: str
    quote_date: str
    valid_until: str
    items: list[LineItem]
    currency: str = Field("EUR", pattern="^(EUR|USD|GBP|CHF|CAD|AUD|JPY|MXN)$")
    tax_rate: float = 21.0
    discount_percent: float = Field(0.0, ge=0, le=100)
    notes: str = ""
    language: str = Field("en", pattern="^(en|es)$")


# ── Proposal ──────────────────────────────────────────────────────────────

class ProposalData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    project_title: str
    proposal_date: str
    summary: str
    scope: str
    timeline: str
    investment: str
    conditions: str = ""
    language: str = Field("en", pattern="^(en|es)$")
    use_ai: bool = False  # enhance summary/scope with Claude


# ── Statement of Work ─────────────────────────────────────────────────────

class MilestoneItem(BaseModel):
    name: str
    description: str = ""
    due_date: str = ""
    amount: float = 0.0


class SOWData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    project_title: str
    sow_date: str
    description: str
    deliverables: list[str]
    milestones: list[MilestoneItem] = []
    acceptance_criteria: str = ""
    currency: str = Field("EUR", pattern="^(EUR|USD|GBP|CHF|CAD|AUD|JPY|MXN)$")
    language: str = Field("en", pattern="^(en|es)$")
    use_ai: bool = False


# ── Delivery Note ─────────────────────────────────────────────────────────

class DeliveryItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit: str = "pcs"


class DeliveryNoteData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    delivery_number: str
    delivery_date: str
    invoice_reference: str = ""
    items: list[DeliveryItem]
    notes: str = ""
    language: str = Field("en", pattern="^(en|es)$")


# ── Credit Note ───────────────────────────────────────────────────────────

class CreditNoteData(BaseModel):
    company: CompanyInfo
    client: ClientInfo
    credit_note_number: str
    credit_note_date: str
    original_invoice: str
    reason: str
    items: list[LineItem]
    currency: str = Field("EUR", pattern="^(EUR|USD|GBP|CHF|CAD|AUD|JPY|MXN)$")
    tax_rate: float = 21.0
    language: str = Field("en", pattern="^(en|es)$")


# ── Template registry ─────────────────────────────────────────────────────

DOCUMENT_TYPES = {
    "invoice": {"model": InvoiceData, "label_en": "Invoice", "label_es": "Factura"},
    "receipt": {"model": ReceiptData, "label_en": "Receipt", "label_es": "Recibo"},
    "quote": {"model": QuoteData, "label_en": "Quote", "label_es": "Presupuesto"},
    "proposal": {"model": ProposalData, "label_en": "Proposal", "label_es": "Propuesta"},
    "sow": {"model": SOWData, "label_en": "Statement of Work", "label_es": "Pliego de Condiciones"},
    "delivery_note": {"model": DeliveryNoteData, "label_en": "Delivery Note", "label_es": "Albarán"},
    "credit_note": {"model": CreditNoteData, "label_en": "Credit Note", "label_es": "Nota de Crédito"},
}


CURRENCY_SYMBOLS = {
    "EUR": "€", "USD": "$", "GBP": "£", "CHF": "CHF",
    "CAD": "C$", "AUD": "A$", "JPY": "¥", "MXN": "MX$",
}
