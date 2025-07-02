import pytest
from pyminiping import ping, PingTimeout, HostUnreachable


def test_localhost():
    result = ping('127.0.0.1', count=1)
    assert result.received == 1
    assert result.loss == 0.0


def test_host_unreachable():
    with pytest.raises(HostUnreachable):
        ping('definitelynotahost.local', count=1)


def test_timeout():
    # Blocked address should be timeout
    with pytest.raises(PingTimeout):
        ping('10.255.255.1', count=1, timeout=1)
