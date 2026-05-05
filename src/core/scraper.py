import json
import os
import stat
import subprocess
from typing import Any

from tqdm import tqdm

from src.core.session import Session
from src.core.utils import (clean_filename, ensure_dir, get_challenge_dir,
                            get_data_dir, save_json)

# ---------------------------------------------------------------------------
# Data fetching & persistence
# ---------------------------------------------------------------------------


def filter_challenge_data(
    data: dict[str, Any],
    events: list[str] | None = None,
    sections: list[str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    Returns a deep-filtered copy of *data*, keeping only the events / sections /
    challenges that match the supplied filters.  A ``None`` filter means
    "accept everything" for that dimension.
    """
    filtered_events = []

    for event in data.get("events", []):
        event_name = event.get("name", "")
        if events and not any(f in event_name for f in events):
            continue

        filtered_sections = []
        for section in event.get("sections", []):
            section_name = section.get("name", "")
            if sections and not any(f in section_name for f in sections):
                continue

            filtered_challenges = []
            for challenge in section.get("challenges", []):
                if tags:
                    chal_tags = challenge.get("tags", [])
                    if not any(tag in chal_tags for tag in tags):
                        continue
                filtered_challenges.append(challenge)

            if filtered_challenges:
                filtered_sections.append({**section, "challenges": filtered_challenges})

        if filtered_sections:
            filtered_events.append({**event, "sections": filtered_sections})

    return {**data, "events": filtered_events}


def merge_challenge_data(
    old_data: dict[str, Any], new_filtered: dict[str, Any]
) -> dict[str, Any]:
    """
    Performs a deep merge of challenge data.
    Preserves old events/sections/challenges and updates or adds new ones.
    """
    if not old_data:
        return new_filtered

    # Create a mapping of old events {event_name: event_data}
    merged_events = {e["name"]: e for e in old_data.get("events", [])}

    for new_evt in new_filtered.get("events", []):
        evt_name = new_evt.get("name")
        if evt_name not in merged_events:
            merged_events[evt_name] = {"name": evt_name, "sections": []}

        # Mapping of old sections for this event
        old_sections = {
            s["name"]: s for s in merged_events[evt_name].get("sections", [])
        }

        for new_sec in new_evt.get("sections", []):
            sec_name = new_sec.get("name")
            if sec_name not in old_sections:
                old_sections[sec_name] = {"name": sec_name, "challenges": []}

            # Mapping of old challenges {challenge_id: challenge_data}
            old_challenges = {
                c["id"]: c for c in old_sections[sec_name].get("challenges", [])
            }

            # Add or update with newly fetched challenges
            for new_chal in new_sec.get("challenges", []):
                old_challenges[new_chal["id"]] = new_chal

            # Reconstruct the challenges list
            old_sections[sec_name]["challenges"] = list(old_challenges.values())

        # Reconstruct the sections list
        merged_events[evt_name]["sections"] = list(old_sections.values())

    return {**old_data, "events": list(merged_events.values())}


def post_process_pwn_files(files_dir: str) -> str | None:
    """
    Scansiona la cartella dei file scaricati.
    Se trova binari ELF, fa un chmod +x.
    Se trova una libc, lancia pwninit.
    Ritorna un messaggio di log per tqdm se pwninit è stato eseguito.
    """
    if not os.path.exists(files_dir):
        return None

    has_libc = False
    binaries = []

    # 1. Scansiona i file
    for filename in os.listdir(files_dir):
        filepath = os.path.join(files_dir, filename)
        if not os.path.isfile(filepath):
            continue

        # Controllo se è una libc (es. libc.so.6)
        if "libc" in filename.lower() and ".so" in filename.lower():
            has_libc = True

        # Controllo se è un binario ELF tramite i Magic Bytes
        try:
            with open(filepath, "rb") as f:
                magic = f.read(4)
                if magic == b"\x7fELF":
                    binaries.append(filepath)
                    # Applica i permessi di esecuzione (chmod +x)
                    st = os.stat(filepath)
                    os.chmod(
                        filepath,
                        st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
                    )
        except Exception:
            pass

    # 2. Lancia pwninit se abbiamo sia una libc che almeno un binario
    if has_libc and binaries:
        try:
            # Eseguiamo pwninit direttamente dentro la cartella 'files'
            result = subprocess.run(
                ["pwninit"], cwd=files_dir, capture_output=True, text=True, check=True
            )
            return f"🔧 pwninit auto-patched {len(binaries)} binary/ies!"
        except FileNotFoundError:
            return "⚠️ pwninit skipped: command not found on system."
        except subprocess.CalledProcessError as e:
            return f"❌ pwninit failed: {e.stderr.strip()}"

    elif binaries:
        return f"⚡ Made {len(binaries)} ELF file(s) executable."

    return None


def fetch_and_save_challenges(
    session: Session,
    output_dir: str,
    events: list[str] | None = None,
    sections: list[str] | None = None,
    tags: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """
    Fetches challenges from the API, applies optional filters, merges with
    local history to avoid overwrites, persists the result and returns
    ``(filtered_new_data, old_data)``.
    """
    raw_data = session.api_get("challenges")
    new_data = filter_challenge_data(
        raw_data, events=events, sections=sections, tags=tags
    )

    ensure_dir(output_dir)
    file_path = os.path.join(output_dir, ".challenges.json")

    old_data: dict[str, Any] | None = None
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as fh:
            try:
                old_data = json.load(fh)
            except json.JSONDecodeError:
                old_data = None

    # Merge logic: Combine old data with the newly fetched/filtered data
    if old_data:
        data_to_save = merge_challenge_data(old_data, new_data)
    else:
        data_to_save = new_data

    # Save the deep-merged data
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(data_to_save, fh, indent=4)

    return new_data, old_data


# ---------------------------------------------------------------------------
# Per-challenge helpers
# ---------------------------------------------------------------------------


def fetch_challenge_data(session: Session, challenge_id: int) -> dict[str, Any]:
    """Fetches challenge metadata from the API."""
    return session.api_get(f"challenges/{challenge_id}")


# ---------------------------------------------------------------------------
# ID diffing
# ---------------------------------------------------------------------------


def get_new_challenge_ids(
    new_data: dict[str, Any],
    old_data: dict[str, Any] | None,
) -> set[int]:
    """
    Returns the set of challenge IDs present in *new_data* but absent from
    *old_data* (i.e. challenges added since the last run).
    """

    def _extract_ids(data: dict[str, Any]) -> set[int]:
        return {
            chal["id"]
            for event in data.get("events", [])
            for section in event.get("sections", [])
            for chal in section.get("challenges", [])
        }

    new_ids = _extract_ids(new_data)
    return new_ids if not old_data else new_ids - _extract_ids(old_data)


# ---------------------------------------------------------------------------
# Processing
# ---------------------------------------------------------------------------


def process_challenge(
    session: Session,
    challenge: dict[str, Any],
    event: str,
    section: str,
    output_dir: str,
) -> str | None:
    """
    Downloads metadata and attached files for a single challenge, writing a
    ``README.md`` (and any files) into a dedicated subdirectory.
    Now includes Frontmatter with persistent ID for context-aware submissions.
    Returns a log message string if auto-patching occurred, otherwise None.
    """
    title = challenge["title"]
    challenge_id = challenge["id"]
    challenge_dir = get_challenge_dir(output_dir, event, section, title)
    ensure_dir(challenge_dir)

    challenge_data = fetch_challenge_data(session, challenge_id)
    description = challenge_data.get("description", "No description provided.")

    # Frontmatter configuration
    md_lines = [
        "---",
        f"id: {challenge_id}",
        f"event: {event}",
        f"section: {section}",
        "---",
        "",
        f"# {title}",
        "",
        description,
        "",
    ]

    md_file_path = os.path.join(challenge_dir, "README.md")
    with open(md_file_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    files_dir = os.path.join(challenge_dir, "files")
    downloaded_files = False

    for file in challenge_data.get("files", []):
        ensure_dir(files_dir)
        session.download_file(file["url"], os.path.join(files_dir, file["name"]))
        downloaded_files = True

    if downloaded_files:
        return post_process_pwn_files(files_dir)
    return None


def scrape_all(
    session: Session,
    challenge_data: dict[str, Any],
    output_dir: str,
    target_ids: set[int] | None = None,
) -> None:
    """
    Iterates through *challenge_data* (pre-filtered) and downloads every
    challenge's metadata and files.

    Pass ``target_ids`` to further restrict processing to a specific subset of
    challenge IDs (e.g. only newly added challenges).
    """
    tasks = [
        {
            "challenge": challenge,
            "event": event.get("name", "Unknown Event"),
            "section": section.get("name", "Unknown Section"),
        }
        for event in challenge_data.get("events", [])
        for section in event.get("sections", [])
        for challenge in section.get("challenges", [])
        if target_ids is None or int(challenge["id"]) in target_ids
    ]

    if not tasks:
        print("\n\033[94m[*] No new challenges found. Everything is up to date!\033[0m")
        return

    print(f"\n\033[92m[*] Starting sync for {len(tasks)} challenges...\033[0m\n")

    pbar = tqdm(tasks, unit="chal", bar_format="{l_bar}{bar:30}{r_bar}")
    for task in pbar:
        pbar.set_description(f"📥 {task['challenge']['title'][:20].ljust(20)}")

        log_msg = process_challenge(
            session,
            task["challenge"],
            task["event"],
            task["section"],
            output_dir,
        )

        if log_msg:
            tqdm.write(f"\033[90m  ↳ {task['challenge']['title']}: {log_msg}\033[0m")


def display_challenges_tree(
    session: Session, output_dir: str, filtered_data: dict[str, Any]
):
    """
    Disegna una dashboard ad albero nel terminale mostrando lo stato delle challenge.
    Verifica l'esistenza fisica dei file per determinare lo stato 'Local'.
    """
    # Cerchiamo di ottenere le challenge risolte.
    try:
        solved_ids = set(session.get_solved_ids())
    except AttributeError:
        solved_ids = set()

    print(f"\n\033[1;36m{'='*75}\033[0m")
    print(f"\033[1;36m{'🎯 SCCRAPER DASHBOARD':^75}\033[0m")
    print(f"\033[1;36m{'='*75}\033[0m\n")

    events = filtered_data.get("events", [])
    if not events:
        print("\033[93mNessuna challenge trovata per i filtri specificati.\033[0m")
        return

    for event in events:
        print(f"\033[1;35m🏆 {event['name']}\033[0m")
        sections = event.get("sections", [])

        for i, section in enumerate(sections):
            is_last_sec = i == len(sections) - 1
            sec_prefix = "└── " if is_last_sec else "├── "
            print(f"    {sec_prefix}\033[1;33m📁 {section['name']}\033[0m")

            challenges = section.get("challenges", [])
            for j, chal in enumerate(challenges):
                is_last_chal = j == len(challenges) - 1
                chal_prefix = (
                    "    "
                    + ("    " if is_last_sec else "│   ")
                    + ("└── " if is_last_chal else "├── ")
                )

                c_id = chal["id"]
                title = chal["title"]

                # 🚀 LA MODIFICA È QUI: Controlliamo il File System!
                expected_dir = get_challenge_dir(
                    output_dir, event["name"], section["name"], title
                )
                expected_readme = os.path.join(expected_dir, "README.md")
                is_downloaded = os.path.exists(expected_readme)

                # Imposta i Badge di Stato
                is_solved = c_id in solved_ids
                is_downloaded_status = c_id in solved_ids  # Placeholder

                solve_tag = (
                    "\033[92m[✅ Solved]\033[0m"
                    if is_solved
                    else "\033[91m[❌ Unsolved]\033[0m"
                )
                down_tag = (
                    "\033[94m[💾 Local]\033[0m"
                    if is_downloaded
                    else "\033[90m[☁️ Cloud]\033[0m"
                )

                # Stampa la riga della challenge
                print(
                    f"{chal_prefix}{solve_tag} {down_tag} \033[97m{title}\033[0m \033[90m(ID: {c_id})\033[0m"
                )
        print()
