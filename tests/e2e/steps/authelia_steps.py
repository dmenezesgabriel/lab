"""Step definitions for the Authelia E2E scenario (E2E-002)."""
from playwright.sync_api import Page
from pytest_bdd import given, when, then


@given("the sso profile stack is running")
def sso_stack_running() -> None:
    pass  # tests assume the stack is already running


@when(
    "Playwright navigates to http://authelia:9091",
    target_fixture="navigated_page",
)
def navigate_to_authelia(page: Page) -> Page:
    page.goto("http://authelia:9091", wait_until="networkidle", timeout=10_000)
    return page


@then("the page contains a username input field")
def authelia_has_username_input(navigated_page: Page) -> None:
    url = navigated_page.url
    title = navigated_page.title()
    locator = navigated_page.locator(
        'input[name="username"], input[autocomplete="username"]'
    )
    count = locator.count()
    assert count >= 1, (
        f"url={url!r} title={title!r}: expected a username input, found {count} matching elements"
    )
