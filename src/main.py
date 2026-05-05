import sys

from src.cli.handlers import handle_submit
from src.cli.parser import build_parser
from src.config import BASE_URL, EMAIL, PASSWORD
from src.core.scraper import \
    display_challenges_tree  # <-- Nuova importazione per la UI ad albero
from src.core.scraper import (fetch_and_save_challenges, get_new_challenge_ids,
                              scrape_all)
from src.core.session import Session
from src.core.utils import \
    get_id_from_context  # <-- Nuova importazione per il Context-Aware


def main() -> None:
    args = build_parser().parse_args()

    try:
        session = Session(BASE_URL, EMAIL, PASSWORD)
    except Exception as exc:
        print(f"[-] Login failed: {exc}")
        sys.exit(1)

    # ---------------------------------------------------------
    # 1. Gestione Sottomissione (Context-Aware)
    # ---------------------------------------------------------
    if args.submit:
        target_id = args.id

        # Se non è stato fornito un ID tramite flag, proviamo a leggerlo dal README
        if not target_id:
            target_id = get_id_from_context()
            if target_id:
                print(
                    f"\033[92m[*] Context detected: using Challenge ID {target_id} from local README.md\033[0m"
                )
            else:
                print(
                    "\033[91m[-] Error: No ID provided and no README.md found in current folder.\033[0m"
                )
                print(
                    "    Use the -i flag or run this command from inside a challenge directory."
                )
                sys.exit(1)

        handle_submit(session, args.submit, target_id)
        return

    # ---------------------------------------------------------
    # 2. Fetch e Aggiornamento Cache
    # ---------------------------------------------------------
    new_challenges, old_challenges = fetch_and_save_challenges(
        session,
        output_dir=args.output,
        events=args.events,
        sections=args.sections,
        tags=args.tags,
    )

    # ---------------------------------------------------------
    # 3. Visualizzazione Dashboard (Nuova UI)
    # ---------------------------------------------------------
    if args.list:
        display_challenges_tree(session, args.output, new_challenges)
        return

    # ---------------------------------------------------------
    # 4. Selezione Target e Scraping
    # ---------------------------------------------------------
    target_ids: set[int] | None = None
    if args.id:
        target_ids = {args.id}
        print(f"[*] Targeting challenge ID: {args.id}")
    elif args.new:
        target_ids = get_new_challenge_ids(new_challenges, old_challenges)
        if not target_ids:
            print(
                "\033[94m[+] No new challenges found — everything is up to date.\033[0m"
            )
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
