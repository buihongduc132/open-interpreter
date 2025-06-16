"""
Form automation module for ASQ integration.
Provides high-level form filling and interaction capabilities.
"""

import platform
from typing import Dict, Any, List, Optional, Union


class FormAutomation:
    """High-level form automation capabilities."""
    
    def __init__(self, asq_instance=None):
        """Initialize form automation.
        
        Args:
            asq_instance: The ASQ instance to use for form operations
        """
        self.asq = asq_instance
        self._available = platform.system() == 'Linux'
    
    def fill_form(self, form_data: Dict[str, str], form_selector: Optional[str] = None) -> Dict[str, bool]:
        """Fill out a form with provided data.
        
        Args:
            form_data: Dictionary mapping field names to values
            form_selector: Optional selector to scope to specific form
            
        Returns:
            Dictionary mapping field names to success status
            
        Example:
            form_data = {
                'username': 'john_doe',
                'password': 'secret123',
                'email': 'john@example.com'
            }
            results = fill_form(form_data)
        """
        if not self._available:
            raise RuntimeError("Form automation only available on Linux systems")
        
        results = {}
        
        for field_name, value in form_data.items():
            try:
                success = self._fill_field(field_name, value, form_selector)
                results[field_name] = success
            except Exception as e:
                print(f"Error filling field '{field_name}': {e}")
                results[field_name] = False
        
        return results
    
    def submit_form(self, submit_button: str = "Submit") -> bool:
        """Submit a form by clicking the submit button.
        
        Args:
            submit_button: Name or text of the submit button
            
        Returns:
            True if form was submitted successfully
        """
        if not self._available:
            raise RuntimeError("Form automation only available on Linux systems")
        
        try:
            # Try different common submit button patterns
            submit_patterns = [
                f'button[name="{submit_button}"]',
                f'button[text="{submit_button}"]',
                f'input[type="submit"][value="{submit_button}"]',
                'button[type="submit"]',
                'input[type="submit"]'
            ]
            
            for pattern in submit_patterns:
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        elements[0].click()
                        return True
            
            return False
        except Exception as e:
            print(f"Error submitting form: {e}")
            return False
    
    def clear_form(self, form_selector: Optional[str] = None) -> bool:
        """Clear all fields in a form.
        
        Args:
            form_selector: Optional selector to scope to specific form
            
        Returns:
            True if form was cleared successfully
        """
        if not self._available:
            raise RuntimeError("Form automation only available on Linux systems")
        
        try:
            # Find all input fields and clear them
            field_selectors = [
                'text',
                'entry',
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'textarea'
            ]
            
            cleared_count = 0
            for selector in field_selectors:
                if form_selector:
                    selector = f'{form_selector} {selector}'
                
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(selector)
                    for element in elements:
                        if hasattr(element, 'clear'):
                            element.clear()
                            cleared_count += 1
            
            return cleared_count > 0
        except Exception as e:
            print(f"Error clearing form: {e}")
            return False
    
    def validate_form(self, required_fields: List[str]) -> Dict[str, bool]:
        """Validate that required form fields are filled.
        
        Args:
            required_fields: List of required field names
            
        Returns:
            Dictionary mapping field names to validation status
        """
        if not self._available:
            raise RuntimeError("Form automation only available on Linux systems")
        
        validation_results = {}
        
        for field_name in required_fields:
            try:
                # Check if field has content
                field_selector = f'text[name="{field_name}"], entry[name="{field_name}"]'
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(field_selector)
                    if elements and len(elements) > 0:
                        element = elements[0]
                        text = getattr(element, 'text', '') or getattr(element, 'value', '')
                        validation_results[field_name] = bool(text.strip())
                    else:
                        validation_results[field_name] = False
                else:
                    validation_results[field_name] = False
            except Exception as e:
                print(f"Error validating field '{field_name}': {e}")
                validation_results[field_name] = False
        
        return validation_results
    
    def get_form_data(self, form_selector: Optional[str] = None) -> Dict[str, str]:
        """Extract current data from form fields.
        
        Args:
            form_selector: Optional selector to scope to specific form
            
        Returns:
            Dictionary mapping field names to current values
        """
        if not self._available:
            raise RuntimeError("Form automation only available on Linux systems")
        
        form_data = {}
        
        try:
            # Find all input fields and extract their values
            field_selectors = [
                'text',
                'entry',
                'input[type="text"]',
                'input[type="email"]',
                'input[type="password"]',
                'textarea'
            ]
            
            for selector in field_selectors:
                if form_selector:
                    selector = f'{form_selector} {selector}'
                
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(selector)
                    for element in elements:
                        name = getattr(element, 'name', '')
                        text = getattr(element, 'text', '') or getattr(element, 'value', '')
                        if name:
                            form_data[name] = text
        
        except Exception as e:
            print(f"Error extracting form data: {e}")
        
        return form_data
    
    def _fill_field(self, field_name: str, value: str, form_selector: Optional[str] = None) -> bool:
        """Fill a specific form field.
        
        Args:
            field_name: Name of the field to fill
            value: Value to enter
            form_selector: Optional form scope
            
        Returns:
            True if field was filled successfully
        """
        try:
            # Try different field selector patterns
            field_patterns = [
                f'text[name="{field_name}"]',
                f'entry[name="{field_name}"]',
                f'input[name="{field_name}"]',
                f'textarea[name="{field_name}"]',
                f'*[name="{field_name}"]'
            ]
            
            for pattern in field_patterns:
                if form_selector:
                    pattern = f'{form_selector} {pattern}'
                
                if self.asq and hasattr(self.asq, 'find'):
                    elements = self.asq.find(pattern)
                    if elements and len(elements) > 0:
                        element = elements[0]
                        
                        # Clear field first
                        if hasattr(element, 'clear'):
                            element.clear()
                        
                        # Type the value
                        if hasattr(element, 'type'):
                            element.type(value)
                            return True
                        elif hasattr(element, 'set_text'):
                            element.set_text(value)
                            return True
            
            return False
        except Exception as e:
            print(f"Error filling field '{field_name}': {e}")
            return False