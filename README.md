<div align="center"><img src="assets/sCCraper-IT-logo.png" height="100px" alt="sCCraper-IT logo"></div>

<h2 align="center">sCCraper IT</h2>
## ✨ Introduction
**sCCraper IT** is a Python-based CLI tool designed to automate the download of **CTF challenges**, including their metadata and attached files, via the platform APIs. It organizes the retrieved content into a structured, easy-to-navigate folder hierarchy.

## 🌐 Supported Platforms
This tool was designed to work with these platforms:
- <img src="assets/cyberchallenge-logo.png" height="20px" alt="CyberChallenge.IT logo"> [CyberChallenge.IT](https://cyberchallenge.it)
- <img src="assets/olicyber-logo.png" height="20px" alt="Olicyber.IT logo"> [Olicyber.IT](https://training.olicyber.it)

> [!NOTE]
> Access to the above platforms is required. **sCCraper IT** uses your platform **credentials** to authenticate and retrieve challenge data.

## 🚀 Features
- Login with API token via email/password
- Fetches all challenges from the selected platform
- Filter challenges by **event**, **section**, or **tags**
- Downloads all attached files
- Automatically downloads hints (if user is a `SUPERVISOR`)
- Only fetch **new** challenges since the last run (`--new`)
- Submit flags directly from the CLI (`--submit`)
- Saves everything in a clean folder structure

## ⭐ Getting Started

Clone the repository with:
```bash
git clone https://github.com/CreepyMemes/sCCraper-IT.git && cd sCCraper-IT
```

## ⚙️ Configuration

Create a `.env` file in the root directory with your credentials, following the example at `.env.example`:
```bash
# Switch Platform
BASE_URL=https://ctf.cyberchallenge.it
# BASE_URL=https://training.olicyber.it

# Credentials
EMAIL=your@email.com
PASSWORD=your-password
```

## ✅ Installation & Usage

**Recommended: Global CLI via pipx**

This is the preferred method — it handles dependencies automatically and lets you run `sccraper` from any directory:
```bash
pipx install .
```

**Manual: Standard module**

If you prefer not to install globally, install dependencies and run directly:
```bash
pip install -r requirements.txt
python -m src.main
```

## 🖥️ CLI Reference

```
usage: sccraper [-h] [-n] [-s FLAG] [-i ID] [-e EVENT [EVENT ...]]
                [-S SECTION [SECTION ...]] [-t TAG [TAG ...]] [-l] [-o DIR]
```

| Flag | Long form | Description |
|------|-----------|-------------|
| `-n` | `--new` | Only download challenges not present in the local `challenges.json` |
| `-s FLAG` | `--submit FLAG` | Submit a flag for the challenge specified by `--id` |
| `-i ID` | `--id ID` | Target a single challenge by its numeric ID |
| `-e EVENT …` | `--events` | Filter by one or more event name substrings |
| `-S SECTION …` | `--sections` | Filter by one or more section name substrings |
| `-t TAG …` | `--tags` | Filter by one or more tags |
| `-l` | `--list` | List all available events, sections and challenge counts |
| `-o DIR` | `--output DIR` | Output directory (default: `./data`) |

**Examples:**
```bash
# Download everything
sccraper

# List available events and sections
sccraper --list

# Download only new challenges since last run
sccraper --new

# Filter by event and section
sccraper --events "CyberChallenge.IT 2025" --sections "Web" "Crypto"

# Filter by tags and save to a custom directory
sccraper --tags pwn rev --output ./challenges

# Download a single challenge by ID
sccraper --id 42

# Submit a flag
sccraper --submit "flag{example}" --id 42
```

## 📂 Output Structure

After execution, the output folder (default: `data/`) will be structured as follows:
```
data/
├── challenges.json          # Filtered metadata of all fetched challenges
└── challenges/
    └── event/
        └── section/
            └── challenge/
                ├── README.md    # Challenge description (and hints if SUPERVISOR)
                └── files/
                    └── ...      # Attached files
```

## 📌 TODO
- [x] Caching to avoid re-downloading unchanged files
- [ ] Logging (instead of `print()`)
- [ ] `--email` / `--password` CLI overrides for credentials
