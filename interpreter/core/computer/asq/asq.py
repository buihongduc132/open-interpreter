import platform
import sys
from typing import Optional, List, Dict, Any

from .modules.element_finder import ElementFinder
from .modules.form_automation import FormAutomation
from .modules.window_manager import WindowManager
from .modules.application_manager import ApplicationManager
from .modules.dialog_handler import DialogHandler
from .modules.workflow_automation import WorkflowAutomation
from .modules.text_processing import TextProcessor
from .modules.screen_capture import ScreenCapture
from .modules.ocr import OCRProcessor
from .modules.error_handler import (
    error_handler, require_linux, require_atspi, with_error_handling,
    ASQError, PlatformNotSupportedError, ATSPINotAvailableError
)
from .modules.performance import (
    performance_monitor, element_cache, timed, optimized, get_performance_report
)
from .modules.advanced_selectors import (
    selector_parser, selector_optimizer, parse_selector, optimize_selector
)


class ASQ:
    """
    ASQ (AT-SPI-Query) interface for Linux GUI automation.
    
    Provides a jQuery-like interface for automating GUI applications on Linux
    desktop environments using AT-SPI (Assistive Technology Service Provider Interface).
    
    This module only works on Linux systems with AT-SPI support.
    """
    
    def __init__(self, computer):
        self.computer = computer
        self._asq_available = None
        self._check_availability()
        
        # Initialize modules
        self.element_finder = ElementFinder(self)
        self.form_automation = FormAutomation(self)
        self.window_manager = WindowManager(self)
        self.application_manager = ApplicationManager(self)
        self.dialog_handler = DialogHandler(self)
        self.workflow_automation = WorkflowAutomation(self)
        self.text_processing = TextProcessor(self)
        self.screen_capture = ScreenCapture(self)
        self.ocr = OCRProcessor(self)
    
    def _check_availability(self):
        """Check if ASQ is available on this system."""
        if platform.system() != 'Linux':
            self._asq_available = False
            return
        
        try:
            # Try to import and initialize ASQ
            import gi
            gi.require_version('Atspi', '2.0')
            from gi.repository import Atspi
            
            # Try to initialize AT-SPI
            Atspi.init()
            self._asq_available = True
        except Exception as e:
            self._asq_available = False
            if self.computer.verbose:
                print(f"ASQ not available: {e}")
    
    def _ensure_available(self):
        """Ensure ASQ is available, raise error if not."""
        if not self._asq_available:
            if platform.system() != 'Linux':
                raise RuntimeError(
                    "ASQ module only works on Linux systems with AT-SPI support. "
                    "Current platform: " + platform.system()
                )
            else:
                raise RuntimeError(
                    "ASQ module requires AT-SPI libraries. Please install:\n"
                    "Ubuntu/Debian: sudo apt-get install python3-gi gir1.2-atspi-2.0\n"
                    "Fedora: sudo dnf install python3-gobject gtk3-devel\n"
                    "Arch Linux: sudo pacman -S python-gobject gtk3"
                )
    
    def find(self, selector: str) -> "ASQCollection":
        """
        Find GUI elements using CSS-like selectors.
        
        Args:
            selector: CSS-like selector string (e.g., 'button[name="Save"]')
            
        Returns:
            ASQCollection object containing matching elements
            
        Examples:
            computer.asq.find('button')  # Find all buttons
            computer.asq.find('button[name="Save"]')  # Find Save button
            computer.asq.find('text[name="filename"]')  # Find filename text field
        """
        self._ensure_available()
        
        # Import ASQ from the submodule
        sys.path.insert(0, '/workspace/asq')
        try:
            from asq import ASQ as ASQCore
            result = ASQCore(selector)
            return ASQCollection(result, self.computer)
        finally:
            sys.path.pop(0)
    
    def click_button(self, name: str) -> bool:
        """
        High-level method to click a button by name.
        
        Args:
            name: Name of the button to click
            
        Returns:
            True if button was found and clicked, False otherwise
        """
        self._ensure_available()
        
        try:
            button = self.find(f'push button[name="{name}"]')
            if button.exists():
                button.click()
                return True
            return False
        except Exception as e:
            if self.computer.verbose:
                print(f"Error clicking button '{name}': {e}")
            return False
    
    def type_text(self, field_name: str, text: str) -> bool:
        """
        High-level method to type text into a text field.
        
        Args:
            field_name: Name of the text field
            text: Text to type
            
        Returns:
            True if field was found and text was typed, False otherwise
        """
        self._ensure_available()
        
        try:
            field = self.find(f'text[name="{field_name}"]')
            if field.exists():
                field.clear().type(text)
                return True
            return False
        except Exception as e:
            if self.computer.verbose:
                print(f"Error typing text in field '{field_name}': {e}")
            return False
    
    def wait_for_element(self, selector: str, timeout: float = 10.0) -> bool:
        """
        Wait for an element to appear.
        
        Args:
            selector: CSS-like selector string
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if element appeared, False if timeout
        """
        self._ensure_available()
        
        try:
            element = self.find(selector)
            return element.wait_until(lambda: element.exists(), timeout=timeout)
        except Exception as e:
            if self.computer.verbose:
                print(f"Error waiting for element '{selector}': {e}")
            return False
    
    # High-level methods using modules
    def fill_form(self, form_data: Dict[str, str], form_selector: Optional[str] = None) -> Dict[str, bool]:
        """Fill out a form with provided data.
        
        Args:
            form_data: Dictionary mapping field names to values
            form_selector: Optional selector to scope to specific form
            
        Returns:
            Dictionary mapping field names to success status
        """
        return self.form_automation.fill_form(form_data, form_selector)
    
    def submit_form(self, submit_button: str = "Submit") -> bool:
        """Submit a form by clicking the submit button.
        
        Args:
            submit_button: Name or text of the submit button
            
        Returns:
            True if form was submitted successfully
        """
        return self.form_automation.submit_form(submit_button)
    
    def clear_form(self, form_selector: Optional[str] = None) -> bool:
        """Clear all fields in a form.
        
        Args:
            form_selector: Optional selector to scope to specific form
            
        Returns:
            True if form was cleared successfully
        """
        return self.form_automation.clear_form(form_selector)
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window.
        
        Returns:
            Dictionary with window information or None if not available
        """
        return self.window_manager.get_active_window()
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """List all available windows.
        
        Returns:
            List of dictionaries with window information
        """
        return self.window_manager.list_windows()
    
    def focus_window(self, window_name: str) -> bool:
        """Focus a specific window by name.
        
        Args:
            window_name: Name or title of the window to focus
            
        Returns:
            True if window was focused successfully
        """
        return self.window_manager.focus_window(window_name)
    
    def close_window(self, window_name: str) -> bool:
        """Close a specific window by name.
        
        Args:
            window_name: Name or title of the window to close
            
        Returns:
            True if window was closed successfully
        """
        return self.window_manager.close_window(window_name)
    
    def find_by_text(self, text: str, element_type: Optional[str] = None) -> List[Any]:
        """Find elements by their text content.
        
        Args:
            text: Text to search for
            element_type: Optional element type filter
            
        Returns:
            List of matching elements
        """
        return self.element_finder.find_by_text(text, element_type)
    
    def find_by_role(self, role: str, name: Optional[str] = None) -> List[Any]:
        """Find elements by their accessibility role.
        
        Args:
            role: Accessibility role (button, text, dialog, etc.)
            name: Optional name filter
            
        Returns:
            List of matching elements
        """
        return self.element_finder.find_by_role(role, name)
    
    def find_in_window(self, window_name: str, selector: str) -> List[Any]:
        """Find elements within a specific window.
        
        Args:
            window_name: Name of the window to search in
            selector: Element selector
            
        Returns:
            List of matching elements
        """
        return self.element_finder.find_in_window(window_name, selector)
    
    # Enhanced methods with performance optimization and error handling
    @optimized(cache_ttl=60.0)
    @with_error_handling
    def find_optimized(self, selector: str) -> 'ASQCollection':
        """Find elements with performance optimization and caching.
        
        Args:
            selector: CSS-like selector string
            
        Returns:
            ASQCollection object containing matching elements
        """
        optimized_selector = optimize_selector(selector)
        return self.find(optimized_selector)
    
    @timed
    @with_error_handling
    def find_advanced(self, selector: str) -> List[Any]:
        """Find elements using advanced selectors with spatial relations.
        
        Args:
            selector: Advanced CSS-like selector with spatial relations
            
        Returns:
            List of matching elements
            
        Examples:
            find_advanced('button near text[name="username"]')
            find_advanced('label above text[name="password"]')
            find_advanced('button[name*="save"]:visible')
        """
        self._ensure_available()
        
        try:
            selector_parts = parse_selector(selector)
            # Implementation would use the parsed selector parts
            # For now, fall back to basic find
            return self.find(selector).elements
        except Exception as e:
            if self.computer.verbose:
                print(f"Error in advanced find '{selector}': {e}")
            return []
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get ASQ performance statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        return performance_monitor.get_stats()
    
    def get_performance_report(self) -> str:
        """Get formatted performance report.
        
        Returns:
            Formatted performance report string
        """
        return get_performance_report()
    
    def clear_cache(self) -> None:
        """Clear element cache and performance statistics."""
        element_cache.clear()
        performance_monitor.clear_stats()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics.
        
        Returns:
            Dictionary with error statistics
        """
        return error_handler.get_error_statistics()
    
    def set_verbose(self, verbose: bool) -> None:
        """Set verbose mode for detailed error reporting.
        
        Args:
            verbose: Whether to enable verbose mode
        """
        self.computer.verbose = verbose
        error_handler.verbose = verbose
    
    # Convenience methods for common operations
    def click_if_exists(self, selector: str, timeout: float = 5.0) -> bool:
        """Click an element if it exists within timeout.
        
        Args:
            selector: Element selector
            timeout: Maximum time to wait
            
        Returns:
            True if element was found and clicked
        """
        try:
            if self.wait_for_element(selector, timeout):
                element = self.find(selector)
                if element and len(element.elements) > 0:
                    element.elements[0].click()
                    return True
        except Exception as e:
            if self.computer.verbose:
                print(f"Error in click_if_exists '{selector}': {e}")
        return False
    
    def type_if_exists(self, selector: str, text: str, timeout: float = 5.0) -> bool:
        """Type text into an element if it exists within timeout.
        
        Args:
            selector: Element selector
            text: Text to type
            timeout: Maximum time to wait
            
        Returns:
            True if element was found and text was typed
        """
        try:
            if self.wait_for_element(selector, timeout):
                element = self.find(selector)
                if element and len(element.elements) > 0:
                    element.elements[0].type(text)
                    return True
        except Exception as e:
            if self.computer.verbose:
                print(f"Error in type_if_exists '{selector}': {e}")
        return False
    
    def get_text_if_exists(self, selector: str, timeout: float = 5.0) -> Optional[str]:
        """Get text from an element if it exists within timeout.
        
        Args:
            selector: Element selector
            timeout: Maximum time to wait
            
        Returns:
            Element text or None if not found
        """
        try:
            if self.wait_for_element(selector, timeout):
                element = self.find(selector)
                if element and len(element.elements) > 0:
                    return getattr(element.elements[0], 'text', '')
        except Exception as e:
            if self.computer.verbose:
                print(f"Error in get_text_if_exists '{selector}': {e}")
        return None
    
    # High-level application management methods
    def launch_app(self, app_name: str, app_path: Optional[str] = None, 
                   wait_for_window: bool = True, timeout: float = 10.0) -> bool:
        """Launch an application by name or path.
        
        Args:
            app_name: Name of the application to launch
            app_path: Optional path to application executable
            wait_for_window: Whether to wait for application window to appear
            timeout: Maximum time to wait for application to start
            
        Returns:
            True if application was launched successfully
        """
        return self.application_manager.launch_application(app_name, app_path, wait_for_window, timeout)
    
    def close_app(self, app_name: str, force: bool = False) -> bool:
        """Close an application gracefully or forcefully.
        
        Args:
            app_name: Name of the application to close
            force: Whether to force close the application
            
        Returns:
            True if application was closed successfully
        """
        return self.application_manager.close_application(app_name, force)
    
    def switch_to_app(self, app_name: str) -> bool:
        """Switch focus to a specific application.
        
        Args:
            app_name: Name of the application to focus
            
        Returns:
            True if application was focused successfully
        """
        return self.application_manager.switch_to_application(app_name)
    
    def get_running_apps(self) -> List[Any]:
        """Get list of currently running applications.
        
        Returns:
            List of ApplicationInfo objects
        """
        return self.application_manager.get_running_applications()
    
    def is_app_running(self, app_name: str) -> bool:
        """Check if an application is currently running.
        
        Args:
            app_name: Name of the application to check
            
        Returns:
            True if application is running
        """
        return self.application_manager.is_application_running(app_name)
    
    # High-level dialog handling methods
    def handle_dialog(self, action: str = "ok") -> bool:
        """Handle the current dialog with specified action.
        
        Args:
            action: Action to take ("ok", "cancel", "yes", "no")
            
        Returns:
            True if dialog was handled successfully
        """
        return self.dialog_handler.handle_alert_dialog(action)
    
    def handle_file_dialog(self, dialog_type: str, file_path: Optional[str] = None, 
                          filename: Optional[str] = None) -> bool:
        """Handle file dialogs (open, save, browse).
        
        Args:
            dialog_type: Type of file dialog ("open", "save", "browse")
            file_path: Path to file or directory
            filename: Name of file (for save dialogs)
            
        Returns:
            True if dialog was handled successfully
        """
        return self.dialog_handler.handle_file_dialog(dialog_type, file_path, filename)
    
    def login(self, username: str, password: str, remember_me: bool = False) -> bool:
        """Handle login dialog or form.
        
        Args:
            username: Username to enter
            password: Password to enter
            remember_me: Whether to check "remember me" option
            
        Returns:
            True if login was successful
        """
        return self.dialog_handler.handle_login_dialog(username, password, remember_me)
    
    def get_dialog_text(self) -> Optional[str]:
        """Get text content from current dialog.
        
        Returns:
            Dialog text content or None if no dialog
        """
        return self.dialog_handler.get_dialog_text()
    
    # High-level workflow methods
    def login_workflow(self, username: str, password: str, 
                      app_name: Optional[str] = None, remember_me: bool = False) -> Any:
        """Execute a complete login workflow.
        
        Args:
            username: Username to enter
            password: Password to enter
            app_name: Optional application name to focus first
            remember_me: Whether to check remember me option
            
        Returns:
            WorkflowResult with login status
        """
        return self.workflow_automation.login_workflow(username, password, app_name, remember_me)
    
    def form_workflow(self, form_data: Dict[str, str], submit_button: str = "Submit") -> Any:
        """Execute a complete form submission workflow.
        
        Args:
            form_data: Dictionary of field names to values
            submit_button: Name of submit button
            
        Returns:
            WorkflowResult with submission status
        """
        return self.workflow_automation.form_submission_workflow(form_data, submit_button)
    
    def file_workflow(self, operation: str, file_path: str, 
                     app_name: Optional[str] = None) -> Any:
        """Execute a file operation workflow (open, save, etc.).
        
        Args:
            operation: Type of operation ("open", "save", "save_as")
            file_path: Path to file
            app_name: Optional application name
            
        Returns:
            WorkflowResult with operation status
        """
        return self.workflow_automation.file_operation_workflow(operation, file_path, app_name)
    
    def startup_workflow(self, app_name: str, initial_actions: Optional[List[Dict[str, Any]]] = None) -> Any:
        """Execute application startup workflow with initial setup.
        
        Args:
            app_name: Name of application to start
            initial_actions: Optional list of initial actions to perform
            
        Returns:
            WorkflowResult with startup status
        """
        return self.workflow_automation.application_startup_workflow(app_name, initial_actions)
    
    # Convenience methods for common tasks
    def open_file(self, file_path: str, app_name: Optional[str] = None) -> bool:
        """Open a file in the specified or default application.
        
        Args:
            file_path: Path to file to open
            app_name: Optional application name
            
        Returns:
            True if file was opened successfully
        """
        result = self.file_workflow("open", file_path, app_name)
        return result.status.value == "success"
    
    def save_file(self, file_path: str, app_name: Optional[str] = None) -> bool:
        """Save current file with specified path.
        
        Args:
            file_path: Path where to save the file
            app_name: Optional application name
            
        Returns:
            True if file was saved successfully
        """
        result = self.file_workflow("save", file_path, app_name)
        return result.status.value == "success"
    
    def quick_login(self, username: str, password: str) -> bool:
        """Quick login without workflow complexity.
        
        Args:
            username: Username to enter
            password: Password to enter
            
        Returns:
            True if login was successful
        """
        return self.login(username, password)
    
    def fill_and_submit(self, form_data: Dict[str, str]) -> bool:
        """Fill form and submit in one operation.
        
        Args:
            form_data: Dictionary of field names to values
            
        Returns:
            True if form was filled and submitted successfully
        """
        result = self.form_workflow(form_data)
        return result.status.value == "success"
    
    # Text Processing Methods
    def extract_text(self, selector: str) -> Optional[str]:
        """Extract text content from a specific element.
        
        Args:
            selector: Element selector
            
        Returns:
            Text content or None if element not found
        """
        return self.text_processing.extract_text_from_element(selector)
    
    def search_text(self, search_term: str, case_sensitive: bool = False, 
                   regex: bool = False) -> List[Any]:
        """Search for text in the current interface.
        
        Args:
            search_term: Text to search for
            case_sensitive: Whether search should be case sensitive
            regex: Whether search_term is a regular expression
            
        Returns:
            List of TextMatch objects
        """
        return self.text_processing.search_text(search_term, case_sensitive, regex)
    
    def replace_text(self, selector: str, old_text: str, new_text: str) -> bool:
        """Replace text in a text field.
        
        Args:
            selector: Selector for the text field
            old_text: Text to replace
            new_text: Replacement text
            
        Returns:
            True if replacement was successful
        """
        return self.text_processing.replace_text_in_field(selector, old_text, new_text)
    
    def copy_text(self, selector: str) -> Optional[str]:
        """Copy text from an element to clipboard.
        
        Args:
            selector: Element selector
            
        Returns:
            Copied text or None if failed
        """
        return self.text_processing.copy_text_from_element(selector)
    
    def paste_text(self, selector: str, text: str) -> bool:
        """Paste text to an element via clipboard.
        
        Args:
            selector: Element selector
            text: Text to paste
            
        Returns:
            True if paste was successful
        """
        return self.text_processing.paste_text_to_element(selector, text)
    
    def format_text(self, selector: str, formatting: str) -> bool:
        """Apply text formatting to a field.
        
        Args:
            selector: Selector for the text field
            formatting: Formatting to apply ('bold', 'italic', 'underline', etc.)
            
        Returns:
            True if formatting was applied successfully
        """
        return self.text_processing.format_text_in_field(selector, formatting)
    
    # Screen Capture Methods
    def take_screenshot(self, save_path: Optional[str] = None, 
                       return_base64: bool = True) -> Optional[Any]:
        """Take a screenshot of the entire screen.
        
        Args:
            save_path: Optional path to save screenshot
            return_base64: Whether to include base64 data in result
            
        Returns:
            ScreenshotInfo object or None if failed
        """
        return self.screen_capture.take_screenshot(save_path, return_base64)
    
    def screenshot_element(self, selector: str, save_path: Optional[str] = None,
                          return_base64: bool = True) -> Optional[Any]:
        """Take a screenshot of a specific element.
        
        Args:
            selector: Element selector
            save_path: Optional path to save screenshot
            return_base64: Whether to include base64 data in result
            
        Returns:
            ScreenshotInfo object or None if failed
        """
        return self.screen_capture.take_element_screenshot(selector, save_path, return_base64)
    
    def compare_screenshots(self, image1_path: str, image2_path: str, 
                           threshold: float = 0.95) -> Dict[str, Any]:
        """Compare two screenshots for similarity.
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            threshold: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Dictionary with comparison results
        """
        return self.screen_capture.compare_screenshots(image1_path, image2_path, threshold)
    
    def wait_for_visual_change(self, timeout: float = 10.0, 
                              check_interval: float = 1.0) -> bool:
        """Wait for visual change on screen.
        
        Args:
            timeout: Maximum time to wait
            check_interval: How often to check for changes
            
        Returns:
            True if visual change detected
        """
        return self.screen_capture.wait_for_visual_change(timeout, check_interval)
    
    def verify_element_visible(self, selector: str) -> bool:
        """Verify an element is visually present on screen.
        
        Args:
            selector: Element selector
            
        Returns:
            True if element is visible
        """
        return self.screen_capture.verify_element_visible(selector)
    
    # OCR Methods
    def extract_text_from_image(self, image_path: str, 
                               engine: Optional[str] = None,
                               language: str = 'eng') -> Optional[Any]:
        """Extract text from an image file using OCR.
        
        Args:
            image_path: Path to image file
            engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr')
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        return self.ocr.extract_text_from_image(image_path, engine, language)
    
    def extract_text_from_screen(self, region: Optional[Tuple[int, int, int, int]] = None,
                                engine: Optional[str] = None,
                                language: str = 'eng') -> Optional[Any]:
        """Extract text from screen or screen region using OCR.
        
        Args:
            region: Optional (x, y, width, height) region to capture
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        return self.ocr.extract_text_from_screen(region, engine, language)
    
    def extract_text_from_element_ocr(self, selector: str,
                                     engine: Optional[str] = None,
                                     language: str = 'eng') -> Optional[Any]:
        """Extract text from a specific element using OCR.
        
        Args:
            selector: Element selector
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        return self.ocr.extract_text_from_element(selector, engine, language)
    
    def find_text_in_image(self, image_path: str, search_text: str,
                          engine: Optional[str] = None,
                          language: str = 'eng',
                          case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Find specific text in an image using OCR.
        
        Args:
            image_path: Path to image file
            search_text: Text to search for
            engine: OCR engine to use
            language: Language code for OCR
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            List of matches with bounding box information
        """
        return self.ocr.find_text_in_image(image_path, search_text, engine, language, case_sensitive)
    
    def get_text_at_position(self, x: int, y: int, 
                            region_size: int = 100,
                            engine: Optional[str] = None,
                            language: str = 'eng') -> Optional[str]:
        """Get text at a specific screen position using OCR.
        
        Args:
            x: X coordinate
            y: Y coordinate
            region_size: Size of region around position to capture
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            Text found at position or None
        """
        return self.ocr.get_text_at_position(x, y, region_size, engine, language)
    
    # Utility Methods
    def get_available_ocr_engines(self) -> List[str]:
        """Get list of available OCR engines.
        
        Returns:
            List of available engine names
        """
        return self.ocr.get_available_engines()
    
    def get_available_screenshot_backends(self) -> List[str]:
        """Get list of available screenshot backends.
        
        Returns:
            List of available backend names
        """
        return self.screen_capture.get_available_backends()
    
    def cleanup_temp_files(self):
        """Clean up temporary files created by ASQ modules."""
        self.ocr.cleanup_temp_files()
        self.screen_capture.cleanup_screenshots(older_than_hours=1)


class ASQCollection:
    """
    Wrapper for ASQ collection objects to provide computer-module-style interface.
    """
    
    def __init__(self, asq_collection, computer):
        self._collection = asq_collection
        self.computer = computer
    
    def __len__(self):
        return len(self._collection)
    
    def __bool__(self):
        return bool(self._collection)
    
    def exists(self) -> bool:
        """Check if any elements exist in the collection."""
        return bool(self._collection)
    
    def click(self, button: str = 'left') -> "ASQCollection":
        """Click the elements in the collection."""
        try:
            self._collection.click(button=button)
            return self
        except Exception as e:
            if self.computer.verbose:
                print(f"Error clicking elements: {e}")
            return self
    
    def type(self, text: str) -> "ASQCollection":
        """Type text into the elements."""
        try:
            self._collection.type(text)
            return self
        except Exception as e:
            if self.computer.verbose:
                print(f"Error typing text: {e}")
            return self
    
    def clear(self) -> "ASQCollection":
        """Clear the text in the elements."""
        try:
            self._collection.clear()
            return self
        except Exception as e:
            if self.computer.verbose:
                print(f"Error clearing elements: {e}")
            return self
    
    def get_text(self) -> List[str]:
        """Get text content from all elements."""
        try:
            return self._collection.get_text()
        except Exception as e:
            if self.computer.verbose:
                print(f"Error getting text: {e}")
            return []
    
    def wait_until(self, condition, timeout: float = 10.0) -> bool:
        """Wait until a condition is met."""
        try:
            return self._collection.wait_until(condition, timeout=timeout)
        except Exception as e:
            if self.computer.verbose:
                print(f"Error waiting for condition: {e}")
            return False
    
    def find(self, selector: str) -> "ASQCollection":
        """Find child elements within this collection."""
        try:
            result = self._collection.find(selector)
            return ASQCollection(result, self.computer)
        except Exception as e:
            if self.computer.verbose:
                print(f"Error finding child elements: {e}")
            return ASQCollection(None, self.computer)