"""
Element finder module for ASQ integration.
Provides advanced element finding capabilities with CSS-like selectors.
"""

import platform
from typing import List, Dict, Any, Optional, Union


class ElementFinder:
    """Advanced element finder with CSS-like selector support."""
    
    def __init__(self, asq_instance=None):
        """Initialize element finder.
        
        Args:
            asq_instance: The ASQ instance to use for finding elements
        """
        self.asq = asq_instance
        self._available = platform.system() == 'Linux'
    
    def find_by_selector(self, selector: str) -> List[Any]:
        """Find elements using CSS-like selectors.
        
        Args:
            selector: CSS-like selector string
            
        Returns:
            List of matching elements
            
        Examples:
            find_by_selector('button')  # All buttons
            find_by_selector('button[name="Save"]')  # Save button
            find_by_selector('text[name*="search"]')  # Text fields with "search" in name
        """
        if not self._available:
            raise RuntimeError("Element finder only available on Linux systems")
        
        if not self.asq:
            raise RuntimeError("ASQ instance not available")
        
        try:
            # Parse selector and find elements
            return self._parse_and_find(selector)
        except Exception as e:
            if "gi" in str(e):
                raise RuntimeError("AT-SPI libraries not available. Install with: sudo apt-get install python3-gi gir1.2-atspi-2.0")
            raise
    
    def find_by_text(self, text: str, element_type: Optional[str] = None) -> List[Any]:
        """Find elements by their text content.
        
        Args:
            text: Text to search for
            element_type: Optional element type filter
            
        Returns:
            List of matching elements
        """
        if not self._available:
            raise RuntimeError("Element finder only available on Linux systems")
        
        # Implementation would use ASQ to find elements by text
        selector = f'{element_type or "*"}[text*="{text}"]'
        return self.find_by_selector(selector)
    
    def find_by_role(self, role: str, name: Optional[str] = None) -> List[Any]:
        """Find elements by their accessibility role.
        
        Args:
            role: Accessibility role (button, text, dialog, etc.)
            name: Optional name filter
            
        Returns:
            List of matching elements
        """
        if not self._available:
            raise RuntimeError("Element finder only available on Linux systems")
        
        selector = role
        if name:
            selector += f'[name="{name}"]'
        
        return self.find_by_selector(selector)
    
    def find_in_window(self, window_name: str, selector: str) -> List[Any]:
        """Find elements within a specific window.
        
        Args:
            window_name: Name of the window to search in
            selector: Element selector
            
        Returns:
            List of matching elements
        """
        if not self._available:
            raise RuntimeError("Element finder only available on Linux systems")
        
        # Implementation would scope search to specific window
        window_selector = f'frame[name*="{window_name}"] {selector}'
        return self.find_by_selector(window_selector)
    
    def _parse_and_find(self, selector: str) -> List[Any]:
        """Parse CSS-like selector and find matching elements.
        
        Args:
            selector: CSS-like selector string
            
        Returns:
            List of matching elements
        """
        # This would be implemented using the actual ASQ library
        # For now, return empty list as placeholder
        return []
    
    def get_element_info(self, element: Any) -> Dict[str, Any]:
        """Get detailed information about an element.
        
        Args:
            element: Element to inspect
            
        Returns:
            Dictionary with element information
        """
        if not self._available:
            return {"error": "Element finder only available on Linux systems"}
        
        # Implementation would extract element properties
        return {
            "name": getattr(element, 'name', ''),
            "role": getattr(element, 'role', ''),
            "text": getattr(element, 'text', ''),
            "position": getattr(element, 'position', (0, 0)),
            "size": getattr(element, 'size', (0, 0)),
            "visible": getattr(element, 'visible', False),
            "enabled": getattr(element, 'enabled', False)
        }