"""
Window management module for ASQ integration.
Provides window and application management capabilities.
"""

import platform
from typing import List, Dict, Any, Optional, Tuple


class WindowManager:
    """Window and application management capabilities."""
    
    def __init__(self, asq_instance=None):
        """Initialize window manager.
        
        Args:
            asq_instance: The ASQ instance to use for window operations
        """
        self.asq = asq_instance
        self._available = platform.system() == 'Linux'
    
    def get_active_window(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active window.
        
        Returns:
            Dictionary with window information or None if not available
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Implementation would use ASQ to get active window
            return {
                "name": "Active Window",
                "title": "Window Title",
                "position": (0, 0),
                "size": (800, 600),
                "visible": True,
                "focused": True
            }
        except Exception as e:
            print(f"Error getting active window: {e}")
            return None
    
    def list_windows(self) -> List[Dict[str, Any]]:
        """List all available windows.
        
        Returns:
            List of dictionaries with window information
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Implementation would use ASQ to list windows
            windows = []
            
            if self.asq and hasattr(self.asq, 'find'):
                # Find all frame/window elements
                window_elements = self.asq.find('frame, window')
                
                for element in window_elements:
                    window_info = {
                        "name": getattr(element, 'name', ''),
                        "title": getattr(element, 'title', ''),
                        "position": getattr(element, 'position', (0, 0)),
                        "size": getattr(element, 'size', (0, 0)),
                        "visible": getattr(element, 'visible', False),
                        "focused": getattr(element, 'focused', False)
                    }
                    windows.append(window_info)
            
            return windows
        except Exception as e:
            print(f"Error listing windows: {e}")
            return []
    
    def focus_window(self, window_name: str) -> bool:
        """Focus a specific window by name.
        
        Args:
            window_name: Name or title of the window to focus
            
        Returns:
            True if window was focused successfully
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Try different window selector patterns
            window_patterns = [
                f'frame[name="{window_name}"]',
                f'window[name="{window_name}"]',
                f'frame[title="{window_name}"]',
                f'window[title="{window_name}"]',
                f'frame[name*="{window_name}"]',
                f'window[name*="{window_name}"]'
            ]
            
            for pattern in window_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        element = elements[0]
                        if hasattr(element, 'focus'):
                            element.focus()
                            return True
                        elif hasattr(element, 'click'):
                            element.click()
                            return True
            
            return False
        except Exception as e:
            print(f"Error focusing window '{window_name}': {e}")
            return False
    
    def close_window(self, window_name: str) -> bool:
        """Close a specific window by name.
        
        Args:
            window_name: Name or title of the window to close
            
        Returns:
            True if window was closed successfully
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # First try to find and click close button
            close_patterns = [
                f'frame[name*="{window_name}"] button[name="Close"]',
                f'window[name*="{window_name}"] button[name="Close"]',
                f'frame[name*="{window_name}"] button[text="×"]',
                f'window[name*="{window_name}"] button[text="×"]'
            ]
            
            for pattern in close_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        elements[0].click()
                        return True
            
            # If no close button found, try to close window directly
            window_patterns = [
                f'frame[name*="{window_name}"]',
                f'window[name*="{window_name}"]'
            ]
            
            for pattern in window_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        element = elements[0]
                        if hasattr(element, 'close'):
                            element.close()
                            return True
            
            return False
        except Exception as e:
            print(f"Error closing window '{window_name}': {e}")
            return False
    
    def minimize_window(self, window_name: str) -> bool:
        """Minimize a specific window by name.
        
        Args:
            window_name: Name or title of the window to minimize
            
        Returns:
            True if window was minimized successfully
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Try to find and click minimize button
            minimize_patterns = [
                f'frame[name*="{window_name}"] button[name="Minimize"]',
                f'window[name*="{window_name}"] button[name="Minimize"]',
                f'frame[name*="{window_name}"] button[text="-"]',
                f'window[name*="{window_name}"] button[text="-"]'
            ]
            
            for pattern in minimize_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        elements[0].click()
                        return True
            
            return False
        except Exception as e:
            print(f"Error minimizing window '{window_name}': {e}")
            return False
    
    def maximize_window(self, window_name: str) -> bool:
        """Maximize a specific window by name.
        
        Args:
            window_name: Name or title of the window to maximize
            
        Returns:
            True if window was maximized successfully
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Try to find and click maximize button
            maximize_patterns = [
                f'frame[name*="{window_name}"] button[name="Maximize"]',
                f'window[name*="{window_name}"] button[name="Maximize"]',
                f'frame[name*="{window_name}"] button[text="□"]',
                f'window[name*="{window_name}"] button[text="□"]'
            ]
            
            for pattern in maximize_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        elements[0].click()
                        return True
            
            return False
        except Exception as e:
            print(f"Error maximizing window '{window_name}': {e}")
            return False
    
    def wait_for_window(self, window_name: str, timeout: int = 10) -> bool:
        """Wait for a window to appear.
        
        Args:
            window_name: Name or title of the window to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if window appeared within timeout
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Use ASQ's wait functionality if available
            window_patterns = [
                f'frame[name*="{window_name}"]',
                f'window[name*="{window_name}"]'
            ]
            
            for pattern in window_patterns:
                if self.asq and hasattr(self.asq, 'wait_for_element'):
                    result = self.asq.wait_for_element(pattern, timeout)
                    if result:
                        return True
            
            return False
        except Exception as e:
            print(f"Error waiting for window '{window_name}': {e}")
            return False
    
    def get_window_screenshot(self, window_name: str) -> Optional[bytes]:
        """Take a screenshot of a specific window.
        
        Args:
            window_name: Name or title of the window to screenshot
            
        Returns:
            Screenshot data as bytes or None if failed
        """
        if not self._available:
            raise RuntimeError("Window manager only available on Linux systems")
        
        try:
            # Implementation would capture window screenshot
            # This is a placeholder - actual implementation would use
            # system screenshot capabilities
            return None
        except Exception as e:
            print(f"Error taking screenshot of window '{window_name}': {e}")
            return None