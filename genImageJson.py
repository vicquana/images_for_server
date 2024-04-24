import requests
import json


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
                    folder_data[folder_name] = []
                folder_data[folder_name].append({
                    'id': str(len(folder_data[folder_name]) + 1),
                    # Add your style data here (if available)
                    'style': 'French',
                    'price': '2000',  # Add your price data here (if available)
                    # Add your duration data here (if available)
                    'duration': '2 hours',
                    # Format URL of the image
                    'image': f'({item["download_url"]})'
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
with open('imurl.json', 'w') as f:
    json.dump(folder_data, f, indent=4)
