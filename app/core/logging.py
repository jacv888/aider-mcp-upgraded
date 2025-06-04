import logging

def get_logger(name):
    """
    Get a configured logger instance with consistent formatting.
    
    Args:
        name: The name of the logger (typically __name__)
        
    Returns:
        A configured logger instance with standard formatting
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
