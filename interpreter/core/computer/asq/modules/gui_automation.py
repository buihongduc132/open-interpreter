"""
High-level GUI automation utilities for ASQ module.

This module provides convenient methods for common GUI automation tasks,
building on top of the core ASQ functionality.
"""

from typing import Optional, List, Dict, Any, Tuple


class GUIAutomation:
    """
    High-level GUI automation methods for common tasks.
    """
    
    def __init__(self, asq_instance):
        self.asq = asq_instance
        self.computer = asq_instance.computer
    
    def open_application(self, app_name: str) -> bool:
        """
        Attempt to open an application by name.
        
        Args:
            app_name: Name of the application to open
            
        Returns:
            True if application appears to have opened, False otherwise
        """
        try:
            # Try to find if the application is already running
            app_window = self.asq.find(f'frame[name*="{app_name}"]')
            if app_window.exists():
                return True
            
            # Try to open via system launcher (this is a simplified approach)
            # In a real implementation, you might use the OS module or terminal
            self.computer.terminal.run(f"nohup {app_name.lower()} &")
            
            # Wait for the application window to appear
            return self.asq.wait_for_element(f'frame[name*="{app_name}"]', timeout=10.0)
            
        except Exception as e:
            if self.computer.verbose:
                print(f"Error opening application '{app_name}': {e}")
            return False
    
    def close_application(self, app_name: str) -> bool:
        """
        Attempt to close an application by name.
        
        Args:
            app_name: Name of the application to close
            
        Returns:
            True if application was closed, False otherwise
        """
        try:
            # Find the application window
            app_window = self.asq.find(f'frame[name*="{app_name}"]')
            if not app_window.exists():
                return True  # Already closed
            
            # Try to find and click close button
            close_button = app_window.find('push button[name="Close"]')
            if close_button.exists():
                close_button.click()
                return True
            
            # Alternative: try window controls
            close_button = app_window.find('push button[name="×"]')
            if close_button.exists():
                close_button.click()
                return True
            
            return False
            
        except Exception as e:
            if self.computer.verbose:
                print(f"Error closing application '{app_name}': {e}")
            return False
    
    def fill_form(self, form_data: Dict[str, str]) -> Dict[str, bool]:
        """
        Fill out a form with the provided data.
        
        Args:
            form_data: Dictionary mapping field names to values
            
        Returns:
            Dictionary mapping field names to success status
        """
        results = {}
        
        for field_name, value in form_data.items():
            try:
                success = self.asq.type_text(field_name, value)
                results[field_name] = success
            except Exception as e:
                if self.computer.verbose:
                    print(f"Error filling field '{field_name}': {e}")
                results[field_name] = False
        
        return results
    
    def navigate_menu(self, menu_path: List[str]) -> bool:
        """
        Navigate through a menu hierarchy.
        
        Args:
            menu_path: List of menu item names to click in order
            
        Returns:
            True if navigation was successful, False otherwise
        """
        try:
            for menu_item in menu_path:
                # Look for menu items or buttons
                item = self.asq.find(f'menu item[name="{menu_item}"]')
                if not item.exists():
                    item = self.asq.find(f'push button[name="{menu_item}"]')
                
                if item.exists():
                    item.click()
                    # Small delay to allow menu to open
                    import time
                    time.sleep(0.5)
                else:
                    if self.computer.verbose:
                        print(f"Menu item '{menu_item}' not found")
                    return False
            
            return True
            
        except Exception as e:
            if self.computer.verbose:
                print(f"Error navigating menu: {e}")
            return False
    
    def take_screenshot_of_element(self, selector: str) -> Optional[str]:
        """
        Take a screenshot of a specific element.
        
        Args:
            selector: CSS-like selector for the element
            
        Returns:
            Base64 encoded screenshot data, or None if failed
        """
        try:
            element = self.asq.find(selector)
            if element.exists():
                # This would need to be implemented with actual screenshot capability
                # For now, return a placeholder
                if self.computer.verbose:
                    print(f"Screenshot functionality not yet implemented for element: {selector}")
                return None
            else:
                if self.computer.verbose:
                    print(f"Element not found for screenshot: {selector}")
                return None
                
        except Exception as e:
            if self.computer.verbose:
                print(f"Error taking screenshot of element '{selector}': {e}")
            return None
    
    def get_window_list(self) -> List[Dict[str, str]]:
        """
        Get a list of open windows.
        
        Returns:
            List of dictionaries with window information
        """
        try:
            windows = self.asq.find('frame')
            window_list = []
            
            for i in range(len(windows)):
                window = windows[i] if hasattr(windows, '__getitem__') else windows
                try:
                    name = window.get_text()[0] if window.get_text() else "Unknown"
                    window_list.append({
                        'name': name,
                        'type': 'frame'
                    })
                except:
                    window_list.append({
                        'name': 'Unknown',
                        'type': 'frame'
                    })
            
            return window_list
            
        except Exception as e:
            if self.computer.verbose:
                print(f"Error getting window list: {e}")
            return []
    
    def wait_for_dialog(self, dialog_name: str, timeout: float = 10.0) -> bool:
        """
        Wait for a specific dialog to appear.
        
        Args:
            dialog_name: Name of the dialog to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if dialog appeared, False if timeout
        """
        try:
            return self.asq.wait_for_element(f'dialog[name="{dialog_name}"]', timeout=timeout)
        except Exception as e:
            if self.computer.verbose:
                print(f"Error waiting for dialog '{dialog_name}': {e}")
            return False
    
    def dismiss_dialog(self, button_name: str = "OK") -> bool:
        """
        Dismiss a dialog by clicking a button.
        
        Args:
            button_name: Name of the button to click (default: "OK")
            
        Returns:
            True if dialog was dismissed, False otherwise
        """
        try:
            # Look for the button in any visible dialog
            dialog = self.asq.find('dialog')
            if dialog.exists():
                button = dialog.find(f'push button[name="{button_name}"]')
                if button.exists():
                    button.click()
                    return True
            
            # If no dialog found, try to find the button globally
            button = self.asq.find(f'push button[name="{button_name}"]')
            if button.exists():
                button.click()
                return True
            
            return False
            
        except Exception as e:
            if self.computer.verbose:
                print(f"Error dismissing dialog: {e}")
            return False