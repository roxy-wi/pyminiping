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
    parser.add_argument("-j", "--json", action="store_true", help="Output in JSON format")
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
        if args.json:
            import json
            print(json.dumps(result.as_dict(), indent=2, default=str))
        else:
            print(result)
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
