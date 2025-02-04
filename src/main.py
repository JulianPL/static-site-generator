import shutil
import os
from blocknode import markdown_to_html, extract_title

PUBLIC_FOLDER = "./public"
STATIC_FOLDER = "./static"
CONTENT_FOLDER = "./content"
TEMPLATE_FILE = "./template.html"

def main():
    copy_static()
    generate_page_recursive(CONTENT_FOLDER, TEMPLATE_FILE, PUBLIC_FOLDER)
    
def generate_page_recursive(from_path_folder, template_path, dest_path_folder):
    files, _ = list_dir_recursively(from_path_folder)
    for file in files:
        new_file = dest_path_folder+file[len(from_path_folder):][:-len("md")]+"html"
        generate_page(file, template_path, new_file)

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    content_origin = ""
    content_template = ""
    with open(from_path, 'r') as file:
        content_origin = file.read()
    with open(template_path, 'r') as file:
        content_template = file.read()
    title = extract_title(content_origin)
    content = markdown_to_html(content_origin).to_html()
    content_html = content_template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, 'w') as file:
        file.write(content_html)
    
    
    
def copy_static():
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
