import logging
import os
from typing import Optional

class LinkedFormatter(logging.Formatter):
    """Custom formatter that creates clickable links to source code in log messages."""
    
    def __init__(self, fmt: Optional[str] = None):
        super().__init__(fmt or '%(levelname)s:%(filename)s:%(lineno)d: %(message)s')
        
    def format(self, record):
        # Get the absolute path of the source file
        filepath = os.path.abspath(record.pathname)
        
        # Format the basic message
        message = super().format(record)
        
        # Create a link format that most IDEs and terminals will recognize
        # Format: file://filepath:line:column
        link = f"file://{filepath}:{record.lineno}:1"
        
        # Wrap the message with the link
        return f"\u001B]8;;{link}\u001B\\{message}\u001B]8;;\u001B\\"

def setup_logging(level: int = logging.INFO):
    """Set up logging with the custom linked formatter."""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Create console handler with linked formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LinkedFormatter())
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

# Example usage
if __name__ == "__main__":
    logger = setup_logging()
    
    def process_data():
        logger.info("Processing data...")
        try:
            # Simulate some error
            result = 1 / 0
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
    
    process_data()
