import os
import time
import requests
import zipfile
import shutil

# Constants
REPO_URL = "https://github.com/StarCpt/PluginHub"
ZIP_URL = f"{REPO_URL}/archive/refs/heads/main.zip"
SUBDIR_NAME = "PluginHub"


def should_update(subdir_path):
    if not os.path.exists(subdir_path):
        return True
    # Check if older than 2 hours
    mod_time = os.path.getmtime(subdir_path)
    current_time = time.time()
    return (current_time - mod_time) > 2 * 3600


def download_and_extract():
    # Check if we need to update
    subdir_path = os.path.join(os.getcwd(), SUBDIR_NAME)
    if os.path.exists(subdir_path) and not should_update(subdir_path):
        print(f"{SUBDIR_NAME} exists and is up to date.")
        return

    # Delete old directory if exists
    if os.path.exists(subdir_path):
        shutil.rmtree(subdir_path)
        print(f"Deleted old {SUBDIR_NAME} directory.")

    # Download ZIP
    print("Downloading ZIP...")
    response = requests.get(ZIP_URL)
    response.raise_for_status()
    zip_path = "temp.zip"
    with open(zip_path, "wb") as f:
        f.write(response.content)
    print("ZIP downloaded.")

    # Extract ZIP
    print("Extracting ZIP...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall()

    # The extracted directory name is PluginHub-main
    extracted_dir = "PluginHub-main"
    if os.path.exists(extracted_dir):
        # Remove destination if it exists (handles Windows permission issues)
        if os.path.exists(SUBDIR_NAME):
            try:
                shutil.rmtree(SUBDIR_NAME)
            except Exception as e:
                print(f"Warning: Could not remove existing {SUBDIR_NAME}: {e}")
        # Try rename, fall back to move if rename fails
        try:
            os.rename(extracted_dir, SUBDIR_NAME)
        except OSError:
            shutil.move(extracted_dir, SUBDIR_NAME)
    print(f"Extracted to {SUBDIR_NAME}.")

    # Clean up
    os.remove(zip_path)
    print("Done.")


if __name__ == "__main__":
    download_and_extract()
