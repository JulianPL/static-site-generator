import logging

def setup_logging(log_level='INFO'):
    logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")