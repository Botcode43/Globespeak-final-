"""
OCR (Optical Character Recognition) service using Tesseract
"""

import cv2
import pytesseract
import logging
import os

logger = logging.getLogger(__name__)

# # Configure Tesseract path for your installation
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Try to detect Tesseract automatically
try:
    pytesseract.get_tesseract_version()
    TESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR detected and configured successfully!")
except Exception as e:
    TESSERACT_AVAILABLE = False
    logger.warning(f"Tesseract OCR not found: {str(e)}")
    logger.info("Please check the Tesseract installation path.")

# Add all supported languages for Tesseract OCR
LANGUAGES = (
    "hin+eng+tam+tel+kan+mal+ben+guj+pan+mar+"
    "asm+ori+urd+san+nep+snd+"
    "ara+jpn+chi_sim+chi_tra+kor+tha+"
    "fra+deu+spa+ita+por+rus+ukr+pol+tur+"
    "nld+swe+dan+fin+nor+hun+ces+slk+ron+bul+srp+hrv+"
    "gre+heb+vie+ind+msa+fil+lat+est+lit+slv+isl"
)

# Supported languages for OCR (for reference and UI)
SUPPORTED_OCR_LANGUAGES = {
    'eng': 'English',
    'hin': 'Hindi',
    'tam': 'Tamil',
    'tel': 'Telugu',
    'kan': 'Kannada',
    'mal': 'Malayalam',
    'ben': 'Bengali',
    'guj': 'Gujarati',
    'pan': 'Punjabi',
    'mar': 'Marathi',
    'asm': 'Assamese',
    'ori': 'Odia',
    'urd': 'Urdu',
    'san': 'Sanskrit',
    'nep': 'Nepali',
    'snd': 'Sindhi',
    'ara': 'Arabic',
    'jpn': 'Japanese',
    'chi_sim': 'Chinese (Simplified)',
    'chi_tra': 'Chinese (Traditional)',
    'kor': 'Korean',
    'tha': 'Thai',
    'fra': 'French',
    'deu': 'German',
    'spa': 'Spanish',
    'ita': 'Italian',
    'por': 'Portuguese',
    'rus': 'Russian',
    'ukr': 'Ukrainian',
    'pol': 'Polish',
    'tur': 'Turkish',
    'nld': 'Dutch',
    'swe': 'Swedish',
    'dan': 'Danish',
    'fin': 'Finnish',
    'nor': 'Norwegian',
    'hun': 'Hungarian',
    'ces': 'Czech',
    'slk': 'Slovak',
    'ron': 'Romanian',
    'bul': 'Bulgarian',
    'srp': 'Serbian',
    'hrv': 'Croatian',
    'gre': 'Greek',
    'heb': 'Hebrew',
    'vie': 'Vietnamese',
    'ind': 'Indonesian',
    'msa': 'Malay',
    'fil': 'Filipino',
    'lat': 'Latin',
    'est': 'Estonian',
    'lit': 'Lithuanian',
    'slv': 'Slovenian',
    'isl': 'Icelandic',
}


def extract_text_from_image(image_path, language='eng', preprocess=True):
    """
    Extract text from an image using Tesseract OCR with multi-language support.
    
    Args:
        image_path (str): Path to the image file
        language (str): Language code for OCR (default: 'eng') - used for fallback
        preprocess (bool): Whether to preprocess the image for better OCR
    
    Returns:
        str: Extracted text
        
    Raises:
        Exception: If OCR extraction fails
    """
    try:
        # Check if Tesseract is available
        if not TESSERACT_AVAILABLE:
            raise Exception("Tesseract OCR is not installed or not in PATH. Please install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki")
        
        # Check if image file exists
        if not os.path.exists(image_path):
            raise Exception(f"Image file not found: {image_path}")
        
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            raise Exception("Could not read image file")
        
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Preprocess image for better OCR results
        if preprocess:
            gray = preprocess_image(gray)
        
        # First try with multi-language OCR for better accuracy
        try:
            text = pytesseract.image_to_string(gray, lang=LANGUAGES)
            if text.strip():  # If we got results with multi-language
                logger.info(f"Multi-language OCR successful: {len(text)} characters extracted")
                return text.strip()
        except Exception as e:
            logger.warning(f"Multi-language OCR failed, trying single language: {str(e)}")
        
        # Fallback to single language if multi-language fails
        text = pytesseract.image_to_string(gray, lang=language)
        
        # Clean up the text
        text = text.strip()
        
        logger.info(f"OCR successful: {language} - {len(text)} characters extracted")
        return text
        
    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise Exception(f"OCR extraction failed: {str(e)}")


def enhance_ocr_with_ai(extracted_text, image_path=None):
    """
    Enhance OCR results using Gemini AI for better accuracy and context.
    
    Args:
        extracted_text (str): Text extracted by OCR
        image_path (str): Path to the original image (optional)
    
    Returns:
        str: Enhanced text or original text if enhancement fails
    """
    try:
        from django.conf import settings
        import google.generativeai as genai
        
        if not settings.GEMINI_API_KEY or not extracted_text:
            return extracted_text
        
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create AI prompt for OCR enhancement
        prompt = f"""
        The following text was extracted from an image using OCR (Optical Character Recognition). 
        Please clean up and enhance this text by:
        1. Fixing obvious OCR errors and typos
        2. Correcting spacing and punctuation
        3. Improving readability while preserving the original meaning
        4. Maintaining the original structure and format
        5. If the text appears to be in a non-English language, preserve it as is
        
        OCR Extracted Text:
        {extracted_text}
        
        Enhanced Text:
        """
        
        # Generate enhanced text
        response = model.generate_content(prompt)
        enhanced_text = response.text.strip()
        
        logger.info(f"OCR enhancement successful: {len(enhanced_text)} characters")
        return enhanced_text
        
    except Exception as e:
        logger.warning(f"OCR enhancement failed: {str(e)}")
        return extracted_text


def preprocess_image(image):
    """
    Preprocess image for better OCR results.
    
    Args:
        image: OpenCV image object (can be grayscale or color)
    
    Returns:
        OpenCV image object: Preprocessed image
    """
    try:
        # Convert to grayscale if it's a color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
        
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {str(e)}")
        return image


def extract_text_from_image_bytes(image_bytes, language='eng', preprocess=True):
    """
    Extract text from image bytes using Tesseract OCR with multi-language support.
    
    Args:
        image_bytes (bytes): Image data as bytes
        language (str): Language code for OCR (default: 'eng') - used for fallback
        preprocess (bool): Whether to preprocess the image for better OCR
    
    Returns:
        str: Extracted text
        
    Raises:
        Exception: If OCR extraction fails
    """
    try:
        import tempfile
        import numpy as np
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise Exception("Could not decode image from bytes")
        
        # Convert to grayscale for better OCR
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Preprocess image for better OCR results
        if preprocess:
            gray = preprocess_image(gray)
        
        # First try with multi-language OCR for better accuracy
        try:
            text = pytesseract.image_to_string(gray, lang=LANGUAGES)
            if text.strip():  # If we got results with multi-language
                logger.info(f"Multi-language OCR from bytes successful: {len(text)} characters extracted")
                return text.strip()
        except Exception as e:
            logger.warning(f"Multi-language OCR from bytes failed, trying single language: {str(e)}")
        
        # Fallback to single language if multi-language fails
        text = pytesseract.image_to_string(gray, lang=language)
        
        # Clean up the text
        text = text.strip()
        
        logger.info(f"OCR from bytes successful: {language} - {len(text)} characters extracted")
        return text
        
    except Exception as e:
        logger.error(f"OCR from bytes failed: {str(e)}")
        raise Exception(f"OCR extraction failed: {str(e)}")


def get_supported_ocr_languages():
    """
    Get list of supported languages for OCR.
    
    Returns:
        dict: Dictionary of language codes and names
    """
    return SUPPORTED_OCR_LANGUAGES


def detect_language_in_image(image_path):
    """
    Attempt to detect the language of text in an image.
    
    Args:
        image_path (str): Path to the image file
    
    Returns:
        str: Detected language code or 'eng' as default
    """
    try:
        # Try with multiple languages and see which gives the best result
        languages_to_try = ['eng', 'hin', 'spa', 'fra', 'deu', 'chi_sim', 'jpn', 'ara']
        best_result = ""
        best_language = 'eng'
        
        for lang in languages_to_try:
            try:
                text = extract_text_from_image(image_path, language=lang, preprocess=True)
                if len(text.strip()) > len(best_result.strip()):
                    best_result = text
                    best_language = lang
            except:
                continue
        
        logger.info(f"Language detection result: {best_language}")
        return best_language
        
    except Exception as e:
        logger.warning(f"Language detection failed: {str(e)}")
        return 'eng'  # Default to English
