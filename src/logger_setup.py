import logging

def setup_logger(name):
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create and return a logger object
    return logging.getLogger(name)
