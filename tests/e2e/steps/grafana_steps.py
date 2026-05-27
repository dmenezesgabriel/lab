"""Step definitions for the Grafana E2E scenario (E2E-003)."""
from playwright.sync_api import Page
from pytest_bdd import given, when, then


@given("the observability profile stack is running")
def observability_stack_running() -> None:
    pass  # tests assume the stack is already running


@when(
    "Playwright navigates to http://grafana:3000/login",
    target_fixture="navigated_page",
)
def navigate_to_grafana(page: Page) -> Page:
    page.goto("http://grafana:3000/login", wait_until="networkidle", timeout=10_000)
    return page


@then('the page title contains "Grafana"')
def grafana_title_contains(navigated_page: Page) -> None:
    title = navigated_page.title()
    url = navigated_page.url
    assert "Grafana" in title, (
        f"url={url!r}: expected page title to contain 'Grafana', got {title!r}"
    )
