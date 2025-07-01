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
    PacketError,
)

ICMP_ECHO_REQUEST = 8


def checksum(source: bytes) -> int:
    """Calculate the ICMP checksum."""
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


def create_packet(packet_id: int, seq: int) -> bytes:
    """Create an ICMP Echo Request packet with current timestamp as payload."""
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, 0, packet_id, seq)
    data = struct.pack('d', time.time())
    packet = header + data
    my_checksum = checksum(packet)
    header = struct.pack('!BBHHH', ICMP_ECHO_REQUEST, 0, my_checksum, packet_id, seq)
    return header + data


def calc_hops(received_ttl: int) -> Optional[int]:
    """Estimate hop count based on common initial TTL values."""
    for initial_ttl in (64, 128, 255):
        if received_ttl <= initial_ttl:
            return initial_ttl - received_ttl + 1
    return None


@dataclass
class PingResult:
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

    def as_dict(self) -> dict:
        """Return result as a dictionary."""
        return self.__dict__


def ping(
    host: str,
    count: int = 1,
    timeout: int = 1,
    interval: float = 0.1
) -> PingResult:
    """
    Perform ICMP echo requests to the given host.

    Returns PingResult with all statistics.
    RTTs are returned in seconds!
    """
    try:
        addr = socket.gethostbyname(host)
    except socket.gaierror:
        raise HostUnreachable(f"Cannot resolve host: {host}")

    try:
        icmp = socket.getprotobyname('icmp')
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except PermissionError:
        raise RootRequired("Root privileges or CAP_NET_RAW are required to create RAW socket.")
    except Exception as e:
        raise PyMiniPingException(f"Socket error: {e}")

    packet_id = os.getpid() & 0xFFFF
    rtt_list: List[float] = []
    received = 0
    ttl = None

    for seq in range(1, count + 1):
        packet = create_packet(packet_id, seq)
        try:
            sock.sendto(packet, (addr, 1))
            sock.settimeout(timeout)
            rec_packet, _ = sock.recvfrom(1024)
            time_received = time.time()
            ip_header = rec_packet[:20]
            icmp_header = rec_packet[20:28]
            recv_ttl = ip_header[8]
            _type, code, _chksum, recv_id, recv_seq = struct.unpack('!BBHHH', icmp_header)
            if recv_id == packet_id and recv_seq == seq:
                bytes_in_double = struct.calcsize('d')
                time_sent = struct.unpack('d', rec_packet[28:28 + bytes_in_double])[0]
                rtt = time_received - time_sent  # RTT in seconds
                rtt_list.append(rtt)
                received += 1
                if ttl is None:
                    ttl = recv_ttl
            else:
                raise PacketError("Received malformed or unexpected ICMP packet")
        except socket.timeout:
            # Packet lost, ignore and continue
            pass
        except Exception as e:
            raise PingTimeout(f"Ping failed: {e}")
        time.sleep(interval if seq < count else 0)
    sock.close()

    loss = ((count - received) / count) * 100 if count else 100
    stats = {
        "sent": count,
        "received": received,
        "loss": loss,
        "min": min(rtt_list) if rtt_list else 0,
        "max": max(rtt_list) if rtt_list else 0,
        "mean": mean(rtt_list) if rtt_list else 0,
        "median": median(rtt_list) if rtt_list else 0,
        "jitter": stdev(rtt_list) if len(rtt_list) > 1 else 0,
        "rtt_list": rtt_list,
        "ttl": ttl,
        "hops": calc_hops(ttl) if ttl is not None else 0,
    }
    return PingResult(**stats)


def ping_stats(
    host: str,
    count: int = 1,
    timeout: int = 1,
    interval: float = 0.1
) -> dict:
    """
    Returns result as a dict (wrapper for ping).
    RTTs are in seconds!
    """
    return ping(host, count, timeout, interval).as_dict()
