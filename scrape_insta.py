
# %% check if using environment
import re
import requests
import json
import instaloader
import os
import sys


def in_venv():
    return sys.prefix != sys.base_prefix


in_venv()

# %% use powershell to scraping instagram accounts
instaloader - -post-filter = "not is_video and likes>1000" ach_nails_studio

instaloader - -login = pihousmith - -no-videos - -no-pictures - -no-metadata - -no-compress-json profile 12am_nail
# %% remove profile picture in each subfoler


def remove_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('_UTC_profile_pic.jpg'):
                file_path = os.path.join(dirpath, filename)
                os.remove(file_path)
                print(f"Removed file: {file_path}")


# Replace 'root_directory_path' with the path of the root directory where you want to start the removal process
root_directory_path = 'C:\yeeder\scraping nail images\images_for_server'
remove_files(root_directory_path)

# %% get biography of an account

# Create an instance of Instaloader
loader = instaloader.Instaloader()
loader.load_session_from_file("pihousmith")
# Load the profile of the user '12_am'
profile = instaloader.Profile.from_username(loader.context, "dayday__nail")

# Get the biography of the profile
biography = profile.biography

# Print or process the biography as needed
print("Biography:", biography)

# %% saves biography for each subfolder

# Function to get all subfolder names in a directory


def get_subfolder_names(directory):
    #    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
    return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name)) and name == 'yeeder0']

# Function to download biography using instaloader


def download_biography(username, folder_path):
    L = instaloader.Instaloader()
    L.load_session_from_file("pihousmith")
    profile = instaloader.Profile.from_username(L.context, username)
    biography_file_path = os.path.join(folder_path, 'biography.txt')
    with open(biography_file_path, 'w', encoding='utf-8') as file:
        file.write(profile.biography)
# Main function


def main():
    try:
        # Navigate to target folder relative to current code file
        target_folder = os.path.join(
            os.path.dirname(__file__), 'images_for_server')
        # Get all subfolder names in the target folder
        subfolder_names = get_subfolder_names(target_folder)

        print(subfolder_names)
        # Iterate through each subfolder
        for subfolder_name in subfolder_names[0:]:
            subfolder_path = os.path.join(target_folder, subfolder_name)
            # Download biography of the account (subfolder name)
            biography = download_biography(subfolder_name, subfolder_path)
            print(f"Biography of {subfolder_name} saving")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()

# %% generate the json of only biography


def generate_biography_json(root_folder):
    biography_data = {}

    # Traverse through each subfolder in the root folder
    for subdir, _, files in os.walk(root_folder):
        # Look for biography.txt in each subfolder
        if 'biography.txt' in files:
            biography_file_path = os.path.join(subdir, 'biography.txt')
            with open(biography_file_path, 'r', encoding='utf-8') as f:
                biography = f.read().strip()
                folder_name = os.path.basename(subdir)
                # Replace newline characters with escaped newlines
                # biography = biography.replace('\n', '\\n')
                biography_data[folder_name] = biography

     # Get the path to save biography_data.json in the root folder
    output_file_path = os.path.join(root_folder, 'biography_data.json')

    # Write the biography data to a JSON file
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(biography_data, json_file, ensure_ascii=False, indent=4)


# Example usage
generate_biography_json('images_for_server')

# %% generate json of images and biography
# no good. this generates a large json file containing the same biography for each image


def get_biography_text(owner, repo, path):
    try:
        response = requests.get(
            f'https://raw.githubusercontent.com/{owner}/{repo}/master/{path}/biography.txt')
        response.raise_for_status()
        return response.text.strip()  # Remove leading/trailing whitespaces
    except requests.exceptions.RequestException as e:
        print('Error fetching biography text:', e)
        return None


def get_all_file_data(owner, repo, path=''):
    try:
        response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/contents/{path}')
        response.raise_for_status()

        folder_data = {}

        # Dictionary to store biography texts for each folder_name
        biography_texts = {}

        # Iterate through the response data
        for item in response.json():
            if item['type'] == 'file' and item['name'].endswith('.jpg'):
                # If it's a .jpg file, add data to the folder_data dictionary
                folder_name = path.split('/')[-1]
                if folder_name not in folder_data:
                    folder_data[folder_name] = []

                # Fetch biography text if exists and not fetched already
                if folder_name not in biography_texts:
                    biography_texts[folder_name] = get_biography_text(
                        owner, repo, path)

                folder_data[folder_name].append({
                    'id': str(len(folder_data[folder_name]) + 1),
                    # Add your style data here (if available)
                    'style': 'French',
                    'price': '2000',  # Add your price data here (if available)
                    # Add your duration data here (if available)
                    'duration': '2 hours',
                    # Format URL of the image
                    'image': f'({item["download_url"]})',
                    # Add biography text
                    'biography': biography_texts[folder_name]
                })
            elif item['type'] == 'dir':
                # If it's a directory, recursively fetch files from it and add to folder_data
                sub_folder_data = get_all_file_data(owner, repo, item['path'])
                folder_data.update(sub_folder_data)

        return folder_data
    except requests.exceptions.RequestException as e:
        print('Error fetching file data:', e)
        return {}


# Example usage:
owner = 'vicquana'
repo = 'images_for_server'
folder_data = get_all_file_data(owner, repo)

# Save folder_data as JSON file
with open('imurl.json', 'w', encoding='utf-8') as f:
    json.dump(folder_data, f, ensure_ascii=False, indent=4)

# %% generate json including biography and description


def get_biography_text(owner, repo, path):
    try:
        response = requests.get(
            f'https://raw.githubusercontent.com/{owner}/{repo}/master/{path}/biography.txt')
        response.raise_for_status()
        return response.text.strip()  # Remove leading/trailing whitespaces
    except requests.exceptions.RequestException as e:
        print('Error fetching biography text:', e)
        return None


def get_description_text(owner, repo, path, jpg_filename):
    try:
        # Extract the base filename before "UTC"
        base_filename = re.search(r'(.+)_UTC', jpg_filename).group(1)
        response = requests.get(
            f'https://raw.githubusercontent.com/{owner}/{repo}/master/{path}/{base_filename}_UTC.txt')
        response.raise_for_status()
        return response.text.strip()  # Remove leading/trailing whitespaces
    except requests.exceptions.RequestException as e:
        print('Error fetching description text:', e)
        return ''


def get_all_file_data(owner, repo, path=''):
    try:
        response = requests.get(
            f'https://api.github.com/repos/{owner}/{repo}/contents/{path}')
        response.raise_for_status()

        folder_data = {}

        # Iterate through the response data
        for item in response.json():
            if item['type'] == 'file' and item['name'].endswith('.jpg'):
                # If it's a .jpg file, add data to the folder_data dictionary
                folder_name = path.split('/')[-1]
                if folder_name not in folder_data:
                    folder_data[folder_name] = {
                        'biography': get_biography_text(owner, repo, path),
                        'images': []
                    }

                # Fetch description text from corresponding .txt file
                description_text = get_description_text(
                    owner, repo, path, item['name'])

                folder_data[folder_name]['images'].append({
                    'id': str(len(folder_data[folder_name]['images']) + 1),
                    # Format URL of the image
                    'image': f'({item["download_url"]})',
                    'description': description_text  # Add description text
                })
            elif item['type'] == 'dir':
                # If it's a directory, recursively fetch files from it and add to folder_data
                sub_folder_data = get_all_file_data(owner, repo, item['path'])
                folder_data.update(sub_folder_data)
        return folder_data
    except requests.exceptions.RequestException as e:
        print('Error fetching file data:', e)
        return {}


# Example usage:
owner = 'vicquana'
repo = 'images_for_server'
folder_data = get_all_file_data(owner, repo, 'yeeder0')

# Save folder_data as JSON file
with open('data1.json', 'w', encoding='utf-8') as f:
    json.dump(folder_data, f, ensure_ascii=False, indent=4)

# %%
