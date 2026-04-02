"""HTML to PDF conversion using Playwright (headless Chromium)."""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def _html_to_pdf_async(html_content: str) -> bytes:
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = await page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"},
        )
        await browser.close()
        return pdf_bytes


def html_to_pdf(html_content: str) -> bytes:
    """Convert HTML string to PDF bytes using Playwright."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        # We're inside an async context — create a new thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, _html_to_pdf_async(html_content))
            return future.result(timeout=30)
    else:
        return asyncio.run(_html_to_pdf_async(html_content))


def is_pdf_available() -> bool:
    try:
        from playwright.async_api import async_playwright
        return True
    except ImportError:
        return False
