import subprocess
import update_biography
import generate_json
import generate_json_private_repo
# Run update_biography
update_biography.update_biography()

# commit git

# Add changes
subprocess.run(["git", "add", "."])

# Commit changes
commit_message = "update biography"
subprocess.run(["git", "commit", "-m", commit_message])

# Push changes
subprocess.run(["git", "push"])

# Run generate_json
generate_json.generate_json('vicquana', 'images_for_server', '')
# generate_json_private_repo.generate_json('vicquana', 'images_for_server', '')
