"""Statement of Work template."""

from core.models import SOWData, CURRENCY_SYMBOLS

LABELS = {
    "en": {"title": "STATEMENT OF WORK", "parties": "Parties", "provider": "Service Provider", "client_label": "Client", "date": "Date", "description": "Project Description", "deliverables": "Deliverables", "milestones": "Milestones & Payments", "milestone": "Milestone", "due": "Due Date", "amount": "Amount", "acceptance": "Acceptance Criteria", "total": "Total"},
    "es": {"title": "PLIEGO DE CONDICIONES", "parties": "Partes", "provider": "Proveedor", "client_label": "Cliente", "date": "Fecha", "description": "Descripción del Proyecto", "deliverables": "Entregables", "milestones": "Hitos y Pagos", "milestone": "Hito", "due": "Fecha", "amount": "Importe", "acceptance": "Criterios de Aceptación", "total": "Total"},
}

def _fmt(v: float, c: str) -> str:
    sym = CURRENCY_SYMBOLS.get(c, c)
    return f"{v:,.2f} {sym}" if c == "EUR" else f"{sym}{v:,.2f}"

def render_sow(data: SOWData) -> str:
    L = LABELS.get(data.language, LABELS["en"])
    co = data.company
    cl = data.client
    deliverables_html = "".join(f'<li style="margin-bottom:6px;color:#4b5563;">{d}</li>' for d in data.deliverables)
    milestones_html = ""
    if data.milestones:
        ms_rows = ""
        total = 0.0
        for m in data.milestones:
            total += m.amount
            ms_rows += f'<tr><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{m.name}{f"<br/><span style=color:#6b7280;font-size:12px;>{m.description}</span>" if m.description else ""}</td><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;">{m.due_date}</td><td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;">{_fmt(m.amount, data.currency)}</td></tr>'
        milestones_html = f'''<div style="margin-top:28px;"><h3 style="color:#2563eb;font-size:16px;margin-bottom:12px;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">{L["milestones"]}</h3>
<table style="width:100%;border-collapse:collapse;"><thead><tr style="background:#2563eb;color:white;"><th style="padding:10px 12px;text-align:left;font-weight:600;font-size:12px;text-transform:uppercase;border-radius:6px 0 0 0;">{L["milestone"]}</th><th style="padding:10px 12px;text-align:center;font-weight:600;font-size:12px;text-transform:uppercase;">{L["due"]}</th><th style="padding:10px 12px;text-align:right;font-weight:600;font-size:12px;text-transform:uppercase;border-radius:0 6px 0 0;">{L["amount"]}</th></tr></thead><tbody>{ms_rows}</tbody>
<tfoot><tr style="border-top:2px solid #2563eb;"><td colspan="2" style="padding:12px;text-align:right;font-weight:700;color:#2563eb;">{L["total"]}</td><td style="padding:12px;text-align:right;font-weight:700;font-size:16px;color:#2563eb;">{_fmt(total, data.currency)}</td></tr></tfoot></table></div>'''
    acceptance_html = f'<div style="margin-top:28px;"><h3 style="color:#2563eb;font-size:16px;margin-bottom:8px;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">{L["acceptance"]}</h3><div style="color:#4b5563;white-space:pre-line;">{data.acceptance_criteria}</div></div>' if data.acceptance_criteria else ""
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif;color:#1f2937;font-size:14px;line-height:1.6;">
<div style="max-width:210mm;margin:0 auto;padding:40px 48px;">
<div style="text-align:center;margin-bottom:40px;padding-bottom:24px;border-bottom:3px solid #2563eb;">
<div style="font-size:28px;font-weight:700;color:#2563eb;letter-spacing:1px;margin-bottom:8px;">{L["title"]}</div>
<div style="font-size:18px;font-weight:600;color:#374151;">{data.project_title}</div>
<div style="margin-top:8px;color:#6b7280;font-size:13px;">{L["date"]}: {data.sow_date}</div></div>
<div style="display:flex;gap:32px;margin-bottom:36px;">
<div style="flex:1;background:#f9fafb;border-radius:8px;padding:16px 20px;"><div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;margin-bottom:6px;">{L["provider"]}</div>{f'<img src="{co.logo_url}" style="max-height:60px;max-width:180px;margin-bottom:8px;" /><br/>' if co.logo_url else ''}<strong>{co.name}</strong>{f'<br/><span style="color:#6b7280;font-size:13px;">{co.address}</span>' if co.address else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{co.email}</span>' if co.email else ''}</div>
<div style="flex:1;background:#f9fafb;border-radius:8px;padding:16px 20px;"><div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;margin-bottom:6px;">{L["client_label"]}</div><strong>{cl.name}</strong>{f'<br/><span style="color:#6b7280;font-size:13px;">{cl.address}</span>' if cl.address else ''}{f'<br/><span style="color:#6b7280;font-size:13px;">{cl.email}</span>' if cl.email else ''}</div></div>
<div style="margin-top:28px;"><h3 style="color:#2563eb;font-size:16px;margin-bottom:8px;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">{L["description"]}</h3><div style="color:#4b5563;white-space:pre-line;">{data.description}</div></div>
<div style="margin-top:28px;"><h3 style="color:#2563eb;font-size:16px;margin-bottom:8px;border-bottom:2px solid #e5e7eb;padding-bottom:6px;">{L["deliverables"]}</h3><ol style="padding-left:20px;">{deliverables_html}</ol></div>
{milestones_html}
{acceptance_html}
<div style="margin-top:48px;text-align:center;color:#d1d5db;font-size:11px;">Generated by DocForge</div>
</div></body></html>"""
