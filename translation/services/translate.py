"""
Translation service using Google Translate via deep_translator
"""

from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

def translate_text(text, source_lang='auto', target_lang='en'):
    """
    Translate text from source language to target language using Google Translate with AI enhancement.
    """
    try:
        if not text or not text.strip():
            return ""

        # Handle auto-detection
        if source_lang == 'auto':
            try:
                detected_lang = GoogleTranslator().detect(text)
                source_lang = detected_lang
                logger.info(f"Detected language: {source_lang}")
            except Exception as e:
                logger.warning(f"Language detection failed: {str(e)}")
                source_lang = 'en'  # Default to English if detection fails

        # Clean text for better translation
        cleaned_text = clean_text_for_translation(text)

        # Try AI-enhanced translation first (if available)
        try:
            ai_translation = translate_with_ai(cleaned_text, source_lang, target_lang)
            if ai_translation and ai_translation.strip().lower() != cleaned_text.strip().lower():
                logger.info(f"AI-enhanced translation successful: {source_lang} -> {target_lang}")
                return ai_translation
        except Exception as e:
            logger.warning(f"AI translation failed, falling back to Google Translate: {str(e)}")

        # Fallback to Google Translate
        max_retries = 3
        for attempt in range(max_retries):
            try:
                translator = GoogleTranslator(source=source_lang, target=target_lang)
                translated_text = translator.translate(cleaned_text)
                translated_text = post_process_translation(translated_text, source_lang, target_lang)

                # If translation is the same as input, treat as failure
                if translated_text.strip().lower() == cleaned_text.strip().lower():
                    logger.warning(f"Translation attempt {attempt + 1} returned input text, treating as failure.")
                    continue

                logger.info(f"Translation successful: {source_lang} -> {target_lang} (attempt {attempt + 1})")
                return translated_text

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
                continue

        # If all attempts fail, raise error
        raise Exception("Translation failed: Output is same as input or all attempts failed.")

    except Exception as e:
        logger.error(f"Translation failed: {str(e)}")
        raise Exception(f"Translation failed: {str(e)}")


# def translate_text(text, source_lang='auto', target_lang='en'):
#     """
#     Translate text from source language to target language using Google Translate with AI enhancement.
    
#     Args:
#         text (str): Text to translate
#         source_lang (str): Source language code (e.g., 'en', 'hi', 'auto')
#         target_lang (str): Target language code (e.g., 'en', 'hi', 'es')
#         # ... inside image_translation view, after detected_lang is set ...
#     context = {
#         'extracted_text': extracted_text,
#         'translated_text': translated_text,
#         'target_lang': target_lang,
#         'detected_lang': detected_lang,  # <-- add this
#         'image_url': f"/media/{filepath}",
#         'supported_languages': get_supported_languages(),
#         'supported_ocr_languages': get_supported_ocr_languages(),
#     }
#     Returns:
#         str: Translated text
        
#     Raises:
#         Exception: If translation fails
#     """
#     try:
#         if not text or not text.strip():
#             return ""
        
#         # Handle auto-detection
#         if source_lang == 'auto':
#             # Try to detect language first
#             try:
#                 detected_lang = GoogleTranslator().detect(text)
#                 source_lang = detected_lang
#             except:
#                 source_lang = 'en'  # Default to English if detection fails
        
#         # Clean text for better translation
#         cleaned_text = clean_text_for_translation(text)
        
#         # Try AI-enhanced translation first (if available)
#         try:
#             ai_translation = translate_with_ai(cleaned_text, source_lang, target_lang)
#             if ai_translation:
#                 logger.info(f"AI-enhanced translation successful: {source_lang} -> {target_lang}")
#                 return ai_translation
#         except Exception as e:
#             logger.warning(f"AI translation failed, falling back to Google Translate: {str(e)}")
        
#         # Fallback to Google Translate
#         max_retries = 3
#         for attempt in range(max_retries):
#             try:
#                 translator = GoogleTranslator(source=source_lang, target=target_lang)
#                 translated_text = translator.translate(cleaned_text)
                
#                 # Post-process translation for better quality
#                 translated_text = post_process_translation(translated_text, source_lang, target_lang)
                
#                 logger.info(f"Translation successful: {source_lang} -> {target_lang} (attempt {attempt + 1})")
#                 return translated_text
                
#             except Exception as e:
#                 if attempt == max_retries - 1:
#                     raise e
#                 logger.warning(f"Translation attempt {attempt + 1} failed: {str(e)}")
#                 continue
        
#     except Exception as e:
#         logger.error(f"Translation failed: {str(e)}")
#         raise Exception(f"Translation failed: {str(e)}")


def clean_text_for_translation(text):
    """Clean text before translation for better accuracy"""
    try:
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Only remove truly problematic characters, preserve Unicode text
        import re
        # Remove only control characters and some problematic symbols, but keep Unicode letters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
        
    except Exception as e:
        logger.warning(f"Text cleaning failed: {str(e)}")
        return text


def post_process_translation(translated_text, source_lang, target_lang):
    """Post-process translation for better quality"""
    try:
        # Remove extra whitespace
        translated_text = ' '.join(translated_text.split())
        
        # Fix common translation issues
        if target_lang == 'hi':  # Hindi specific fixes
            translated_text = translated_text.replace('।।', '।')  # Remove double periods
            translated_text = translated_text.replace('  ', ' ')  # Remove double spaces
        
        return translated_text.strip()
        
    except Exception as e:
        logger.warning(f"Translation post-processing failed: {str(e)}")
        return translated_text


def translate_with_ai(text, source_lang, target_lang):
    """
    Translate text using Gemini AI for better context understanding.
    
    Args:
        text (str): Text to translate
        source_lang (str): Source language code
        target_lang (str): Target language code
    
    Returns:
        str: AI-translated text or None if failed
    """
    try:
        from django.conf import settings
        import google.generativeai as genai
        if not settings.GEMINI_API_KEY:
            return None
        # Use the correct public Gemini model name
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        lang_names = get_language_names()
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        prompt = f"""
        Translate the following text from {source_name} to {target_name}.
        Requirements:
        1. Maintain the original meaning and context
        2. Use natural, fluent language in the target language
        3. Preserve the tone and style of the original text
        4. If the text contains names, places, or technical terms, keep them as appropriate
        5. Return only the translated text, no explanations
        
        Text to translate:
        {text}
        
        Translation:
        """
        response = model.generate_content(prompt)
        translation = response.text.strip()
        translation = post_process_translation(translation, source_lang, target_lang)
        logger.info(f"AI translation successful: {source_lang} -> {target_lang}")
        return translation
    except Exception as e:
        logger.warning(f"AI translation failed: {str(e)}")
        return None


def get_language_names():
    """Get mapping of language codes to names"""
    return {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'pa': 'Punjabi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ur': 'Urdu',
    }


def get_supported_languages():
    """
    Get list of supported languages for translation.
    
    Returns:
        dict: Dictionary of language codes and names
    """
    return {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'kn': 'Kannada',
        'ml': 'Malayalam',
        'mr': 'Marathi',
        'ne': 'Nepali',
        'pa': 'Punjabi',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ur': 'Urdu',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'tr': 'Turkish',
        'pl': 'Polish',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'cs': 'Czech',
        'hu': 'Hungarian',
        'ro': 'Romanian',
        'bg': 'Bulgarian',
        'hr': 'Croatian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'et': 'Estonian',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'mt': 'Maltese',
        'cy': 'Welsh',
        'ga': 'Irish',
        'is': 'Icelandic',
        'mk': 'Macedonian',
        'sq': 'Albanian',
        'sr': 'Serbian',
        'bs': 'Bosnian',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'ka': 'Georgian',
        'hy': 'Armenian',
        'az': 'Azerbaijani',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'uz': 'Uzbek',
        'tg': 'Tajik',
        'mn': 'Mongolian',
        'my': 'Burmese',
        'km': 'Khmer',
        'lo': 'Lao',
        'si': 'Sinhala',
        'dz': 'Dzongkha',
        'bo': 'Tibetan',
        'am': 'Amharic',
        'sw': 'Swahili',
        'zu': 'Zulu',
        'af': 'Afrikaans',
        'eu': 'Basque',
        'ca': 'Catalan',
        'gl': 'Galician',
        'he': 'Hebrew',
        'fa': 'Persian',
        'ps': 'Pashto',
        'sd': 'Sindhi',
        'or': 'Odia',
        'as': 'Assamese',
        'sa': 'Sanskrit',
    }
