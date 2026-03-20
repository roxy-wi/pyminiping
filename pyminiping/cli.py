import argparse
from pyminiping import ping, PingTimeout, HostUnreachable, RootRequired, DestinationUnreachable

# ANSI colors
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def packet_printer(info):
    if info["received"]:
        ttl_part = f" ttl={info['ttl']}" if info["ttl"] is not None else ""
        line = (
            f"{info['size']} bytes from {info['reply_from']}: "
            f"seq={info['seq']}{ttl_part} time={info['rtt']:.4f} sec"
        )
        print(colorize(line, GREEN))
    else:
        print(colorize(f"Request timeout for seq {info['seq']}", RED))


def main():
    parser = argparse.ArgumentParser(
        description="Python minimal ICMP ping utility (pyminiping)"
    )
    parser.add_argument("host", help="Host to ping")
    parser.add_argument("-c", "--count", type=int, default=4, help="Number of packets (default: 4)")
    parser.add_argument("-t", "--timeout", type=int, default=1, help="Timeout per packet in seconds (default: 1)")
    parser.add_argument("-i", "--interval", type=float, default=0.1, help="Interval between packets in seconds (default: 0.1)")
    parser.add_argument("-s", "--size", type=int, default=8, help="Payload size in bytes (default: 8)")
    parser.add_argument("--dscp", type=int, help="DSCP value (0-63, optional)")
    parser.add_argument("--ttl", type=int, help="Outgoing TTL / hop limit (1-255)")
    parser.add_argument("--show-rtts", action="store_true", help="Show per-packet RTT output")
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--precise", action="store_true", help="Use kernel timestamping (SO_TIMESTAMPNS) for more accurate RTT")
    args = parser.parse_args()

    try:
        if args.show_rtts and not args.json:
            print(colorize(f"PING {args.host} with {args.size} bytes of data:", CYAN))

        result = ping(
            args.host,
            count=args.count,
            timeout=args.timeout,
            interval=args.interval,
            size=args.size,
            dscp=args.dscp,
            ttl=args.ttl,
            packet_callback=packet_printer if args.show_rtts and not args.json else None,
            use_kernel_timestamp=args.precise,
        )
        print()
        if args.json:
            print(result.as_json(indent=2))
        else:
            if result.received == 0:
                summary_color = RED
            elif result.loss > 0:
                summary_color = YELLOW
            else:
                summary_color = GREEN

            print(colorize(f"Ping statistics for {args.host}:", CYAN))
            print(colorize(
                f"  Packets: sent={result.sent}, received={result.received}, loss={result.loss:.1f}%",
                summary_color
            ))

            if result.received > 0:
                print(colorize(
                    f"  RTT min/avg/max/median/jitter: "
                    f"{result.min:.4f}/{result.mean:.4f}/{result.max:.4f}/{result.median:.4f}/{result.jitter:.4f} sec",
                    summary_color
                ))
                print(colorize(f"  p95: {result.p95:.4f} sec", summary_color))
                print(colorize(
                    f"  TTL: {result.ttl}, hops: {result.hops}, OS guess: {result.os_guess}",
                    summary_color
                ))
            else:
                print(colorize("  No replies received.", RED))

    except HostUnreachable:
        print(colorize("Host unreachable or cannot resolve host.", RED))
    except RootRequired:
        print(colorize("Root privileges or CAP_NET_RAW are required to use ICMP RAW sockets.", RED))
    except PingTimeout:
        print(colorize("Request timed out: no replies received.", RED))
    except DestinationUnreachable as e:
        print(colorize(f"Destination unreachable: {e.message} (code {e.code})", RED))
    except Exception as e:
        print(colorize(f"Error: {e}", RED))


if __name__ == "__main__":
    main()
