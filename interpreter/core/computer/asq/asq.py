import platform
import sys
from typing import Optional, List, Dict, Any

from .modules.element_finder import ElementFinder
from .modules.form_automation import FormAutomation
from .modules.window_manager import WindowManager


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