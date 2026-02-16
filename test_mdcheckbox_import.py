#!/usr/bin/env python3
"""Test script to check MDCheckbox import paths"""

print("Testing MDCheckbox import paths...")

# Test 1: Der ursprüngliche Import aus selectioncontrol
try:
    from kivymd.uix.selectioncontrol import MDCheckbox
    print("✅ SUCCESS: from kivymd.uix.selectioncontrol import MDCheckbox")
    mdcheckbox_class_old = MDCheckbox
except ImportError as e:
    print(f"❌ FAILED: from kivymd.uix.selectioncontrol import MDCheckbox - {e}")
    mdcheckbox_class_old = None

# Test 2: Neuer möglicher Import path
try:
    from kivymd.uix.checkbox import MDCheckbox  
    print("✅ SUCCESS: from kivymd.uix.checkbox import MDCheckbox")
    mdcheckbox_class_new = MDCheckbox
except ImportError as e:
    print(f"❌ FAILED: from kivymd.uix.checkbox import MDCheckbox - {e}")
    mdcheckbox_class_new = None

# Test 3: Alternative Import-Pfade
try:
    from kivymd.uix.selection import MDCheckbox
    print("✅ SUCCESS: from kivymd.uix.selection import MDCheckbox")
except ImportError as e:
    print(f"❌ FAILED: from kivymd.uix.selection import MDCheckbox - {e}")

# Test 4: Direkte Überprüfung der KivyMD-Version
try:
    import kivymd
    print(f"KivyMD version: {kivymd.__version__}")
except:
    print("Could not determine KivyMD version")

print("Test completed.")