import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sccraper",
        description="sCCraper IT — CTF Challenge Downloader",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "-n",
        "--new",
        action="store_true",
        help="Only download challenges absent from the local challenges.json",
    )
    parser.add_argument(
        "-s",
        "--submit",
        metavar="FLAG",
        help="Submit FLAG for the challenge specified by --id",
    )
    parser.add_argument(
        "-i",
        "--id",
        type=int,
        metavar="ID",
        help="Target a single challenge by its numeric ID",
    )
    parser.add_argument(
        "-e",
        "--events",
        nargs="+",
        metavar="EVENT",
        help="Filter by one or more event name substrings  (-e Finals Quals)",
    )
    parser.add_argument(
        "-S",
        "--sections",
        nargs="+",
        metavar="SECTION",
        help="Filter by one or more section name substrings (-S Web Crypto)",
    )
    parser.add_argument(
        "-t",
        "--tags",
        nargs="+",
        metavar="TAG",
        help="Filter by one or more tags                   (-t web pwn rev)",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="List all events, sections and challenge counts, then exit",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=".",
        metavar="DIR",
        help="Output directory (default: ./data)",
    )
    return parser
