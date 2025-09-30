#!/usr/bin/env python3
"""
Simple script to add your API key to the AI service
"""

import re

def add_api_key():
    """Add API key to the AI service"""
    print("🔑 API Key Setup")
    print("================")
    
    # Get API key from user
    api_key = input("Enter your API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key doesn't start with 'sk-'")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Read the current file
    try:
        with open('services/ai_venue_service.py', 'r') as f:
            content = f.read()
        
        # Replace the placeholder
        old_pattern = r'hardcoded_key = "sk-your-api-key-here-replace-this-with-real-key"'
        new_line = f'hardcoded_key = "{api_key}"'
        
        if old_pattern in content:
            new_content = content.replace(
                'hardcoded_key = "sk-your-api-key-here-replace-this-with-real-key"',
                f'hardcoded_key = "{api_key}"'
            )
            
            # Write back to file
            with open('services/ai_venue_service.py', 'w') as f:
                f.write(new_content)
            
            print("✅ API key added successfully!")
            print("🚀 You can now run: streamlit run app.py")
            
        else:
            print("❌ Could not find placeholder in file")
            print("Please manually replace the placeholder in services/ai_venue_service.py")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    add_api_key()