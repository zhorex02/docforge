"""Quote/Estimate template — like invoice but with validity date, no bank details."""

from core.models import QuoteData, CURRENCY_SYMBOLS

LABELS = {
    "en": {"title": "QUOTE", "to": "Quote For", "quote_num": "Quote #", "date": "Date", "valid": "Valid Until", "description": "Description", "qty": "Qty", "unit_price": "Unit Price", "amount": "Amount", "subtotal": "Subtotal", "discount": "Discount", "tax": "Tax", "total": "TOTAL", "notes": "Notes"},
    "es": {"title": "PRESUPUESTO", "to": "Presupuesto Para", "quote_num": "Presupuesto Nº", "date": "Fecha", "valid": "Válido Hasta", "description": "Descripción", "qty": "Cant.", "unit_price": "Precio Unit.", "amount": "Importe", "subtotal": "Subtotal", "discount": "Descuento", "tax": "Impuesto", "total": "TOTAL", "notes": "Notas"},
}

def _fmt(v: float, c: str) -> str:
    sym = CURRENCY_SYMBOLS.get(c, c)
    return f"{v:,.2f} {sym}" if c == "EUR" else f"{sym}{v:,.2f}"

def render_quote(data: QuoteData) -> str:
    L = LABELS.get(data.language, LABELS["en"])
    cur = data.currency
    rows = ""
    subtotal = 0.0
    for item in data.items:
        lt = item.quantity * item.unit_price
        subtotal += lt
        rows += f'<tr><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{item.description}</td><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;">{item.quantity:g}</td><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;">{_fmt(item.unit_price,cur)}</td><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;">{_fmt(lt,cur)}</td></tr>'
    disc = subtotal * (data.discount_percent / 100) if data.discount_percent > 0 else 0
    taxable = subtotal - disc
    tax = taxable * (data.tax_rate / 100)
    total = taxable + tax
    disc_row = f'<tr><td style="padding:6px 12px;text-align:right;color:#6b7280;">{L["discount"]} ({data.discount_percent:g}%)</td><td style="padding:6px 12px;text-align:right;color:#dc2626;">-{_fmt(disc,cur)}</td></tr>' if disc > 0 else ""
    co = data.company
    cl = data.client
    notes_html = f'<div style="margin-top:24px;"><div style="font-weight:600;color:#374151;margin-bottom:4px;">{L["notes"]}</div><div style="color:#6b7280;font-size:13px;white-space:pre-line;">{data.notes}</div></div>' if data.notes else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif;color:#1f2937;font-size:14px;line-height:1.5;">
<div style="max-width:210mm;margin:0 auto;padding:40px 48px;">
<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:40px;">
<div>{f'<img src="{co.logo_url}" style="max-height:60px;max-width:180px;margin-bottom:8px;" /><br/>' if co.logo_url else ''}<strong>{co.name}</strong>{f'<br/><span style="color:#6b7280;font-size:13px;">{co.address}</span>' if co.address else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{co.tax_id}</span>' if co.tax_id else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{co.email}</span>' if co.email else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{co.phone}</span>' if co.phone else ''}</div>
<div style="text-align:right;"><div style="font-size:28px;font-weight:700;color:#2563eb;letter-spacing:1px;margin-bottom:12px;">{L["title"]}</div>
<table style="margin-left:auto;border-collapse:collapse;"><tr><td style="padding:4px 0;color:#6b7280;font-size:13px;">{L["quote_num"]}</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;">{data.quote_number}</td></tr><tr><td style="padding:4px 0;color:#6b7280;font-size:13px;">{L["date"]}</td><td style="padding:4px 0 4px 16px;font-size:13px;">{data.quote_date}</td></tr><tr><td style="padding:4px 0;color:#6b7280;font-size:13px;font-weight:600;color:#dc2626;">{L["valid"]}</td><td style="padding:4px 0 4px 16px;font-size:13px;font-weight:600;color:#dc2626;">{data.valid_until}</td></tr></table></div></div>
<div style="background:#f9fafb;border-radius:8px;padding:16px 20px;margin-bottom:32px;"><div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;margin-bottom:6px;">{L["to"]}</div><strong>{cl.name}</strong>{f'<br/><span style="color:#6b7280;font-size:13px;">{cl.address}</span>' if cl.address else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{cl.tax_id}</span>' if cl.tax_id else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{cl.email}</span>' if cl.email else ''}</div>
<table style="width:100%;border-collapse:collapse;margin-bottom:24px;"><thead><tr style="background:#2563eb;color:white;"><th style="padding:10px 12px;text-align:left;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;border-radius:6px 0 0 0;">{L["description"]}</th><th style="padding:10px 12px;text-align:center;font-weight:600;font-size:12px;text-transform:uppercase;">{L["qty"]}</th><th style="padding:10px 12px;text-align:right;font-weight:600;font-size:12px;text-transform:uppercase;">{L["unit_price"]}</th><th style="padding:10px 12px;text-align:right;font-weight:600;font-size:12px;text-transform:uppercase;border-radius:0 6px 0 0;">{L["amount"]}</th></tr></thead><tbody>{rows}</tbody></table>
<div style="display:flex;justify-content:flex-end;margin-bottom:32px;"><table style="border-collapse:collapse;min-width:280px;"><tr><td style="padding:6px 12px;text-align:right;color:#6b7280;">{L["subtotal"]}</td><td style="padding:6px 12px;text-align:right;">{_fmt(subtotal,cur)}</td></tr>{disc_row}<tr><td style="padding:6px 12px;text-align:right;color:#6b7280;">{L["tax"]} ({data.tax_rate:g}%)</td><td style="padding:6px 12px;text-align:right;">{_fmt(tax,cur)}</td></tr><tr style="border-top:2px solid #2563eb;"><td style="padding:12px;text-align:right;font-size:16px;font-weight:700;color:#2563eb;">{L["total"]}</td><td style="padding:12px;text-align:right;font-size:18px;font-weight:700;color:#2563eb;">{_fmt(total,cur)}</td></tr></table></div>
{notes_html}
<div style="margin-top:48px;text-align:center;color:#d1d5db;font-size:11px;">Generated by DocForge</div>
</div></body></html>"""
