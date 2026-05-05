import json
import os
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
    file_path = os.path.join(output_dir, "challenges.json")

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


def fetch_challenge_hints(
    session: Session, challenge_hints: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Fetches every hint attached to a challenge."""
    return [session.api_get(f"hint/{hint['id']}") for hint in challenge_hints]


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
) -> None:
    """
    Downloads metadata and attached files for a single challenge, writing a
    ``README.md`` (and any files) into a dedicated subdirectory.
    Now includes Frontmatter with persistent ID for context-aware submissions.
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

    if session.group == "SUPERVISOR":
        hints = fetch_challenge_hints(session, challenge_data["hints"])
        md_lines += ["", "## Hints"]
        for i, hint in enumerate(hints):
            md_lines.append(f"- **Hint {i}**: {hint.get('content', 'No content')}")

    md_file_path = os.path.join(challenge_dir, "README.md")
    with open(md_file_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(md_lines))

    files_dir = os.path.join(challenge_dir, "files")
    for file in challenge_data["files"]:
        ensure_dir(files_dir)
        session.download_file(file["url"], os.path.join(files_dir, file["name"]))


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
        print("[-] No challenges found to download.")
        return

    pbar = tqdm(tasks, unit="chal")
    for task in pbar:
        pbar.set_description(
            f"Downloading: {task['challenge']['title'][:20].ljust(20)}"
        )
        process_challenge(
            session,
            task["challenge"],
            task["event"],
            task["section"],
            output_dir,
        )
