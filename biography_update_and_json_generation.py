import subprocess
import update_biography
import generate_json

def run_git_command(args, check=True):
    try:
        subprocess.run(["git"] + args, check=check)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

def main():
    # Update biographies
    print("Updating biographies...")
    update_biography.update_biography()

    # Commit and push biographies
    run_git_command(["add", "."])
    # Don't check=True for commit because it fails if there are no changes
    run_git_command(["commit", "-m", "update biography text files"], check=False)
    run_git_command(["push"])

    # Generate JSON
    print("Generating JSON payload...")
    generate_json.generate_json("vicquana", "images_for_server", ".")

    # Commit and push JSON
    run_git_command(["add", "."])
    run_git_command(["commit", "-m", "update json database"], check=False)
    run_git_command(["push"])

if __name__ == "__main__":
    main()
