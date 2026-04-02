"""Input validation for document data."""

from pydantic import ValidationError
from core.models import DOCUMENT_TYPES


def validate_document(doc_type: str, data: dict) -> dict:
    """Validate data for a document type. Returns {"valid": True} or {"valid": False, "errors": [...]}."""
    if doc_type not in DOCUMENT_TYPES:
        return {
            "valid": False,
            "errors": [f"Unknown document type: {doc_type}. Available: {list(DOCUMENT_TYPES.keys())}"],
        }

    model_class = DOCUMENT_TYPES[doc_type]["model"]
    try:
        model_class(**data)
        return {"valid": True}
    except ValidationError as e:
        errors = []
        for err in e.errors():
            loc = " → ".join(str(x) for x in err["loc"])
            errors.append(f"{loc}: {err['msg']}")
        return {"valid": False, "errors": errors}
