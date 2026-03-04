#!/usr/bin/env python3
"""
ALM Documentation Zip Creator
Creates a zip file containing all ALM documentation files
"""

import zipfile
import os
from pathlib import Path

# Configuration
ZIP_OUTPUT_PATH = 'static/ALM/Documents.zip'
SOURCE_DIR = 'static/ALM'

# Files to include in the zip archive
# Add or remove files as needed
FILES_TO_INCLUDE = [
    # Research Documentation
    'alm_complete_documentation.html',
    'alm_conversation_thread.html',
    'alm_thread_navigation.html',
    'alm_design_decisions.html',
    
    # Process & Architecture
    'alm_interactive_demo.html',
    'alm_architecture_decisions.html',
    
    # Marketing & Product
    'alm_marketing_complete.html',
    
    # Index Pages
    'research_index.html',
    'process_index.html',
]

def create_documentation_zip():
    """Create the documentation zip file"""
    
    # Ensure the ALM directory exists
    alm_dir = os.path.dirname(ZIP_OUTPUT_PATH)
    if not os.path.exists(alm_dir):
        print(f"❌ Error: ALM directory not found: {alm_dir}")
        print("   Please make sure the static/ALM folder exists.")
        return False
    
    print("=" * 60)
    print("ALM Documentation Zip Creator")
    print("=" * 60)
    print()
    
    # Check if source directory exists
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Error: Source directory not found: {SOURCE_DIR}")
        print("   Please make sure you're running this from the project root.")
        return False
    
    # Create the zip file
    files_added = 0
    files_missing = 0
    
    with zipfile.ZipFile(ZIP_OUTPUT_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in FILES_TO_INCLUDE:
            file_path = os.path.join(SOURCE_DIR, filename)
            
            if os.path.exists(file_path):
                # Add file to zip (without directory structure)
                zipf.write(file_path, filename)
                file_size = os.path.getsize(file_path)
                print(f"✓ Added: {filename} ({file_size:,} bytes)")
                files_added += 1
            else:
                print(f"⚠ Warning: File not found - {filename}")
                files_missing += 1
    
    print()
    print("=" * 60)
    print("Summary:")
    print(f"  Files added: {files_added}")
    print(f"  Files missing: {files_missing}")
    
    if os.path.exists(ZIP_OUTPUT_PATH):
        zip_size = os.path.getsize(ZIP_OUTPUT_PATH)
        print(f"  Zip file size: {zip_size:,} bytes ({zip_size / 1024:.2f} KB)")
        print(f"  Output location: {ZIP_OUTPUT_PATH}")
        print()
        print("✅ Zip file created successfully!")
        print()
        print("Next steps:")
        print("  1. Start your Flask app: python app.py")
        print("  2. Login and navigate to ALM Dashboard")
        print("  3. Click 'Documents' button")
        print("  4. Click 'Download Documentation Package'")
        return True
    else:
        print()
        print("❌ Error: Failed to create zip file")
        return False

if __name__ == "__main__":
    success = create_documentation_zip()
    exit(0 if success else 1)