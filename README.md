# Instagram Scraper & Server Data Pipeline 💅

A data pipeline automation repository that scrapes Instagram profiles (nail studios/artists), gathers their images, bios, and descriptions, and compiles them into a structured JSON database (`data.json`) designed to be served directly from the repository.

## Overview
1. **Bio Fetching**: Uses `instaloader` to routinely fetch the biography texts for various Instagram subdirectories.
2. **JSON Generation**: Analyzes local `.jpg` images and descriptions downloaded previously, structures them, and creates a lightweight `data.json` lookup file. No unnecessary Github API operations are performed.
3. **Automated Synchronization (Git)**: Commits and pushes the latest updates to Github automatically.
4. **Scheduling**: A schedule watcher script ensures data pulls are kept perfectly in sync on a weekly basis.

---

## 🚀 Getting Started

This repository uses [uv](https://github.com/astral-sh/uv), an extremely fast Python package and project manager.

### Prerequisites

You need `uv` installed on your machine.
If you do not have it installed, run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Installation

Clone the repository and install the dependencies easily with `uv`:

```bash
uv sync
```

This will automatically create a `.venv` container and resolve all libraries securely.

---

## 🛠 Usage & Scripts

We use standard Python commands via `uv`.

### 1. Manual Scraping & JSON Compilation

This script handles the full pipeline:
- Updating biographies in all valid subdirectories.
- Generating the master `data.json` database.
- Committing everything automatically via Git.
- Pushing updates to the remote repository.

```bash
uv run biography_update_and_json_generation.py
```

### 2. Manual JSON Generation Only
If you only want to compile the local folders into `data.json` without any network requests to Instagram or Github:

```bash
uv run generate_json.py
```

### 3. Automatic Schedule Watcher

If this repository operates on a server/host device (like an always-on Raspberry Pi or backend server), you can launch the watch task. By default, it is configured to run `biography_update_and_json_generation.py` every Monday at `00:00`.

```bash
uv run schedule_update.py
```

---

## 🗂 File Structure Overview

- **`biography_update_and_json_generation.py`**: The pipeline orchestrator.
- **`generate_json.py`**: Parses downloaded profiles and output JSON cleanly. Very fast and executes using `os.walk`.
- **`schedule_update.py`**: Run-forever task that manages execution timing.
- **`update_biography.py`**: Interacts with `instaloader` and downloads `biography.txt` files for local user folders.

### 🧹 Recent Refactors

- Migrated Python environment mapping to `uv` and `pyproject.toml`.
- Rebuilt `.gitignore` to prevent any large Python garbage/environment artifacts.
- Removed redundant scraper scratchpad scripts (`scrape_insta.py` and GitHub API scripts) that significantly slowed down operations and duplicated codebase efforts.
- Replaced dangerous hardcoded absolute paths (`D:\yeeder\...`) referencing old developer machines with safe Python relative variables (`os.path.join()`).
