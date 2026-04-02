# DocForge

Generate professional business documents as PDF. Invoices, receipts, quotes, proposals, SOWs, delivery notes, and credit notes.

**3 ways to use:**
- MCP Server (Claude Desktop, Cursor, VS Code)
- REST API (RapidAPI, self-hosted)
- CLI / Python import

## Supported Documents

| Type | Description | Free | Pro |
|------|-------------|------|-----|
| Invoice | Professional invoice with line items, taxes, discounts | Yes | Yes |
| Receipt | Payment receipt marked as PAID | Yes | Yes |
| Quote | Estimate with validity date | Yes | Yes |
| Proposal | Project proposal with sections | - | Yes |
| SOW | Statement of Work with milestones | - | Yes |
| Delivery Note | Packing slip with signature field | - | Yes |
| Credit Note | Refund document referencing original invoice | - | Yes |

## Quick Start

### As MCP Server (Claude Desktop)

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "docforge": {
      "command": "python",
      "args": ["C:/path/to/docforge/mcp_server/server.py"]
    }
  }
}
```

Then ask Claude: "Generate an invoice for my company TechCo to ClientCorp for 10 hours of consulting at $150/hour"

### As REST API

```bash
uvicorn api_server.main:app --reload
```

```bash
curl -X POST http://localhost:8000/v1/invoice \
  -H "X-API-Key: df_test_key" \
  -H "Content-Type: application/json" \
  -d '{
    "company": {"name": "My Company", "address": "Madrid, Spain"},
    "client": {"name": "Client Corp", "address": "Berlin, Germany"},
    "invoice_number": "INV-001",
    "invoice_date": "2026-04-02",
    "items": [{"description": "Consulting", "quantity": 10, "unit_price": 150}]
  }' --output invoice.pdf
```

API docs: http://localhost:8000/docs

## Features

- 7 document types
- Multi-currency (EUR, USD, GBP, CHF, CAD, AUD, JPY, MXN)
- Bilingual (English / Spanish)
- Professional A4 PDF output
- Tax calculations with discounts
- AI text enhancement for proposals (optional, requires Anthropic API key)

## API Pricing (RapidAPI)

| Plan | Documents/month | Price |
|------|----------------|-------|
| Free | 10 | $0 |
| Basic | 100 | $9/mo |
| Pro | 1,000 | $25/mo |
| Business | 10,000 | $79/mo |

## Docker

```bash
docker build -t docforge .

# MCP Server
docker run docforge

# REST API
docker run -p 8000:8000 docforge uvicorn api_server.main:app --host 0.0.0.0 --port 8000
```

## License

MIT
