FROM mcr.microsoft.com/playwright/python:v1.49.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium

COPY . .

# Default: run MCP server. Override CMD for API server.
# MCP: python mcp_server/server.py
# API: uvicorn api_server.main:app --host 0.0.0.0 --port 8000
CMD ["python", "mcp_server/server.py"]
