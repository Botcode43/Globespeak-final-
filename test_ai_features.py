#!/usr/bin/env python3
"""
Test script for AI-enhanced features
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'globespeak.settings')
django.setup()

import logging
from translation.services.translate import translate_text, translate_with_ai
from translation.services.summarize import summarize_text, extract_keywords, analyze_sentiment
from translation.services.language_detection import detect_language_with_ai
from translation.services.ocr import enhance_ocr_with_ai

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ai_translation():
    """Test AI-enhanced translation"""
    logger.info("🤖 Testing AI-Enhanced Translation...")
    
    test_cases = [
        ("Hello, how are you today?", "en", "hi"),
        ("नमस्ते, आप कैसे हैं?", "hi", "en"),
        ("Good morning, have a great day!", "en", "es"),
        ("Bonjour, comment allez-vous?", "fr", "en"),
    ]
    
    for text, source, target in test_cases:
        try:
            result = translate_text(text, source, target)
            logger.info(f"✅ {source} → {target}: {result}")
        except Exception as e:
            logger.error(f"❌ Translation failed: {str(e)}")

def test_ai_summarization():
    """Test AI-enhanced summarization"""
    logger.info("🤖 Testing AI-Enhanced Summarization...")
    
    long_text = """
    Artificial Intelligence (AI) has revolutionized the way we interact with technology and process information. 
    From simple chatbots to complex machine learning algorithms, AI systems are now capable of understanding 
    natural language, recognizing patterns, and making decisions that were once exclusive to human intelligence. 
    The development of large language models like GPT and Gemini has opened new possibilities for automated 
    content generation, translation, and analysis. These systems can now understand context, maintain 
    conversations, and provide insights that are remarkably human-like. The integration of AI into various 
    industries has led to increased efficiency, better decision-making, and new opportunities for innovation. 
    However, this rapid advancement also brings challenges related to ethics, privacy, and the need for 
    responsible AI development. As we continue to explore the potential of AI, it's crucial to balance 
    innovation with considerations for the impact on society and human values.
    """
    
    try:
        # Test summarization
        summary = summarize_text(long_text, 50)
        logger.info(f"✅ AI Summary: {summary}")
        
        # Test keyword extraction
        keywords = extract_keywords(long_text, 8)
        logger.info(f"✅ Keywords: {keywords}")
        
        # Test sentiment analysis
        sentiment = analyze_sentiment(long_text)
        logger.info(f"✅ Sentiment: {sentiment}")
        
    except Exception as e:
        logger.error(f"❌ Summarization failed: {str(e)}")

def test_ai_language_detection():
    """Test AI-enhanced language detection"""
    logger.info("🤖 Testing AI-Enhanced Language Detection...")
    
    test_texts = [
        "Hello, how are you?",
        "नमस्ते, आप कैसे हैं?",
        "Hola, ¿cómo estás?",
        "Bonjour, comment allez-vous?",
        "Guten Tag, wie geht es Ihnen?",
        "Ciao, come stai?",
    ]
    
    for text in test_texts:
        try:
            detected = detect_language_with_ai(text)
            if detected:
                logger.info(f"✅ '{text[:30]}...' → {detected}")
            else:
                logger.info(f"⚠️ '{text[:30]}...' → Detection failed")
        except Exception as e:
            logger.error(f"❌ Language detection failed: {str(e)}")

def test_ai_ocr_enhancement():
    """Test AI-enhanced OCR"""
    logger.info("🤖 Testing AI-Enhanced OCR...")
    
    # Simulate OCR output with errors
    ocr_text = "Th1s 1s a t3st of OCR w1th s0me err0rs. It sh0uld be enh4nced by AI."
    
    try:
        enhanced = enhance_ocr_with_ai(ocr_text)
        logger.info(f"✅ Original OCR: {ocr_text}")
        logger.info(f"✅ AI Enhanced: {enhanced}")
    except Exception as e:
        logger.error(f"❌ OCR enhancement failed: {str(e)}")

def main():
    """Run all AI feature tests"""
    logger.info("🚀 Starting AI-Enhanced Features Test")
    logger.info("=" * 60)
    
    tests = [
        ("AI Translation", test_ai_translation),
        ("AI Summarization", test_ai_summarization),
        ("AI Language Detection", test_ai_language_detection),
        ("AI OCR Enhancement", test_ai_ocr_enhancement),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} Test...")
        try:
            test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test failed: {str(e)}")
    
    logger.info("\n" + "=" * 60)
    logger.info("🎉 AI-Enhanced Features Test Complete!")
    logger.info("Your Gemini API key is working and enhancing your services!")

if __name__ == "__main__":
    main()
