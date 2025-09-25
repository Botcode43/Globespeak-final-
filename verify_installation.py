#!/usr/bin/env python3
"""
GlobeSpeak Installation Verification Script
Checks if all required packages and dependencies are properly installed
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.12+")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed and importable"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} - Installed")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_external_tool(tool_name, command):
    """Check if external tool is available"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {tool_name} - Available")
            return True
        else:
            print(f"❌ {tool_name} - Not found")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print(f"❌ {tool_name} - Not found")
        return False

def check_django_setup():
    """Check if Django is properly configured"""
    print("\n🔧 Checking Django setup...")
    try:
        import django
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globespeak.settings')
        django.setup()
        
        print("✅ Django - Properly configured")
        return True
    except Exception as e:
        print(f"❌ Django - Configuration error: {e}")
        return False

def check_ai_models():
    """Check if AI models can be loaded"""
    print("\n🤖 Checking AI models...")
    
    # Check Whisper
    try:
        import whisper
        model = whisper.load_model("base")
        print("✅ Whisper - Model loaded successfully")
        whisper_ok = True
    except Exception as e:
        print(f"❌ Whisper - Model loading failed: {e}")
        whisper_ok = False
    
    # Check Transformers
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
        print("✅ Transformers - BART model accessible")
        transformers_ok = True
    except Exception as e:
        print(f"❌ Transformers - Model loading failed: {e}")
        transformers_ok = False
    
    return whisper_ok and transformers_ok

def main():
    """Main verification function"""
    print("=" * 60)
    print("🚀 GlobeSpeak Installation Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Check Python version
    if not check_python_version():
        all_checks_passed = False
    
    # Check core packages
    print("\n📦 Checking core packages...")
    core_packages = [
        ('Django', 'django'),
        ('NumPy', 'numpy'),
        ('OpenCV', 'cv2'),
        ('Pillow', 'PIL'),
        ('Requests', 'requests'),
        ('PyTesseract', 'pytesseract'),
        ('SpeechRecognition', 'speech_recognition'),
        ('gTTS', 'gtts'),
        ('Deep Translator', 'deep_translator'),
        ('Google Generative AI', 'google.generativeai'),
    ]
    
    for package_name, import_name in core_packages:
        if not check_package(package_name, import_name):
            all_checks_passed = False
    
    # Check AI/ML packages
    print("\n🧠 Checking AI/ML packages...")
    ai_packages = [
        ('PyTorch', 'torch'),
        ('Transformers', 'transformers'),
        ('Whisper', 'whisper'),
        ('NLTK', 'nltk'),
        ('youtube-dl', 'yt_dlp'),
    ]
    
    for package_name, import_name in ai_packages:
        if not check_package(package_name, import_name):
            all_checks_passed = False
    
    # Check external tools
    print("\n🛠️ Checking external tools...")
    external_tools = [
        ('FFmpeg', 'ffmpeg'),
        ('Tesseract', 'tesseract'),
    ]
    
    for tool_name, command in external_tools:
        if not check_external_tool(tool_name, command):
            all_checks_passed = False
    
    # Check Django setup
    if not check_django_setup():
        all_checks_passed = False
    
    # Check AI models (optional, takes time)
    print("\n⚠️  Checking AI models (this may take a few minutes)...")
    if not check_ai_models():
        print("⚠️  AI models check failed - this is normal on first run")
        print("   Models will be downloaded automatically when first used")
    
    # Final result
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 All checks passed! GlobeSpeak is ready to use.")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://localhost:8000")
        print("3. Start translating! 🌍")
    else:
        print("❌ Some checks failed. Please review the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure virtual environment is activated")
        print("2. Run: pip install -r requirements.txt")
        print("3. Install FFmpeg and Tesseract OCR")
        print("4. See SETUP_GUIDE.md for detailed instructions")
    
    print("=" * 60)
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
