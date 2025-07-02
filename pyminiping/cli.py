import argparse
from pyminiping import ping, PingTimeout, HostUnreachable, RootRequired, DestinationUnreachable


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
    parser.add_argument("--show-rtts", action="store_true", help="Show all individual RTTs")
    args = parser.parse_args()

    try:
        result = ping(
            args.host,
            count=args.count,
            timeout=args.timeout,
            interval=args.interval,
            size=args.size,
            dscp=args.dscp,
        )
        print(f"\nPing statistics for {args.host}:")
        print(f"  Packets: sent={result.sent}, received={result.received}, loss={result.loss:.1f}%")
        if result.received > 0:
            print(f"  RTT min/avg/max/median/jitter: "
                  f"{result.min:.4f}/{result.mean:.4f}/{result.max:.4f}/{result.median:.4f}/{result.jitter:.4f} sec")
            print(f"  p95: "
                  f"{result.p95:.4f} sec")
            print(f"  TTL: {result.ttl}, hops: {result.hops}, OS guess: {result.os_guess}")
            if args.show_rtts:
                print(f"  All RTTs: {['%.4f' % v for v in result.rtt_list]}")
        else:
            print("  No replies received.")
    except HostUnreachable:
        print("Host unreachable or cannot resolve host.")
    except RootRequired:
        print("Root privileges or CAP_NET_RAW are required to use ICMP RAW sockets.")
    except PingTimeout:
        print("Request timed out: no replies received.")
    except DestinationUnreachable as e:
        print(f"Destination unreachable: {e.message} (code {e.code})")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
