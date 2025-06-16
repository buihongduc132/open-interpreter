#!/usr/bin/env python3
"""
Simple test script to verify ASQ integration into open-interpreter.

This script tests the basic integration without requiring a full GUI environment.
"""

import sys
import os
import platform

# Add the interpreter path to sys.path
sys.path.insert(0, '/workspace')

def test_asq_import():
    """Test that ASQ module can be imported."""
    print("Testing ASQ module import...")
    
    try:
        from interpreter.core.computer.computer import Computer
        print("✓ Computer class imported successfully")
        
        # Create a mock interpreter object
        class MockInterpreter:
            max_output = 1000
        
        mock_interpreter = MockInterpreter()
        computer = Computer(mock_interpreter)
        print("✓ Computer instance created successfully")
        
        # Check if ASQ attribute exists
        if hasattr(computer, 'asq'):
            print("✓ ASQ module is available as computer.asq")
            
            # Test platform detection
            print(f"Current platform: {platform.system()}")
            
            if platform.system() == 'Linux':
                print("✓ Running on Linux - ASQ should be functional")
                try:
                    # This will test the availability check
                    computer.asq._check_availability()
                    if computer.asq._asq_available:
                        print("✓ ASQ is available and AT-SPI is accessible")
                    else:
                        print("⚠ ASQ detected but AT-SPI libraries may not be installed")
                except Exception as e:
                    print(f"⚠ ASQ availability check failed: {e}")
            else:
                print(f"⚠ Running on {platform.system()} - ASQ will show appropriate error")
                try:
                    computer.asq.find('button')
                    print("✗ Expected error for non-Linux platform")
                except RuntimeError as e:
                    print(f"✓ Correct error for non-Linux platform: {e}")
            
            # Test method availability
            methods_to_test = ['find', 'click_button', 'type_text', 'wait_for_element']
            for method in methods_to_test:
                if hasattr(computer.asq, method):
                    print(f"✓ Method {method} is available")
                else:
                    print(f"✗ Method {method} is missing")
            
        else:
            print("✗ ASQ module not found in computer object")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    return True

def test_asq_methods():
    """Test ASQ method signatures and docstrings."""
    print("\nTesting ASQ method signatures...")
    
    try:
        from interpreter.core.computer.asq.asq import ASQ
        
        # Create a mock computer object
        class MockComputer:
            verbose = True
        
        mock_computer = MockComputer()
        asq = ASQ(mock_computer)
        
        # Test method signatures
        methods = [
            ('find', 'Find GUI elements using CSS-like selectors'),
            ('click_button', 'High-level method to click a button by name'),
            ('type_text', 'High-level method to type text into a text field'),
            ('wait_for_element', 'Wait for an element to appear')
        ]
        
        for method_name, expected_desc in methods:
            if hasattr(asq, method_name):
                method = getattr(asq, method_name)
                if method.__doc__ and expected_desc.lower() in method.__doc__.lower():
                    print(f"✓ Method {method_name} has correct description")
                else:
                    print(f"⚠ Method {method_name} description may need review")
            else:
                print(f"✗ Method {method_name} not found")
        
    except Exception as e:
        print(f"✗ Error testing methods: {e}")
        return False
    
    return True

def test_computer_tools_list():
    """Test that ASQ is included in computer tools list."""
    print("\nTesting computer tools list...")
    
    try:
        from interpreter.core.computer.computer import Computer
        
        class MockInterpreter:
            max_output = 1000
        
        computer = Computer(MockInterpreter())
        tools = computer._get_all_computer_tools_list()
        
        # Check if ASQ is in the tools list
        asq_found = any(tool.__class__.__name__ == 'ASQ' for tool in tools)
        
        if asq_found:
            print("✓ ASQ is included in computer tools list")
        else:
            print("✗ ASQ not found in computer tools list")
            return False
        
        # Test signature extraction
        try:
            signatures = computer._get_all_computer_tools_signature_and_description()
            asq_signatures = [sig for sig in signatures if 'computer.asq.' in sig]
            
            if asq_signatures:
                print(f"✓ Found {len(asq_signatures)} ASQ method signatures")
                for sig in asq_signatures[:3]:  # Show first 3
                    print(f"  - {sig}")
                if len(asq_signatures) > 3:
                    print(f"  ... and {len(asq_signatures) - 3} more")
            else:
                print("⚠ No ASQ method signatures found")
                
        except Exception as e:
            print(f"⚠ Error extracting signatures: {e}")
        
    except Exception as e:
        print(f"✗ Error testing tools list: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("ASQ Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_asq_import,
        test_asq_methods,
        test_computer_tools_list
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ASQ integration appears to be working correctly.")
        return 0
    else:
        print("⚠ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())