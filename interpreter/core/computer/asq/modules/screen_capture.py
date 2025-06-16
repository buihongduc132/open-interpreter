"""
Screen capture module for ASQ integration.
Provides methods for taking screenshots and visual verification.
"""

import os
import base64
import tempfile
import time
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScreenshotInfo:
    """Information about a screenshot."""
    path: str
    base64_data: str
    width: int
    height: int
    timestamp: float
    element_bounds: Optional[Tuple[int, int, int, int]] = None


class ScreenCapture:
    """Screen capture functionality for desktop automation."""
    
    def __init__(self, asq_instance):
        """Initialize screen capture.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._screenshot_dir = None
        self._setup_screenshot_dir()
        self._available_backends = self._detect_backends()
    
    def _setup_screenshot_dir(self):
        """Setup directory for storing screenshots."""
        try:
            self._screenshot_dir = Path(tempfile.gettempdir()) / "asq_screenshots"
            self._screenshot_dir.mkdir(exist_ok=True)
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Warning: Could not setup screenshot directory: {e}")
            self._screenshot_dir = None
    
    def _detect_backends(self) -> List[str]:
        """Detect available screenshot backends."""
        backends = []
        
        try:
            import PIL.ImageGrab
            backends.append('pil')
        except ImportError:
            pass
        
        try:
            import pyautogui
            backends.append('pyautogui')
        except ImportError:
            pass
        
        # Check for system tools
        import subprocess
        try:
            subprocess.run(['gnome-screenshot', '--version'], 
                          capture_output=True, check=True)
            backends.append('gnome-screenshot')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            subprocess.run(['scrot', '--version'], 
                          capture_output=True, check=True)
            backends.append('scrot')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        try:
            subprocess.run(['import', '-version'], 
                          capture_output=True, check=True)
            backends.append('imagemagick')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return backends
    
    def take_screenshot(self, save_path: Optional[str] = None, 
                       return_base64: bool = True) -> Optional[ScreenshotInfo]:
        """Take a screenshot of the entire screen.
        
        Args:
            save_path: Optional path to save screenshot
            return_base64: Whether to include base64 data in result
            
        Returns:
            ScreenshotInfo object or None if failed
        """
        try:
            # Generate filename if not provided
            if not save_path:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
                if self._screenshot_dir:
                    save_path = str(self._screenshot_dir / filename)
                else:
                    save_path = filename
            
            # Try different backends
            success = False
            
            # Try PIL first (most reliable)
            if 'pil' in self._available_backends:
                success = self._take_screenshot_pil(save_path)
            
            # Try pyautogui
            elif 'pyautogui' in self._available_backends:
                success = self._take_screenshot_pyautogui(save_path)
            
            # Try system tools
            elif 'gnome-screenshot' in self._available_backends:
                success = self._take_screenshot_gnome(save_path)
            
            elif 'scrot' in self._available_backends:
                success = self._take_screenshot_scrot(save_path)
            
            elif 'imagemagick' in self._available_backends:
                success = self._take_screenshot_imagemagick(save_path)
            
            if not success:
                if self.asq.computer.verbose:
                    print("No screenshot backend available")
                return None
            
            # Get image info
            width, height = self._get_image_dimensions(save_path)
            
            # Get base64 data if requested
            base64_data = ""
            if return_base64:
                base64_data = self._image_to_base64(save_path)
            
            return ScreenshotInfo(
                path=save_path,
                base64_data=base64_data,
                width=width,
                height=height,
                timestamp=time.time()
            )
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error taking screenshot: {e}")
            return None
    
    def _take_screenshot_pil(self, save_path: str) -> bool:
        """Take screenshot using PIL."""
        try:
            from PIL import ImageGrab
            screenshot = ImageGrab.grab()
            screenshot.save(save_path)
            return True
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"PIL screenshot failed: {e}")
            return False
    
    def _take_screenshot_pyautogui(self, save_path: str) -> bool:
        """Take screenshot using pyautogui."""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)
            return True
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"pyautogui screenshot failed: {e}")
            return False
    
    def _take_screenshot_gnome(self, save_path: str) -> bool:
        """Take screenshot using gnome-screenshot."""
        try:
            import subprocess
            result = subprocess.run([
                'gnome-screenshot', '-f', save_path
            ], capture_output=True, check=True)
            return result.returncode == 0
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"gnome-screenshot failed: {e}")
            return False
    
    def _take_screenshot_scrot(self, save_path: str) -> bool:
        """Take screenshot using scrot."""
        try:
            import subprocess
            result = subprocess.run([
                'scrot', save_path
            ], capture_output=True, check=True)
            return result.returncode == 0
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"scrot failed: {e}")
            return False
    
    def _take_screenshot_imagemagick(self, save_path: str) -> bool:
        """Take screenshot using ImageMagick import."""
        try:
            import subprocess
            result = subprocess.run([
                'import', '-window', 'root', save_path
            ], capture_output=True, check=True)
            return result.returncode == 0
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"ImageMagick screenshot failed: {e}")
            return False
    
    def take_element_screenshot(self, selector: str, 
                               save_path: Optional[str] = None,
                               return_base64: bool = True) -> Optional[ScreenshotInfo]:
        """Take a screenshot of a specific element.
        
        Args:
            selector: Element selector
            save_path: Optional path to save screenshot
            return_base64: Whether to include base64 data in result
            
        Returns:
            ScreenshotInfo object or None if failed
        """
        try:
            element = self.asq.find(selector)
            if not element or not element.exists():
                if self.asq.computer.verbose:
                    print(f"Element not found for screenshot: {selector}")
                return None
            
            # Get element bounds (placeholder - would need actual implementation)
            # This would require getting the actual element position and size
            bounds = (0, 0, 100, 100)  # x, y, width, height
            
            # Take full screenshot first
            full_screenshot = self.take_screenshot(return_base64=False)
            if not full_screenshot:
                return None
            
            # Crop to element bounds
            cropped_path = self._crop_image(full_screenshot.path, bounds, save_path)
            if not cropped_path:
                return None
            
            # Get cropped image info
            width, height = self._get_image_dimensions(cropped_path)
            
            # Get base64 data if requested
            base64_data = ""
            if return_base64:
                base64_data = self._image_to_base64(cropped_path)
            
            return ScreenshotInfo(
                path=cropped_path,
                base64_data=base64_data,
                width=width,
                height=height,
                timestamp=time.time(),
                element_bounds=bounds
            )
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error taking element screenshot '{selector}': {e}")
            return None
    
    def _crop_image(self, image_path: str, bounds: Tuple[int, int, int, int], 
                   save_path: Optional[str] = None) -> Optional[str]:
        """Crop an image to specified bounds.
        
        Args:
            image_path: Path to source image
            bounds: (x, y, width, height) bounds
            save_path: Optional path to save cropped image
            
        Returns:
            Path to cropped image or None if failed
        """
        try:
            if not save_path:
                timestamp = int(time.time())
                filename = f"cropped_{timestamp}.png"
                if self._screenshot_dir:
                    save_path = str(self._screenshot_dir / filename)
                else:
                    save_path = filename
            
            # Try PIL first
            if 'pil' in self._available_backends:
                from PIL import Image
                with Image.open(image_path) as img:
                    x, y, width, height = bounds
                    cropped = img.crop((x, y, x + width, y + height))
                    cropped.save(save_path)
                    return save_path
            
            # Try ImageMagick
            elif 'imagemagick' in self._available_backends:
                import subprocess
                x, y, width, height = bounds
                result = subprocess.run([
                    'convert', image_path, 
                    '-crop', f'{width}x{height}+{x}+{y}',
                    save_path
                ], capture_output=True, check=True)
                if result.returncode == 0:
                    return save_path
            
            return None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error cropping image: {e}")
            return None
    
    def _get_image_dimensions(self, image_path: str) -> Tuple[int, int]:
        """Get image dimensions.
        
        Args:
            image_path: Path to image
            
        Returns:
            (width, height) tuple
        """
        try:
            if 'pil' in self._available_backends:
                from PIL import Image
                with Image.open(image_path) as img:
                    return img.size
            
            # Try ImageMagick identify
            import subprocess
            result = subprocess.run([
                'identify', '-format', '%wx%h', image_path
            ], capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                dimensions = result.stdout.strip().split('x')
                return int(dimensions[0]), int(dimensions[1])
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error getting image dimensions: {e}")
        
        return 0, 0
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string.
        
        Args:
            image_path: Path to image
            
        Returns:
            Base64 encoded image data
        """
        try:
            with open(image_path, 'rb') as img_file:
                return base64.b64encode(img_file.read()).decode('utf-8')
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error converting image to base64: {e}")
            return ""
    
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
        try:
            if 'pil' in self._available_backends:
                from PIL import Image
                import numpy as np
                
                # Load images
                with Image.open(image1_path) as img1, Image.open(image2_path) as img2:
                    # Resize to same dimensions if different
                    if img1.size != img2.size:
                        img2 = img2.resize(img1.size)
                    
                    # Convert to arrays
                    arr1 = np.array(img1)
                    arr2 = np.array(img2)
                    
                    # Calculate similarity
                    diff = np.abs(arr1.astype(float) - arr2.astype(float))
                    similarity = 1.0 - (np.mean(diff) / 255.0)
                    
                    return {
                        'similarity': similarity,
                        'is_similar': similarity >= threshold,
                        'threshold': threshold,
                        'difference_percentage': (1.0 - similarity) * 100
                    }
            
            # Fallback: basic file size comparison
            size1 = os.path.getsize(image1_path)
            size2 = os.path.getsize(image2_path)
            size_diff = abs(size1 - size2) / max(size1, size2)
            similarity = 1.0 - size_diff
            
            return {
                'similarity': similarity,
                'is_similar': similarity >= threshold,
                'threshold': threshold,
                'difference_percentage': size_diff * 100,
                'method': 'file_size_comparison'
            }
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error comparing screenshots: {e}")
            return {
                'similarity': 0.0,
                'is_similar': False,
                'threshold': threshold,
                'error': str(e)
            }
    
    def wait_for_visual_change(self, timeout: float = 10.0, 
                              check_interval: float = 1.0) -> bool:
        """Wait for visual change on screen.
        
        Args:
            timeout: Maximum time to wait
            check_interval: How often to check for changes
            
        Returns:
            True if visual change detected
        """
        try:
            # Take initial screenshot
            initial_screenshot = self.take_screenshot(return_base64=False)
            if not initial_screenshot:
                return False
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(check_interval)
                
                # Take new screenshot
                current_screenshot = self.take_screenshot(return_base64=False)
                if not current_screenshot:
                    continue
                
                # Compare screenshots
                comparison = self.compare_screenshots(
                    initial_screenshot.path, 
                    current_screenshot.path,
                    threshold=0.95
                )
                
                if not comparison.get('is_similar', True):
                    return True
            
            return False
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error waiting for visual change: {e}")
            return False
    
    def verify_element_visible(self, selector: str) -> bool:
        """Verify an element is visually present on screen.
        
        Args:
            selector: Element selector
            
        Returns:
            True if element is visible
        """
        try:
            # Take screenshot of element
            element_screenshot = self.take_element_screenshot(selector, return_base64=False)
            return element_screenshot is not None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error verifying element visibility '{selector}': {e}")
            return False
    
    def get_available_backends(self) -> List[str]:
        """Get list of available screenshot backends.
        
        Returns:
            List of available backend names
        """
        return self._available_backends.copy()
    
    def cleanup_screenshots(self, older_than_hours: int = 24):
        """Clean up old screenshot files.
        
        Args:
            older_than_hours: Remove files older than this many hours
        """
        try:
            if not self._screenshot_dir or not self._screenshot_dir.exists():
                return
            
            cutoff_time = time.time() - (older_than_hours * 3600)
            
            for file_path in self._screenshot_dir.glob("*.png"):
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                except Exception as e:
                    if self.asq.computer.verbose:
                        print(f"Error removing old screenshot {file_path}: {e}")
                        
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error cleaning up screenshots: {e}")