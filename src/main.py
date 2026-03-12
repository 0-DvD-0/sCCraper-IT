import sys

from src.cli.parser import build_parser
from src.cli.handlers import handle_submit, list_challenges
from src.core.session import Session
from src.core.scraper import fetch_and_save_challenges, scrape_all, get_new_challenge_ids
from src.config import BASE_URL, EMAIL, PASSWORD


def main() -> None:
    args = build_parser().parse_args()

    try:
        session = Session(BASE_URL, EMAIL, PASSWORD)
    except Exception as exc:
        print(f"[-] Login failed: {exc}")
        sys.exit(1)

    if args.submit:
        handle_submit(session, args.submit, args.id)
        return

    new_challenges, old_challenges = fetch_and_save_challenges(
        session,
        output_dir=args.output,
        events=args.events,
        sections=args.sections,
        tags=args.tags,
    )

    if args.list:
        list_challenges(new_challenges)
        return

    target_ids: set[int] | None = None
    if args.id:
        target_ids = {args.id}
        print(f"[*] Targeting challenge ID: {args.id}")
    elif args.new:
        target_ids = get_new_challenge_ids(new_challenges, old_challenges)
        if not target_ids:
            print("[+] No new challenges found — everything is up to date.")
            return
        print(f"[*] Found {len(target_ids)} new challenge(s).")

    scrape_all(
        session=session,
        challenge_data=new_challenges,
        output_dir=args.output,
        target_ids=target_ids,
    )


if __name__ == "__main__":
    main()
