"""
Error handling module for ASQ integration.
Provides enhanced error handling, recovery, and user-friendly messages.
"""

import platform
import time
from typing import Any, Callable, Optional, Dict, List
from functools import wraps


class ASQError(Exception):
    """Base exception for ASQ-related errors."""
    pass


class PlatformNotSupportedError(ASQError):
    """Raised when ASQ is used on non-Linux platforms."""
    pass


class ATSPINotAvailableError(ASQError):
    """Raised when AT-SPI libraries are not available."""
    pass


class ElementNotFoundError(ASQError):
    """Raised when an element cannot be found."""
    pass


class TimeoutError(ASQError):
    """Raised when an operation times out."""
    pass


class ErrorHandler:
    """Enhanced error handling for ASQ operations."""
    
    def __init__(self, verbose: bool = False):
        """Initialize error handler.
        
        Args:
            verbose: Whether to print detailed error information
        """
        self.verbose = verbose
        self.error_counts = {}
        self.last_errors = {}
    
    def handle_platform_check(self) -> None:
        """Check platform compatibility and raise appropriate error."""
        if platform.system() != 'Linux':
            raise PlatformNotSupportedError(
                f"ASQ is only supported on Linux systems. "
                f"Current platform: {platform.system()}. "
                f"Consider using alternative automation tools for your platform."
            )
    
    def handle_atspi_check(self) -> None:
        """Check AT-SPI availability and provide installation guidance."""
        try:
            import gi
            gi.require_version('Atspi', '2.0')
            from gi.repository import Atspi
        except ImportError as e:
            if "gi" in str(e):
                raise ATSPINotAvailableError(
                    "PyGObject (gi) is not installed. Install with:\n"
                    "  Ubuntu/Debian: sudo apt-get install python3-gi\n"
                    "  Fedora: sudo dnf install python3-gobject\n"
                    "  Arch: sudo pacman -S python-gobject"
                )
            elif "Atspi" in str(e):
                raise ATSPINotAvailableError(
                    "AT-SPI libraries are not installed. Install with:\n"
                    "  Ubuntu/Debian: sudo apt-get install gir1.2-atspi-2.0\n"
                    "  Fedora: sudo dnf install at-spi2-core-devel\n"
                    "  Arch: sudo pacman -S at-spi2-core"
                )
            else:
                raise ATSPINotAvailableError(f"AT-SPI import error: {e}")
    
    def with_retry(self, max_retries: int = 3, delay: float = 0.5):
        """Decorator to add retry logic to methods.
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                
                for attempt in range(max_retries + 1):
                    try:
                        return func(*args, **kwargs)
                    except (ElementNotFoundError, TimeoutError) as e:
                        last_exception = e
                        if attempt < max_retries:
                            if self.verbose:
                                print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                            time.sleep(delay)
                        else:
                            self._log_error(func.__name__, e)
                            raise
                    except (PlatformNotSupportedError, ATSPINotAvailableError):
                        # Don't retry platform/dependency errors
                        raise
                    except Exception as e:
                        last_exception = e
                        if attempt < max_retries:
                            if self.verbose:
                                print(f"Unexpected error on attempt {attempt + 1}: {e}. Retrying...")
                            time.sleep(delay)
                        else:
                            self._log_error(func.__name__, e)
                            raise
                
                raise last_exception
            return wrapper
        return decorator
    
    def with_timeout(self, timeout: float = 10.0):
        """Decorator to add timeout to methods.
        
        Args:
            timeout: Timeout in seconds
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    if elapsed > timeout:
                        raise TimeoutError(
                            f"Operation '{func.__name__}' timed out after {elapsed:.2f}s "
                            f"(limit: {timeout}s)"
                        )
                    
                    return result
                except Exception as e:
                    elapsed = time.time() - start_time
                    if elapsed > timeout:
                        raise TimeoutError(
                            f"Operation '{func.__name__}' timed out after {elapsed:.2f}s "
                            f"(limit: {timeout}s). Original error: {e}"
                        )
                    raise
            return wrapper
        return decorator
    
    def safe_execute(self, func: Callable, *args, **kwargs) -> Any:
        """Safely execute a function with comprehensive error handling.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if error occurred
        """
        try:
            return func(*args, **kwargs)
        except PlatformNotSupportedError as e:
            if self.verbose:
                print(f"Platform error: {e}")
            return None
        except ATSPINotAvailableError as e:
            if self.verbose:
                print(f"AT-SPI error: {e}")
            return None
        except ElementNotFoundError as e:
            if self.verbose:
                print(f"Element not found: {e}")
            return None
        except TimeoutError as e:
            if self.verbose:
                print(f"Timeout error: {e}")
            return None
        except Exception as e:
            if self.verbose:
                print(f"Unexpected error in {func.__name__}: {e}")
            self._log_error(func.__name__, e)
            return None
    
    def get_user_friendly_error(self, error: Exception) -> str:
        """Convert technical errors to user-friendly messages.
        
        Args:
            error: The exception to convert
            
        Returns:
            User-friendly error message
        """
        if isinstance(error, PlatformNotSupportedError):
            return (
                "ASQ GUI automation is only available on Linux systems. "
                "For Windows, consider using pyautogui or selenium. "
                "For macOS, consider using pyautogui or applescript."
            )
        
        elif isinstance(error, ATSPINotAvailableError):
            return (
                "GUI automation libraries are not installed. "
                "Please install the required packages and try again. "
                "See the error details for specific installation commands."
            )
        
        elif isinstance(error, ElementNotFoundError):
            return (
                "The requested GUI element could not be found. "
                "Make sure the application is open and the element is visible. "
                "Try using a more specific selector or wait for the element to appear."
            )
        
        elif isinstance(error, TimeoutError):
            return (
                "The operation took too long to complete. "
                "The application might be slow to respond or the element might not exist. "
                "Try increasing the timeout or checking if the application is responsive."
            )
        
        else:
            return (
                f"An unexpected error occurred: {str(error)}. "
                "Please check the application state and try again."
            )
    
    def _log_error(self, operation: str, error: Exception) -> None:
        """Log error for debugging and statistics.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
        """
        error_key = f"{operation}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_errors[error_key] = {
            'error': str(error),
            'timestamp': time.time(),
            'count': self.error_counts[error_key]
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for debugging.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            'error_counts': self.error_counts.copy(),
            'last_errors': self.last_errors.copy(),
            'total_errors': sum(self.error_counts.values())
        }
    
    def clear_error_statistics(self) -> None:
        """Clear error statistics."""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
error_handler = ErrorHandler()


def require_linux(func: Callable) -> Callable:
    """Decorator to ensure function only runs on Linux."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        error_handler.handle_platform_check()
        return func(*args, **kwargs)
    return wrapper


def require_atspi(func: Callable) -> Callable:
    """Decorator to ensure AT-SPI is available."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        error_handler.handle_atspi_check()
        return func(*args, **kwargs)
    return wrapper


def with_error_handling(func: Callable) -> Callable:
    """Decorator to add comprehensive error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            friendly_message = error_handler.get_user_friendly_error(e)
            if error_handler.verbose:
                print(f"Error in {func.__name__}: {friendly_message}")
            raise type(e)(friendly_message) from e
    return wrapper