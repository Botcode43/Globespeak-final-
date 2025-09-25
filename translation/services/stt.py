"""
Speech-to-Text service using Google Speech Recognition
"""

import speech_recognition as sr
import tempfile
import os
import logging
import wave
import struct
from io import BytesIO

logger = logging.getLogger(__name__)


def speech_to_text_from_file(audio_file_path, language_code='en-US'):
    """
    Convert speech from audio file to text using Google Speech Recognition.
    
    Args:
        audio_file_path (str): Path to audio file
        language_code (str): Language code (e.g., 'en-US', 'hi-IN')
    
    Returns:
        str: Recognized text
        
    Raises:
        Exception: If speech recognition fails
    """
    try:
        recognizer = sr.Recognizer()
        
        with sr.AudioFile(audio_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.record(source)
        
        # Recognize speech using Google Speech Recognition
        text = recognizer.recognize_google(audio, language=language_code)
        
        logger.info(f"Speech recognition successful: {language_code}")
        return text
        
    except sr.UnknownValueError:
        logger.warning("Google Speech Recognition could not understand audio")
        return ""
    except sr.RequestError as e:
        logger.error(f"Could not request results from Google Speech Recognition service: {e}")
        raise Exception(f"Speech recognition service error: {e}")
    except Exception as e:
        logger.error(f"Speech recognition failed: {str(e)}")
        raise Exception(f"Speech recognition failed: {str(e)}")


def speech_to_text_from_bytes(audio_bytes, language_code='en-US'):
    """
    Convert speech from audio bytes to text using Google Speech Recognition.
    
    Args:
        audio_bytes (bytes): Audio data as bytes
        language_code (str): Language code (e.g., 'en-US', 'hi-IN')
    
    Returns:
        str: Recognized text
        
    Raises:
        Exception: If speech recognition fails
    """
    try:
        # Try direct recognition first (most efficient)
        recognizer = sr.Recognizer()
        
        # Try different audio parameters
        audio_params = [
            (16000, 2),  # 16kHz, 16-bit
            (44100, 2),  # 44.1kHz, 16-bit
            (8000, 2),   # 8kHz, 16-bit
        ]
        
        for sample_rate, sample_width in audio_params:
            try:
                audio_data = sr.AudioData(audio_bytes, sample_rate, sample_width)
                text = recognizer.recognize_google(audio_data, language=language_code)
                if text and text.strip():
                    logger.info(f"Direct speech recognition successful: {language_code} (rate: {sample_rate})")
                    return text
            except Exception as e:
                logger.warning(f"Direct recognition failed with rate {sample_rate}: {str(e)}")
                continue
        
        # If direct recognition fails, try with temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_file_path = temp_file.name
        
        try:
            result = speech_to_text_from_file(temp_file_path, language_code)
            if result and result.strip():
                logger.info(f"File-based speech recognition successful: {language_code}")
                return result
            else:
                logger.warning("No speech detected in audio")
                return ""
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Speech recognition from bytes failed: {str(e)}")
        raise Exception(f"Speech recognition failed: {str(e)}")


def get_supported_stt_languages():
    """
    Get list of supported languages for speech recognition.
    
    Returns:
        dict: Dictionary of language codes and names
    """
    return {
        'en-US': 'English (US)',
        'en-GB': 'English (UK)',
        'en-AU': 'English (Australia)',
        'en-CA': 'English (Canada)',
        'en-IN': 'English (India)',
        'hi-IN': 'Hindi (India)',
        'es-ES': 'Spanish (Spain)',
        'es-MX': 'Spanish (Mexico)',
        'es-AR': 'Spanish (Argentina)',
        'fr-FR': 'French (France)',
        'fr-CA': 'French (Canada)',
        'de-DE': 'German (Germany)',
        'it-IT': 'Italian (Italy)',
        'pt-BR': 'Portuguese (Brazil)',
        'pt-PT': 'Portuguese (Portugal)',
        'ru-RU': 'Russian (Russia)',
        'ja-JP': 'Japanese (Japan)',
        'ko-KR': 'Korean (South Korea)',
        'zh-CN': 'Chinese (Simplified)',
        'zh-TW': 'Chinese (Traditional)',
        'ar-SA': 'Arabic (Saudi Arabia)',
        'bn-BD': 'Bengali (Bangladesh)',
        'gu-IN': 'Gujarati (India)',
        'kn-IN': 'Kannada (India)',
        'ml-IN': 'Malayalam (India)',
        'mr-IN': 'Marathi (India)',
        'ne-NP': 'Nepali (Nepal)',
        'pa-IN': 'Punjabi (India)',
        'ta-IN': 'Tamil (India)',
        'te-IN': 'Telugu (India)',
        'ur-PK': 'Urdu (Pakistan)',
        'th-TH': 'Thai (Thailand)',
        'vi-VN': 'Vietnamese (Vietnam)',
        'tr-TR': 'Turkish (Turkey)',
        'pl-PL': 'Polish (Poland)',
        'nl-NL': 'Dutch (Netherlands)',
        'sv-SE': 'Swedish (Sweden)',
        'da-DK': 'Danish (Denmark)',
        'no-NO': 'Norwegian (Norway)',
        'fi-FI': 'Finnish (Finland)',
        'cs-CZ': 'Czech (Czech Republic)',
        'hu-HU': 'Hungarian (Hungary)',
        'ro-RO': 'Romanian (Romania)',
        'bg-BG': 'Bulgarian (Bulgaria)',
        'hr-HR': 'Croatian (Croatia)',
        'sk-SK': 'Slovak (Slovakia)',
        'sl-SI': 'Slovenian (Slovenia)',
        'et-EE': 'Estonian (Estonia)',
        'lv-LV': 'Latvian (Latvia)',
        'lt-LT': 'Lithuanian (Lithuania)',
        'mt-MT': 'Maltese (Malta)',
        'cy-GB': 'Welsh (UK)',
        'ga-IE': 'Irish (Ireland)',
        'is-IS': 'Icelandic (Iceland)',
        'mk-MK': 'Macedonian (North Macedonia)',
        'sq-AL': 'Albanian (Albania)',
        'sr-RS': 'Serbian (Serbia)',
        'bs-BA': 'Bosnian (Bosnia)',
        'uk-UA': 'Ukrainian (Ukraine)',
        'be-BY': 'Belarusian (Belarus)',
        'ka-GE': 'Georgian (Georgia)',
        'hy-AM': 'Armenian (Armenia)',
        'az-AZ': 'Azerbaijani (Azerbaijan)',
        'kk-KZ': 'Kazakh (Kazakhstan)',
        'ky-KG': 'Kyrgyz (Kyrgyzstan)',
        'uz-UZ': 'Uzbek (Uzbekistan)',
        'tg-TJ': 'Tajik (Tajikistan)',
        'mn-MN': 'Mongolian (Mongolia)',
        'my-MM': 'Burmese (Myanmar)',
        'km-KH': 'Khmer (Cambodia)',
        'lo-LA': 'Lao (Laos)',
        'si-LK': 'Sinhala (Sri Lanka)',
        'dz-BT': 'Dzongkha (Bhutan)',
        'bo-CN': 'Tibetan (China)',
        'am-ET': 'Amharic (Ethiopia)',
        'sw-KE': 'Swahili (Kenya)',
        'zu-ZA': 'Zulu (South Africa)',
        'af-ZA': 'Afrikaans (South Africa)',
        'eu-ES': 'Basque (Spain)',
        'ca-ES': 'Catalan (Spain)',
        'gl-ES': 'Galician (Spain)',
        'he-IL': 'Hebrew (Israel)',
        'fa-IR': 'Persian (Iran)',
        'ps-AF': 'Pashto (Afghanistan)',
        'sd-PK': 'Sindhi (Pakistan)',
        'or-IN': 'Odia (India)',
        'as-IN': 'Assamese (India)',
        'sa-IN': 'Sanskrit (India)',
    }
