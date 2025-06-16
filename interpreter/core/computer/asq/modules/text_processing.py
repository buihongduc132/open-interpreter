"""
Text processing module for ASQ integration.
Provides advanced text manipulation and extraction methods.
"""

import re
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass


@dataclass
class TextMatch:
    """Information about a text match."""
    text: str
    element: Any
    position: Tuple[int, int]
    confidence: float = 1.0


class TextProcessor:
    """Advanced text processing for desktop automation."""
    
    def __init__(self, asq_instance):
        """Initialize text processor.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._text_cache = {}
        self._last_cache_update = 0
        self._cache_ttl = 5.0  # Cache for 5 seconds
    
    def extract_text_from_element(self, selector: str) -> Optional[str]:
        """Extract text content from a specific element.
        
        Args:
            selector: Element selector
            
        Returns:
            Text content or None if element not found
        """
        try:
            element = self.asq.find(selector)
            if element and element.exists():
                return element.get_text()[0] if element.get_text() else None
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting text from element '{selector}': {e}")
        return None
    
    def extract_all_text(self, window_name: Optional[str] = None) -> List[str]:
        """Extract all text from the current window or specified window.
        
        Args:
            window_name: Optional window name to extract text from
            
        Returns:
            List of text strings found
        """
        try:
            if window_name:
                # Focus the specified window first
                self.asq.focus_window(window_name)
                time.sleep(0.5)  # Allow window to focus
            
            # Find all text elements
            text_elements = self.asq.find('text, label, button, menuitem')
            if text_elements and text_elements.exists():
                return text_elements.get_text()
            return []
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting all text: {e}")
            return []
    
    def search_text(self, search_term: str, case_sensitive: bool = False, 
                   regex: bool = False) -> List[TextMatch]:
        """Search for text in the current interface.
        
        Args:
            search_term: Text to search for
            case_sensitive: Whether search should be case sensitive
            regex: Whether search_term is a regular expression
            
        Returns:
            List of TextMatch objects
        """
        matches = []
        try:
            all_text_elements = self.asq.find('text, label, button, menuitem')
            if not all_text_elements or not all_text_elements.exists():
                return matches
            
            for i, element in enumerate(all_text_elements._collection):
                try:
                    element_text = getattr(element, 'text', '') or ''
                    if not element_text:
                        continue
                    
                    # Perform search
                    found = False
                    if regex:
                        flags = 0 if case_sensitive else re.IGNORECASE
                        found = bool(re.search(search_term, element_text, flags))
                    else:
                        if case_sensitive:
                            found = search_term in element_text
                        else:
                            found = search_term.lower() in element_text.lower()
                    
                    if found:
                        # Get element position (placeholder - would need actual implementation)
                        position = (0, 0)  # Would get from element bounds
                        matches.append(TextMatch(
                            text=element_text,
                            element=element,
                            position=position,
                            confidence=1.0
                        ))
                except Exception as e:
                    if self.asq.computer.verbose:
                        print(f"Error processing element {i}: {e}")
                    continue
                    
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error searching text: {e}")
        
        return matches
    
    def replace_text_in_field(self, selector: str, old_text: str, new_text: str) -> bool:
        """Replace text in a text field.
        
        Args:
            selector: Selector for the text field
            old_text: Text to replace
            new_text: Replacement text
            
        Returns:
            True if replacement was successful
        """
        try:
            element = self.asq.find(selector)
            if not element or not element.exists():
                return False
            
            current_text = element.get_text()
            if not current_text:
                return False
            
            current_text = current_text[0] if isinstance(current_text, list) else current_text
            if old_text not in current_text:
                return False
            
            new_full_text = current_text.replace(old_text, new_text)
            element.clear().type(new_full_text)
            return True
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error replacing text in field '{selector}': {e}")
            return False
    
    def format_text_in_field(self, selector: str, formatting: str) -> bool:
        """Apply text formatting to a field (if supported by the application).
        
        Args:
            selector: Selector for the text field
            formatting: Formatting to apply ('bold', 'italic', 'underline', etc.)
            
        Returns:
            True if formatting was applied successfully
        """
        try:
            element = self.asq.find(selector)
            if not element or not element.exists():
                return False
            
            # Focus the element first
            element.click()
            
            # Apply keyboard shortcuts for common formatting
            formatting_shortcuts = {
                'bold': 'ctrl+b',
                'italic': 'ctrl+i', 
                'underline': 'ctrl+u',
                'select_all': 'ctrl+a',
                'copy': 'ctrl+c',
                'paste': 'ctrl+v',
                'cut': 'ctrl+x',
                'undo': 'ctrl+z',
                'redo': 'ctrl+y'
            }
            
            if formatting.lower() in formatting_shortcuts:
                # Use keyboard module to send shortcut
                shortcut = formatting_shortcuts[formatting.lower()]
                self.asq.computer.keyboard.hotkey(*shortcut.split('+'))
                return True
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error formatting text in field '{selector}': {e}")
            return False
    
    def copy_text_from_element(self, selector: str) -> Optional[str]:
        """Copy text from an element to clipboard.
        
        Args:
            selector: Element selector
            
        Returns:
            Copied text or None if failed
        """
        try:
            element = self.asq.find(selector)
            if not element or not element.exists():
                return None
            
            # Click element to focus it
            element.click()
            
            # Select all text and copy
            self.asq.computer.keyboard.hotkey('ctrl', 'a')
            time.sleep(0.1)
            self.asq.computer.keyboard.hotkey('ctrl', 'c')
            time.sleep(0.1)
            
            # Get text from clipboard
            return self.asq.computer.clipboard.get_text()
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error copying text from element '{selector}': {e}")
            return None
    
    def paste_text_to_element(self, selector: str, text: str) -> bool:
        """Paste text to an element via clipboard.
        
        Args:
            selector: Element selector
            text: Text to paste
            
        Returns:
            True if paste was successful
        """
        try:
            element = self.asq.find(selector)
            if not element or not element.exists():
                return False
            
            # Set clipboard content
            self.asq.computer.clipboard.set_text(text)
            time.sleep(0.1)
            
            # Click element to focus it
            element.click()
            
            # Paste text
            self.asq.computer.keyboard.hotkey('ctrl', 'v')
            return True
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error pasting text to element '{selector}': {e}")
            return False
    
    def get_text_statistics(self, text: str) -> Dict[str, Any]:
        """Get statistics about text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with text statistics
        """
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'paragraph_count': 0,
                'sentence_count': 0
            }
        
        lines = text.split('\n')
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        
        return {
            'character_count': len(text),
            'character_count_no_spaces': len(text.replace(' ', '')),
            'word_count': len(words),
            'line_count': len(lines),
            'paragraph_count': len(paragraphs),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'average_sentence_length': len(words) / len([s for s in sentences if s.strip()]) if sentences else 0
        }
    
    def extract_structured_data(self, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract structured data using regex patterns.
        
        Args:
            patterns: Dictionary mapping data types to regex patterns
            
        Returns:
            Dictionary mapping data types to found matches
        """
        results = {}
        try:
            # Get all text from current interface
            all_text = ' '.join(self.extract_all_text())
            
            for data_type, pattern in patterns.items():
                try:
                    matches = re.findall(pattern, all_text, re.IGNORECASE)
                    results[data_type] = matches
                except re.error as e:
                    if self.asq.computer.verbose:
                        print(f"Invalid regex pattern for '{data_type}': {e}")
                    results[data_type] = []
                    
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting structured data: {e}")
        
        return results
    
    def find_text_near_element(self, element_selector: str, direction: str = 'right', 
                              distance: int = 100) -> Optional[str]:
        """Find text near a specific element.
        
        Args:
            element_selector: Selector for the reference element
            direction: Direction to search ('left', 'right', 'above', 'below')
            distance: Maximum distance in pixels to search
            
        Returns:
            Text found near the element or None
        """
        try:
            # This would require spatial analysis of elements
            # For now, return a placeholder implementation
            element = self.asq.find(element_selector)
            if not element or not element.exists():
                return None
            
            # Simplified implementation - find text elements and return first one
            text_elements = self.asq.find('text, label')
            if text_elements and text_elements.exists():
                texts = text_elements.get_text()
                return texts[0] if texts else None
            
            return None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error finding text near element '{element_selector}': {e}")
            return None
    
    def validate_text_format(self, text: str, format_type: str) -> bool:
        """Validate text against common formats.
        
        Args:
            text: Text to validate
            format_type: Type of format to validate against
            
        Returns:
            True if text matches the format
        """
        if not text:
            return False
        
        patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^[\+]?[1-9][\d]{0,15}$',
            'url': r'^https?://[^\s/$.?#].[^\s]*$',
            'ip_address': r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$',
            'date_iso': r'^\d{4}-\d{2}-\d{2}$',
            'time_24h': r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$',
            'number': r'^-?\d+(\.\d+)?$',
            'integer': r'^-?\d+$',
            'postal_code': r'^\d{5}(-\d{4})?$',
            'credit_card': r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$'
        }
        
        pattern = patterns.get(format_type.lower())
        if not pattern:
            return False
        
        return bool(re.match(pattern, text.strip()))
    
    def clear_cache(self):
        """Clear the text processing cache."""
        self._text_cache.clear()
        self._last_cache_update = 0