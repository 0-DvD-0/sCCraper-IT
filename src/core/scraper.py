import os
import json
from typing import Any
from src.core.session import Session
from src.core.utils import (
    clean_filename, 
    ensure_dir, save_json, 
    get_challenge_dir, 
    get_data_dir
)

def fetch_and_save_challenges(session: Session) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """
    Fetches new data and loads old data if it exists.
    Returns: (new_data, old_data)
    """
    new_data = session.api_get("challenges")
    data_dir = get_data_dir()
    ensure_dir(data_dir)
    file_path = os.path.join(data_dir, 'challenges.json')

    old_data = None
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = None

    save_json(file_path, new_data)
    return new_data, old_data

def fetch_challenge_data(session: Session, challenge_id: int) -> dict[str, Any]:
    """
    Fetches challenge metadata from the API in JSON format
    """
    return session.api_get(f"challenges/{challenge_id}")


def fetch_challenge_hints(session: Session, challenge_hints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Fetches all hints for the given challenge from the API as a List
    """
    return [session.api_get(f"hint/{hint['id']}") for hint in challenge_hints]

def get_new_challenge_ids(new_data: dict, old_data: dict | None) -> set[int]:
    """
    Extracts IDs from both datasets and returns only the ones present in 'new' but not 'old'.
    """
    def extract_ids(data):
        ids = set()
        for event in data.get('events', []):
            for section in event.get('sections', []):
                for chal in section.get('challenges', []):
                    ids.add(chal['id'])
        return ids

    new_ids = extract_ids(new_data)
    if not old_data:
        return new_ids
    
    old_ids = extract_ids(old_data)
    return new_ids - old_ids


def process_challenge(session: Session, challenge: dict[str, Any], event: str, section: str):
    """
    Process current given challenge, downloading it's metadata (in JSON format) and any attached files.
    """
    title = challenge["title"]
    challenge_dir = get_challenge_dir(event, section, title)
    ensure_dir(challenge_dir)

    challenge_data = fetch_challenge_data(session, challenge["id"])

    if session.group == "SUPERVISOR":
        challenge_data['hints'] = fetch_challenge_hints(session, challenge_data['hints'])

    save_json(os.path.join(challenge_dir, f"{clean_filename(title)}.json"), challenge_data)

    files_dir = os.path.join(challenge_dir, 'files')

    for file in challenge_data['files']: 
        ensure_dir(files_dir)
        file_path = os.path.join(files_dir, file['name'])
        session.download_file(file['url'], file_path)
    
    print(f'Done downloading: {title}')


def scrape_all(session: Session, challenge_data: dict[str, Any]):
    """
    Iterates through all challenges, downloading their metadata (in JSON format) and any attached files.
    Each challenge is stored in its own subdirectory within a central output folder.
    """
    for event in challenge_data['events']:
        for section in event['sections']:
            for challenge in section['challenges']:   
                process_challenge(session, challenge, event['name'], section['name'])
