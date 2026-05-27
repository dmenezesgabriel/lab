"""Step definitions for the homepage E2E scenario (E2E-001)."""
from playwright.sync_api import Page
from pytest_bdd import given, when, then


@given("the management profile stack is running")
def management_stack_running() -> None:
    pass  # tests assume the stack is already running


@when(
    "Playwright navigates to http://homepage:3000",
    target_fixture="navigated_page",
)
def navigate_to_homepage(page: Page) -> Page:
    page.goto("http://homepage:3000", wait_until="networkidle", timeout=10_000)
    return page


@then('the page title contains "Homepage"')
def homepage_title_contains(navigated_page: Page) -> None:
    title = navigated_page.title()
    url = navigated_page.url
    assert "Homepage" in title, (
        f"url={url!r}: expected page title to contain 'Homepage', got {title!r}"
    )


@then("no unhandled console errors are logged")
def no_console_errors(navigated_page: Page) -> None:
    errors = navigated_page.console_errors  # type: ignore[attr-defined]
    url = navigated_page.url
    title = navigated_page.title()
    assert not errors, (
        f"url={url!r} title={title!r}: unhandled console errors={errors!r}"
    )
