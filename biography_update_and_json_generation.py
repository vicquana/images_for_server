import subprocess
from pathlib import Path

import generate_json
import update_biography


PROJECT_DIR = Path(__file__).resolve().parent


def run_git_command(args, check=True):
    try:
        return subprocess.run(
            ["git", *args],
            cwd=PROJECT_DIR,
            check=check,
        )
    except subprocess.CalledProcessError as error:
        print(f"Git command failed: {error}")
        raise


def has_staged_changes(paths: list[str]) -> bool:
    result = run_git_command(
        ["diff", "--cached", "--quiet", "--", *paths],
        check=False,
    )
    if result.returncode not in (0, 1):
        raise RuntimeError(f"Unable to inspect staged changes: exit {result.returncode}")
    return result.returncode == 1


def publish_updates(result: update_biography.BiographyUpdateResult) -> bool:
    paths_to_stage = [
        f"{account}/biography.txt"
        for account in result.updated
    ]
    paths_to_stage.append("data.json")

    run_git_command(["add", "--", *paths_to_stage])

    if not has_staged_changes(paths_to_stage):
        print("No biography or JSON changes to publish.")
        return False

    commit_message = (
        "update biographies and json database "
        f"({len(result.updated)} updated, {len(result.failed)} failed)"
    )
    run_git_command(
        ["commit", "--only", "-m", commit_message, "--", *paths_to_stage]
    )
    run_git_command(["push"])
    print("Published available biography and JSON updates.")
    return True


def main() -> int:
    print("Updating biographies...")
    result = update_biography.update_biography(PROJECT_DIR)

    print("Generating JSON payload...")
    generate_json.generate_json(
        "vicquana",
        "images_for_server",
        str(PROJECT_DIR),
    )

    publish_updates(result)

    if result.failed:
        print(
            "Finished with partial success: failed biographies kept their "
            "previous content."
        )
        return 2

    print("Finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
