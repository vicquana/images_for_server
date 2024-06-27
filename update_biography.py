import os
import time
import random
import instaloader

def update_biography():
    # Function to get all subfolder names in the directory of update_biography.py
    directory = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(directory, '')

    def get_subfolder_names(directory):
        return [name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name)) and not name.startswith('.')]

    def download_biography(username, folder_path):
        L = instaloader.Instaloader()
        # L.load_session_from_file("pihousmith") # this causes error in mac
        profile = instaloader.Profile.from_username(L.context, username)
        biography_file_path = os.path.join(folder_path, 'biography.txt')
        with open(biography_file_path, 'w', encoding='utf-8') as file:
            file.write(profile.biography)

    subfolder_names = get_subfolder_names(target_folder)

    print(subfolder_names)
    for subfolder_name in subfolder_names:
        try:
            subfolder_path = os.path.join(target_folder, subfolder_name)
            biography = download_biography(subfolder_name, subfolder_path)
            print(f"Biography of {subfolder_name} saved")
            # Introduce a random delay to avoid request frequency restriction
            delay = random.randint(30, 90)  # Random delay between 30 and 90 seconds
            print(f"Waiting for {delay} seconds before the next request...")
            time.sleep(delay)
        except Exception as e:
            print(f"An error occurred while processing {subfolder_name}: {str(e)}")

if __name__ == "__main__":
    update_biography()
