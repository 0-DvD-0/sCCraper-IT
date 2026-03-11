<div align="center"><img src="assets/sCCraper-IT-logo.png" height="100px" alt="sCCraper-IT logo"></div>

<h2 align="center">sCCraper IT</h2>

## ✨ Introduction

**sCCraper IT** is a Python-based tool designed to automate the download of all the available **CTF challenges**, including their metadata and attached files, via the platform APIs. It organizes the retrieved content into a structured, easy-to-navigate folder hierarchy.

## 🌐 Supported Platforms

This tool was designed to work with these platforms:

- <img src="assets/cyberchallenge-logo.png" height="20px" alt="CyberChallenge.IT logo"> [CyberChallenge.IT](https://cyberchallenge.it)
- <img src="assets/olicyber-logo.png" height="20px" alt="Olicyber.IT logo"> [Olicyber.IT](https://training.olicyber.it)

> [!NOTE]  
> Access to the above platforms is required. **sCCraper IT** uses your platform **credentials** to authenticate and retrieve challenge data.

## 🚀 Features

- Login with API token via email/password
- Fetches all challenges in the selected platform
- Downloads all attached files
- Automatically downloads hints (if user is a `SUPERVISOR`)
- Saves everything in a clean folder structure

## ⭐ Getting Started

Clone the repository with:

```bash
git clone https://github.com/CreepyMemes/sCCraper-IT.git && cd sCCraper-IT
```

## ⚙️ Configuration

Make a new `.env` file in root directory, and enter your credentials there, follow the example at  `.env.example`:

```bash
# Switch Platform
BASE_URL=https://ctf.cyberchallenge.it
# BASE_URL=https://training.olicyber.it

# Credentials
EMAIL=your@email.com
PASSWORD=your-password
```

## ✅ Usage
Recommended: Global CLI (pipx)

This is the preferred method for Linux and macOS. It handles dependencies automatically and allows you to run sccraper from any directory.

pipx install .

Manual: Standard Script (python -m)

If you prefer not to install the tool globally, or are working in a temporary virtual environment, you can run it as a standard module.
### Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the script:

```bash
python -m src.main
```

## 📂 Output structure

After execution, you’ll find the output folder `data/` generated in the **root directory**, with the following structure:

```bash
data/
├── challenges.json                # Metadata of all challenges
├── challenges/
│   ├── event/
│   │   ├── section/
│   │   │   ├── challenge/
│   │   │   │   ├── challenge.json # Challenge description
│   │   │   │   └── files/
│   │   │   │       ├── file       # Attached file
         ...
```

## 📌 TODO

- [ ] CLI support (e.g. `--email`, `--save-to`)
- [ ] Caching to avoid re-downloading
- [ ] Logging (instead of `print()`)
