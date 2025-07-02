import pytest
import os
from pyminiping import ping, PingTimeout, HostUnreachable, RootRequired


def is_root():
    return os.geteuid() == 0 if hasattr(os, "geteuid") else False


def test_root_required():
    if not is_root():
        with pytest.raises(RootRequired):
            ping('127.0.0.1', count=1)


@pytest.mark.skipif(not is_root(), reason="Requires root privileges")
def test_localhost():
    result = ping('127.0.0.1', count=1)
    assert result.received == 1
    assert result.loss == 0.0


@pytest.mark.skipif(not is_root(), reason="Requires root privileges")
def test_timeout():
    with pytest.raises(PingTimeout):
        ping('10.255.255.1', count=1, timeout=1)


@pytest.mark.skipif(not is_root(), reason="Requires root privileges")
def test_host_unreachable():
    with pytest.raises(HostUnreachable):
        ping('definitelynotahost.local', count=1)
