import sys
import argparse
from src.core.session import Session
from src.core.scraper import fetch_and_save_challenges, scrape_all, get_new_challenge_ids 
from src.config import BASE_URL, EMAIL, PASSWORD

def main():

    parser = argparse.ArgumentParser(description="sCCraper IT - CTF Challenge Downloader")
    
    # Modes
    parser.add_argument("-n", "--new", action="store_true", help="Only download challenges not present in local challenges.json")
    parser.add_argument("-s", "--submit", type=str, help="Submit a flag for the challenge specified by --id")
    parser.add_argument("-i","--id",type=int, help="Download a specific challenge by ID")
    parser.add_argument("-e","--event",type=str, help="Filter by event name")
    parser.add_argument("-t", "--tags", nargs="+", help="Filter by one or more tags (-t web pwn)")
    parser.add_argument("-l", "--list", action="store_true", help="List all available events and their sections")
    args = parser.parse_args()
    try:

        session = Session(BASE_URL, EMAIL, PASSWORD)
    except Exception as e:
        print(f"[-] Login failed: {e}")
        sys.exit(1)
    if args.submit:
        if not args.id:
            print("[-] Error: Specify the challenge ID using --id [ID] to submit a flag.")
            sys.exit(1)

        print(f"[*] Submitting flag for challenge {args.id}...")
        result = session.submit_flag(args.id, args.submit)
        
        is_valid = result.get("valid")
        
        if is_valid is True:
            print(f"[+]  Flag is CORRECT!")
        elif is_valid is False:
            print(f"[-] Flag is WRONG.")
        else:
            # Handle potential 500 error or unexpected response
            msg = result.get('message', 'Unknown error occurred.')
            print(f"[-]  Server response: {msg}")
        
        return

    new_challenges, old_challenges = fetch_and_save_challenges(session)
    
    if args.list:
        print(f"\n{'-'*30}")
        print(f" Available Events:")
        print(f"{'-'*30}")
        
        for event in new_challenges.get('events', []):
            event_name = event.get('name', 'Unknown Event')
            sections = [s.get('name') for s in event.get('sections', [])]
            
            print(f"\n Event:  {event_name}")
            if sections:
                print(f"  Sections: {', '.join(sections)}")
            
            count = sum(len(s.get('challenges', [])) for s in event.get('sections', []))
            print(f"    Challenges: {count}")
            
        print(f"\n{'-'*30}\n")
        return

    target_ids = None

    if args.id:
        target_ids = {args.id}
        print(f"[*] Focusing on ID: {args.id}")
    elif args.new:
        target_ids = get_new_challenge_ids(new_challenges, old_challenges)
        if not target_ids:
            print("[+] No new challenges found. Everything is up to date.")
            return
        print(f"[*] Found {len(target_ids)} new challenges.")
    
    scrape_all(
        session=session,
        challenge_data=new_challenges,
        target_ids=target_ids,
        filter_event=args.event,
        filter_tags=args.tags,
    )


if __name__ == "__main__":
    main()
