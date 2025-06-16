"""
OCR (Optical Character Recognition) module for ASQ integration.
Provides text extraction from images and screen captures.
"""

import os
import tempfile
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OCRResult:
    """Result from OCR text extraction."""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    words: List[Dict[str, Any]]
    lines: List[Dict[str, Any]]


class OCRProcessor:
    """OCR functionality for text extraction from images."""
    
    def __init__(self, asq_instance):
        """Initialize OCR processor.
        
        Args:
            asq_instance: Reference to main ASQ instance
        """
        self.asq = asq_instance
        self._available_engines = self._detect_ocr_engines()
        self._temp_dir = Path(tempfile.gettempdir()) / "asq_ocr"
        self._temp_dir.mkdir(exist_ok=True)
    
    def _detect_ocr_engines(self) -> List[str]:
        """Detect available OCR engines."""
        engines = []
        
        # Check for pytesseract
        try:
            import pytesseract
            import PIL
            engines.append('tesseract')
        except ImportError:
            pass
        
        # Check for easyocr
        try:
            import easyocr
            engines.append('easyocr')
        except ImportError:
            pass
        
        # Check for paddleocr
        try:
            import paddleocr
            engines.append('paddleocr')
        except ImportError:
            pass
        
        # Check for system tesseract
        import subprocess
        try:
            subprocess.run(['tesseract', '--version'], 
                          capture_output=True, check=True)
            if 'tesseract' not in engines:
                engines.append('tesseract_system')
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return engines
    
    def extract_text_from_image(self, image_path: str, 
                               engine: Optional[str] = None,
                               language: str = 'eng') -> Optional[OCRResult]:
        """Extract text from an image file.
        
        Args:
            image_path: Path to image file
            engine: OCR engine to use ('tesseract', 'easyocr', 'paddleocr')
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        if not os.path.exists(image_path):
            if self.asq.computer.verbose:
                print(f"Image file not found: {image_path}")
            return None
        
        # Use first available engine if none specified
        if not engine:
            if not self._available_engines:
                if self.asq.computer.verbose:
                    print("No OCR engines available")
                return None
            engine = self._available_engines[0]
        
        if engine not in self._available_engines:
            if self.asq.computer.verbose:
                print(f"OCR engine '{engine}' not available")
            return None
        
        try:
            if engine == 'tesseract':
                return self._extract_with_tesseract(image_path, language)
            elif engine == 'easyocr':
                return self._extract_with_easyocr(image_path, language)
            elif engine == 'paddleocr':
                return self._extract_with_paddleocr(image_path, language)
            elif engine == 'tesseract_system':
                return self._extract_with_tesseract_system(image_path, language)
            else:
                if self.asq.computer.verbose:
                    print(f"Unknown OCR engine: {engine}")
                return None
                
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting text with {engine}: {e}")
            return None
    
    def _extract_with_tesseract(self, image_path: str, language: str) -> Optional[OCRResult]:
        """Extract text using pytesseract."""
        try:
            import pytesseract
            from PIL import Image
            
            with Image.open(image_path) as img:
                # Get text
                text = pytesseract.image_to_string(img, lang=language)
                
                # Get detailed data
                data = pytesseract.image_to_data(img, lang=language, output_type=pytesseract.Output.DICT)
                
                # Process bounding boxes and words
                words = []
                lines = []
                bounding_boxes = []
                
                for i in range(len(data['text'])):
                    if int(data['conf'][i]) > 0:  # Only include confident detections
                        word_info = {
                            'text': data['text'][i],
                            'confidence': float(data['conf'][i]) / 100.0,
                            'bbox': (data['left'][i], data['top'][i], 
                                   data['width'][i], data['height'][i])
                        }
                        words.append(word_info)
                        bounding_boxes.append(word_info['bbox'])
                
                # Calculate overall confidence
                confidences = [w['confidence'] for w in words if w['confidence'] > 0]
                overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                return OCRResult(
                    text=text.strip(),
                    confidence=overall_confidence,
                    bounding_boxes=bounding_boxes,
                    words=words,
                    lines=lines
                )
                
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Tesseract OCR error: {e}")
            return None
    
    def _extract_with_easyocr(self, image_path: str, language: str) -> Optional[OCRResult]:
        """Extract text using EasyOCR."""
        try:
            import easyocr
            
            # Map language codes
            lang_map = {'eng': 'en', 'fra': 'fr', 'deu': 'de', 'spa': 'es'}
            lang_code = lang_map.get(language, language)
            
            reader = easyocr.Reader([lang_code])
            results = reader.readtext(image_path)
            
            words = []
            bounding_boxes = []
            text_parts = []
            confidences = []
            
            for bbox, text, confidence in results:
                # Convert bbox format
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                width = x2 - x1
                height = y2 - y1
                
                word_info = {
                    'text': text,
                    'confidence': confidence,
                    'bbox': (int(x1), int(y1), int(width), int(height))
                }
                words.append(word_info)
                bounding_boxes.append(word_info['bbox'])
                text_parts.append(text)
                confidences.append(confidence)
            
            overall_text = ' '.join(text_parts)
            overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=overall_text,
                confidence=overall_confidence,
                bounding_boxes=bounding_boxes,
                words=words,
                lines=[]
            )
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"EasyOCR error: {e}")
            return None
    
    def _extract_with_paddleocr(self, image_path: str, language: str) -> Optional[OCRResult]:
        """Extract text using PaddleOCR."""
        try:
            from paddleocr import PaddleOCR
            
            # Map language codes
            lang_map = {'eng': 'en', 'fra': 'fr', 'deu': 'german', 'spa': 'es'}
            lang_code = lang_map.get(language, 'en')
            
            ocr = PaddleOCR(use_angle_cls=True, lang=lang_code, show_log=False)
            results = ocr.ocr(image_path, cls=True)
            
            words = []
            bounding_boxes = []
            text_parts = []
            confidences = []
            
            if results and results[0]:
                for line in results[0]:
                    bbox, (text, confidence) = line
                    
                    # Convert bbox format
                    x1, y1 = bbox[0]
                    x2, y2 = bbox[2]
                    width = x2 - x1
                    height = y2 - y1
                    
                    word_info = {
                        'text': text,
                        'confidence': confidence,
                        'bbox': (int(x1), int(y1), int(width), int(height))
                    }
                    words.append(word_info)
                    bounding_boxes.append(word_info['bbox'])
                    text_parts.append(text)
                    confidences.append(confidence)
            
            overall_text = ' '.join(text_parts)
            overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return OCRResult(
                text=overall_text,
                confidence=overall_confidence,
                bounding_boxes=bounding_boxes,
                words=words,
                lines=[]
            )
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"PaddleOCR error: {e}")
            return None
    
    def _extract_with_tesseract_system(self, image_path: str, language: str) -> Optional[OCRResult]:
        """Extract text using system tesseract command."""
        try:
            import subprocess
            
            # Create temporary output file
            temp_output = self._temp_dir / f"ocr_output_{int(time.time())}.txt"
            
            # Run tesseract
            result = subprocess.run([
                'tesseract', image_path, str(temp_output.with_suffix('')), 
                '-l', language
            ], capture_output=True, text=True, check=True)
            
            if result.returncode == 0 and temp_output.exists():
                with open(temp_output, 'r', encoding='utf-8') as f:
                    text = f.read().strip()
                
                # Clean up
                temp_output.unlink()
                
                return OCRResult(
                    text=text,
                    confidence=0.8,  # Default confidence for system tesseract
                    bounding_boxes=[],
                    words=[],
                    lines=[]
                )
            
            return None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"System tesseract error: {e}")
            return None
    
    def extract_text_from_screen(self, region: Optional[Tuple[int, int, int, int]] = None,
                                engine: Optional[str] = None,
                                language: str = 'eng') -> Optional[OCRResult]:
        """Extract text from screen or screen region.
        
        Args:
            region: Optional (x, y, width, height) region to capture
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        try:
            # Take screenshot
            if hasattr(self.asq, 'screen_capture'):
                screenshot = self.asq.screen_capture.take_screenshot(return_base64=False)
            else:
                # Fallback to basic screenshot
                screenshot = None
                
            if not screenshot:
                if self.asq.computer.verbose:
                    print("Could not take screenshot for OCR")
                return None
            
            image_path = screenshot.path
            
            # Crop to region if specified
            if region:
                if hasattr(self.asq, 'screen_capture'):
                    cropped_path = self.asq.screen_capture._crop_image(image_path, region)
                    if cropped_path:
                        image_path = cropped_path
            
            # Extract text from image
            return self.extract_text_from_image(image_path, engine, language)
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting text from screen: {e}")
            return None
    
    def extract_text_from_element(self, selector: str,
                                 engine: Optional[str] = None,
                                 language: str = 'eng') -> Optional[OCRResult]:
        """Extract text from a specific element using OCR.
        
        Args:
            selector: Element selector
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            OCRResult object or None if failed
        """
        try:
            # Take screenshot of element
            if hasattr(self.asq, 'screen_capture'):
                element_screenshot = self.asq.screen_capture.take_element_screenshot(
                    selector, return_base64=False
                )
            else:
                element_screenshot = None
                
            if not element_screenshot:
                if self.asq.computer.verbose:
                    print(f"Could not take screenshot of element: {selector}")
                return None
            
            # Extract text from element screenshot
            return self.extract_text_from_image(element_screenshot.path, engine, language)
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error extracting text from element '{selector}': {e}")
            return None
    
    def find_text_in_image(self, image_path: str, search_text: str,
                          engine: Optional[str] = None,
                          language: str = 'eng',
                          case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Find specific text in an image.
        
        Args:
            image_path: Path to image file
            search_text: Text to search for
            engine: OCR engine to use
            language: Language code for OCR
            case_sensitive: Whether search should be case sensitive
            
        Returns:
            List of matches with bounding box information
        """
        try:
            ocr_result = self.extract_text_from_image(image_path, engine, language)
            if not ocr_result:
                return []
            
            matches = []
            search_lower = search_text.lower() if not case_sensitive else search_text
            
            for word in ocr_result.words:
                word_text = word['text']
                word_lower = word_text.lower() if not case_sensitive else word_text
                
                if search_lower in word_lower:
                    matches.append({
                        'text': word_text,
                        'bbox': word['bbox'],
                        'confidence': word['confidence'],
                        'match_type': 'partial' if search_lower != word_lower else 'exact'
                    })
            
            return matches
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error finding text in image: {e}")
            return []
    
    def get_text_at_position(self, x: int, y: int, 
                            region_size: int = 100,
                            engine: Optional[str] = None,
                            language: str = 'eng') -> Optional[str]:
        """Get text at a specific screen position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            region_size: Size of region around position to capture
            engine: OCR engine to use
            language: Language code for OCR
            
        Returns:
            Text found at position or None
        """
        try:
            # Define region around position
            half_size = region_size // 2
            region = (x - half_size, y - half_size, region_size, region_size)
            
            # Extract text from region
            ocr_result = self.extract_text_from_screen(region, engine, language)
            if ocr_result and ocr_result.text:
                return ocr_result.text.strip()
            
            return None
            
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error getting text at position ({x}, {y}): {e}")
            return None
    
    def validate_text_quality(self, ocr_result: OCRResult, 
                             min_confidence: float = 0.5) -> Dict[str, Any]:
        """Validate the quality of OCR results.
        
        Args:
            ocr_result: OCR result to validate
            min_confidence: Minimum confidence threshold
            
        Returns:
            Dictionary with quality metrics
        """
        if not ocr_result:
            return {
                'is_valid': False,
                'confidence': 0.0,
                'word_count': 0,
                'issues': ['No OCR result']
            }
        
        issues = []
        
        # Check overall confidence
        if ocr_result.confidence < min_confidence:
            issues.append(f'Low confidence: {ocr_result.confidence:.2f}')
        
        # Check for empty text
        if not ocr_result.text.strip():
            issues.append('No text extracted')
        
        # Check word count
        word_count = len(ocr_result.text.split())
        if word_count == 0:
            issues.append('No words found')
        
        # Check for suspicious characters
        suspicious_chars = sum(1 for c in ocr_result.text if ord(c) > 127)
        if suspicious_chars > len(ocr_result.text) * 0.1:
            issues.append('High number of non-ASCII characters')
        
        return {
            'is_valid': len(issues) == 0,
            'confidence': ocr_result.confidence,
            'word_count': word_count,
            'character_count': len(ocr_result.text),
            'suspicious_character_ratio': suspicious_chars / len(ocr_result.text) if ocr_result.text else 0,
            'issues': issues
        }
    
    def get_available_engines(self) -> List[str]:
        """Get list of available OCR engines.
        
        Returns:
            List of available engine names
        """
        return self._available_engines.copy()
    
    def get_supported_languages(self, engine: Optional[str] = None) -> List[str]:
        """Get list of supported languages for an OCR engine.
        
        Args:
            engine: OCR engine name
            
        Returns:
            List of supported language codes
        """
        # Common language codes supported by most OCR engines
        common_languages = [
            'eng', 'fra', 'deu', 'spa', 'ita', 'por', 'rus', 'chi_sim', 'chi_tra',
            'jpn', 'kor', 'ara', 'hin', 'tha', 'vie', 'nld', 'swe', 'nor', 'dan'
        ]
        
        if not engine or engine not in self._available_engines:
            return common_languages
        
        try:
            if engine == 'tesseract':
                import pytesseract
                return pytesseract.get_languages()
            elif engine == 'tesseract_system':
                import subprocess
                result = subprocess.run(['tesseract', '--list-langs'], 
                                      capture_output=True, text=True, check=True)
                if result.returncode == 0:
                    languages = result.stdout.strip().split('\n')[1:]  # Skip header
                    return languages
        except Exception:
            pass
        
        return common_languages
    
    def cleanup_temp_files(self):
        """Clean up temporary OCR files."""
        try:
            if self._temp_dir.exists():
                for file_path in self._temp_dir.glob("*"):
                    try:
                        file_path.unlink()
                    except Exception as e:
                        if self.asq.computer.verbose:
                            print(f"Error removing temp file {file_path}: {e}")
        except Exception as e:
            if self.asq.computer.verbose:
                print(f"Error cleaning up OCR temp files: {e}")