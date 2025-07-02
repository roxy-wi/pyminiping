# pyminiping

**pyminiping** is a pure Python ICMP ping library for Linux servers.

![PyPI version](https://img.shields.io/pypi/v/pyminiping)
![Build status](https://github.com/roxy-wi/pyminiping/actions/workflows/ci.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/pyminiping)
![License](https://img.shields.io/pypi/l/pyminiping)

It sends one or more ICMP echo packets and provides detailed statistics: min, max, mean, median, jitter, TTL, estimated number 
of hops, and an OS family guess based on TTL.

## Features

- Pure Python ICMP Echo (RAW socket, requires root or `CAP_NET_RAW`)
- Statistics: min, max, mean, median, jitter (standard deviation)
- Sent/received packet count and loss percentage
- TTL and estimated hop count (`hops`)
- Operating system family guess (`os_guess`) based on received TTL
- Customizable parameters: count, timeout, interval, size
- IPv4 and IPv6 supporting
- dscp value (0-63) for traffic prioritization

## Installation

```bash
git clone https://github.com/roxy-wi/pyminiping.git
cd pyminiping
python3 -m pip install .
```

## Example usage
```python
from pyminiping import ping, DestinationUnreachable

try:
    result = ping('8.8.8.8', count=5, timeout=1, interval=0.2)
    print(result)
    print(result.as_dict())
except DestinationUnreachable as e:
    print(f"Unreachable: {e.message} (code {e.code})")
except Exception as e:
    print(f"Ping failed: {e}")

```

## Example Output

```python
PingResult(
    sent=5,
    received=5,
    loss=0.0,
    min=0.0044,
    max=0.0062,
    mean=0.0048,
    median=0.0045,
    jitter=0.0007,
    rtt_list=[0.0062, 0.0044, 0.0045, 0.0044, 0.0045],
    ttl=110,
    hops=19,
    os_guess='Windows'
)
```

or as dict

```python
{
    'sent': 5,
    'received': 5,
    'loss': 0.0,
    'min': 0.0044,
    'max': 0.0062,
    'mean': 0.0048,
    'median': 0.0045,
    'jitter': 0.0007,
    'rtt_list': [0.0062, 0.0044, 0.0045, 0.0044, 0.0045],
    'ttl': 110,
    'hops': 19,
    'os_guess': 'Windows'
}


```
## Common DSCP values

| Name    | DSCP | Use Case             |
| ------- | ---- | -------------------- |
| Default | 0    | Best Effort          |
| CS1     | 8    | Background           |
| AF11    | 10   | Low-priority data    |
| AF21    | 18   | Standard             |
| AF41    | 46   | Voice, high-priority |
| EF      | 46   | Expedited Forwarding |


## Notes

Requires root privileges or CAP_NET_RAW capability (e.g., sudo python3 yourscript.py)

Linux only (tested on Ubuntu/Debian)

The hop count (hops) is calculated using common initial TTL values (64, 128, 255). For most Linux servers this is accurate.


## Troubleshooting RAW socket permissions

- If you see: "Root privileges or CAP_NET_RAW are required to create RAW socket"
    - Run your script as root, e.g. `sudo python3 script.py`
    - Or, to allow your Python interpreter to use RAW sockets without root:
        - On Linux: `sudo setcap cap_net_raw+ep $(readlink -f $(which python3))`
    - For more details, see: https://man7.org/linux/man-pages/man7/capabilities.7.html
