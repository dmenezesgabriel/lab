"""IT-001: lab-net hostname resolution. Covers FR-006, AC-003."""
import socket

from pytest_bdd import given, scenario, then, when


@scenario("features/lab_net.feature", "test-runner resolves postgres-db by hostname")
def test_hostname_resolution():
    pass


@given("the test-runner container is running on lab-net")
def running_on_lab_net():
    pass  # test itself runs inside the container on lab-net


@when("it resolves postgres-db by hostname", target_fixture="resolved_ips")
def resolve_hostname():
    return socket.getaddrinfo("postgres-db", None)


@then("the hostname resolves to a valid IP on lab-net")
def valid_ip(resolved_ips):
    assert resolved_ips, "postgres-db did not resolve to any address"
    ip = resolved_ips[0][4][0]
    assert ip, "resolved address is empty"
