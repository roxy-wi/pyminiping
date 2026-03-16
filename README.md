
# pyminiping

Lightweight Python ICMP ping library for monitoring, SRE and networking tools.

![PyPI version](https://img.shields.io/pypi/v/pyminiping)
![Build status](https://github.com/roxy-wi/pyminiping/actions/workflows/ci.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/pyminiping)
![License](https://img.shields.io/pypi/l/pyminiping)

`pyminiping` is a pure Python ICMP ping library designed for Linux servers and monitoring tools.

It sends ICMP echo packets and returns detailed latency statistics such as RTT metrics, packet loss, TTL information and estimated hop count.

The library supports **IPv4**, **IPv6**, **DSCP**, **custom TTL**, and includes a **command-line interface**.

⭐ If you find this project useful, please consider starring the repository.

---

# Quick Start

Install:

```bash
pip install pyminiping
```

Simple example:

```python
from pyminiping import ping

result = ping("8.8.8.8")

print(result.mean)
```

Example output:

```
0.0042
```

CLI usage:

```bash
sudo pyminiping 8.8.8.8
```

---

# Features

- Pure Python ICMP Echo (RAW sockets)
- IPv4 and IPv6 support
- Detailed latency statistics
- Packet loss calculation
- TTL detection
- Estimated hop count
- OS guess based on TTL
- Customizable parameters:
  - packet count
  - timeout
  - interval
  - payload size
  - TTL
  - DSCP
- Percentile metrics (p95)
- CLI tool included
- No runtime dependencies
- Designed for monitoring systems

---

# Installation

### From PyPI

```bash
pip install pyminiping
```

### From source

```bash
git clone https://github.com/roxy-wi/pyminiping.git
cd pyminiping
python3 -m pip install .
```

---

# Example Usage

```python
from pyminiping import ping, DestinationUnreachable

try:
    result = ping("8.8.8.8", count=5, timeout=1, interval=0.2)

    print(result)
    print(result.as_dict())

except DestinationUnreachable as e:
    print(f"Unreachable: {e.message} (code {e.code})")

except Exception as e:
    print(f"Ping failed: {e}")
```

---

# Example Output

```
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
    os_guess='Windows',
    p95=0.0061
)
```

Or as dictionary:

```python
{
    "sent": 5,
    "received": 5,
    "loss": 0.0,
    "min": 0.0044,
    "max": 0.0062,
    "mean": 0.0048,
    "median": 0.0045,
    "jitter": 0.0007,
    "rtt_list": [0.0062, 0.0044, 0.0045, 0.0044, 0.0045],
    "ttl": 110,
    "hops": 19,
    "os_guess": "Windows",
    "p95": 0.0061
}
```

---

# PingResult Object

The `ping()` function returns a `PingResult` dataclass.

| Field | Description |
|------|------|
| sent | Number of packets sent |
| received | Number of packets received |
| loss | Packet loss percentage |
| min | Minimum RTT |
| max | Maximum RTT |
| mean | Average RTT |
| median | Median RTT |
| jitter | Standard deviation of RTT |
| p95 | 95th percentile |
| ttl | TTL from response |
| hops | Estimated hop count |
| os_guess | OS guess based on TTL |
| rtt_list | List of RTT values |

Example:

```python
result = ping("1.1.1.1")

print(result.mean)
print(result.packet_loss)
print(result.success)
```

---

# Latency Metrics Explained

`pyminiping` returns several latency metrics commonly used in networking.

| Metric | Description |
|------|------|
| min | Fastest response |
| max | Slowest response |
| mean | Average latency |
| median | Middle value |
| jitter | Standard deviation of latency |
| p95 | 95th percentile latency |
| loss | Packet loss percentage |

Example:

```
min=4ms
avg=5ms
max=30ms
p95=25ms
```

Meaning:

- most packets arrive in ~5ms
- occasional spikes reach 30ms
- 95% of packets arrive under 25ms

---

# Command-Line Interface (CLI)

After installing `pyminiping`, the CLI tool becomes available.

```
pyminiping <host>
```

Example:

```
sudo pyminiping 8.8.8.8
```

---

# CLI Options

| Option | Description | Default |
|------|-------------|-------|
| host | Hostname or IP address | required |
| -c, --count | Number of packets | 4 |
| -t, --timeout | Timeout per packet (seconds) | 1 |
| -i, --interval | Interval between packets | 0.1 |
| -s, --size | Payload size in bytes | 8 |
| --ttl | Outgoing TTL / hop limit | system default |
| --dscp | DSCP value (0–63) | not set |
| --show-rtts | Print per-packet RTT | disabled |
| -j, --json | Output JSON | disabled |

---

# CLI Examples

Basic ping:

```
sudo pyminiping 8.8.8.8
```

Send multiple packets:

```
sudo pyminiping 8.8.8.8 -c 10
```

Custom interval:

```
sudo pyminiping 8.8.8.8 -i 0.5
```

Set TTL:

```
sudo pyminiping 8.8.8.8 --ttl 32
```

Show packet RTTs:

```
sudo pyminiping 8.8.8.8 --show-rtts
```

Example output:

```
PING 8.8.8.8 with 8 bytes of data:
8 bytes from 8.8.8.8: seq=1 ttl=117 time=0.0042 sec
8 bytes from 8.8.8.8: seq=2 ttl=117 time=0.0041 sec
```

JSON output:

```
sudo pyminiping 8.8.8.8 -j
```

---

# Common DSCP values

| Name | DSCP | Use Case |
|-----|-----|----------|
| Default | 0 | Best effort |
| CS1 | 8 | Background traffic |
| AF11 | 10 | Low priority |
| AF21 | 18 | Standard |
| AF41 | 34 | High priority |
| EF | 46 | Voice / real-time |

---

# Comparison with system ping

| Feature | system ping | pyminiping |
|------|------|------|
| ICMP Echo | ✔ | ✔ |
| IPv4 | ✔ | ✔ |
| IPv6 | ✔ | ✔ |
| RTT statistics | ✔ | ✔ |
| Jitter calculation | ✖ | ✔ |
| Percentiles | ✖ | ✔ |
| Python API | ✖ | ✔ |
| JSON output | ✖ | ✔ |
| DSCP support | Limited | ✔ |

---

# Use Cases

Typical applications:

- monitoring systems
- SRE tooling
- network diagnostics
- infrastructure automation

Example monitoring check:

```python
result = ping("1.1.1.1", count=3)

if not result.success:
    alert("Connectivity issue")
```

---

# Performance Notes

`pyminiping` is designed to be lightweight:

- minimal memory usage
- no subprocess calls
- no external dependencies
- suitable for monitoring agents

---

# Security

`pyminiping` uses RAW sockets and requires elevated privileges.

Run with sudo:

```
sudo pyminiping 8.8.8.8
```

Allow Python RAW sockets:

```
sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
```

More details:

https://man7.org/linux/man-pages/man7/capabilities.7.html

---

# Troubleshooting

Error:

```
Root privileges or CAP_NET_RAW are required to create RAW socket
```

Solution:

Run the script with root privileges or allow RAW socket capability.

---

# License

MIT License
