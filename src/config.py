import os
from pathlib import Path

from dotenv import load_dotenv


def find_env_file(start_path: Path) -> Path | None:
    """
    Risale la struttura delle cartelle partendo da start_path
    fino a trovare un file .env o arrivare alla root del filesystem.
    """
    for parent in [start_path] + list(start_path.parents):
        env_path = parent / ".env"
        if env_path.exists():
            return env_path
    return None


def initialize_config():
    """Cerca il file .env risalendo dal CWD attuale."""
    env_file = find_env_file(Path.cwd())

    if env_file:
        load_dotenv(env_file)
        return env_file
    return None


# Inizializziamo e salviamo il percorso trovato per l'errore
found_env_path = initialize_config()

# Definiamo cosa ci serve
REQUIRED_VARS = ["BASE_URL", "EMAIL", "PASSWORD"]
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]

if missing_vars:
    print(f"\n\033[1;91m[!] CONFIGURATION ERROR\033[0m")
    print(f"\033[91mThe following environment variables are missing:\033[0m")
    for var in missing_vars:
        print(f"  \033[1m- {var}\033[0m")

    print(f"\n\033[94m[*] How to fix it:\033[0m")
    print(f"Create a file named \033[1m.env\033[0m in your project root.")
    print(f"Currently searching upwards from: \033[3m{Path.cwd()}\033[0m\n")

    example_env = (
        "BASE_URL=https://ctf.cyberchallenge.it\n"
        "EMAIL=your-email@example.com\n"
        "PASSWORD=your-secure-password"
    )
    print(f"\033[90m{'-'*40}\033[0m")
    print(f"\033[97m{example_env}\033[0m")
    print(f"\033[90m{'-'*40}\033[0m\n")

    raise SystemExit(1)

# Variabili esportate
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
