import os
import random
import time

import instaloader


def update_biography():
    directory = os.path.dirname(os.path.abspath(__file__))
    target_folder = directory  # 簡化路徑處理

    # 1. 統一初始化實例
    L = instaloader.Instaloader(user_agent="Mozilla/5.0 ...")  # 可自定義 User-Agent

    def get_subfolder_names(directory):
        return [
            name
            for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))
            and not name.startswith(".")
            and name != "__pycache__"
        ]

    subfolder_names = get_subfolder_names(target_folder)
    print(f"Found {len(subfolder_names)} subfolders.")

    for subfolder_name in subfolder_names:
        try:
            subfolder_path = os.path.join(target_folder, subfolder_name)

            # 2. 直接使用外部傳入的 L 實例
            profile = instaloader.Profile.from_username(L.context, subfolder_name)

            biography_file_path = os.path.join(subfolder_path, "biography.txt")
            with open(biography_file_path, "w", encoding="utf-8") as file:
                file.write(profile.biography)

            print(f"Success: {subfolder_name}")

            # 3. 顯著增加延遲時間
            delay = random.randint(30, 90)
            print(f"Waiting {delay}s...")
            time.sleep(delay)

        except instaloader.exceptions.ConnectionException as e:
            print(f"IP 被暫時封鎖: {e}")
            break  # 建議直接停止，避免持續撞牆導致永久封鎖
        except Exception as e:
            print(f"Error processing {subfolder_name}: {e}")


if __name__ == "__main__":
    update_biography()
