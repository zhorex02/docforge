"""Invoice template — professional A4 PDF."""

from core.models import InvoiceData, CURRENCY_SYMBOLS

LABELS = {
    "en": {
        "title": "INVOICE",
        "bill_to": "Bill To",
        "invoice_num": "Invoice #",
        "date": "Date",
        "due_date": "Due Date",
        "description": "Description",
        "qty": "Qty",
        "unit_price": "Unit Price",
        "amount": "Amount",
        "subtotal": "Subtotal",
        "discount": "Discount",
        "tax": "Tax",
        "total": "TOTAL",
        "notes": "Notes",
        "payment_terms": "Payment Terms",
        "bank_details": "Bank Details",
    },
    "es": {
        "title": "FACTURA",
        "bill_to": "Facturar A",
        "invoice_num": "Factura Nº",
        "date": "Fecha",
        "due_date": "Fecha de Vencimiento",
        "description": "Descripción",
        "qty": "Cant.",
        "unit_price": "Precio Unit.",
        "amount": "Importe",
        "subtotal": "Subtotal",
        "discount": "Descuento",
        "tax": "Impuesto",
        "total": "TOTAL",
        "notes": "Notas",
        "payment_terms": "Condiciones de Pago",
        "bank_details": "Datos Bancarios",
    },
}


def _fmt(value: float, currency: str) -> str:
    sym = CURRENCY_SYMBOLS.get(currency, currency)
    if currency in ("EUR",):
        return f"{value:,.2f} {sym}"
    return f"{sym}{value:,.2f}"


def render_invoice(data: InvoiceData) -> str:
    L = LABELS.get(data.language, LABELS["en"])
    cur = data.currency

    # Compute line items
    rows_html = ""
    subtotal = 0.0
    for item in data.items:
        line_total = item.quantity * item.unit_price
        subtotal += line_total
        rows_html += f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;">{item.description}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:center;">{item.quantity:g}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;">{_fmt(item.unit_price, cur)}</td>
            <td style="padding:10px 12px;border-bottom:1px solid #e5e7eb;text-align:right;">{_fmt(line_total, cur)}</td>
        </tr>"""

    discount_amount = subtotal * (data.discount_percent / 100) if data.discount_percent > 0 else 0
    taxable = subtotal - discount_amount
    tax_amount = taxable * (data.tax_rate / 100)
    total = taxable + tax_amount

    # Discount row
    discount_row = ""
    if data.discount_percent > 0:
        discount_row = f"""
        <tr>
            <td style="padding:6px 12px;text-align:right;color:#6b7280;">{L['discount']} ({data.discount_percent:g}%)</td>
            <td style="padding:6px 12px;text-align:right;color:#dc2626;">-{_fmt(discount_amount, cur)}</td>
        </tr>"""

    # Logo
    logo_html = ""
    if data.company.logo_url:
        logo_html = f'<img src="{data.company.logo_url}" style="max-height:60px;max-width:180px;margin-bottom:8px;" /><br/>'

    # Due date
    due_html = ""
    if data.due_date:
        due_html = f"""
        <tr>
            <td style="padding:4px 0;color:#6b7280;font-size:13px;">{L['due_date']}</td>
            <td style="padding:4px 0;font-size:13px;text-align:right;">{data.due_date}</td>
        </tr>"""

    # Footer sections
    footer_sections = ""
    if data.notes:
        footer_sections += f"""
        <div style="margin-top:24px;">
            <div style="font-weight:600;color:#374151;margin-bottom:4px;">{L['notes']}</div>
            <div style="color:#6b7280;font-size:13px;white-space:pre-line;">{data.notes}</div>
        </div>"""
    if data.payment_terms:
        footer_sections += f"""
        <div style="margin-top:16px;">
            <div style="font-weight:600;color:#374151;margin-bottom:4px;">{L['payment_terms']}</div>
            <div style="color:#6b7280;font-size:13px;white-space:pre-line;">{data.payment_terms}</div>
        </div>"""
    if data.bank_details:
        footer_sections += f"""
        <div style="margin-top:16px;">
            <div style="font-weight:600;color:#374151;margin-bottom:4px;">{L['bank_details']}</div>
            <div style="color:#6b7280;font-size:13px;white-space:pre-line;">{data.bank_details}</div>
        </div>"""

    company = data.company
    client = data.client

    # Company details block
    company_details = f"<strong>{company.name}</strong>"
    if company.address:
        company_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{company.address}</span>"
    if company.tax_id:
        company_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{company.tax_id}</span>"
    if company.email:
        company_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{company.email}</span>"
    if company.phone:
        company_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{company.phone}</span>"

    # Client details block
    client_details = f"<strong>{client.name}</strong>"
    if client.address:
        client_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{client.address}</span>"
    if client.tax_id:
        client_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{client.tax_id}</span>"
    if client.email:
        client_details += f"<br/><span style='color:#6b7280;font-size:13px;'>{client.email}</span>"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;font-family:system-ui,-apple-system,sans-serif;color:#1f2937;font-size:14px;line-height:1.5;">
<div style="max-width:210mm;margin:0 auto;padding:40px 48px;">

    <!-- Header -->
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:40px;">
        <div>
            {logo_html}
            {company_details}
        </div>
        <div style="text-align:right;">
            <div style="font-size:28px;font-weight:700;color:#2563eb;letter-spacing:1px;margin-bottom:12px;">{L['title']}</div>
            <table style="margin-left:auto;border-collapse:collapse;">
                <tr>
                    <td style="padding:4px 0;color:#6b7280;font-size:13px;">{L['invoice_num']}</td>
                    <td style="padding:4px 0 4px 16px;font-size:13px;text-align:right;font-weight:600;">{data.invoice_number}</td>
                </tr>
                <tr>
                    <td style="padding:4px 0;color:#6b7280;font-size:13px;">{L['date']}</td>
                    <td style="padding:4px 0 4px 16px;font-size:13px;text-align:right;">{data.invoice_date}</td>
                </tr>
                {due_html}
            </table>
        </div>
    </div>

    <!-- Bill To -->
    <div style="background:#f9fafb;border-radius:8px;padding:16px 20px;margin-bottom:32px;">
        <div style="font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#9ca3af;margin-bottom:6px;">{L['bill_to']}</div>
        {client_details}
    </div>

    <!-- Items Table -->
    <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
        <thead>
            <tr style="background:#2563eb;color:white;">
                <th style="padding:10px 12px;text-align:left;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;border-radius:6px 0 0 0;">{L['description']}</th>
                <th style="padding:10px 12px;text-align:center;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">{L['qty']}</th>
                <th style="padding:10px 12px;text-align:right;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;">{L['unit_price']}</th>
                <th style="padding:10px 12px;text-align:right;font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:0.5px;border-radius:0 6px 0 0;">{L['amount']}</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <!-- Totals -->
    <div style="display:flex;justify-content:flex-end;margin-bottom:32px;">
        <table style="border-collapse:collapse;min-width:280px;">
            <tr>
                <td style="padding:6px 12px;text-align:right;color:#6b7280;">{L['subtotal']}</td>
                <td style="padding:6px 12px;text-align:right;">{_fmt(subtotal, cur)}</td>
            </tr>
            {discount_row}
            <tr>
                <td style="padding:6px 12px;text-align:right;color:#6b7280;">{L['tax']} ({data.tax_rate:g}%)</td>
                <td style="padding:6px 12px;text-align:right;">{_fmt(tax_amount, cur)}</td>
            </tr>
            <tr style="border-top:2px solid #2563eb;">
                <td style="padding:12px;text-align:right;font-size:16px;font-weight:700;color:#2563eb;">{L['total']}</td>
                <td style="padding:12px;text-align:right;font-size:18px;font-weight:700;color:#2563eb;">{_fmt(total, cur)}</td>
            </tr>
        </table>
    </div>

    <!-- Footer -->
    {footer_sections}

    <!-- Powered by -->
    <div style="margin-top:48px;text-align:center;color:#d1d5db;font-size:11px;">
        Generated by DocForge
    </div>
</div>
</body>
</html>"""
