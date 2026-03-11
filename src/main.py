import argparse
from src.core.session import Session
from src.core.scraper import fetch_and_save_challenges, scrape_all, get_new_challenge_ids 
from src.config import BASE_URL, EMAIL, PASSWORD

def main():

    parser = argparse.ArgumentParser(description="sCCraper IT - CTF Challenge Downloader")
    
    # Modes
    parser.add_argument("-n", "--new", action="store_true", help="Only download challenges not present in local challenges.json")
    args = parser.parse_args()
    
    session = Session(BASE_URL, EMAIL, PASSWORD)
    
    new_challenges, old_challenges = fetch_and_save_challenges(session)

    
    if args.new:
        new_ids = get_new_challenge_ids(new_challenges, old_challenges)
        if not new_ids:
            print("[+] No new challenges found. Everything is up to date.")
        else:
            print(f"[*] Found {len(new_ids)} new challenges. Starting download...")
            scrape_all(session, new_challenges)
            
    else:
        # Default behavior (or if --all is flagged)
        print("[*] Downloading all challenges...")
        scrape_all(session, new_challenges)



if __name__ == "__main__":
    main()
