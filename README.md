<div align="center"><img src="assets/sCCraper-IT-logo.png" height="100px" alt="sCCraper-IT logo"></div>

<h2 align="center">sCCraper IT</h2>

## ✨ Introduction
**sCCraper IT** is a Python-based CLI tool designed to automate the download of **CTF challenges**, including their metadata and attached files, via the platform APIs. It organizes the retrieved content into a structured, easy-to-navigate folder hierarchy directly in your current working directory.

## 🌐 Supported Platforms
This tool was designed to work with these platforms:
- <img src="assets/cyberchallenge-logo.png" height="20px" alt="CyberChallenge.IT logo"> [CyberChallenge.IT](https://cyberchallenge.it)
- <img src="assets/olicyber-logo.png" height="20px" alt="Olicyber.IT logo"> [Olicyber.IT](https://training.olicyber.it)

> [!NOTE]
> Access to the above platforms is required. **sCCraper IT** uses your platform **credentials** to authenticate and retrieve challenge data.

## 🚀 Features
- Login with API token via email/password.
- Fetches all challenges from the selected platform.
- Filter challenges by **event**, **section**, or **tags**.
- **[NEW] Auto-Patching**: Automatically applies `chmod +x` to ELF binaries and runs `pwninit` silently if a `libc` is found in the attached files.
- **[NEW] Dashboard UI**: Use `--list` to view a beautiful tree structure tracking your progress (`[✅ Solved]`/`[❌ Unsolved]`) and local file status (`[💾 Local]`/`[☁️ Cloud]`).
- Only fetch **new** challenges since the last run (`--new`) using a hidden local cache.
- **[NEW] Smart Submit**: Submit flags directly from the CLI (`--submit`). Automatically detects the challenge ID from the local directory context (via Markdown frontmatter) — no need to specify the ID manually!
- Saves everything in a clean folder structure directly in your current terminal directory.

## ⭐ Getting Started

Clone the repository with:
```bash
git clone [https://github.com/CreepyMemes/sCCraper-IT.git](https://github.com/CreepyMemes/sCCraper-IT.git) && cd sCCraper-IT

⚙️ Configuration

Create a .env file in the root directory with your credentials, following the example at .env.example:

```bash
BASE_URL=[https://ctf.cyberchallenge.it](https://ctf.cyberchallenge.it)
# BASE_URL=[https://training.olicyber.it](https://training.olicyber.it)

# Credentials
EMAIL=your@email.com
PASSWORD=your-password
``
✅ Installation & Usage

Recommended: Global CLI via pipx

This is the preferred method — it handles dependencies automatically, compiles the tool, and lets you run sccraper from any directory without polluting your global python environment:

```bash 
    pipx install .

```

🖥️ CLI Reference

Flag,Long form,Description
-n,--new,Only download challenges not present in the local .challenges.json cache
-s FLAG,--submit FLAG,Submit a flag. Automatically uses the ID of the current directory
-i ID,--id ID,Target a single challenge by its numeric ID (or force an ID for --submit)
-e EVENT …,--events,Filter by one or more event name substrings
-S SECTION …,--sections,Filter by one or more section name substrings
-t TAG …,--tags,Filter by one or more tags
-l,--list,Open the Interactive Tree Dashboard for events and challenges
-o DIR,--output DIR,Output directory (default: . - Current Working Directory)


