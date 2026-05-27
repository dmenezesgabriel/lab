"""Step definitions for the SSO profile stack (authelia)."""
import httpx
from pytest_bdd import given, when


@given("the sso profile stack is running")
def sso_stack_running() -> None:
    pass  # tests assume the stack is already running; Docker healthchecks confirm readiness


@when(
    "GET http://authelia:9091/api/health is called",
    target_fixture="response",
)
def get_authelia_health() -> httpx.Response:
    return httpx.get("http://authelia:9091/api/health", timeout=5)
