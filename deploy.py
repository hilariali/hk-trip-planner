#!/usr/bin/env python3
"""
Deployment script for SilverJoy Planner HK
Prepares the application for Streamlit Cloud deployment
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'app.py',
        'requirements.txt',
        'database.py',
        'models.py',
        '.streamlit/config.toml',
        '.streamlit/secrets.toml.template'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True

def initialize_database():
    """Initialize the database with sample data"""
    try:
        print("🗄️ Initializing database...")
        subprocess.run([sys.executable, 'database.py'], check=True)
        print("✅ Database initialized successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_app():
    """Test if the app can start without errors"""
    try:
        print("🧪 Testing application...")
        # Import main modules to check for errors
        import app
        import models
        import database
        print("✅ Application modules loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def git_status():
    """Check git status and provide deployment instructions"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("📝 Uncommitted changes detected:")
            print(result.stdout)
            print("\n🚀 To deploy:")
            print("1. git add .")
            print("2. git commit -m 'Deploy SilverJoy Planner HK'")
            print("3. git push origin main")
        else:
            print("✅ No uncommitted changes")
            print("🚀 Ready to deploy! Run: git push origin main")
            
    except subprocess.CalledProcessError:
        print("⚠️ Not a git repository or git not available")

def main():
    """Main deployment preparation"""
    print("🏙️ SilverJoy Planner HK - Deployment Preparation")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Test app
    if not test_app():
        sys.exit(1)
    
    # Check git status
    git_status()
    
    print("\n🎉 Deployment preparation complete!")
    print("\n📋 Next steps:")
    print("1. Push to GitHub: git push origin main")
    print("2. Go to https://share.streamlit.io")
    print("3. Connect your GitHub repository")
    print("4. Set main file: app.py")
    print("5. Add secrets in Streamlit Cloud dashboard")
    print("\n🔐 Don't forget to add your API key in Streamlit Cloud secrets!")

if __name__ == "__main__":
    main()