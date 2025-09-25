#!/usr/bin/env python3
"""
Comprehensive fix script for Globespeak project issues
"""

import os
import sys
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command and log the result"""
    logger.info(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ {description} - Success")
            return True
        else:
            logger.error(f"❌ {description} - Failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ {description} - Exception: {str(e)}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("Checking dependencies...")
    
    required_packages = [
        'django',
        'djangorestframework',
        'channels',
        'deep-translator',
        'pytesseract',
        'opencv-python',
        'speechrecognition',
        'gtts',
        'google-generativeai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info(f"✅ {package} - Installed")
        except ImportError:
            logger.warning(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        logger.info(f"Installing missing packages: {', '.join(missing_packages)}")
        run_command(f"pip install {' '.join(missing_packages)}", "Install missing packages")
    
    return len(missing_packages) == 0

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    logger.info("Checking Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.info(f"✅ Tesseract OCR - Installed (Version: {version})")
        return True
    except Exception as e:
        logger.error(f"❌ Tesseract OCR - Not found: {str(e)}")
        logger.info("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

def run_migrations():
    """Run Django migrations"""
    logger.info("Running Django migrations...")
    return run_command("python manage.py makemigrations", "Create migrations") and \
           run_command("python manage.py migrate", "Apply migrations")

def collect_static():
    """Collect static files"""
    logger.info("Collecting static files...")
    return run_command("python manage.py collectstatic --noinput", "Collect static files")

def create_superuser():
    """Create a superuser if none exists"""
    logger.info("Checking for superuser...")
    
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            logger.info("Creating superuser...")
            # This would need to be interactive, so we'll skip for now
            logger.info("Please run: python manage.py createsuperuser")
        else:
            logger.info("✅ Superuser already exists")
    except Exception as e:
        logger.error(f"❌ Error checking superuser: {str(e)}")

def test_services():
    """Test all services"""
    logger.info("Testing services...")
    
    # Test translation service
    try:
        from translation.services.translate import translate_text
        result = translate_text("Hello", "en", "hi")
        logger.info(f"✅ Translation service - Working: {result}")
    except Exception as e:
        logger.error(f"❌ Translation service - Failed: {str(e)}")
    
    # Test TTS service
    try:
        from translation.services.tts import text_to_speech
        result = text_to_speech("Hello", "en")
        logger.info(f"✅ TTS service - Working: {result}")
    except Exception as e:
        logger.error(f"❌ TTS service - Failed: {str(e)}")
    
    # Test STT service
    try:
        from translation.services.stt import speech_to_text_from_file
        logger.info("✅ STT service - Available")
    except Exception as e:
        logger.error(f"❌ STT service - Failed: {str(e)}")
    
    # Test OCR service
    try:
        from translation.services.ocr import TESSERACT_AVAILABLE
        if TESSERACT_AVAILABLE:
            logger.info("✅ OCR service - Available")
        else:
            logger.warning("⚠️ OCR service - Tesseract not installed")
    except Exception as e:
        logger.error(f"❌ OCR service - Failed: {str(e)}")

def main():
    """Main fix function"""
    logger.info("🔧 Starting Globespeak Fix Script")
    logger.info("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        logger.error("❌ Not in Django project directory. Please run this script from the project root.")
        return False
    
    # Run all checks and fixes
    success = True
    
    success &= check_dependencies()
    success &= check_tesseract()
    success &= run_migrations()
    success &= collect_static()
    create_superuser()
    test_services()
    
    logger.info("=" * 50)
    if success:
        logger.info("🎉 All fixes completed successfully!")
        logger.info("You can now run: python manage.py runserver 8000")
    else:
        logger.error("❌ Some fixes failed. Please check the logs above.")
    
    return success

if __name__ == "__main__":
    main()
