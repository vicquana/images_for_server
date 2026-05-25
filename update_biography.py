import os
import random
import time
import json

import instaloader


STATE_FILE_NAME = ".biography_update_state.json"


def load_state(state_path):
    try:
        with open(state_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Unable to read state file: {e}")
    return {}


def save_state(state_path, last_processed=None, blocked=False):
    payload = {
        "last_processed": last_processed,
        "blocked": blocked,
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }

    try:
        with open(state_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Unable to write state file: {e}")


def update_biography():
    directory = os.path.dirname(os.path.abspath(__file__))
    target_folder = directory  # 簡化路徑處理
    state_path = os.path.join(target_folder, STATE_FILE_NAME)
    state = load_state(state_path)

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
    random.shuffle(subfolder_names)

    last_processed = state.get("last_processed")
    if last_processed in subfolder_names:
        last_index = subfolder_names.index(last_processed)
        subfolder_names = subfolder_names[last_index + 1 :] + subfolder_names[: last_index + 1]

    print(f"Found {len(subfolder_names)} subfolders.")

    for index, subfolder_name in enumerate(subfolder_names):
        try:
            subfolder_path = os.path.join(target_folder, subfolder_name)

            # 2. 直接使用外部傳入的 L 實例
            profile = instaloader.Profile.from_username(L.context, subfolder_name)

            biography_file_path = os.path.join(subfolder_path, "biography.txt")
            with open(biography_file_path, "w", encoding="utf-8") as file:
                file.write(profile.biography)

            print(f"Success: {subfolder_name}")
            save_state(state_path, last_processed=subfolder_name, blocked=False)

            if index < len(subfolder_names) - 1:
                delay = random.randint(30, 90)

                if (index + 1) % 5 == 0:
                    delay += random.randint(60, 180)
                    print(f"Taking a longer break for {delay}s...")
                else:
                    print(f"Waiting {delay}s...")

                time.sleep(delay)

        except instaloader.exceptions.ConnectionException as e:
            print(f"IP 被暫時封鎖: {e}")
            save_state(state_path, last_processed=subfolder_name, blocked=True)
            break  # 建議直接停止，避免持續撞牆導致永久封鎖
        except Exception as e:
            print(f"Error processing {subfolder_name}: {e}")
            save_state(state_path, last_processed=subfolder_name, blocked=False)


if __name__ == "__main__":
    update_biography()
