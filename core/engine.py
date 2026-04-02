"""DocForge engine — central document generation logic."""

from core.models import (
    DOCUMENT_TYPES,
    InvoiceData, ReceiptData, QuoteData, ProposalData,
    SOWData, DeliveryNoteData, CreditNoteData,
)
from core.validators import validate_document
from core.pdf_generator import html_to_pdf
from core.templates.invoice import render_invoice


# Template renderers — we'll add more as we build them
_RENDERERS = {
    "invoice": lambda data: render_invoice(InvoiceData(**data)),
}


def _get_renderer(doc_type: str):
    """Lazy-import renderers to avoid circular imports and allow incremental builds."""
    if doc_type in _RENDERERS:
        return _RENDERERS[doc_type]

    # Dynamic import for templates added later
    if doc_type == "receipt":
        from core.templates.receipt import render_receipt
        _RENDERERS["receipt"] = lambda data: render_receipt(ReceiptData(**data))
    elif doc_type == "quote":
        from core.templates.quote import render_quote
        _RENDERERS["quote"] = lambda data: render_quote(QuoteData(**data))
    elif doc_type == "proposal":
        from core.templates.proposal import render_proposal
        _RENDERERS["proposal"] = lambda data: render_proposal(ProposalData(**data))
    elif doc_type == "sow":
        from core.templates.sow import render_sow
        _RENDERERS["sow"] = lambda data: render_sow(SOWData(**data))
    elif doc_type == "delivery_note":
        from core.templates.delivery_note import render_delivery_note
        _RENDERERS["delivery_note"] = lambda data: render_delivery_note(DeliveryNoteData(**data))
    elif doc_type == "credit_note":
        from core.templates.credit_note import render_credit_note
        _RENDERERS["credit_note"] = lambda data: render_credit_note(CreditNoteData(**data))
    else:
        raise ValueError(f"Unknown document type: {doc_type}")

    return _RENDERERS[doc_type]


class DocForgeEngine:
    """Main engine for generating professional business documents."""

    def generate(self, doc_type: str, data: dict) -> bytes:
        """Generate PDF bytes for a document."""
        validation = validate_document(doc_type, data)
        if not validation["valid"]:
            raise ValueError(f"Validation errors: {validation['errors']}")

        renderer = _get_renderer(doc_type)
        html = renderer(data)
        return html_to_pdf(html)

    def preview(self, doc_type: str, data: dict) -> str:
        """Return HTML preview without generating PDF."""
        validation = validate_document(doc_type, data)
        if not validation["valid"]:
            raise ValueError(f"Validation errors: {validation['errors']}")

        renderer = _get_renderer(doc_type)
        return renderer(data)

    def list_templates(self) -> list[dict]:
        """List available document templates with their fields."""
        result = []
        for doc_type, info in DOCUMENT_TYPES.items():
            model = info["model"]
            fields = {}
            for name, field in model.model_fields.items():
                fields[name] = {
                    "type": str(field.annotation),
                    "required": field.is_required(),
                    "default": field.default if not field.is_required() else None,
                }
            result.append({
                "type": doc_type,
                "label_en": info["label_en"],
                "label_es": info["label_es"],
                "fields": fields,
            })
        return result

    def validate(self, doc_type: str, data: dict) -> dict:
        """Validate data without generating. Returns errors if any."""
        return validate_document(doc_type, data)
