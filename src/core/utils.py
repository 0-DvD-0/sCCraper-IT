import json
import os
import re
from typing import Any


def clean_filename(title: str) -> str:
    """
    Cleans the title from trash so it can be safely used as a filename.
    """
    return re.sub(r"[^a-zA-Z0-9_-]", "", title.replace(" ", "_"))


def get_data_dir() -> str:
    """
    Restituisce la cartella corrente del terminale.
    Questo fa comportare sccraper come un vero tool Linux.
    """
    # ✅ MODIFICA QUI: Ora usa la directory corrente in cui hai lanciato il comando
    return os.getcwd()


def get_challenge_dir(base_dir: str, event: str, section: str, title: str) -> str:
    """
    Returns directory path for a challenge.
    """
    return os.path.join(
        base_dir, clean_filename(event), clean_filename(section), clean_filename(title)
    )


def ensure_dir(path: str):
    """
    Create a directory if it doesn't exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def get_id_from_context():
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            content = f.read()
            # Cerca "id: 12345" o simile nel testo
            match = re.search(r"id:\s*(\d+)", content)
            if match:
                return match.group(1)
    return None


def save_json(file_path: str, data: dict[str, Any]):
    """
    Saves the given dict to a json file in the given path
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def print_separator(label: str | None = None, width: int = 40) -> None:
    print(f"\n{'-' * width}")
    if label:
        print(f" {label}")
        print(f"{'-' * width}")
