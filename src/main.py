import shutil
import os

PUBLIC_FOLDER = "./public"
STATIC_FOLDER = "./static"

def main():
    shutil.rmtree(PUBLIC_FOLDER, True)
    files, folders = list_dir_recursively(STATIC_FOLDER)
    for folder in folders:
        new_folder = PUBLIC_FOLDER+folder[len(STATIC_FOLDER):]
        os.mkdir(new_folder)
    for file in files:
        new_file = PUBLIC_FOLDER+file[len(STATIC_FOLDER):]
        if os.path.exists(file):
            shutil.copy(file, new_file)
    
    

def list_dir_recursively(path):
    files_and_dirs_raw = os.listdir(path)
    files = []
    folders = [path]
    for file_or_dir_raw in files_and_dirs_raw:
        file_or_dir = os.path.join(path, file_or_dir_raw)
        if os.path.isfile(file_or_dir):
            files.append(file_or_dir)
        else:
            files_new, folders_new = list_dir_recursively(file_or_dir)
            files += files_new
            folders += folders_new
    return files, folders

if __name__ == "__main__":
    main()
