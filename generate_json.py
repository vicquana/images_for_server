import requests
import re
import json


def generate_json(owner='vicquana', repo='images_for_server', path=''):
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
                    print(item['name'])
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
                    sub_folder_data = get_all_file_data(
                        owner, repo, item['path'])
                    folder_data.update(sub_folder_data)
                    print(item['name'])
            return folder_data
        except requests.exceptions.RequestException as e:
            print('Error fetching file data:', e)
            return {}

    # Example usage:
    folder_data = get_all_file_data(owner, repo, '')

    # Save folder_data as JSON file
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(folder_data, f, ensure_ascii=False, indent=4)
