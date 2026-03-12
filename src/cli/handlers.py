import sys
from src.core.utils import print_separator
from src.core.session import Session


def handle_submit(session: Session, flag: str, challenge_id: int | None) -> None:
    if not challenge_id:
        print("[-] --id is required when submitting a flag.")
        sys.exit(1)

    print(f"[*] Submitting flag for challenge {challenge_id} ...")
    result = session.submit_flag(challenge_id, flag)
    is_valid = result.get("valid")

    if is_valid is True:
        print("[+] Flag is CORRECT!")
    elif is_valid is False:
        print("[-] Flag is WRONG.")
    else:
        print(f"[-] Server response: {result.get('message', 'Unknown error occurred.')}")


def list_challenges(data: dict) -> None:
    print_separator("Available Events")
    for event in data.get("events", []):
        event_name = event.get("name", "Unknown Event")
        sections = event.get("sections", [])
        section_names = [s.get("name", "?") for s in sections]
        challenge_count = sum(len(s.get("challenges", [])) for s in sections)

        print(f"\n  Event:      {event_name}")
        if section_names:
            print(f"  Sections:   {', '.join(section_names)}")
        print(f"  Challenges: {challenge_count}")

    print_separator()
