"""
Text-to-Speech service using Google Text-to-Speech (gTTS)
"""

from gtts import gTTS
import os
import uuid
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def text_to_speech(text, language_code='en', output_dir=None, fast_mode=True):
    """
    Convert text to speech using Google Text-to-Speech and save as MP3.
    Optimized for real-time conversation communication.
    
    Args:
        text (str): Text to convert to speech
        language_code (str): Language code (e.g., 'en', 'hi', 'es')
        output_dir (str): Directory to save the audio file (optional)
        fast_mode (bool): Use fast mode for real-time processing
    
    Returns:
        str: Path to the generated audio file
        
    Raises:
        Exception: If text-to-speech conversion fails
    """
    try:
        if not text or not text.strip():
            raise Exception("Text cannot be empty")
        
        # Truncate text for faster processing in real-time mode
        if fast_mode and len(text) > 200:
            text = text[:200] + "..."
            logger.info(f"Text truncated for fast TTS processing: {len(text)} characters")
        
        # Generate unique filename
        filename = f"tts_{uuid.uuid4().hex[:8]}.mp3"
        
        # Set output directory
        if output_dir is None:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'audio')
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Full file path
        filepath = os.path.join(output_dir, filename)
        
        # Generate TTS with optimized settings for real-time
        tts = gTTS(
            text=text, 
            lang=language_code, 
            slow=False,  # Fast speech for real-time
            tld='com'    # Use .com domain for faster response
        )
        tts.save(filepath)
        
        logger.info(f"TTS successful: {language_code} - {filename} (fast_mode: {fast_mode})")
        return filepath
        
    except Exception as e:
        logger.error(f"TTS failed: {str(e)}")
        raise Exception(f"Text-to-speech conversion failed: {str(e)}")


def text_to_speech_bytes(text, language_code='en'):
    """
    Convert text to speech and return audio bytes.
    
    Args:
        text (str): Text to convert to speech
        language_code (str): Language code (e.g., 'en', 'hi', 'es')
    
    Returns:
        bytes: Audio data as bytes
        
    Raises:
        Exception: If text-to-speech conversion fails
    """
    try:
        if not text or not text.strip():
            raise Exception("Text cannot be empty")
        
        # Generate TTS
        tts = gTTS(text=text, lang=language_code, slow=False)
        
        # Save to temporary file and read bytes
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            tts.save(temp_file.name)
            
            # Read the file as bytes
            with open(temp_file.name, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(temp_file.name)
        
        logger.info(f"TTS bytes successful: {language_code}")
        return audio_bytes
        
    except Exception as e:
        logger.error(f"TTS bytes failed: {str(e)}")
        raise Exception(f"Text-to-speech conversion failed: {str(e)}")


def get_supported_tts_languages():
    """
    Get list of supported languages for text-to-speech.
    
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
