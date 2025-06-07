import os
import shutil
from datetime import datetime
import logging
from typing import Optional # Added this import

try:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
except ImportError:
    # Fallback logger for standalone testing or if logging module is not yet integrated
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

class AiderHistoryManager:
    """
    Manages the backup and rotation of the .aider.chat.history.md file.
    """
    def __init__(self, history_file_path: str = ".aider.chat.history.md", backup_dir: str = None, max_backup_size_mb: int = 10):
        """
        Initializes the AiderHistoryManager.

        Args:
            history_file_path (str): The path to the .aider.chat.history.md file.
            backup_dir (str, optional): The base directory for backups. Defaults to ~/.aider/history_backups.
            max_backup_size_mb (int): The maximum size in MB before the history file is rotated (truncated).
        """
        self.history_file_path = history_file_path
        self.max_backup_size_mb = max_backup_size_mb

        if backup_dir:
            self.backup_base_dir = backup_dir
        else:
            # Default backup directory: ~/.aider/history_backups
            aider_home = os.path.join(os.path.expanduser("~"), ".aider")
            self.backup_base_dir = os.path.join(aider_home, "history_backups")
        
        os.makedirs(self.backup_base_dir, exist_ok=True)
        logger.debug(f"AiderHistoryManager initialized. History file: {self.history_file_path}, Backup dir: {self.backup_base_dir}, Max size: {self.max_backup_size_mb}MB")

    def backup_history(self) -> Optional[str]:
        """
        Creates a timestamped backup of the current history file.
        Returns the path to the created backup file, or None if backup fails or file doesn't exist.
        """
        if not os.path.exists(self.history_file_path):
            logger.info(f"Aider history file not found at '{self.history_file_path}'. Skipping backup.")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"aider_history_{timestamp}.md"
        backup_path = os.path.join(self.backup_base_dir, backup_filename)

        try:
            shutil.copy2(self.history_file_path, backup_path)
            logger.info(f"Backed up '{self.history_file_path}' to '{backup_path}'")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to backup history file '{self.history_file_path}': {e}", exc_info=True)
            return None

    def rotate_history_if_large(self) -> bool:
        """
        Checks the size of the current history file. If it exceeds max_backup_size_mb,
        it truncates the original history file after a backup (if not already done by backup_history).
        Returns True if rotation occurred, False otherwise.
        """
        if not os.path.exists(self.history_file_path):
            logger.info(f"Aider history file not found at '{self.history_file_path}'. Skipping rotation check.")
            return False

        file_size_bytes = os.path.getsize(self.history_file_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        logger.debug(f"Aider history file size: {file_size_mb:.2f} MB (Max: {self.max_backup_size_mb} MB)")

        if file_size_mb > self.max_backup_size_mb:
            logger.info(f"Aider history file size ({file_size_mb:.2f} MB) exceeds max ({self.max_backup_size_mb} MB). Truncating...")
            try:
                # Truncate the original history file
                with open(self.history_file_path, 'w') as f:
                    f.write("") # Clear content
                logger.info(f"Aider history file '{self.history_file_path}' truncated.")
                return True
            except Exception as e:
                logger.error(f"Failed to truncate history file '{self.history_file_path}': {e}", exc_info=True)
        else:
            logger.info(f"Aider history file size ({file_size_mb:.2f} MB) is within limits. No truncation needed.")
        return False
