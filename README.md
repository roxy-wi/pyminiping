# pyminiping

**pyminiping** is a pure Python ICMP ping library for Linux servers.

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

## Installation

```bash
git clone https://github.com/roxy-wi/pyminiping.git
cd pyminiping
python3 -m pip install .
```

## Example usage
```python
from pyminiping import ping

try:
    result = ping('8.8.8.8', count=5, timeout=1, interval=0.2)
    print(result)
    print(result.as_dict())
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

## Notes

Requires root privileges or CAP_NET_RAW capability (e.g., sudo python3 yourscript.py)

Linux only (tested on Ubuntu/Debian)

The hop count (hops) is calculated using common initial TTL values (64, 128, 255). For most Linux servers this is accurate.
