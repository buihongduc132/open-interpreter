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


class ScreenCaptureError(ASQError):
    """Raised when screen capture operations fail."""
    pass


class OCRError(ASQError):
    """Raised when OCR operations fail."""
    pass


class TextProcessingError(ASQError):
    """Raised when text processing operations fail."""
    pass


class DependencyError(ASQError):
    """Raised when required dependencies are missing."""
    pass


class ResourceError(ASQError):
    """Raised when system resources are insufficient."""
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
        
        elif isinstance(error, ScreenCaptureError):
            return (
                "Screen capture failed. This could be due to missing screenshot libraries "
                "or insufficient permissions. Try installing PIL (Pillow) or pyautogui, "
                "or check if your desktop environment supports screenshots."
            )
        
        elif isinstance(error, OCRError):
            return (
                "Text extraction from image failed. This could be due to missing OCR libraries "
                "or poor image quality. Try installing tesseract, easyocr, or paddleocr, "
                "or ensure the image contains clear, readable text."
            )
        
        elif isinstance(error, TextProcessingError):
            return (
                "Text processing operation failed. This could be due to invalid input "
                "or inaccessible text elements. Check that the target element contains "
                "editable text and is currently visible."
            )
        
        elif isinstance(error, DependencyError):
            return (
                "Required software dependencies are missing. Please install the missing "
                "packages as indicated in the error details and try again."
            )
        
        elif isinstance(error, ResourceError):
            return (
                "System resources are insufficient for this operation. This could be due to "
                "low memory, disk space, or CPU limitations. Try closing other applications "
                "or simplifying the operation."
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
    
    def validate_input(self, value: Any, expected_type: type, name: str) -> None:
        """Validate input parameters.
        
        Args:
            value: Value to validate
            expected_type: Expected type
            name: Parameter name for error messages
            
        Raises:
            ValueError: If validation fails
        """
        if not isinstance(value, expected_type):
            raise ValueError(
                f"Parameter '{name}' must be of type {expected_type.__name__}, "
                f"got {type(value).__name__}"
            )
    
    def validate_selector(self, selector: str) -> None:
        """Validate CSS-like selector string.
        
        Args:
            selector: Selector to validate
            
        Raises:
            ValueError: If selector is invalid
        """
        if not selector or not isinstance(selector, str):
            raise ValueError("Selector must be a non-empty string")
        
        if len(selector.strip()) == 0:
            raise ValueError("Selector cannot be empty or whitespace only")
    
    def check_resource_availability(self, resource_type: str, 
                                   required_memory_mb: Optional[int] = None,
                                   required_disk_mb: Optional[int] = None) -> None:
        """Check if system resources are sufficient.
        
        Args:
            resource_type: Type of resource being checked
            required_memory_mb: Required memory in MB
            required_disk_mb: Required disk space in MB
            
        Raises:
            ResourceError: If resources are insufficient
        """
        import psutil
        import shutil
        
        try:
            # Check memory if specified
            if required_memory_mb:
                available_memory = psutil.virtual_memory().available / (1024 * 1024)
                if available_memory < required_memory_mb:
                    raise ResourceError(
                        f"Insufficient memory for {resource_type}. "
                        f"Required: {required_memory_mb}MB, Available: {available_memory:.1f}MB"
                    )
            
            # Check disk space if specified
            if required_disk_mb:
                available_disk = shutil.disk_usage('/tmp').free / (1024 * 1024)
                if available_disk < required_disk_mb:
                    raise ResourceError(
                        f"Insufficient disk space for {resource_type}. "
                        f"Required: {required_disk_mb}MB, Available: {available_disk:.1f}MB"
                    )
                    
        except ImportError:
            # psutil not available, skip resource checks
            if self.verbose:
                print("Warning: psutil not available, skipping resource checks")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Resource check failed: {e}")
    
    def check_dependency(self, module_name: str, package_name: Optional[str] = None,
                        install_command: Optional[str] = None) -> bool:
        """Check if a dependency is available.
        
        Args:
            module_name: Name of the module to import
            package_name: Name of the package (if different from module)
            install_command: Command to install the package
            
        Returns:
            True if dependency is available
            
        Raises:
            DependencyError: If dependency is missing
        """
        try:
            __import__(module_name)
            return True
        except ImportError:
            package = package_name or module_name
            install_cmd = install_command or f"pip install {package}"
            
            raise DependencyError(
                f"Required dependency '{package}' is not installed. "
                f"Install with: {install_cmd}"
            )
    
    def with_fallback(self, primary_func: Callable, fallback_func: Callable,
                     fallback_message: str = "Using fallback method"):
        """Execute function with fallback on failure.
        
        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            fallback_message: Message to display when using fallback
            
        Returns:
            Result from primary or fallback function
        """
        try:
            return primary_func()
        except Exception as e:
            if self.verbose:
                print(f"Primary method failed: {e}. {fallback_message}")
            try:
                return fallback_func()
            except Exception as fallback_error:
                if self.verbose:
                    print(f"Fallback method also failed: {fallback_error}")
                raise e  # Raise original error
    
    def create_error_context(self, operation: str, **context) -> Dict[str, Any]:
        """Create structured error context for LLMs.
        
        Args:
            operation: Name of the operation
            **context: Additional context information
            
        Returns:
            Dictionary with error context
        """
        return {
            'operation': operation,
            'timestamp': time.time(),
            'platform': platform.system(),
            'context': context,
            'suggestions': self._get_operation_suggestions(operation),
            'alternatives': self._get_operation_alternatives(operation)
        }
    
    def _get_operation_suggestions(self, operation: str) -> List[str]:
        """Get suggestions for failed operations.
        
        Args:
            operation: Name of the operation
            
        Returns:
            List of suggestions
        """
        suggestions = {
            'find': [
                "Try using a more specific selector",
                "Wait for the element to appear",
                "Check if the application window is active",
                "Verify the element is visible on screen"
            ],
            'click': [
                "Ensure the element is clickable",
                "Try clicking with different button (left/right/middle)",
                "Wait for the element to become enabled",
                "Check if element is not obscured by other windows"
            ],
            'type': [
                "Make sure the text field is focused",
                "Clear the field before typing",
                "Check if the field accepts text input",
                "Try using paste instead of typing"
            ],
            'screenshot': [
                "Install PIL (Pillow) or pyautogui",
                "Check desktop environment permissions",
                "Try different screenshot backends",
                "Ensure sufficient disk space"
            ],
            'ocr': [
                "Install tesseract, easyocr, or paddleocr",
                "Improve image quality or resolution",
                "Try different OCR engines",
                "Check if image contains readable text"
            ]
        }
        
        # Find matching suggestions
        for key, suggestions_list in suggestions.items():
            if key in operation.lower():
                return suggestions_list
        
        return ["Check application state and try again"]
    
    def _get_operation_alternatives(self, operation: str) -> List[str]:
        """Get alternative approaches for failed operations.
        
        Args:
            operation: Name of the operation
            
        Returns:
            List of alternatives
        """
        alternatives = {
            'find': [
                "Use find_by_text() to search by text content",
                "Use find_by_role() to search by accessibility role",
                "Try broader selectors and filter results",
                "Use computer.vision for image-based finding"
            ],
            'click': [
                "Use keyboard shortcuts instead",
                "Try double-click or right-click",
                "Use computer.mouse for direct coordinate clicking",
                "Navigate using Tab key and Enter"
            ],
            'type': [
                "Use clipboard operations (copy/paste)",
                "Try keyboard shortcuts for text input",
                "Use computer.keyboard for direct key sending",
                "Break text into smaller chunks"
            ],
            'screenshot': [
                "Use computer.vision for screen analysis",
                "Try system screenshot tools",
                "Use application-specific export features",
                "Capture specific windows instead of full screen"
            ],
            'ocr': [
                "Use accessibility APIs for text extraction",
                "Try computer.vision for text detection",
                "Use application-specific text export",
                "Manually extract text using copy operations"
            ]
        }
        
        # Find matching alternatives
        for key, alternatives_list in alternatives.items():
            if key in operation.lower():
                return alternatives_list
        
        return ["Try using different computer module methods"]


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


def with_input_validation(func: Callable) -> Callable:
    """Decorator to add input validation."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Basic validation for common parameters
        if 'selector' in kwargs:
            error_handler.validate_selector(kwargs['selector'])
        elif len(args) > 1 and isinstance(args[1], str):
            # Assume first string argument is selector
            error_handler.validate_selector(args[1])
        
        return func(*args, **kwargs)
    return wrapper


def with_resource_check(memory_mb: Optional[int] = None, 
                       disk_mb: Optional[int] = None):
    """Decorator to check resource availability."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            error_handler.check_resource_availability(
                func.__name__, memory_mb, disk_mb
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def with_dependency_check(*dependencies):
    """Decorator to check dependencies before execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for dep in dependencies:
                if isinstance(dep, str):
                    error_handler.check_dependency(dep)
                elif isinstance(dep, dict):
                    error_handler.check_dependency(**dep)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def safe_operation(fallback_result=None, log_errors: bool = True):
    """Decorator for safe operations that should not raise exceptions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    error_handler._log_error(func.__name__, e)
                if error_handler.verbose:
                    print(f"Safe operation {func.__name__} failed: {e}")
                return fallback_result
        return wrapper
    return decorator


def with_retry_and_fallback(max_retries: int = 3, delay: float = 0.5,
                           fallback_func: Optional[Callable] = None):
    """Decorator combining retry logic with fallback."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try with retry logic
            retry_decorator = error_handler.with_retry(max_retries, delay)
            retry_func = retry_decorator(func)
            
            try:
                return retry_func(*args, **kwargs)
            except Exception as e:
                if fallback_func:
                    if error_handler.verbose:
                        print(f"Primary function failed, trying fallback: {e}")
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        if error_handler.verbose:
                            print(f"Fallback also failed: {fallback_error}")
                        raise e  # Raise original error
                else:
                    raise
        return wrapper
    return decorator