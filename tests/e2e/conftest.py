"""Session-scoped browser fixture and function-scoped page fixture for E2E tests.

Usage example:
    def test_something(page):
        page.goto("http://homepage:3000")
        assert "Homepage" in page.title()
"""
import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

# Allow step modules to be imported as a plain package.
sys.path.insert(0, str(Path(__file__).parent))

pytest_plugins = [
    "steps.homepage_steps",
    "steps.authelia_steps",
    "steps.grafana_steps",
    "steps.mlflow_steps",
    "steps.airflow_steps",
]

_PLAYWRIGHT_ARTIFACTS = os.environ.get("PLAYWRIGHT_ARTIFACTS", "") == "1"


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    """Headless Chromium browser shared across all scenarios in the session."""
    launched = playwright_instance.chromium.launch(headless=True)
    yield launched
    launched.close()


@pytest.fixture
def page(browser: Browser) -> Generator[Page, None, None]:
    """Fresh browser context and page per scenario (function-scoped)."""
    context: BrowserContext = browser.new_context()
    console_errors: list[str] = []

    scenario_page: Page = context.new_page()
    scenario_page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    scenario_page.console_errors = console_errors  # type: ignore[attr-defined]

    yield scenario_page

    if _PLAYWRIGHT_ARTIFACTS:
        scenario_page.screenshot(path=f"/tmp/e2e-{scenario_page.url.replace('/', '_')}.png")

    context.close()
