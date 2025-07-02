import os
import socket
import struct
import time
from statistics import mean, median, stdev
from dataclasses import dataclass, field
from typing import Optional, List

from .exceptions import (
    PyMiniPingException,
    HostUnreachable,
    RootRequired,
    PingTimeout,
    DestinationUnreachable
)

ICMP_ECHO_REQUEST = 8
ICMP6_ECHO_REQUEST = 128


def icmp_code_to_text(code: int) -> str:
    # See RFC 792
    codes = {
        0: "Network unreachable",
        1: "Host unreachable",
        2: "Protocol unreachable",
        3: "Port unreachable",
        4: "Fragmentation needed and DF set",
        5: "Source route failed",
        13: "Communication administratively prohibited (firewalled)",
    }
    return codes.get(code, "Unknown reason")


def icmpv6_code_to_text(code: int) -> str:
    codes = {
        0: "No route to destination",
        1: "Communication administratively prohibited (firewalled)",
        2: "Beyond scope of source address",
        3: "Address unreachable",
        4: "Port unreachable",
        5: "Source address failed ingress/egress policy",
        6: "Reject route to destination",
        7: "Error in Source Routing Header",
    }
    return codes.get(code, "Unknown reason")


def percentile(data, percent):
    """
    Calculate the desired percentile of a list of numbers (0-100).
    """
    if not data:
        return None
    data = sorted(data)
    k = (len(data) - 1) * (percent / 100)
    f = int(k)
    c = f + 1
    if c > len(data) - 1:
        return data[-1]
    d0 = data[f] * (c - k)
    d1 = data[c] * (k - f)
    return d0 + d1


def checksum(source: bytes) -> int:
    sum_p = 0
    count = 0
    count_to = (len(source) // 2) * 2
    while count < count_to:
        this_val = (source[count + 1] << 8) + source[count]
        sum_p = sum_p + this_val
        sum_p = sum_p & 0xffffffff
        count = count + 2
    if count_to < len(source):
        sum_p = sum_p + source[-1]
        sum_p = sum_p & 0xffffffff
    sum_p = (sum_p >> 16) + (sum_p & 0xffff)
    sum_p = sum_p + (sum_p >> 16)
    answer = ~sum_p
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def resolve_host(host: str):
    """Try to resolve host to IPv4 or IPv6, return (family, address)."""
    try:
        info = socket.getaddrinfo(host, None, 0, socket.SOCK_RAW)
        family, _, _, _, sockaddr = info[0]
        return family, sockaddr[0]
    except Exception:
        raise HostUnreachable(f"Cannot resolve host: {host}")


def create_packet(family: int, packet_id: int, seq: int, size: int = 8) -> bytes:
    """Create an ICMP Echo packet with a custom payload size."""
    if family == socket.AF_INET:
        header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, packet_id, seq)
    else:
        header = struct.pack('!BbHHh', ICMP6_ECHO_REQUEST, 0, 0, packet_id, seq)
    # First 8 bytes: timestamp, the rest: padding with zero bytes
    if size < 8:
        raise ValueError("Minimum size is 8 bytes.")
    payload = struct.pack('d', time.time()) + bytes(size - 8)
    packet = header + payload
    my_checksum = checksum(packet)
    if family == socket.AF_INET:
        header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, my_checksum, packet_id, seq)
    else:
        header = struct.pack('!BbHHh', ICMP6_ECHO_REQUEST, 0, my_checksum, packet_id, seq)
    return header + payload


def guess_initial_ttl(received_ttl: int) -> int:
    """Guess the initial TTL based on received TTL, using OS heuristics."""
    if received_ttl <= 64:
        return 64    # Linux/Unix/BSD/macOS/Android
    elif received_ttl <= 128:
        return 128   # Windows
    else:
        return 255   # Cisco/network equipment


def guess_os(received_ttl: int) -> str:
    """Guess operating system family based on received TTL."""
    if received_ttl <= 64:
        return "Linux/Unix/BSD/macOS/Android"
    elif received_ttl <= 128:
        return "Windows"
    else:
        return "Network device (e.g., Cisco)"


def calc_hops(received_ttl: int) -> Optional[int]:
    """Estimate hop count based on common initial TTL values."""
    initial_ttl = guess_initial_ttl(received_ttl)
    return initial_ttl - received_ttl + 1


@dataclass
class PingResult:
    """
    Holds the statistics and result details for a ping operation.

    Attributes:
        sent (int): Number of packets sent.
        received (int): Number of packets received.
        loss (float): Percentage of lost packets.
        min (Optional[float]): Minimum round-trip time (seconds).
        max (Optional[float]): Maximum round-trip time (seconds).
        mean (Optional[float]): Mean round-trip time (seconds).
        median (Optional[float]): Median round-trip time (seconds).
        jitter (float): Standard deviation of round-trip times (seconds).
        rtt_list (List[float]): List of all round-trip times (seconds).
        ttl (Optional[int]): Time to Live from a response packet.
        hops (Optional[int]): Estimated number of network hops.
        os_guess (Optional[str]): Guessed operating system family based on TTL.
        p95 (Optional[float]): 95th percentile of round-trip times (seconds).
    """
    sent: int
    received: int
    loss: float
    min: Optional[float] = 0
    max: Optional[float] = 0
    mean: Optional[float] = 0
    median: Optional[float] = 0
    jitter: float = 0
    rtt_list: List[float] = field(default_factory=list)
    ttl: Optional[int] = 0
    hops: Optional[int] = 0
    os_guess: Optional[str] = None
    p95: Optional[float] = None

    def as_dict(self) -> dict:
        """Return a result as a dictionary."""
        return self.__dict__


def ping(
    host: str,
    count: int = 1,
    timeout: int = 1,
    interval: float = 0.1,
    size: int = 56,
    dscp: int = None,
) -> PingResult:
    """
    Send ICMP echo requests (ping) to a host.

    Parameters:
        host (str): Hostname or IP address to ping.
        count (int): Number of packets to send. Default is 1.
        timeout (int): Timeout for each packet in seconds. Default is 1.
        interval (float): Interval between packets (seconds). Default is 0.1.
        size (int): Payload size in bytes (minimum 8). Default is 8.
        dscp (int): Optional DSCP value (0-63) for packet prioritization.

    Returns:
        PingResult: Dataclass with statistics for the operation.

    Raises:
        HostUnreachable: If host cannot be resolved.
        RootRequired: If insufficient privileges to create a RAW socket.
        PingTimeout: If no response is received.
        PyMiniPingException: For other low-level socket errors.

    Example:
        >>> from pyminiping import ping
        >>> result = ping('8.8.8.8', count=3)
        >>> print(result.mean)
    """
    family, addr = resolve_host(host)
    packet_id = os.getpid() & 0xFFFF
    rtt_list: List[float] = []
    received = 0
    ttl = None

    if family == socket.AF_INET:
        proto = socket.getprotobyname('icmp')
    else:
        proto = socket.getprotobyname('ipv6-icmp')

    try:
        sock = socket.socket(family, socket.SOCK_RAW, proto)
    except PermissionError:
        raise RootRequired("Root privileges or CAP_NET_RAW are required to create RAW socket.")
    except Exception as e:
        raise PyMiniPingException(f"Socket error: {e}")

    if dscp is not None:
        # DSCP is 6 bits in the IP header; the 2 lowest bits are ECN.
        # Shift DSCP left by 2 to align with ToS field.
        if family == socket.AF_INET:
            tos = dscp << 2
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, tos)
        elif family == socket.AF_INET6:
            # For IPv6, traffic class is set with IPV6_TCLASS option
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_TCLASS, dscp << 2)

    for seq in range(1, count + 1):
        packet = create_packet(family, packet_id, seq, size)
        try:
            sock.sendto(packet, (addr, 0, 0, 0) if family == socket.AF_INET6 else (addr, 1))
            sock.settimeout(timeout)
            while True:
                try:
                    rec_packet, _ = sock.recvfrom(1024)
                    time_received = time.time()
                    if family == socket.AF_INET:
                        ip_header = rec_packet[:20]
                        icmp_header = rec_packet[20:28]
                        recv_ttl = ip_header[8]
                        _type, code, _chksum, recv_id, recv_seq = struct.unpack('!BBHHH', icmp_header)
                        if _type == 3:  # ICMP Destination Unreachable
                            raise DestinationUnreachable(code, message=icmp_code_to_text(code))
                        is_ours = recv_id == packet_id and recv_seq == seq
                    else:
                        # IPv6: ICMP header is first 8 bytes
                        icmp_header = rec_packet[:8]
                        recv_ttl = None  # Getting TTL for IPv6 is non-trivial
                        _type, code, _chksum, recv_id, recv_seq = struct.unpack('!BbHHh', icmp_header)
                        if _type == 1:  # ICMPv6 Destination Unreachable
                            raise DestinationUnreachable(code, message=icmpv6_code_to_text(code))
                        is_ours = recv_id == packet_id and recv_seq == seq
                    if is_ours:
                        bytes_in_double = struct.calcsize('d')  # always 8
                        if family == socket.AF_INET:
                            time_sent = struct.unpack('d', rec_packet[28:28 + bytes_in_double])[0]
                        else:
                            time_sent = struct.unpack('d', rec_packet[8:8 + bytes_in_double])[0]
                        rtt = time_received - time_sent
                        rtt_list.append(rtt)
                        received += 1
                        if ttl is None:
                            ttl = recv_ttl
                        break
                except socket.timeout:
                    break
        except Exception as e:
            raise PyMiniPingException(f"Ping failed: {e}")
        time.sleep(interval if seq < count else 0)
    sock.close()

    if received == 0:
        raise PingTimeout(f"No reply from host {host} (timeout after {timeout}s).")

    loss = ((count - received) / count) * 100 if count else 100
    os_guess = guess_os(ttl) if (ttl is not None and family == socket.AF_INET) else None
    stats = {
        "sent": count,
        "received": received,
        "loss": loss,
        "min": min(rtt_list) if rtt_list else None,
        "max": max(rtt_list) if rtt_list else None,
        "mean": mean(rtt_list) if rtt_list else None,
        "median": median(rtt_list) if rtt_list else None,
        "jitter": stdev(rtt_list) if len(rtt_list) > 1 else 0,
        "rtt_list": rtt_list,
        "ttl": ttl,
        "hops": calc_hops(ttl) if ttl is not None and family == socket.AF_INET else None,
        "os_guess": os_guess,
        "p95": percentile(rtt_list, 95) if rtt_list else None,
    }
    return PingResult(**stats)


def ping_stats(
    host: str,
    count: int = 1,
    timeout: int = 1,
    interval: float = 0.1,
    size: int = 56,
    dscp: int = None,
) -> dict:
    """
    Convenience wrapper around ping() that returns results as a dictionary.

    See ping() for parameters and exception details.

    Returns:
        dict: Ping statistics.
    """
    return ping(host, count, timeout, interval, size, dscp).as_dict()
