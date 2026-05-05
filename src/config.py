import os
from pathlib import Path

from dotenv import load_dotenv


def initialize_config():
    """Cerca il file .env in CWD o nella Home dell'utente."""
    cwd_env = Path.cwd() / ".env"
    home_env = Path.home() / ".env"

    if cwd_env.exists():
        load_dotenv(cwd_env)
    elif home_env.exists():
        load_dotenv(home_env)


# Inizializziamo il caricamento
initialize_config()

# Definiamo cosa ci serve
REQUIRED_VARS = ["BASE_URL", "EMAIL", "PASSWORD"]
missing_vars = [var for var in REQUIRED_VARS if not os.getenv(var)]

if missing_vars:
    print(f"\n\033[1;91m[!] CONFIGURATION ERROR\033[0m")
    print(f"\033[91mThe following environment variables are missing:\033[0m")
    for var in missing_vars:
        print(f"  \033[1m- {var}\033[0m")

    print(f"\n\033[94m[*] How to fix it:\033[0m")
    print(
        f"Create a file named \033[1m.env\033[0m in \033[3m{Path.cwd()}\033[0m or \033[3m{Path.home()}\033[0m"
    )
    print(f"with the following content:\n")

    # Esempio di file .env pronto all'uso
    example_env = (
        "BASE_URL=https://ctf.cyberchallenge.it\n"
        "EMAIL=your-email@example.com\n"
        "PASSWORD=your-secure-password"
    )
    print(f"\033[90m{'-'*40}\033[0m")
    print(f"\033[97m{example_env}\033[0m")
    print(f"\033[90m{'-'*40}\033[0m\n")

    raise SystemExit(1)

# Se arriviamo qui, le variabili esistono
BASE_URL = os.getenv("BASE_URL")
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
