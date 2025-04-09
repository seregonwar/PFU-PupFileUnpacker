import logging
import os
from datetime import datetime
from typing import Optional

class PupLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self._setup_logging()
        
    def _setup_logging(self) -> None:
        """Config setup logging"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        log_file = os.path.join(
            self.log_dir,
            f"pup_unpacker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('PupUnpacker')
        
    def info(self, message: str) -> None:
        """register info message"""
        self.logger.info(message)
        
    def warning(self, message: str) -> None:
        """register warning message"""
        self.logger.warning(message)
        
    def error(self, message: str) -> None:
        """register error message"""
        self.logger.error(message)
        
    def debug(self, message: str) -> None:
        """register debug message"""
        self.logger.debug(message)
        
    def log_operation(self, operation: str, status: str, details: Optional[dict] = None) -> None:
        """register operation with its status and details"""
        message = f"Operation: {operation} - Status: {status}"
        if details:
            message += f" - Details: {details}"
        self.info(message) 