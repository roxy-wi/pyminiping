# pyminiping

**pyminiping** is a pure Python ICMP ping library for Linux servers.

It sends one or more ICMP echo packets and provides detailed statistics: min, max, mean, median, jitter, TTL, and estimated number of hops.

## Features

- Pure Python ICMP Echo (RAW socket, requires root or `CAP_NET_RAW`)
- Statistics: min, max, mean, median, jitter (standard deviation)
- Sent/received packet count and loss percentage
- TTL and estimated hop count (`hops`)
- Customizable parameters: count, timeout, interval

## Installation

```bash
git clone https://github.com/roxy-wi/pyminiping.git
cd pyminiping
python3 -m pip install .
# pyminiping
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
    min=19.3,
    max=21.1,
    mean=20.2,
    median=20.0,
    jitter=0.7,
    rtt_list=[19.3, 19.7, 20.0, 20.8, 21.1],
    ttl=57,
    hops=8
)
```

or as dict

```python
{
    'sent': 5,
    'received': 5,
    'loss': 0.0,
    'min': 19.3,
    'max': 21.1,
    'mean': 20.2,
    'median': 20.0,
    'jitter': 0.7,
    'rtt_list': [19.3, 19.7, 20.0, 20.8, 21.1],
    'ttl': 57,
    'hops': 8
}

```

## Notes

Requires root privileges or CAP_NET_RAW capability (e.g., sudo python3 yourscript.py)

Linux only (tested on Ubuntu/Debian)

The hop count (hops) is calculated using common initial TTL values (64, 128, 255). For most Linux servers this is accurate.
