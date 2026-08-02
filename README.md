#  Server Data Pipeline 💅

A data pipeline automation repository that extract Instagram profiles (nail studios/artists), gathers their images, bios, and descriptions, and compiles them into a structured JSON database (`data.json`) designed to be served directly from the repository.

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

### 0. Adding a New Instagram Account

To add a new Instagram account to the scraping pipeline:

1. **Create a Folder:** Create a new directory inside the project root (`images_for_server`). The folder name must match **exactly** the Instagram username you want to scrape (e.g., `new_nail_artist`).
2. **Add Images (Optional):** If you already have images and descriptions for this account, place them inside the new folder. Ensure images are saved as `.jpg` and descriptions are saved using the format `<base_filename>_UTC.txt`.
3. **Run the Update Pipeline:** Run the main automation script to fetch the new biography and compile everything.
   ```bash
   uv run biography_update_and_json_generation.py
   ```

### 1. Manual arrangement & JSON Compilation

This script handles the full pipeline:
- Updating biographies in all valid subdirectories.
- Generating the master `data.json` database.
- Committing changed biography files and `data.json` automatically via Git.
- Pushing successful updates even when some Instagram profiles fail.

```bash
uv run biography_update_and_json_generation.py
```

The command exits with status `2` when only part of the Instagram update succeeds.
Successful biographies are still published, while failed profiles keep their previous
`biography.txt` content. A blocking `401` or `429` response stops further Instagram
requests, but biographies completed earlier in the run are still generated and pushed.

### 1.1 Recommended Instagram Session Setup

Anonymous Instagram access is more likely to be rate-limited. Create a reusable
Instaloader session interactively (never put the Instagram password in this repository):

```bash
uv run instaloader --login YOUR_INSTAGRAM_USERNAME \
  --sessionfile .instaloader-session
chmod 600 .instaloader-session
```

Configure the same account and session path for manual runs and the scheduler:

```bash
export INSTAGRAM_USERNAME="YOUR_INSTAGRAM_USERNAME"
export INSTALOADER_SESSION_FILE="$PWD/.instaloader-session"
uv run biography_update_and_json_generation.py
```

The session file, local update state, and scheduler lock are ignored by Git. If no
`INSTAGRAM_USERNAME` is configured, the updater continues in anonymous mode and prints
a warning.

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

### 4. Tests

The tests simulate successful, failed, and blocked Instagram responses without making
network requests:

```bash
uv run python -m unittest discover -s tests -v
```
