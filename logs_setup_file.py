import logging
import os
from datetime import datetime



def setup_logging(module_name):
    """
    Setup logging for a specific module (file).
    
    Args:
        module_name (str): The name of the module/file using this logging setup.
    
    Returns:
        logger (logging.Logger): Configured logger instance.
    """
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(BASE_DIR, "logs_detail")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate a log file name based on the current date and module name
    log_file = os.path.join(log_dir, f"{module_name}_log_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    # Set up logging configuration
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,  # Set the logging level to INFO
        format="%(asctime)s - %(levelname)s - %(message)s",
        filemode='a'  # Append to the existing log file
    )
    
    logger = logging.getLogger(module_name)
    return logger
