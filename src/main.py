import logging

import logger_config
import fileutils

from constants import LOG_LEVEL, STATIC_FOLDER, CONTENT_FOLDER, PUBLIC_FOLDER, TEMPLATE_FILE

logger = logging.getLogger(__name__)

def main():
    logger_config.setup_logging(LOG_LEVEL)
    
    fileutils.delete_directory_recursively(PUBLIC_FOLDER)
    fileutils.process_directory_recursively(STATIC_FOLDER, PUBLIC_FOLDER, fileutils.copy)
    fileutils.process_directory_recursively(CONTENT_FOLDER, PUBLIC_FOLDER, fileutils.markdown_to_html_page, path_template=TEMPLATE_FILE)

if __name__ == "__main__":
    main()
