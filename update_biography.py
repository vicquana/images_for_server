import os
import random
import time

import instaloader


def update_biography():
    # Function to get all subfolder names in the directory of update_biography.py
    directory = os.path.dirname(os.path.abspath(__file__))
    target_folder = os.path.join(directory, "")

    def get_subfolder_names(directory):
        return [
            name
            for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name)) and not name.startswith(".")
        ]

    def download_biography(username, folder_path):
        L = instaloader.Instaloader()
        # L.load_session_from_file("pihousmith") # this causes error in mac
        profile = instaloader.Profile.from_username(L.context, username)
        biography_file_path = os.path.join(folder_path, "biography.txt")
        with open(biography_file_path, "w", encoding="utf-8") as file:
            file.write(profile.biography)

    subfolder_names = get_subfolder_names(target_folder)

    print(f"Found {len(subfolder_names)} subfolders: {subfolder_names}")
    for index, subfolder_name in enumerate(subfolder_names):
        try:
            subfolder_path = os.path.join(target_folder, subfolder_name)
            download_biography(subfolder_name, subfolder_path)
            print(f"Biography of {subfolder_name} saved")
            
            # Don't sleep after the very last item
            if index < len(subfolder_names) - 1:
                # Introduce a random delay to avoid Instagram's strict rate limits
                # Random delay between 30 and 60 seconds to mimic human behavior
                delay = random.randint(30, 60)
                
                # Take a longer breather every 5 requests
                if (index + 1) % 5 == 0:
                    delay += random.randint(60, 120)
                    print(f"Taking a longer break for {delay} seconds to prevent rate-limiting...")
                else:
                    print(f"Waiting for {delay} seconds before the next request...")
                    
                time.sleep(delay)
                
        except Exception as e:
            print(f"An error occurred while processing {subfolder_name}: {str(e)}")


if __name__ == "__main__":
    update_biography()
