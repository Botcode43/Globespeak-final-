#!/usr/bin/env python3
"""
Test script to demonstrate multi-language OCR functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globespeak.settings')
django.setup()

from translation.services.ocr import extract_text_from_image, LANGUAGES
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multilang_ocr():
    """Test the multi-language OCR functionality"""
    logger.info("🧪 Testing Multi-Language OCR")
    logger.info("=" * 50)
    
    # Test with an existing image from the media folder
    media_images = "media/images"
    if os.path.exists(media_images):
        image_files = [f for f in os.listdir(media_images) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if image_files:
            test_image = os.path.join(media_images, image_files[0])
            logger.info(f"Testing with image: {test_image}")
            
            try:
                # Test multi-language OCR
                text = extract_text_from_image(test_image)
                logger.info(f"✅ Multi-language OCR result:")
                logger.info(f"📝 Extracted text: {text[:200]}{'...' if len(text) > 200 else ''}")
                logger.info(f"📊 Total characters: {len(text)}")
                
                # Show supported languages
                logger.info(f"🌍 Supported languages: {LANGUAGES}")
                
            except Exception as e:
                logger.error(f"❌ OCR test failed: {str(e)}")
        else:
            logger.warning("⚠️ No image files found in media/images folder")
    else:
        logger.warning("⚠️ Media images folder not found")
    
    logger.info("=" * 50)
    logger.info("🎉 Multi-language OCR test completed!")

if __name__ == "__main__":
    test_multilang_ocr()

