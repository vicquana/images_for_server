import json
import os
import random
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import instaloader


STATE_FILE_NAME = ".biography_update_state.json"
BLOCKING_ERROR_MARKERS = (
    "401",
    "429",
    "unauthorized",
    "please wait",
    "too many queries",
    "rate limit",
)


@dataclass
class BiographyUpdateResult:
    total: int
    updated: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)
    stopped_early: bool = False
    blocked: bool = False

    @property
    def attempted(self) -> int:
        return len(self.updated) + len(self.unchanged) + len(self.failed)

    def print_summary(self) -> None:
        print("Biography update summary:")
        print(f"  Total: {self.total}")
        print(f"  Updated: {len(self.updated)}")
        print(f"  Unchanged: {len(self.unchanged)}")
        print(f"  Failed: {len(self.failed)}")
        print(f"  Skipped: {len(self.skipped)}")
        print(f"  Blocked: {'yes' if self.blocked else 'no'}")
        if self.failed:
            print(f"  Failed accounts: {', '.join(self.failed)}")
        if self.skipped:
            print(f"  Skipped accounts: {', '.join(self.skipped)}")


def load_state(state_path: Path) -> dict:
    try:
        with state_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        pass
    except Exception as error:
        print(f"Unable to read state file: {error}")
    return {}


def _atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            file.write(content)
            temporary_path = Path(file.name)

        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def save_state(state_path: Path, last_processed=None, blocked=False) -> None:
    payload = {
        "last_processed": last_processed,
        "blocked": blocked,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    try:
        _atomic_write_text(
            state_path,
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        )
    except Exception as error:
        print(f"Unable to write state file: {error}")


def create_instaloader() -> instaloader.Instaloader:
    loader = instaloader.Instaloader(
        max_connection_attempts=1,
        fatal_status_codes=[400, 401, 429],
    )

    username = os.environ.get("INSTAGRAM_USERNAME")
    session_file = os.environ.get("INSTALOADER_SESSION_FILE")

    if session_file and not username:
        raise RuntimeError(
            "INSTALOADER_SESSION_FILE requires INSTAGRAM_USERNAME to be set."
        )

    if username:
        if session_file:
            loader.load_session_from_file(username, session_file)
        else:
            loader.load_session_from_file(username)

        logged_in_username = loader.test_login()
        if not logged_in_username:
            raise RuntimeError("Instagram session is invalid or expired.")
        print(f"Using Instagram session for: {logged_in_username}")
    else:
        print(
            "Warning: no INSTAGRAM_USERNAME configured; "
            "using anonymous Instagram access."
        )

    return loader


def _get_subfolder_names(directory: Path) -> list[str]:
    return sorted(
        path.name
        for path in directory.iterdir()
        if path.is_dir()
        and not path.name.startswith(".")
        and path.name != "__pycache__"
        and (
            (path / "biography.txt").is_file()
            or any(child.suffix.lower() == ".jpg" for child in path.iterdir())
        )
    )


def _rotate_after_last_processed(names: list[str], last_processed: str | None) -> list[str]:
    if last_processed not in names:
        return names

    last_index = names.index(last_processed)
    return names[last_index + 1 :] + names[: last_index + 1]


def _is_blocking_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(marker in message for marker in BLOCKING_ERROR_MARKERS)


def _wait_before_next_request(
    request_number: int,
    sleep_fn: Callable[[float], None],
    random_source,
) -> None:
    delay = random_source.randint(30, 90)

    if request_number % 5 == 0:
        delay += random_source.randint(60, 180)
        print(f"Taking a longer break for {delay}s...")
    else:
        print(f"Waiting {delay}s...")

    sleep_fn(delay)


def update_biography(
    directory: str | os.PathLike | None = None,
    loader: instaloader.Instaloader | None = None,
    sleep_fn: Callable[[float], None] = time.sleep,
    random_source=random,
) -> BiographyUpdateResult:
    target_folder = Path(directory or Path(__file__).resolve().parent)
    state_path = target_folder / STATE_FILE_NAME
    state = load_state(state_path)
    loader = loader or create_instaloader()

    subfolder_names = _rotate_after_last_processed(
        _get_subfolder_names(target_folder),
        state.get("last_processed"),
    )
    result = BiographyUpdateResult(total=len(subfolder_names))

    print(f"Found {len(subfolder_names)} subfolders.")

    for index, subfolder_name in enumerate(subfolder_names):
        biography_path = target_folder / subfolder_name / "biography.txt"
        should_stop = False

        try:
            profile = instaloader.Profile.from_username(
                loader.context,
                subfolder_name,
            )
            current_biography = (
                biography_path.read_text(encoding="utf-8")
                if biography_path.exists()
                else None
            )

            if current_biography == profile.biography:
                result.unchanged.append(subfolder_name)
                print(f"Unchanged: {subfolder_name}")
            else:
                _atomic_write_text(biography_path, profile.biography)
                result.updated.append(subfolder_name)
                print(f"Updated: {subfolder_name}")

            save_state(
                state_path,
                last_processed=subfolder_name,
                blocked=False,
            )
        except instaloader.exceptions.ProfileNotExistsException as error:
            result.failed[subfolder_name] = str(error)
            print(f"Profile unavailable: {subfolder_name}: {error}")
            save_state(
                state_path,
                last_processed=subfolder_name,
                blocked=False,
            )
        except instaloader.exceptions.BadResponseException as error:
            is_blocked = _is_blocking_error(error)
            result.failed[subfolder_name] = str(error)
            result.blocked = result.blocked or is_blocked
            should_stop = is_blocked
            print(f"Instagram rejected {subfolder_name}: {error}")
            save_state(
                state_path,
                last_processed=subfolder_name,
                blocked=is_blocked,
            )
        except instaloader.exceptions.ConnectionException as error:
            result.failed[subfolder_name] = str(error)
            result.blocked = _is_blocking_error(error)
            should_stop = True
            print(f"Instagram connection stopped at {subfolder_name}: {error}")
            save_state(
                state_path,
                last_processed=subfolder_name,
                blocked=result.blocked,
            )
        except Exception as error:
            result.failed[subfolder_name] = str(error)
            print(f"Error processing {subfolder_name}: {error}")
            save_state(
                state_path,
                last_processed=subfolder_name,
                blocked=False,
            )

        if should_stop:
            result.stopped_early = True
            result.skipped.extend(subfolder_names[index + 1 :])
            break

        if index < len(subfolder_names) - 1:
            _wait_before_next_request(index + 1, sleep_fn, random_source)

    result.print_summary()
    return result


if __name__ == "__main__":
    update_biography()
