import json
import os
import re


def generate_json(owner="vicquana", repo="images_for_server", root_dir="."):
    """
    Generates a structured JSON string by iterating through local directories.
    Instead of making network calls to GitHub, we construct the download raw URLs
    manually and read texts from the local disk directly.
    """
    folder_data = {}

    # Define the base raw content URL for GitHub
    base_raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master"

    # Iterate through the subdirectories in the given local directory
    for root, dirs, files in os.walk(root_dir):
        # Ignore hidden folders like .git, .venv, .venv1, __pycache__, etc.
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]

        folder_name = os.path.basename(root)
        
        # Skip the top-level directory itself to only process subfolders
        if root == root_dir:
            continue
            
        # Get biography if the file exists
        biography = ""
        biography_path = os.path.join(root, "biography.txt")
        if os.path.exists(biography_path):
            with open(biography_path, "r", encoding="utf-8") as f:
                biography = f.read().strip()

        # Gather images and descriptions
        if folder_name not in folder_data:
            folder_data[folder_name] = {"biography": biography, "images": []}

        # Filter out all jpgs
        jpg_files = [f for f in files if f.endswith(".jpg")]
        
        for jpg_file in jpg_files:
            # Construct description file name: base_UTC.txt
            match = re.search(r"(.+)_UTC", jpg_file)
            description_text = ""
            if match:
                base_filename = match.group(1)
                desc_path = os.path.join(root, f"{base_filename}_UTC.txt")
                if os.path.exists(desc_path):
                    with open(desc_path, "r", encoding="utf-8") as f:
                        description_text = f.read().strip()

            # Formulate the simulated github path
            relative_path = os.path.relpath(root, root_dir).replace("\\", "/")
            download_url = f"{base_raw_url}/{relative_path}/{jpg_file}"

            folder_data[folder_name]["images"].append(
                {
                    "id": str(len(folder_data[folder_name]["images"]) + 1),
                    "image": f"({download_url})",
                    "description": description_text,
                }
            )

        # If a folder has no images and no biography (maybe an empty folder),
        # we can choose to ignore it or keep it. We'll keep it for now as per
        # original logic but prune if it's completely empty arrays.
        if not folder_data[folder_name]["images"] and not biography:
            del folder_data[folder_name]

    # Save to JSON file
    output_path = os.path.join(root_dir, "data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(folder_data, f, ensure_ascii=False, indent=4)
    
    print(f"Generated {output_path} successfully.")

if __name__ == "__main__":
    generate_json()
