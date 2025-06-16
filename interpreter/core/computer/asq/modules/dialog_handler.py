"""
Dialog and modal handling module for ASQ integration.
Provides specialized methods for handling dialogs, alerts, and modal windows.
"""

import time
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class DialogType(Enum):
    """Types of dialogs that can be handled."""
    ALERT = "alert"
    CONFIRMATION = "confirmation"
    FILE_OPEN = "file_open"
    FILE_SAVE = "file_save"
    FOLDER_BROWSE = "folder_browse"
    LOGIN = "login"
    SETTINGS = "settings"
    ABOUT = "about"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    CUSTOM = "custom"


@dataclass
class DialogInfo:
    """Information about a detected dialog."""
    dialog_type: DialogType
    title: str
    message: str
    buttons: List[str]
    fields: List[str]
    is_modal: bool = True


class DialogHandler:
    """High-level dialog and modal window handling."""
    
    def __init__(self, asq_instance):
        """Initialize dialog handler.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._dialog_patterns = self._init_dialog_patterns()
    
    def detect_dialog(self, timeout: float = 5.0) -> Optional[DialogInfo]:
        """Detect if a dialog is currently open.
        
        Args:
            timeout: Maximum time to wait for dialog detection
            
        Returns:
            DialogInfo object if dialog detected, None otherwise
        """
        try:
            # Look for common dialog indicators
            dialog_selectors = [
                'dialog',
                'window[role="dialog"]',
                'frame[name*="dialog"]',
                'frame[name*="Dialog"]',
                'window[name*="dialog"]',
                'window[name*="Dialog"]'
            ]
            
            for selector in dialog_selectors:
                if self.asq.wait_for_element(selector, timeout=1.0):
                    dialog_element = self.asq.find(selector)
                    if dialog_element and len(dialog_element.elements) > 0:
                        return self._analyze_dialog(dialog_element.elements[0])
            
            return None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error detecting dialog: {e}")
            return None
    
    def handle_alert_dialog(self, action: str = "ok") -> bool:
        """Handle alert dialogs (OK, Cancel).
        
        Args:
            action: Action to take ("ok", "cancel", "yes", "no")
            
        Returns:
            True if dialog was handled successfully
        """
        try:
            dialog = self.detect_dialog()
            if not dialog or dialog.dialog_type != DialogType.ALERT:
                return False
            
            # Map actions to button names
            button_map = {
                'ok': ['OK', 'Ok', 'ok', 'Okay'],
                'cancel': ['Cancel', 'cancel'],
                'yes': ['Yes', 'yes', 'Y'],
                'no': ['No', 'no', 'N'],
                'close': ['Close', 'close', 'X']
            }
            
            button_names = button_map.get(action.lower(), [action])
            
            for button_name in button_names:
                if self.asq.click_if_exists(f'button[name="{button_name}"]', timeout=2.0):
                    return True
                if self.asq.click_if_exists(f'button:contains("{button_name}")', timeout=2.0):
                    return True
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error handling alert dialog: {e}")
            return False
    
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
        try:
            dialog = self.detect_dialog()
            if not dialog:
                return False
            
            if dialog_type.lower() == "open":
                return self._handle_file_open_dialog(file_path)
            elif dialog_type.lower() == "save":
                return self._handle_file_save_dialog(file_path, filename)
            elif dialog_type.lower() == "browse":
                return self._handle_folder_browse_dialog(file_path)
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error handling file dialog: {e}")
            return False
    
    def handle_login_dialog(self, username: str, password: str, 
                           remember_me: bool = False) -> bool:
        """Handle login dialogs.
        
        Args:
            username: Username to enter
            password: Password to enter
            remember_me: Whether to check "remember me" option
            
        Returns:
            True if login was successful
        """
        try:
            dialog = self.detect_dialog()
            if not dialog:
                return False
            
            # Find username field
            username_selectors = [
                'text[name*="user"]',
                'text[name*="User"]',
                'text[name*="login"]',
                'text[name*="Login"]',
                'text[name*="email"]',
                'text[name*="Email"]'
            ]
            
            username_entered = False
            for selector in username_selectors:
                if self.asq.type_if_exists(selector, username, timeout=2.0):
                    username_entered = True
                    break
            
            if not username_entered:
                return False
            
            # Find password field
            password_selectors = [
                'text[name*="pass"]',
                'text[name*="Pass"]',
                'password',
                'text[type="password"]'
            ]
            
            password_entered = False
            for selector in password_selectors:
                if self.asq.type_if_exists(selector, password, timeout=2.0):
                    password_entered = True
                    break
            
            if not password_entered:
                return False
            
            # Handle remember me checkbox
            if remember_me:
                remember_selectors = [
                    'checkbox[name*="remember"]',
                    'checkbox[name*="Remember"]',
                    'checkbox[name*="keep"]',
                    'checkbox[name*="stay"]'
                ]
                
                for selector in remember_selectors:
                    if self.asq.click_if_exists(selector, timeout=1.0):
                        break
            
            # Click login button
            login_buttons = ['Login', 'Log in', 'Sign in', 'Submit', 'OK']
            for button_name in login_buttons:
                if self.asq.click_if_exists(f'button[name="{button_name}"]', timeout=2.0):
                    return True
                if self.asq.click_if_exists(f'button:contains("{button_name}")', timeout=2.0):
                    return True
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error handling login dialog: {e}")
            return False
    
    def wait_for_dialog_close(self, timeout: float = 10.0) -> bool:
        """Wait for a dialog to close.
        
        Args:
            timeout: Maximum time to wait for dialog to close
            
        Returns:
            True if dialog closed within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.detect_dialog(timeout=1.0):
                return True
            time.sleep(0.5)
        return False
    
    def get_dialog_text(self) -> Optional[str]:
        """Get text content from current dialog.
        
        Returns:
            Dialog text content or None if no dialog
        """
        try:
            dialog = self.detect_dialog()
            if not dialog:
                return None
            
            # Try to find text content
            text_selectors = [
                'label',
                'text[role="static"]',
                'text[readonly="true"]',
                'statictext'
            ]
            
            text_content = []
            for selector in text_selectors:
                text = self.asq.get_text_if_exists(selector, timeout=1.0)
                if text and text.strip():
                    text_content.append(text.strip())
            
            return '\n'.join(text_content) if text_content else None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error getting dialog text: {e}")
            return None
    
    def _analyze_dialog(self, dialog_element: Any) -> DialogInfo:
        """Analyze a dialog element to determine its type and properties.
        
        Args:
            dialog_element: Dialog element to analyze
            
        Returns:
            DialogInfo object with dialog details
        """
        try:
            # Get dialog title
            title = getattr(dialog_element, 'name', '') or getattr(dialog_element, 'title', '')
            
            # Detect dialog type based on title and content
            dialog_type = self._detect_dialog_type(title)
            
            # Find buttons
            buttons = self._find_dialog_buttons(dialog_element)
            
            # Find input fields
            fields = self._find_dialog_fields(dialog_element)
            
            # Get message text
            message = self._get_dialog_message(dialog_element)
            
            return DialogInfo(
                dialog_type=dialog_type,
                title=title,
                message=message,
                buttons=buttons,
                fields=fields,
                is_modal=True
            )
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error analyzing dialog: {e}")
            return DialogInfo(
                dialog_type=DialogType.CUSTOM,
                title="Unknown",
                message="",
                buttons=[],
                fields=[]
            )
    
    def _detect_dialog_type(self, title: str) -> DialogType:
        """Detect dialog type from title and content.
        
        Args:
            title: Dialog title
            
        Returns:
            Detected dialog type
        """
        title_lower = title.lower()
        
        # File dialogs
        if any(word in title_lower for word in ['open', 'file', 'browse']):
            if 'save' in title_lower:
                return DialogType.FILE_SAVE
            elif 'folder' in title_lower or 'directory' in title_lower:
                return DialogType.FOLDER_BROWSE
            else:
                return DialogType.FILE_OPEN
        
        # Alert dialogs
        if any(word in title_lower for word in ['alert', 'warning', 'error', 'info']):
            if 'error' in title_lower:
                return DialogType.ERROR
            elif 'warning' in title_lower:
                return DialogType.WARNING
            else:
                return DialogType.INFO
        
        # Login dialogs
        if any(word in title_lower for word in ['login', 'sign in', 'authenticate']):
            return DialogType.LOGIN
        
        # Settings dialogs
        if any(word in title_lower for word in ['settings', 'preferences', 'options']):
            return DialogType.SETTINGS
        
        # About dialogs
        if any(word in title_lower for word in ['about', 'version', 'help']):
            return DialogType.ABOUT
        
        # Confirmation dialogs
        if any(word in title_lower for word in ['confirm', 'sure', 'delete', 'remove']):
            return DialogType.CONFIRMATION
        
        return DialogType.CUSTOM
    
    def _find_dialog_buttons(self, dialog_element: Any) -> List[str]:
        """Find buttons in a dialog.
        
        Args:
            dialog_element: Dialog element to search
            
        Returns:
            List of button names
        """
        # This would be implemented with actual AT-SPI traversal
        # For now, return common button names
        return ['OK', 'Cancel', 'Yes', 'No', 'Apply', 'Close']
    
    def _find_dialog_fields(self, dialog_element: Any) -> List[str]:
        """Find input fields in a dialog.
        
        Args:
            dialog_element: Dialog element to search
            
        Returns:
            List of field names
        """
        # This would be implemented with actual AT-SPI traversal
        # For now, return empty list
        return []
    
    def _get_dialog_message(self, dialog_element: Any) -> str:
        """Get message text from dialog.
        
        Args:
            dialog_element: Dialog element to search
            
        Returns:
            Dialog message text
        """
        # This would be implemented with actual AT-SPI traversal
        return getattr(dialog_element, 'description', '') or ""
    
    def _handle_file_open_dialog(self, file_path: Optional[str]) -> bool:
        """Handle file open dialog.
        
        Args:
            file_path: Path to file to open
            
        Returns:
            True if successful
        """
        if not file_path:
            return False
        
        # Type file path in location bar
        location_selectors = [
            'text[name*="location"]',
            'text[name*="path"]',
            'text[name*="file"]'
        ]
        
        for selector in location_selectors:
            if self.asq.type_if_exists(selector, file_path, timeout=2.0):
                # Press Enter or click Open
                if self.asq.click_if_exists('button[name="Open"]', timeout=2.0):
                    return True
                # Try pressing Enter
                break
        
        return False
    
    def _handle_file_save_dialog(self, file_path: Optional[str], 
                                filename: Optional[str]) -> bool:
        """Handle file save dialog.
        
        Args:
            file_path: Directory path
            filename: Name of file to save
            
        Returns:
            True if successful
        """
        if filename:
            # Type filename
            filename_selectors = [
                'text[name*="name"]',
                'text[name*="filename"]',
                'text[name*="file"]'
            ]
            
            for selector in filename_selectors:
                if self.asq.type_if_exists(selector, filename, timeout=2.0):
                    break
        
        if file_path:
            # Navigate to directory
            # This would require more complex navigation logic
            pass
        
        # Click Save
        return self.asq.click_if_exists('button[name="Save"]', timeout=2.0)
    
    def _handle_folder_browse_dialog(self, folder_path: Optional[str]) -> bool:
        """Handle folder browse dialog.
        
        Args:
            folder_path: Path to folder to select
            
        Returns:
            True if successful
        """
        if not folder_path:
            return False
        
        # This would require navigation through folder tree
        # For now, just click OK/Select
        return self.asq.click_if_exists('button[name="Select"]', timeout=2.0) or \
               self.asq.click_if_exists('button[name="OK"]', timeout=2.0)
    
    def _init_dialog_patterns(self) -> Dict[str, Any]:
        """Initialize dialog detection patterns.
        
        Returns:
            Dictionary of dialog patterns
        """
        return {
            'file_dialogs': [
                'Open File', 'Save File', 'Save As', 'Browse', 'Select File'
            ],
            'alert_dialogs': [
                'Alert', 'Warning', 'Error', 'Information', 'Confirm'
            ],
            'login_dialogs': [
                'Login', 'Sign In', 'Authentication', 'Credentials'
            ]
        }