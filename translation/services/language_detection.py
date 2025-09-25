"""
Language detection service for automatic language identification
"""

import logging
from typing import Optional, Dict, List
from deep_translator import GoogleTranslator
import re

logger = logging.getLogger(__name__)

# Language detection patterns
LANGUAGE_PATTERNS = {
    'hi': {
        'patterns': [r'[\u0900-\u097F]', r'[हिंदी]', r'[नमस्ते]', r'[धन्यवाद]'],
        'keywords': ['है', 'हैं', 'का', 'की', 'के', 'में', 'पर', 'से', 'को', 'ने']
    },
    'en': {
        'patterns': [r'[a-zA-Z]'],
        'keywords': ['the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'will', 'would', 'could', 'should']
    },
    'es': {
        'patterns': [r'[ñáéíóúü]', r'[¿¡]'],
        'keywords': ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las']
    },
    'fr': {
        'patterns': [r'[àâäéèêëïîôöùûüÿç]'],
        'keywords': ['le', 'de', 'et', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus', 'par', 'grand', 'en', 'une', 'être', 'et', 'à', 'il', 'avoir', 'ne', 'je', 'son', 'que', 'qui', 'ce', 'dans', 'en', 'du', 'elle', 'au', 'de', 'le', 'à', 'un', 'il', 'être', 'et', 'en', 'avoir', 'que', 'pour', 'dans', 'ce', 'son', 'une', 'sur', 'avec', 'ne', 'se', 'pas', 'tout', 'plus', 'par', 'grand']
    },
    'de': {
        'patterns': [r'[äöüß]'],
        'keywords': ['der', 'die', 'und', 'in', 'den', 'von', 'zu', 'das', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als', 'auch', 'es', 'an', 'werden', 'aus', 'er', 'hat', 'dass', 'sie', 'nach', 'wird', 'bei', 'einer', 'um', 'am', 'sind', 'noch', 'wie', 'einem', 'über', 'einen', 'so', 'zum', 'war', 'haben', 'nur', 'oder', 'aber', 'vor', 'zur', 'bis', 'mehr', 'durch', 'man', 'sein', 'wurde', 'sei', 'in', 'den', 'mit', 'sich', 'des', 'auf', 'für', 'ist', 'im', 'dem', 'nicht', 'ein', 'eine', 'als', 'auch', 'es', 'an', 'werden', 'aus', 'er', 'hat', 'dass', 'sie', 'nach', 'wird', 'bei', 'einer', 'um', 'am', 'sind', 'noch', 'wie', 'einem', 'über', 'einen', 'so', 'zum', 'war', 'haben', 'nur', 'oder', 'aber', 'vor', 'zur', 'bis', 'mehr', 'durch', 'man', 'sein', 'wurde', 'sei']
    },
    'zh': {
        'patterns': [r'[\u4e00-\u9fff]'],
        'keywords': ['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
    },
    'ja': {
        'patterns': [r'[\u3040-\u309f]', r'[\u30a0-\u30ff]', r'[\u4e00-\u9faf]'],
        'keywords': ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や', 'れる', 'られ', 'た', 'ない', 'よう', 'な', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や', 'れる', 'られ', 'た', 'ない', 'よう']
    },
    'ko': {
        'patterns': [r'[\uac00-\ud7af]'],
        'keywords': ['이', '그', '저', '의', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '는', '은', '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '는', '은', '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '도', '는', '은']
    },
    'ar': {
        'patterns': [r'[\u0600-\u06ff]'],
        'keywords': ['في', 'من', 'إلى', 'على', 'هذا', 'هذه', 'التي', 'الذي', 'كان', 'كانت', 'يكون', 'تكون', 'له', 'لها', 'لهما', 'لهم', 'لهن', 'بعد', 'قبل', 'عند', 'مع', 'بدون', 'حول', 'خلال', 'بين', 'أمام', 'خلف', 'فوق', 'تحت', 'داخل', 'خارج', 'يمين', 'يسار', 'شمال', 'جنوب', 'شرق', 'غرب']
    },
    'ru': {
        'patterns': [r'[\u0400-\u04ff]'],
        'keywords': ['и', 'в', 'не', 'на', 'я', 'быть', 'с', 'со', 'как', 'а', 'по', 'но', 'они', 'к', 'у', 'мы', 'для', 'что', 'от', 'за', 'из', 'до', 'при', 'о', 'об', 'про', 'под', 'над', 'между', 'через', 'без', 'вместо', 'кроме', 'среди', 'вокруг', 'около', 'близ', 'далеко', 'здесь', 'там', 'где', 'куда', 'откуда', 'когда', 'как', 'почему', 'зачем', 'сколько', 'какой', 'какая', 'какое', 'какие', 'чей', 'чья', 'чьё', 'чьи']
    }
}

def detect_language(text: str) -> Optional[str]:
    """
    Detect the language of the given text using pattern matching and keyword analysis.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Detected language code or None if detection fails
    """
    if not text or not text.strip():
        return None
    
    text = text.strip().lower()
    language_scores = {}
    
    # Pattern-based detection
    for lang_code, lang_data in LANGUAGE_PATTERNS.items():
        score = 0
        
        # Check for language-specific patterns
        for pattern in lang_data['patterns']:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 2  # Patterns are weighted higher
        
        # Check for language-specific keywords
        for keyword in lang_data['keywords']:
            if keyword.lower() in text:
                score += 1
        
        # Normalize score by text length
        if len(text) > 0:
            language_scores[lang_code] = score / len(text)
        else:
            language_scores[lang_code] = 0
    
    # Return the language with the highest score
    if language_scores:
        detected_lang = max(language_scores, key=language_scores.get)
        confidence = language_scores[detected_lang]
        
        # Only return if confidence is above threshold
        if confidence > 0.01:  # Minimum confidence threshold
            logger.info(f"Language detected: {detected_lang} (confidence: {confidence:.3f})")
            return detected_lang
    
    logger.warning("Language detection failed - no confident match found")
    return None

def detect_language_with_google(text: str) -> Optional[str]:
    """
    Detect language using Google Translate API as fallback.
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: Detected language code or None if detection fails
    """
    try:
        if not text or not text.strip():
            return None
        
        # Use Google Translate for language detection
        detected = GoogleTranslator().detect(text)
        if detected:
            logger.info(f"Google detected language: {detected}")
            return detected
        
    except Exception as e:
        logger.error(f"Google language detection failed: {str(e)}")
    
    return None

def get_language_name(lang_code: str) -> str:
    """
    Get the full language name from language code.
    
    Args:
        lang_code (str): Language code (e.g., 'en', 'hi')
        
    Returns:
        str: Full language name
    """
    language_names = {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'ru': 'Russian',
        'pt': 'Portuguese',
        'it': 'Italian',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'pl': 'Polish',
        'tr': 'Turkish',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'or': 'Odia',
        'as': 'Assamese',
        'ne': 'Nepali',
        'si': 'Sinhala',
        'my': 'Burmese',
        'km': 'Khmer',
        'lo': 'Lao',
        'ka': 'Georgian',
        'hy': 'Armenian',
        'az': 'Azerbaijani',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'uz': 'Uzbek',
        'tg': 'Tajik',
        'mn': 'Mongolian',
        'bo': 'Tibetan',
        'dz': 'Dzongkha',
        'he': 'Hebrew',
        'fa': 'Persian',
        'ur': 'Urdu',
        'sd': 'Sindhi',
        'ps': 'Pashto',
        'ku': 'Kurdish',
        'sw': 'Swahili',
        'am': 'Amharic',
        'ti': 'Tigrinya',
        'om': 'Oromo',
        'so': 'Somali',
        'ha': 'Hausa',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'zu': 'Zulu',
        'xh': 'Xhosa',
        'af': 'Afrikaans',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'mt': 'Maltese',
        'eu': 'Basque',
        'ca': 'Catalan',
        'gl': 'Galician',
        'lb': 'Luxembourgish',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'et': 'Estonian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'hr': 'Croatian',
        'sr': 'Serbian',
        'bs': 'Bosnian',
        'mk': 'Macedonian',
        'bg': 'Bulgarian',
        'ro': 'Romanian',
        'hu': 'Hungarian',
        'cs': 'Czech',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'sq': 'Albanian',
        'mk': 'Macedonian',
        'bg': 'Bulgarian',
        'ro': 'Romanian',
        'hu': 'Hungarian',
        'cs': 'Czech',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'sq': 'Albanian',
    }
    
    return language_names.get(lang_code, lang_code.upper())

def get_supported_languages() -> Dict[str, str]:
    """
    Get dictionary of supported language codes and names.
    
    Returns:
        Dict[str, str]: Dictionary mapping language codes to names
    """
    return {
        'en': 'English',
        'hi': 'Hindi',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'zh': 'Chinese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'ar': 'Arabic',
        'ru': 'Russian',
        'pt': 'Portuguese',
        'it': 'Italian',
        'nl': 'Dutch',
        'sv': 'Swedish',
        'da': 'Danish',
        'no': 'Norwegian',
        'fi': 'Finnish',
        'pl': 'Polish',
        'tr': 'Turkish',
        'th': 'Thai',
        'vi': 'Vietnamese',
        'id': 'Indonesian',
        'ms': 'Malay',
        'tl': 'Filipino',
        'bn': 'Bengali',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'kn': 'Kannada',
        'gu': 'Gujarati',
        'pa': 'Punjabi',
        'or': 'Odia',
        'as': 'Assamese',
        'ne': 'Nepali',
        'si': 'Sinhala',
        'my': 'Burmese',
        'km': 'Khmer',
        'lo': 'Lao',
        'ka': 'Georgian',
        'hy': 'Armenian',
        'az': 'Azerbaijani',
        'kk': 'Kazakh',
        'ky': 'Kyrgyz',
        'uz': 'Uzbek',
        'tg': 'Tajik',
        'mn': 'Mongolian',
        'bo': 'Tibetan',
        'dz': 'Dzongkha',
        'he': 'Hebrew',
        'fa': 'Persian',
        'ur': 'Urdu',
        'sd': 'Sindhi',
        'ps': 'Pashto',
        'ku': 'Kurdish',
        'sw': 'Swahili',
        'am': 'Amharic',
        'ti': 'Tigrinya',
        'om': 'Oromo',
        'so': 'Somali',
        'ha': 'Hausa',
        'yo': 'Yoruba',
        'ig': 'Igbo',
        'zu': 'Zulu',
        'xh': 'Xhosa',
        'af': 'Afrikaans',
        'is': 'Icelandic',
        'ga': 'Irish',
        'cy': 'Welsh',
        'mt': 'Maltese',
        'eu': 'Basque',
        'ca': 'Catalan',
        'gl': 'Galician',
        'lb': 'Luxembourgish',
        'lv': 'Latvian',
        'lt': 'Lithuanian',
        'et': 'Estonian',
        'sk': 'Slovak',
        'sl': 'Slovenian',
        'hr': 'Croatian',
        'sr': 'Serbian',
        'bs': 'Bosnian',
        'mk': 'Macedonian',
        'bg': 'Bulgarian',
        'ro': 'Romanian',
        'hu': 'Hungarian',
        'cs': 'Czech',
        'uk': 'Ukrainian',
        'be': 'Belarusian',
        'sq': 'Albanian',
    }


def detect_language_with_ai(text: str) -> Optional[str]:
    """
    Detect language using Gemini AI for better accuracy.
    
    Args:
        text (str): Text to detect language for
    
    Returns:
        str: Language code or None if failed
    """
    try:
        from django.conf import settings
        import google.generativeai as genai
        
        if not settings.GEMINI_API_KEY:
            return None
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create AI prompt for language detection
        prompt = f"""
        Detect the language of the following text and respond with only the ISO 639-1 language code (e.g., 'en', 'hi', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar').
        
        Text: {text}
        
        Language code:
        """
        
        # Generate language detection
        response = model.generate_content(prompt)
        language_code = response.text.strip().lower()
        
        # Validate language code
        valid_codes = ['en', 'hi', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'bn', 'gu', 'kn', 'ml', 'mr', 'ne', 'pa', 'ta', 'te', 'ur']
        if language_code in valid_codes:
            logger.info(f"AI language detection successful: {language_code}")
            return language_code
        else:
            logger.warning(f"Invalid language code from AI: {language_code}")
            return None
        
    except Exception as e:
        logger.warning(f"AI language detection failed: {str(e)}")
        return None
