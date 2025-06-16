"""
Advanced selectors module for ASQ integration.
Provides sophisticated CSS-like selectors with pseudo-selectors and spatial queries.
"""

import re
import platform
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass


@dataclass
class SelectorPart:
    """Represents a part of a CSS selector."""
    element_type: Optional[str] = None
    attributes: Dict[str, str] = None
    pseudo_selectors: List[str] = None
    spatial_relation: Optional[str] = None
    spatial_target: Optional[str] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
        if self.pseudo_selectors is None:
            self.pseudo_selectors = []


class AdvancedSelectorParser:
    """Parser for advanced CSS-like selectors."""
    
    # Attribute operators
    ATTR_OPERATORS = {
        '=': lambda val, target: val == target,
        '!=': lambda val, target: val != target,
        '^=': lambda val, target: val.startswith(target),
        '$=': lambda val, target: val.endswith(target),
        '*=': lambda val, target: target in val,
        '~=': lambda val, target: target in val.split(),
        '|=': lambda val, target: val == target or val.startswith(target + '-')
    }
    
    # Pseudo-selectors
    PSEUDO_SELECTORS = {
        'visible': lambda elem: getattr(elem, 'visible', True),
        'hidden': lambda elem: not getattr(elem, 'visible', True),
        'enabled': lambda elem: getattr(elem, 'enabled', True),
        'disabled': lambda elem: not getattr(elem, 'enabled', True),
        'focused': lambda elem: getattr(elem, 'focused', False),
        'selected': lambda elem: getattr(elem, 'selected', False),
        'checked': lambda elem: getattr(elem, 'checked', False),
        'empty': lambda elem: not getattr(elem, 'text', '').strip(),
        'first': lambda elem: True,  # Would need context to implement properly
        'last': lambda elem: True,   # Would need context to implement properly
    }
    
    # Spatial relations
    SPATIAL_RELATIONS = {
        'near': 'within_distance',
        'above': 'is_above',
        'below': 'is_below',
        'left_of': 'is_left_of',
        'right_of': 'is_right_of',
        'inside': 'is_inside',
        'contains': 'contains'
    }
    
    def __init__(self):
        """Initialize selector parser."""
        self._available = platform.system() == 'Linux'
    
    def parse(self, selector: str) -> List[SelectorPart]:
        """Parse a CSS-like selector into parts.
        
        Args:
            selector: CSS-like selector string
            
        Returns:
            List of selector parts
            
        Examples:
            'button[name="Save"]:visible' -> button with name Save that is visible
            'text[name*="search"]:enabled' -> text field with search in name that is enabled
            'dialog near button[name="OK"]' -> dialog near OK button
        """
        if not self._available:
            raise RuntimeError("Advanced selectors only available on Linux systems")
        
        # Split by combinators (space, >, +, ~)
        parts = []
        current_selector = selector.strip()
        
        # Handle spatial relations first
        spatial_match = re.search(r'\s+(near|above|below|left_of|right_of|inside|contains)\s+', current_selector)
        if spatial_match:
            main_part = current_selector[:spatial_match.start()].strip()
            spatial_relation = spatial_match.group(1)
            spatial_target = current_selector[spatial_match.end():].strip()
            
            main_selector_part = self._parse_single_selector(main_part)
            main_selector_part.spatial_relation = spatial_relation
            main_selector_part.spatial_target = spatial_target
            parts.append(main_selector_part)
        else:
            # Parse as regular selector
            parts.append(self._parse_single_selector(current_selector))
        
        return parts
    
    def _parse_single_selector(self, selector: str) -> SelectorPart:
        """Parse a single selector part.
        
        Args:
            selector: Single selector string
            
        Returns:
            Parsed selector part
        """
        part = SelectorPart()
        
        # Extract pseudo-selectors
        pseudo_pattern = r':([a-zA-Z_][a-zA-Z0-9_-]*)'
        pseudo_matches = re.findall(pseudo_pattern, selector)
        part.pseudo_selectors = pseudo_matches
        
        # Remove pseudo-selectors from main selector
        main_selector = re.sub(pseudo_pattern, '', selector)
        
        # Extract attributes
        attr_pattern = r'\[([^=\]]+)(([!^$*~|]?=)"?([^"\]]+)"?)\]'
        attr_matches = re.findall(attr_pattern, main_selector)
        
        for match in attr_matches:
            attr_name = match[0]
            operator = match[2] if match[2] else '='
            attr_value = match[3]
            part.attributes[attr_name] = (operator, attr_value)
        
        # Remove attributes from main selector
        main_selector = re.sub(r'\[[^\]]+\]', '', main_selector)
        
        # What's left is the element type
        element_type = main_selector.strip()
        if element_type:
            part.element_type = element_type
        
        return part
    
    def matches_element(self, element: Any, selector_part: SelectorPart) -> bool:
        """Check if an element matches a selector part.
        
        Args:
            element: Element to check
            selector_part: Selector part to match against
            
        Returns:
            True if element matches the selector part
        """
        # Check element type
        if selector_part.element_type:
            element_role = getattr(element, 'role', '').lower()
            if selector_part.element_type.lower() not in element_role:
                return False
        
        # Check attributes
        for attr_name, (operator, attr_value) in selector_part.attributes.items():
            element_value = str(getattr(element, attr_name, ''))
            
            if operator in self.ATTR_OPERATORS:
                if not self.ATTR_OPERATORS[operator](element_value, attr_value):
                    return False
            else:
                # Default to exact match
                if element_value != attr_value:
                    return False
        
        # Check pseudo-selectors
        for pseudo in selector_part.pseudo_selectors:
            if pseudo in self.PSEUDO_SELECTORS:
                if not self.PSEUDO_SELECTORS[pseudo](element):
                    return False
        
        return True
    
    def find_with_spatial_relation(self, elements: List[Any], selector_part: SelectorPart) -> List[Any]:
        """Find elements with spatial relations.
        
        Args:
            elements: List of elements to search
            selector_part: Selector part with spatial relation
            
        Returns:
            List of matching elements
        """
        if not selector_part.spatial_relation or not selector_part.spatial_target:
            return elements
        
        # Parse target selector
        target_parts = self.parse(selector_part.spatial_target)
        target_elements = []
        
        # Find target elements
        for element in elements:
            for target_part in target_parts:
                if self.matches_element(element, target_part):
                    target_elements.append(element)
        
        if not target_elements:
            return []
        
        # Find elements with spatial relation to targets
        matching_elements = []
        relation = selector_part.spatial_relation
        
        for element in elements:
            if self.matches_element(element, selector_part):
                for target in target_elements:
                    if self._check_spatial_relation(element, target, relation):
                        matching_elements.append(element)
                        break
        
        return matching_elements
    
    def _check_spatial_relation(self, element: Any, target: Any, relation: str) -> bool:
        """Check spatial relation between two elements.
        
        Args:
            element: First element
            target: Target element
            relation: Spatial relation type
            
        Returns:
            True if relation exists
        """
        # Get element positions and sizes
        elem_pos = getattr(element, 'position', (0, 0))
        elem_size = getattr(element, 'size', (0, 0))
        target_pos = getattr(target, 'position', (0, 0))
        target_size = getattr(target, 'size', (0, 0))
        
        elem_rect = (elem_pos[0], elem_pos[1], elem_pos[0] + elem_size[0], elem_pos[1] + elem_size[1])
        target_rect = (target_pos[0], target_pos[1], target_pos[0] + target_size[0], target_pos[1] + target_size[1])
        
        if relation == 'near':
            return self._is_near(elem_rect, target_rect)
        elif relation == 'above':
            return elem_rect[3] <= target_rect[1]  # element bottom <= target top
        elif relation == 'below':
            return elem_rect[1] >= target_rect[3]  # element top >= target bottom
        elif relation == 'left_of':
            return elem_rect[2] <= target_rect[0]  # element right <= target left
        elif relation == 'right_of':
            return elem_rect[0] >= target_rect[2]  # element left >= target right
        elif relation == 'inside':
            return (elem_rect[0] >= target_rect[0] and elem_rect[1] >= target_rect[1] and
                    elem_rect[2] <= target_rect[2] and elem_rect[3] <= target_rect[3])
        elif relation == 'contains':
            return (target_rect[0] >= elem_rect[0] and target_rect[1] >= elem_rect[1] and
                    target_rect[2] <= elem_rect[2] and target_rect[3] <= elem_rect[3])
        
        return False
    
    def _is_near(self, rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int], threshold: int = 50) -> bool:
        """Check if two rectangles are near each other.
        
        Args:
            rect1: First rectangle (x1, y1, x2, y2)
            rect2: Second rectangle (x1, y1, x2, y2)
            threshold: Distance threshold in pixels
            
        Returns:
            True if rectangles are near each other
        """
        # Calculate minimum distance between rectangles
        x_dist = max(0, max(rect1[0] - rect2[2], rect2[0] - rect1[2]))
        y_dist = max(0, max(rect1[1] - rect2[3], rect2[1] - rect1[3]))
        distance = (x_dist ** 2 + y_dist ** 2) ** 0.5
        
        return distance <= threshold


class SelectorOptimizer:
    """Optimizer for selector performance."""
    
    def __init__(self):
        """Initialize selector optimizer."""
        self.selector_cache = {}
        self.performance_stats = {}
    
    def optimize_selector(self, selector: str) -> str:
        """Optimize a selector for better performance.
        
        Args:
            selector: Original selector
            
        Returns:
            Optimized selector
        """
        # Cache parsed selectors
        if selector in self.selector_cache:
            return self.selector_cache[selector]
        
        # Simple optimizations
        optimized = selector.strip()
        
        # Remove redundant spaces
        optimized = re.sub(r'\s+', ' ', optimized)
        
        # Reorder attributes for better performance (specific first)
        # This would be more sophisticated in a real implementation
        
        self.selector_cache[selector] = optimized
        return optimized
    
    def get_selector_complexity(self, selector: str) -> int:
        """Calculate selector complexity score.
        
        Args:
            selector: Selector to analyze
            
        Returns:
            Complexity score (higher = more complex)
        """
        complexity = 0
        
        # Count attributes
        complexity += len(re.findall(r'\[[^\]]+\]', selector))
        
        # Count pseudo-selectors
        complexity += len(re.findall(r':[a-zA-Z_][a-zA-Z0-9_-]*', selector))
        
        # Count spatial relations
        spatial_relations = ['near', 'above', 'below', 'left_of', 'right_of', 'inside', 'contains']
        for relation in spatial_relations:
            if relation in selector:
                complexity += 2  # Spatial relations are more expensive
        
        return complexity


# Global instances
selector_parser = AdvancedSelectorParser()
selector_optimizer = SelectorOptimizer()


def parse_selector(selector: str) -> List[SelectorPart]:
    """Parse a CSS-like selector.
    
    Args:
        selector: Selector string to parse
        
    Returns:
        List of parsed selector parts
    """
    return selector_parser.parse(selector)


def optimize_selector(selector: str) -> str:
    """Optimize a selector for performance.
    
    Args:
        selector: Selector to optimize
        
    Returns:
        Optimized selector
    """
    return selector_optimizer.optimize_selector(selector)


def get_selector_examples() -> Dict[str, str]:
    """Get examples of advanced selectors.
    
    Returns:
        Dictionary mapping selector types to examples
    """
    return {
        'basic': 'button[name="Save"]',
        'pseudo': 'button:visible:enabled',
        'attribute_operators': 'text[name^="search"]',  # starts with
        'multiple_attributes': 'button[name="OK"][role="button"]',
        'spatial_near': 'label near text[name="username"]',
        'spatial_above': 'button above text[name="password"]',
        'spatial_inside': 'button inside dialog[name="Settings"]',
        'complex': 'button[name*="save"]:visible near text[name^="file"]:enabled'
    }