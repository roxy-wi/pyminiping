# pyminiping

Lightweight Python ICMP ping library for monitoring, SRE and networking tools.

![PyPI version](https://img.shields.io/pypi/v/pyminiping)
![Build status](https://github.com/roxy-wi/pyminiping/actions/workflows/ci.yml/badge.svg)
![Python versions](https://img.shields.io/pypi/pyversions/pyminiping)
![License](https://img.shields.io/pypi/l/pyminiping)

`pyminiping` is a pure Python ICMP ping library designed for Linux servers and monitoring tools.

It sends ICMP echo packets and returns detailed latency statistics such as RTT metrics, packet loss, TTL information, estimated hop count, and p95 latency.

The library supports **IPv4**, **IPv6**, **DSCP**, **custom TTL**, optional **kernel receive timestamps** via `SO_TIMESTAMPNS`, and includes a **command-line interface**.

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

```text
0.0042
```

You can also export the result as JSON:

```python
from pyminiping import ping

result = ping("8.8.8.8")
print(result.as_json())
print(result.as_json(indent=2))
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
- TTL detection for IPv4
- Estimated hop count for IPv4
- OS guess based on IPv4 TTL
- Customizable parameters:
  - packet count
  - timeout
  - interval
  - payload size
  - TTL
  - DSCP
- Percentile metrics (p95)
- Optional kernel receive timestamping with `SO_TIMESTAMPNS`
- CLI tool included
- No runtime dependencies
- Designed for monitoring systems

---

# Installation

## From PyPI

```bash
pip install pyminiping
```

## From source

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
    print(result.as_dict())

except DestinationUnreachable as e:
    print(f"Unreachable: {e.message} (code {e.code})")

except Exception as e:
    print(f"Ping failed: {e}")
```

---

# Example Output

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
| ttl | TTL from response packet |
| hops | Estimated hop count |
| os_guess | OS guess based on IPv4 TTL |
| rtt_list | List of RTT values |


Methods:

| Method | Description |
|------|------|
| as_dict() | Return result as a Python dictionary |
| as_json() | Return result as a JSON string |

Properties:

| Property | Description |
|------|------|
| success | `True` if at least one packet was received |
| packet_loss | Alias for `loss` |

Example:

```python
from pyminiping import ping

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

```text
min=4ms
avg=5ms
max=30ms
p95=25ms
```

Meaning:

- most packets arrive in about 5 ms
- occasional spikes reach 30 ms
- 95% of packets arrive under 25 ms

---

# Advanced Usage

## Custom packet size

```python
ping("8.8.8.8", size=128)
```

## Change interval

```python
ping("8.8.8.8", interval=0.5)
```

## Set TTL

```python
ping("8.8.8.8", ttl=32)
```

## Send multiple packets

```python
ping("8.8.8.8", count=10)
```

## Use DSCP for QoS testing

```python
ping("8.8.8.8", dscp=46)
```

## Raise exception only when all packets timeout

```python
ping("192.0.2.1", count=3, raise_on_timeout=True)
```

## Use kernel receive timestamps for more precise RTT

```python
ping("8.8.8.8", use_kernel_timestamp=True)
```

---

# Command-Line Interface (CLI)

After installing `pyminiping`, the CLI tool becomes available.

```bash
pyminiping <host>
```

Example:

```bash
sudo pyminiping 8.8.8.8
```

## CLI Options

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
| --precise | Use kernel receive timestamps (`SO_TIMESTAMPNS`) | disabled |

## CLI Examples

Basic ping:

```bash
sudo pyminiping 8.8.8.8
```

Send multiple packets:

```bash
sudo pyminiping 8.8.8.8 -c 10
```

Custom interval:

```bash
sudo pyminiping 8.8.8.8 -i 0.5
```

Set TTL:

```bash
sudo pyminiping 8.8.8.8 --ttl 32
```

Show packet RTTs:

```bash
sudo pyminiping 8.8.8.8 --show-rtts
```

JSON output:

```bash
sudo pyminiping 8.8.8.8 -j
```

Use kernel receive timestamps:

```bash
sudo pyminiping 8.8.8.8 --precise
```

---

# Precise Timing Mode

`pyminiping` can use Linux kernel receive timestamps via `SO_TIMESTAMPNS` for more accurate packet receive timing.

Benefits:

- more stable RTT measurement under CPU load
- lower user-space timing jitter
- useful for latency-sensitive checks

Example:

```python
result = ping("8.8.8.8", use_kernel_timestamp=True)
```

CLI:

```bash
sudo pyminiping 8.8.8.8 --precise
```

Notes:

- this mode is Linux-specific
- support depends on the running Python build and platform socket constants
- if your environment does not expose `SO_TIMESTAMPNS`, precise mode may be unavailable
- it improves receive-side timing only

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
| Custom TTL | ✔ | ✔ |
| Kernel timestamp mode | Limited | ✔ |

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

For most checks, normal timing is enough. Use `use_kernel_timestamp=True` or `--precise` only when you need more stable receive-side timing.

---

# Security

`pyminiping` uses RAW sockets and requires elevated privileges.

Run with sudo:

```bash
sudo pyminiping 8.8.8.8
```

Allow Python RAW sockets:

```bash
sudo setcap cap_net_raw+ep $(readlink -f $(which python3))
```

---

# Troubleshooting

## Error: Root privileges or CAP_NET_RAW are required to create RAW socket

Run the script with root privileges or allow RAW socket capability.

## Error: Cannot resolve host

Check DNS resolution or use an IP address instead of a hostname.

## Error: SO_TIMESTAMPNS is not available on this platform

Precise mode depends on Linux platform support and the Python socket build.

You can:

- run without `use_kernel_timestamp=True`
- avoid `--precise`
- use a Python build that exposes the `SO_TIMESTAMPNS` socket option

---

# License

MIT License
