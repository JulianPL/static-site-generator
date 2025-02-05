import logging
import os
import shutil

from blocknode import markdown_to_html, extract_title
from constants import MARKDOWN_EXTENSION, HTML_EXTENSION

logger = logging.getLogger(__name__)

def delete_directory_recursively(path):
    logger.info(f"Deleting directory {path}")
    shutil.rmtree(path, True)

def process_directory_recursively(path_source, path_dest, file_function, root=True, **kwargs):
    # Higher log-level "INFO" only for initial function call
    if root:
        logger.info(f"Processing directory {path_source} to {path_dest} with {file_function.__name__}")
    else:
        logger.debug(f"Processing directory {path_source} to {path_dest} with {file_function.__name__}")
    
    ensure_directory_exists(path_dest)
    
    # Handle files first for cleaner log
    directories = []
    for filename in os.listdir(path_source):
        file_path_source = os.path.join(path_source, filename)
        file_path_dest = os.path.join(path_dest, filename)
        if not os.path.isfile(file_path_source):
            directories.append((file_path_source, file_path_dest))
            continue
        file_function(file_path_source, file_path_dest, **kwargs)
    
    # Process subdirectories recursively
    for path_source_new, path_dest_new in directories:
        process_directory_recursively(path_source_new, path_dest_new, file_function, root=False, **kwargs)

def copy(path_source, path_dest, **kwargs):
    logger.debug(f"Copying file {path_source} to {path_dest}")
    shutil.copy(path_source, path_dest)

def markdown_to_html_page(path_source, path_dest, path_template, **kwargs):
    if not has_extension(path_source, MARKDOWN_EXTENSION):
        logger.warning(f"Found file {path_source} with unknown extension")
        return
    
    path_dest_html = change_extension(path_dest, HTML_EXTENSION)
    logger.debug(f"Translating and copying file {path_source} to {path_dest_html} using {path_template}")
    
    content_origin = read(path_source)
    content_template = read(path_template)
    
    title = extract_title(content_origin)
    content = markdown_to_html(content_origin).to_html()
    content_file = content_template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    
    write(path_dest_html, content_file)
    
def has_extension(filename, extension):
    return filename.endswith(f".{extension}")

def change_extension(filename, extension):
    return filename.rsplit(".", 1)[0]+f".{extension}"

def read(filename):
    with open(filename, 'r') as file:
        return file.read()

def write(filename, content):
    with open(filename, 'w') as file:
        file.write(content)

def ensure_directory_exists(path):
    if not os.path.exists(path):
        logger.debug(f"Create directory {path}")
        os.mkdir(path)