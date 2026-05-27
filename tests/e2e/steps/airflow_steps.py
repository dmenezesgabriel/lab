"""Step definitions for the Airflow E2E scenario (E2E-005)."""
from playwright.sync_api import Page, Response
from pytest_bdd import given, when, then


@given("the airflow profile stack is running")
def airflow_stack_running() -> None:
    pass  # tests assume the stack is already running


@when(
    "Playwright navigates to http://airflow-webserver:8080",
    target_fixture="navigated_page",
)
def navigate_to_airflow(page: Page) -> Page:
    response: Response | None = page.goto(
        "http://airflow-webserver:8080", wait_until="networkidle", timeout=10_000
    )
    page.last_response = response  # type: ignore[attr-defined]
    return page


@then("the HTTP response status is not 5xx")
def airflow_not_5xx(navigated_page: Page) -> None:
    url = navigated_page.url
    response: Response | None = navigated_page.last_response  # type: ignore[attr-defined]
    if response is not None:
        status = response.status
        assert status < 500, (
            f"url={url!r}: expected non-5xx response, got HTTP {status}"
        )


@then("the rendered page is not blank")
def airflow_page_not_blank(navigated_page: Page) -> None:
    url = navigated_page.url
    title = navigated_page.title()
    body_text = navigated_page.inner_text("body")
    assert body_text.strip(), (
        f"url={url!r} title={title!r}: rendered page body is blank"
    )
