import subprocess
import update_biography
import generate_json

# Run update_biography
update_biography.update_biography()

# # Add changes
subprocess.run(["git", "add", "."])

# # Commit changes
commit_message = "update biography text files"
subprocess.run(["git", "commit", "-m", commit_message])

# # Push changes
subprocess.run(["git", "push"])

# Run generate_json
generate_json.generate_json('vicquana', 'images_for_server', '')
# generate_json_private_repo.generate_json('vicquana', 'images_for_server', '')

# commit git

# Add changes
subprocess.run(["git", "add", "."])

# Commit changes
commit_message = "update json"
subprocess.run(["git", "commit", "-m", commit_message])

# Push changes
subprocess.run(["git", "push"])
