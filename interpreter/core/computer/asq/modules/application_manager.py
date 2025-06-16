"""
Application management module for ASQ integration.
Provides high-level methods for launching, managing, and interacting with applications.
"""

import os
import subprocess
import time
import platform
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ApplicationInfo:
    """Information about a running application."""
    name: str
    pid: int
    window_title: str
    executable_path: str
    is_active: bool = False
    window_count: int = 0


class ApplicationManager:
    """High-level application management for desktop automation."""
    
    def __init__(self, asq_instance):
        """Initialize application manager.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._available = platform.system() == 'Linux'
        self._running_apps = {}
        self._launched_processes = {}
    
    def launch_application(self, app_name: str, app_path: Optional[str] = None, 
                          wait_for_window: bool = True, timeout: float = 10.0) -> bool:
        """Launch an application by name or path.
        
        Args:
            app_name: Name of the application to launch
            app_path: Optional path to application executable
            wait_for_window: Whether to wait for application window to appear
            timeout: Maximum time to wait for application to start
            
        Returns:
            True if application was launched successfully
            
        Examples:
            launch_application('firefox')
            launch_application('calculator', '/usr/bin/gnome-calculator')
            launch_application('gedit', wait_for_window=True, timeout=15)
        """
        if not self._available:
            return False
        
        try:
            # Determine command to run
            if app_path and os.path.exists(app_path):
                command = [app_path]
            else:
                # Try common application names
                command = self._get_application_command(app_name)
                if not command:
                    if self.asq.computer.verbose:
                        print(f"Unknown application: {app_name}")
                    return False
            
            # Launch the application
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            self._launched_processes[app_name] = process
            
            if wait_for_window:
                # Wait for application window to appear
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if self._find_application_window(app_name):
                        return True
                    time.sleep(0.5)
                
                if self.asq.computer.verbose:
                    print(f"Application {app_name} launched but window not found within {timeout}s")
                return False
            
            return True
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error launching application {app_name}: {e}")
            return False
    
    def close_application(self, app_name: str, force: bool = False) -> bool:
        """Close an application gracefully or forcefully.
        
        Args:
            app_name: Name of the application to close
            force: Whether to force close the application
            
        Returns:
            True if application was closed successfully
        """
        if not self._available:
            return False
        
        try:
            # Try to close via window manager first
            windows = self.asq.window_manager.list_windows()
            for window in windows:
                if app_name.lower() in window.get('name', '').lower():
                    if self.asq.window_manager.close_window(window['name']):
                        return True
            
            # If that fails, try to terminate the process
            if app_name in self._launched_processes:
                process = self._launched_processes[app_name]
                if force:
                    process.kill()
                else:
                    process.terminate()
                
                # Wait for process to exit
                try:
                    process.wait(timeout=5)
                    del self._launched_processes[app_name]
                    return True
                except subprocess.TimeoutExpired:
                    if force:
                        process.kill()
                        del self._launched_processes[app_name]
                        return True
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error closing application {app_name}: {e}")
            return False
    
    def switch_to_application(self, app_name: str) -> bool:
        """Switch focus to a specific application.
        
        Args:
            app_name: Name of the application to focus
            
        Returns:
            True if application was focused successfully
        """
        if not self._available:
            return False
        
        try:
            # Find application window
            windows = self.asq.window_manager.list_windows()
            for window in windows:
                if app_name.lower() in window.get('name', '').lower():
                    return self.asq.window_manager.focus_window(window['name'])
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error switching to application {app_name}: {e}")
            return False
    
    def get_running_applications(self) -> List[ApplicationInfo]:
        """Get list of currently running applications.
        
        Returns:
            List of ApplicationInfo objects
        """
        if not self._available:
            return []
        
        try:
            applications = []
            windows = self.asq.window_manager.list_windows()
            active_window = self.asq.window_manager.get_active_window()
            
            # Group windows by application
            app_windows = {}
            for window in windows:
                app_name = self._extract_app_name(window.get('name', ''))
                if app_name not in app_windows:
                    app_windows[app_name] = []
                app_windows[app_name].append(window)
            
            # Create ApplicationInfo objects
            for app_name, windows_list in app_windows.items():
                is_active = any(
                    w.get('name') == active_window.get('name', '') 
                    for w in windows_list
                ) if active_window else False
                
                app_info = ApplicationInfo(
                    name=app_name,
                    pid=windows_list[0].get('pid', 0),
                    window_title=windows_list[0].get('name', ''),
                    executable_path=windows_list[0].get('executable', ''),
                    is_active=is_active,
                    window_count=len(windows_list)
                )
                applications.append(app_info)
            
            return applications
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error getting running applications: {e}")
            return []
    
    def is_application_running(self, app_name: str) -> bool:
        """Check if an application is currently running.
        
        Args:
            app_name: Name of the application to check
            
        Returns:
            True if application is running
        """
        applications = self.get_running_applications()
        return any(
            app_name.lower() in app.name.lower() 
            for app in applications
        )
    
    def wait_for_application(self, app_name: str, timeout: float = 30.0) -> bool:
        """Wait for an application to start and become available.
        
        Args:
            app_name: Name of the application to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if application became available within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_application_running(app_name):
                return True
            time.sleep(1.0)
        return False
    
    def restart_application(self, app_name: str, app_path: Optional[str] = None) -> bool:
        """Restart an application (close and relaunch).
        
        Args:
            app_name: Name of the application to restart
            app_path: Optional path to application executable
            
        Returns:
            True if application was restarted successfully
        """
        # Close the application
        if self.is_application_running(app_name):
            if not self.close_application(app_name):
                return False
            
            # Wait for application to close
            time.sleep(2.0)
        
        # Relaunch the application
        return self.launch_application(app_name, app_path)
    
    def _get_application_command(self, app_name: str) -> Optional[List[str]]:
        """Get command to launch an application by name.
        
        Args:
            app_name: Name of the application
            
        Returns:
            Command list or None if unknown
        """
        # Common application mappings
        app_commands = {
            'firefox': ['firefox'],
            'chrome': ['google-chrome'],
            'chromium': ['chromium-browser'],
            'calculator': ['gnome-calculator', 'kcalc', 'xcalc'],
            'gedit': ['gedit'],
            'kate': ['kate'],
            'nautilus': ['nautilus'],
            'dolphin': ['dolphin'],
            'terminal': ['gnome-terminal', 'konsole', 'xterm'],
            'libreoffice': ['libreoffice'],
            'writer': ['libreoffice', '--writer'],
            'calc': ['libreoffice', '--calc'],
            'impress': ['libreoffice', '--impress'],
            'gimp': ['gimp'],
            'inkscape': ['inkscape'],
            'vlc': ['vlc'],
            'thunderbird': ['thunderbird'],
            'code': ['code'],
            'vscode': ['code'],
            'atom': ['atom'],
            'sublime': ['subl'],
        }
        
        app_name_lower = app_name.lower()
        
        # Try exact match first
        if app_name_lower in app_commands:
            commands = app_commands[app_name_lower]
            if isinstance(commands, str):
                commands = [commands]
            
            # Check if command exists
            for cmd in commands:
                if self._command_exists(cmd):
                    return [cmd] if isinstance(commands[0], str) else commands
        
        # Try partial match
        for key, commands in app_commands.items():
            if app_name_lower in key or key in app_name_lower:
                if isinstance(commands, str):
                    commands = [commands]
                
                for cmd in commands:
                    if self._command_exists(cmd):
                        return [cmd] if isinstance(commands[0], str) else commands
        
        # Try the app name directly
        if self._command_exists(app_name):
            return [app_name]
        
        return None
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH.
        
        Args:
            command: Command to check
            
        Returns:
            True if command exists
        """
        try:
            subprocess.run(
                ['which', command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _find_application_window(self, app_name: str) -> bool:
        """Find if an application window exists.
        
        Args:
            app_name: Name of the application
            
        Returns:
            True if window found
        """
        try:
            windows = self.asq.window_manager.list_windows()
            return any(
                app_name.lower() in window.get('name', '').lower()
                for window in windows
            )
        except:
            return False
    
    def _extract_app_name(self, window_title: str) -> str:
        """Extract application name from window title.
        
        Args:
            window_title: Full window title
            
        Returns:
            Extracted application name
        """
        # Remove common suffixes
        title = window_title.lower()
        
        # Common patterns to extract app name
        if ' - ' in title:
            # "Document - Application" -> "Application"
            parts = title.split(' - ')
            return parts[-1].strip()
        elif ' — ' in title:
            # "Document — Application" -> "Application"
            parts = title.split(' — ')
            return parts[-1].strip()
        elif title.endswith(')'):
            # "Application (Document)" -> "Application"
            return title.split('(')[0].strip()
        else:
            return title.strip()
    
    def get_application_info(self, app_name: str) -> Optional[ApplicationInfo]:
        """Get detailed information about a specific application.
        
        Args:
            app_name: Name of the application
            
        Returns:
            ApplicationInfo object or None if not found
        """
        applications = self.get_running_applications()
        for app in applications:
            if app_name.lower() in app.name.lower():
                return app
        return None