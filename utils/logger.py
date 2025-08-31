"""
Logging system for the game
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class GameLogger:
    """Custom logger for the game with multiple output formats"""

    def __init__(self, log_file: str = "game.log", level: str = "INFO"):
        self.log_file = log_file
        self.level = getattr(logging, level.upper(), logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Configure logger
        self.logger = logging.getLogger('GameLogger')
        self.logger.setLevel(self.level)

        # Remove existing handlers
        self.logger.handlers.clear()

        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(file_formatter)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.level)
        console_handler.setFormatter(console_formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(message, *args, **kwargs)

    def log_performance(self, operation: str, duration: float) -> None:
        """Log performance information"""
        self.logger.info(f"Performance: {operation} took {duration:.3f}s")

    def log_game_event(self, event_type: str, details: str = "") -> None:
        """Log game-specific events"""
        message = f"Game Event: {event_type}"
        if details:
            message += f" - {details}"
        self.logger.info(message)

    def log_error_with_context(self, error: Exception, context: str = "") -> None:
        """Log error with additional context"""
        error_msg = f"Error in {context}: {str(error)}"
        self.logger.error(error_msg, exc_info=True)

    def set_level(self, level: str) -> None:
        """Change logging level"""
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.logger.setLevel(self.level)
        for handler in self.logger.handlers:
            handler.setLevel(self.level)

    def get_recent_logs(self, lines: int = 50) -> list:
        """Get recent log entries"""
        if not os.path.exists(self.log_file):
            return []

        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if len(all_lines) > lines else all_lines
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            return []

    def clear_logs(self) -> bool:
        """Clear the log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"Log cleared at {datetime.now()}\n")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing log file: {e}")
            return False


# Global logger instance
logger = GameLogger()


def get_logger() -> GameLogger:
    """Get the global logger instance"""
    return logger


def log_function_call(func_name: str):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Function {func_name} failed: {e}")
                raise
        return wrapper
    return decorator
