#!/usr/bin/env python3
"""
Demonstration of ASQ module usage in open-interpreter.

This script shows how to use the ASQ module for GUI automation tasks.
Note: This requires a Linux system with AT-SPI libraries installed.
"""

import sys
import platform

# Add the interpreter path to sys.path
sys.path.insert(0, '/workspace')

def demo_asq_usage():
    """Demonstrate ASQ module usage."""
    print("ASQ Module Usage Demonstration")
    print("=" * 50)
    
    try:
        from interpreter.core.computer.computer import Computer
        
        # Create a mock interpreter object
        class MockInterpreter:
            max_output = 1000
        
        mock_interpreter = MockInterpreter()
        computer = Computer(mock_interpreter)
        
        print("✓ Computer instance created with ASQ module")
        print(f"Platform: {platform.system()}")
        
        # Show available ASQ methods
        print(f"\nAvailable ASQ methods: {len([m for m in dir(computer.asq) if not m.startswith('_') and callable(getattr(computer.asq, m))])}")
        
        # Group methods by category
        basic_methods = ['find', 'click_button', 'type_text', 'wait_for_element']
        form_methods = ['fill_form', 'submit_form', 'clear_form']
        window_methods = ['get_active_window', 'list_windows', 'focus_window', 'close_window']
        advanced_methods = ['find_optimized', 'find_advanced', 'find_by_text', 'find_by_role', 'find_in_window']
        utility_methods = ['click_if_exists', 'type_if_exists', 'get_text_if_exists']
        performance_methods = ['get_performance_stats', 'get_performance_report', 'clear_cache']
        
        print("\n📋 Basic GUI Automation:")
        for method in basic_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\n📝 Form Automation:")
        for method in form_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\n🪟 Window Management:")
        for method in window_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\n🔍 Advanced Finding:")
        for method in advanced_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\n⚡ Utility Methods:")
        for method in utility_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\n📊 Performance & Monitoring:")
        for method in performance_methods:
            if hasattr(computer.asq, method):
                print(f"  - computer.asq.{method}()")
        
        print("\nExample usage patterns:")
        print("=" * 30)
        
        # Example 1: Finding elements
        print("\n1. Finding GUI elements:")
        print("   computer.asq.find('button')  # Find all buttons")
        print("   computer.asq.find('button[name=\"Save\"]')  # Find Save button")
        print("   computer.asq.find('text[name=\"filename\"]')  # Find filename field")
        
        # Example 2: High-level actions
        print("\n2. High-level GUI actions:")
        print("   computer.asq.click_button('OK')  # Click OK button")
        print("   computer.asq.type_text('filename', 'document.txt')  # Type in field")
        print("   computer.asq.wait_for_element('dialog[name=\"Save\"]')  # Wait for dialog")
        
        # Example 3: Advanced selectors
        print("\n3. Advanced selectors with spatial relations:")
        print("   computer.asq.find_advanced('button near text[name=\"username\"]')")
        print("   computer.asq.find_advanced('label above text[name=\"password\"]')")
        print("   computer.asq.find_advanced('button[name*=\"save\"]:visible')")
        
        # Example 4: Method chaining
        print("\n4. Method chaining (jQuery-like):")
        print("   computer.asq.find('text[name=\"search\"]').clear().type('hello world')")
        print("   computer.asq.find('button[name=\"Submit\"]').click()")
        
        # Example 5: Utility methods
        print("\n5. Utility methods with timeout:")
        print("   computer.asq.click_if_exists('button[name=\"OK\"]', timeout=10)")
        print("   computer.asq.type_if_exists('text[name=\"search\"]', 'query', timeout=5)")
        print("   text = computer.asq.get_text_if_exists('label[name=\"result\"]')")
        
        # Example 6: Performance monitoring
        print("\n6. Performance monitoring:")
        print("   stats = computer.asq.get_performance_stats()")
        print("   report = computer.asq.get_performance_report()")
        print("   computer.asq.clear_cache()  # Clear cache for fresh start")
        
        # Example 7: Error handling
        print("\n7. Error handling:")
        if platform.system() != 'Linux':
            print("   ⚠ ASQ only works on Linux systems")
            try:
                computer.asq.find('button')
            except RuntimeError as e:
                print(f"   Expected error: {e}")
        else:
            print("   ✓ Running on Linux - ASQ should be available")
            if not computer.asq._asq_available:
                print("   ⚠ AT-SPI libraries may not be installed")
                print("   Install with: sudo apt-get install python3-gi gir1.2-atspi-2.0")
        
        # Example 8: Advanced usage with GUI automation
        print("\n8. Advanced GUI automation:")
        print("""
   # Open an application and interact with it
   if computer.asq.wait_for_element('frame[name*="Calculator"]', timeout=5):
       computer.asq.click_button('1')
       computer.asq.click_button('+')
       computer.asq.click_button('2')
       computer.asq.click_button('=')
       result = computer.asq.find('text[name="result"]').get_text()
       print(f"Calculator result: {result}")
        """)
        
        print("\n9. Form automation:")
        print("""
   # Fill out a form
   form_data = {
       'name': 'John Doe',
       'email': 'john@example.com',
       'message': 'Hello world!'
   }
   
   results = computer.asq.fill_form(form_data)
   if all(results.values()):
       computer.asq.click_button('Submit')
       print("Form submitted successfully")
        """)
        
        print("\nIntegration with LLM:")
        print("=" * 30)
        print("""
The ASQ module is now available to LLMs through the computer API:

```python
# LLM can use these commands directly:
computer.asq.find('button[name="Save"]').click()
computer.asq.type_text('filename', 'my_document.txt')
computer.asq.wait_for_element('dialog[name="Confirmation"]')
```

This enables LLMs to:
- Automate desktop applications
- Fill out forms automatically
- Navigate complex GUI interfaces
- Wait for specific UI states
- Handle dialog boxes and popups
        """)
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"✗ Error: {e}")

def show_asq_capabilities():
    """Show ASQ capabilities and features."""
    print("\nASQ Capabilities Summary:")
    print("=" * 50)
    
    capabilities = [
        "🎯 CSS-like selectors for finding GUI elements",
        "🖱️ Click buttons, links, and other interactive elements",
        "⌨️ Type text into input fields and text areas",
        "⏳ Wait for elements to appear or conditions to be met",
        "🔗 jQuery-like method chaining for complex operations",
        "🛡️ Platform detection and graceful error handling",
        "📱 Support for various GUI element types (buttons, text, dialogs)",
        "🔍 Spatial queries and element relationship navigation",
        "📋 Form automation and bulk data entry",
        "🪟 Window and application management"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")
    
    print("\nSupported Element Types:")
    print("-" * 30)
    element_types = [
        "button, push button - Clickable buttons",
        "text, entry - Text input fields", 
        "dialog - Modal dialogs and popups",
        "frame, window - Application windows",
        "menu, menu item - Menu systems",
        "list, list item - Lists and selections",
        "table, table cell - Data tables",
        "tab, tab list - Tabbed interfaces"
    ]
    
    for element_type in element_types:
        print(f"  • {element_type}")

if __name__ == "__main__":
    demo_asq_usage()
    show_asq_capabilities()
    
    print("\n" + "=" * 50)
    print("🎉 ASQ module successfully integrated into open-interpreter!")
    print("LLMs can now automate Linux desktop applications using computer.asq.*")
    print("=" * 50)