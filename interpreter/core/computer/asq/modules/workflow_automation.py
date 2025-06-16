"""
Workflow automation module for ASQ integration.
Provides composite methods for common automation workflows and multi-step processes.
"""

import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    name: str
    action: Callable
    args: tuple = ()
    kwargs: dict = None
    timeout: float = 10.0
    retry_count: int = 3
    required: bool = True
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class WorkflowResult:
    """Result of workflow execution."""
    status: WorkflowStatus
    completed_steps: List[str]
    failed_step: Optional[str]
    error_message: Optional[str]
    execution_time: float
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class WorkflowAutomation:
    """High-level workflow automation for complex multi-step processes."""
    
    def __init__(self, asq_instance):
        """Initialize workflow automation.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._workflows = {}
        self._current_workflow = None
    
    def create_workflow(self, name: str, steps: List[WorkflowStep]) -> None:
        """Create a new workflow with specified steps.
        
        Args:
            name: Name of the workflow
            steps: List of workflow steps
        """
        self._workflows[name] = steps
    
    def execute_workflow(self, name: str, context: Optional[Dict[str, Any]] = None) -> WorkflowResult:
        """Execute a named workflow.
        
        Args:
            name: Name of the workflow to execute
            context: Optional context data for the workflow
            
        Returns:
            WorkflowResult with execution details
        """
        if name not in self._workflows:
            return WorkflowResult(
                status=WorkflowStatus.FAILED,
                completed_steps=[],
                failed_step=None,
                error_message=f"Workflow '{name}' not found",
                execution_time=0.0
            )
        
        return self._execute_steps(self._workflows[name], context or {})
    
    def login_workflow(self, username: str, password: str, 
                      app_name: Optional[str] = None,
                      remember_me: bool = False) -> WorkflowResult:
        """Execute a complete login workflow.
        
        Args:
            username: Username to enter
            password: Password to enter
            app_name: Optional application name to focus first
            remember_me: Whether to check remember me option
            
        Returns:
            WorkflowResult with login status
        """
        steps = []
        
        # Step 1: Focus application if specified
        if app_name:
            steps.append(WorkflowStep(
                name="focus_application",
                action=self.asq.application_manager.switch_to_application,
                args=(app_name,),
                timeout=5.0
            ))
        
        # Step 2: Wait for login dialog or form
        steps.append(WorkflowStep(
            name="wait_for_login",
            action=self._wait_for_login_elements,
            timeout=10.0
        ))
        
        # Step 3: Enter username
        steps.append(WorkflowStep(
            name="enter_username",
            action=self._enter_username,
            args=(username,),
            timeout=5.0
        ))
        
        # Step 4: Enter password
        steps.append(WorkflowStep(
            name="enter_password",
            action=self._enter_password,
            args=(password,),
            timeout=5.0
        ))
        
        # Step 5: Handle remember me if requested
        if remember_me:
            steps.append(WorkflowStep(
                name="remember_me",
                action=self._check_remember_me,
                timeout=3.0,
                required=False
            ))
        
        # Step 6: Submit login
        steps.append(WorkflowStep(
            name="submit_login",
            action=self._submit_login,
            timeout=5.0
        ))
        
        # Step 7: Wait for login completion
        steps.append(WorkflowStep(
            name="verify_login",
            action=self._verify_login_success,
            timeout=10.0
        ))
        
        return self._execute_steps(steps, {'username': username, 'password': password})
    
    def form_submission_workflow(self, form_data: Dict[str, str], 
                                submit_button: str = "Submit") -> WorkflowResult:
        """Execute a complete form submission workflow.
        
        Args:
            form_data: Dictionary of field names to values
            submit_button: Name of submit button
            
        Returns:
            WorkflowResult with submission status
        """
        steps = [
            WorkflowStep(
                name="wait_for_form",
                action=self._wait_for_form,
                timeout=10.0
            ),
            WorkflowStep(
                name="fill_form",
                action=self.asq.fill_form,
                args=(form_data,),
                timeout=30.0
            ),
            WorkflowStep(
                name="submit_form",
                action=self.asq.submit_form,
                args=(submit_button,),
                timeout=10.0
            ),
            WorkflowStep(
                name="verify_submission",
                action=self._verify_form_submission,
                timeout=15.0,
                required=False
            )
        ]
        
        return self._execute_steps(steps, {'form_data': form_data})
    
    def file_operation_workflow(self, operation: str, file_path: str, 
                               app_name: Optional[str] = None) -> WorkflowResult:
        """Execute a file operation workflow (open, save, etc.).
        
        Args:
            operation: Type of operation ("open", "save", "save_as")
            file_path: Path to file
            app_name: Optional application name
            
        Returns:
            WorkflowResult with operation status
        """
        steps = []
        
        # Focus application if specified
        if app_name:
            steps.append(WorkflowStep(
                name="focus_application",
                action=self.asq.application_manager.switch_to_application,
                args=(app_name,),
                timeout=5.0
            ))
        
        if operation.lower() == "open":
            steps.extend([
                WorkflowStep(
                    name="open_file_menu",
                    action=self._open_file_menu,
                    timeout=5.0
                ),
                WorkflowStep(
                    name="click_open",
                    action=self._click_menu_item,
                    args=("Open",),
                    timeout=5.0
                ),
                WorkflowStep(
                    name="handle_file_dialog",
                    action=self.asq.dialog_handler.handle_file_dialog,
                    args=("open", file_path),
                    timeout=15.0
                )
            ])
        elif operation.lower() in ["save", "save_as"]:
            steps.extend([
                WorkflowStep(
                    name="open_file_menu",
                    action=self._open_file_menu,
                    timeout=5.0
                ),
                WorkflowStep(
                    name="click_save",
                    action=self._click_menu_item,
                    args=("Save As" if operation.lower() == "save_as" else "Save",),
                    timeout=5.0
                ),
                WorkflowStep(
                    name="handle_save_dialog",
                    action=self.asq.dialog_handler.handle_file_dialog,
                    args=("save", file_path),
                    timeout=15.0
                )
            ])
        
        return self._execute_steps(steps, {'operation': operation, 'file_path': file_path})
    
    def application_startup_workflow(self, app_name: str, 
                                   initial_actions: Optional[List[Dict[str, Any]]] = None) -> WorkflowResult:
        """Execute application startup workflow with initial setup.
        
        Args:
            app_name: Name of application to start
            initial_actions: Optional list of initial actions to perform
            
        Returns:
            WorkflowResult with startup status
        """
        steps = [
            WorkflowStep(
                name="launch_application",
                action=self.asq.application_manager.launch_application,
                args=(app_name,),
                timeout=15.0
            ),
            WorkflowStep(
                name="wait_for_ready",
                action=self._wait_for_application_ready,
                args=(app_name,),
                timeout=20.0
            )
        ]
        
        # Add initial actions if specified
        if initial_actions:
            for i, action in enumerate(initial_actions):
                steps.append(WorkflowStep(
                    name=f"initial_action_{i}",
                    action=self._execute_action,
                    args=(action,),
                    timeout=action.get('timeout', 10.0),
                    required=action.get('required', False)
                ))
        
        return self._execute_steps(steps, {'app_name': app_name})
    
    def multi_window_workflow(self, window_actions: List[Dict[str, Any]]) -> WorkflowResult:
        """Execute workflow across multiple windows.
        
        Args:
            window_actions: List of actions for different windows
            
        Returns:
            WorkflowResult with multi-window operation status
        """
        steps = []
        
        for i, window_action in enumerate(window_actions):
            window_name = window_action.get('window_name')
            actions = window_action.get('actions', [])
            
            # Focus window
            steps.append(WorkflowStep(
                name=f"focus_window_{i}",
                action=self.asq.focus_window,
                args=(window_name,),
                timeout=5.0
            ))
            
            # Execute actions in window
            for j, action in enumerate(actions):
                steps.append(WorkflowStep(
                    name=f"window_{i}_action_{j}",
                    action=self._execute_action,
                    args=(action,),
                    timeout=action.get('timeout', 10.0),
                    required=action.get('required', True)
                ))
        
        return self._execute_steps(steps, {'window_actions': window_actions})
    
    def _execute_steps(self, steps: List[WorkflowStep], 
                      context: Dict[str, Any]) -> WorkflowResult:
        """Execute a list of workflow steps.
        
        Args:
            steps: List of steps to execute
            context: Context data for the workflow
            
        Returns:
            WorkflowResult with execution details
        """
        start_time = time.time()
        completed_steps = []
        
        for step in steps:
            step_start = time.time()
            success = False
            
            # Retry logic
            for attempt in range(step.retry_count):
                try:
                    # Execute step action
                    result = step.action(*step.args, **step.kwargs)
                    
                    # Check if step succeeded
                    if result is True or (result is not None and result != False):
                        success = True
                        break
                    
                except Exception as e:
                    if self.asq.computer.verbose:
                        print(f"Step '{step.name}' attempt {attempt + 1} failed: {e}")
                    
                    if attempt < step.retry_count - 1:
                        time.sleep(1.0)  # Wait before retry
                
                # Check timeout
                if time.time() - step_start > step.timeout:
                    break
            
            if success:
                completed_steps.append(step.name)
            elif step.required:
                # Required step failed
                return WorkflowResult(
                    status=WorkflowStatus.FAILED,
                    completed_steps=completed_steps,
                    failed_step=step.name,
                    error_message=f"Required step '{step.name}' failed",
                    execution_time=time.time() - start_time,
                    data=context
                )
            else:
                # Optional step failed, continue
                if self.asq.computer.verbose:
                    print(f"Optional step '{step.name}' failed, continuing...")
        
        # All steps completed
        status = WorkflowStatus.SUCCESS if len(completed_steps) == len(steps) else WorkflowStatus.PARTIAL
        
        return WorkflowResult(
            status=status,
            completed_steps=completed_steps,
            failed_step=None,
            error_message=None,
            execution_time=time.time() - start_time,
            data=context
        )
    
    # Helper methods for common workflow actions
    
    def _wait_for_login_elements(self) -> bool:
        """Wait for login form elements to appear."""
        selectors = [
            'text[name*="user"]',
            'text[name*="login"]',
            'text[name*="email"]',
            'password'
        ]
        
        for selector in selectors:
            if self.asq.wait_for_element(selector, timeout=2.0):
                return True
        return False
    
    def _enter_username(self, username: str) -> bool:
        """Enter username in login form."""
        selectors = [
            'text[name*="user"]',
            'text[name*="login"]',
            'text[name*="email"]'
        ]
        
        for selector in selectors:
            if self.asq.type_if_exists(selector, username, timeout=2.0):
                return True
        return False
    
    def _enter_password(self, password: str) -> bool:
        """Enter password in login form."""
        selectors = [
            'text[name*="pass"]',
            'password',
            'text[type="password"]'
        ]
        
        for selector in selectors:
            if self.asq.type_if_exists(selector, password, timeout=2.0):
                return True
        return False
    
    def _check_remember_me(self) -> bool:
        """Check remember me checkbox."""
        selectors = [
            'checkbox[name*="remember"]',
            'checkbox[name*="keep"]',
            'checkbox[name*="stay"]'
        ]
        
        for selector in selectors:
            if self.asq.click_if_exists(selector, timeout=1.0):
                return True
        return False
    
    def _submit_login(self) -> bool:
        """Submit login form."""
        buttons = ['Login', 'Log in', 'Sign in', 'Submit', 'OK']
        
        for button in buttons:
            if self.asq.click_if_exists(f'button[name="{button}"]', timeout=2.0):
                return True
        return False
    
    def _verify_login_success(self) -> bool:
        """Verify that login was successful."""
        # Look for indicators of successful login
        success_indicators = [
            'Welcome',
            'Dashboard',
            'Home',
            'Profile',
            'Logout'
        ]
        
        for indicator in success_indicators:
            if self.asq.find_by_text(indicator):
                return True
        
        # Check if login dialog disappeared
        return not self.asq.dialog_handler.detect_dialog(timeout=2.0)
    
    def _wait_for_form(self) -> bool:
        """Wait for form elements to appear."""
        form_selectors = [
            'form',
            'text',
            'button[name*="submit"]',
            'button[name*="Send"]'
        ]
        
        for selector in form_selectors:
            if self.asq.wait_for_element(selector, timeout=2.0):
                return True
        return False
    
    def _verify_form_submission(self) -> bool:
        """Verify that form was submitted successfully."""
        success_indicators = [
            'Success',
            'Thank you',
            'Submitted',
            'Sent',
            'Confirmation'
        ]
        
        for indicator in success_indicators:
            if self.asq.find_by_text(indicator):
                return True
        return False
    
    def _open_file_menu(self) -> bool:
        """Open the File menu."""
        return self.asq.click_if_exists('menu[name="File"]', timeout=3.0) or \
               self.asq.click_if_exists('button[name="File"]', timeout=3.0)
    
    def _click_menu_item(self, item_name: str) -> bool:
        """Click a menu item."""
        return self.asq.click_if_exists(f'menuitem[name="{item_name}"]', timeout=3.0) or \
               self.asq.click_if_exists(f'button[name="{item_name}"]', timeout=3.0)
    
    def _wait_for_application_ready(self, app_name: str) -> bool:
        """Wait for application to be ready for interaction."""
        # Wait for main window to appear
        if not self.asq.application_manager.wait_for_application(app_name, timeout=10.0):
            return False
        
        # Wait a bit more for UI to stabilize
        time.sleep(2.0)
        return True
    
    def _execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute a generic action from dictionary."""
        action_type = action.get('type')
        
        if action_type == 'click':
            return self.asq.click_if_exists(action['selector'], timeout=action.get('timeout', 5.0))
        elif action_type == 'type':
            return self.asq.type_if_exists(action['selector'], action['text'], timeout=action.get('timeout', 5.0))
        elif action_type == 'wait':
            return self.asq.wait_for_element(action['selector'], timeout=action.get('timeout', 10.0))
        elif action_type == 'custom':
            # Execute custom function
            func = action.get('function')
            if func and callable(func):
                return func(*action.get('args', []), **action.get('kwargs', {}))
        
        return False