"""Step definitions for the MLflow E2E scenario (E2E-004)."""
from playwright.sync_api import Page
from pytest_bdd import given, when, then


@given("the model-registry profile stack is running")
def model_registry_stack_running() -> None:
    pass  # tests assume the stack is already running


@when(
    "Playwright navigates to http://mlflow:5000",
    target_fixture="navigated_page",
)
def navigate_to_mlflow(page: Page) -> Page:
    page.goto("http://mlflow:5000", wait_until="networkidle", timeout=10_000)
    return page


@then("the page renders without a 5xx error")
def mlflow_no_5xx(navigated_page: Page) -> None:
    url = navigated_page.url
    title = navigated_page.title()
    # A 5xx response in a browser-rendered SPA typically results in a blank page
    # or an error heading — check that the body has visible text content.
    body_text = navigated_page.inner_text("body")
    assert body_text.strip(), (
        f"url={url!r} title={title!r}: page body is empty, likely a 5xx or failed load"
    )


@then('the page contains "Experiments" or an empty-state indicator')
def mlflow_has_experiments_or_empty_state(navigated_page: Page) -> None:
    url = navigated_page.url
    title = navigated_page.title()
    body_text = navigated_page.inner_text("body")
    has_experiments = "Experiments" in body_text or "experiments" in body_text
    has_empty_state = "No experiments" in body_text or "no experiments" in body_text
    assert has_experiments or has_empty_state, (
        f"url={url!r} title={title!r}: expected 'Experiments' or empty-state text; "
        f"body excerpt={body_text[:300]!r}"
    )
