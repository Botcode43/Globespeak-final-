"""
Text summarization service using Google Gemini AI
"""

import google.generativeai as genai
import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# Configure Gemini AI (will be configured when needed)
# genai.configure(api_key=settings.GEMINI_API_KEY)


def summarize_text(text, max_length=150):
    """
    Summarize text using Google Gemini AI.
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum length of summary (default: 150)
    
    Returns:
        str: Summarized text
        
    Raises:
        Exception: If summarization fails
    """
    try:
        if not text or not text.strip():
            return ""
        
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured, using simple truncation")
            return simple_summarize(text, max_length)
        
        # Configure Gemini with API key
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create improved prompt for better summarization
        prompt = f"""
        Summarize the following text in simple, clear, and efficient words. 
        Requirements:
        1. Use simple, everyday language that anyone can understand
        2. Focus on the main ideas and key facts only
        3. Remove unnecessary details and repetition
        4. Make it easy to understand and concise
        5. Keep it under {max_length} words
        6. Maintain the original meaning but make it simpler
        
        Text to summarize:
        {text}
        
        Simple and efficient summary:
        """
        
        # Generate summary
        response = model.generate_content(prompt)
        summary = response.text.strip()
        
        logger.info(f"Summarization successful: {len(summary)} characters")
        return summary
        
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        # Fallback to simple summarization
        return simple_summarize(text, max_length)


def simple_summarize(text, max_length=150):
    """
    Simple text summarization by truncating and adding ellipsis.
    Used as fallback when AI summarization is not available.
    
    Args:
        text (str): Text to summarize
        max_length (int): Maximum length of summary
    
    Returns:
        str: Truncated text
    """
    try:
        if len(text) <= max_length:
            return text
        
        # Find the last complete sentence within the limit
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        
        # Find the last sentence ending
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.7:  # If we found a sentence ending in the last 30%
            return text[:last_sentence_end + 1]
        else:
            return text[:max_length - 3] + "..."
            
    except Exception as e:
        logger.error(f"Simple summarization failed: {str(e)}")
        return text[:max_length - 3] + "..."


def extract_keywords(text, num_keywords=10):
    """
    Extract keywords from text using Google Gemini AI.
    
    Args:
        text (str): Text to extract keywords from
        num_keywords (int): Number of keywords to extract (default: 10)
    
    Returns:
        list: List of keywords
        
    Raises:
        Exception: If keyword extraction fails
    """
    try:
        if not text or not text.strip():
            return []
        
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured, using simple keyword extraction")
            return simple_extract_keywords(text, num_keywords)
        
        # Configure Gemini with API key
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for keyword extraction
        prompt = f"""
        Extract the top {num_keywords} most important keywords from the following text.
        Return only the keywords, separated by commas.
        
        Text:
        {text}
        
        Keywords:
        """
        
        # Generate keywords
        response = model.generate_content(prompt)
        keywords_text = response.text.strip()
        
        # Parse keywords
        keywords = [keyword.strip() for keyword in keywords_text.split(',')]
        keywords = [kw for kw in keywords if kw]  # Remove empty strings
        
        logger.info(f"Keyword extraction successful: {len(keywords)} keywords")
        return keywords[:num_keywords]
        
    except Exception as e:
        logger.error(f"Keyword extraction failed: {str(e)}")
        # Fallback to simple keyword extraction
        return simple_extract_keywords(text, num_keywords)


def simple_extract_keywords(text, num_keywords=10):
    """
    Simple keyword extraction by finding most frequent words.
    Used as fallback when AI keyword extraction is not available.
    
    Args:
        text (str): Text to extract keywords from
        num_keywords (int): Number of keywords to extract
    
    Returns:
        list: List of keywords
    """
    try:
        import re
        from collections import Counter
        
        # Convert to lowercase and remove punctuation
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Split into words
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        # Filter out stop words and short words
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequency
        word_count = Counter(filtered_words)
        
        # Get most common keywords
        keywords = [word for word, count in word_count.most_common(num_keywords)]
        
        logger.info(f"Simple keyword extraction successful: {len(keywords)} keywords")
        return keywords
        
    except Exception as e:
        logger.error(f"Simple keyword extraction failed: {str(e)}")
        return []


def analyze_sentiment(text):
    """
    Analyze sentiment of text using Google Gemini AI.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        dict: Sentiment analysis result with 'sentiment' and 'confidence'
        
    Raises:
        Exception: If sentiment analysis fails
    """
    try:
        if not text or not text.strip():
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API key not configured, using simple sentiment analysis")
            return simple_analyze_sentiment(text)
        
        # Configure Gemini with API key
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # Initialize the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for sentiment analysis
        prompt = f"""
        Analyze the sentiment of the following text and respond with only one word: positive, negative, or neutral.
        
        Text:
        {text}
        
        Sentiment:
        """
        
        # Generate sentiment
        response = model.generate_content(prompt)
        sentiment = response.text.strip().lower()
        
        # Validate sentiment
        if sentiment not in ['positive', 'negative', 'neutral']:
            sentiment = 'neutral'
        
        logger.info(f"Sentiment analysis successful: {sentiment}")
        return {'sentiment': sentiment, 'confidence': 0.8}  # Default confidence
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {str(e)}")
        # Fallback to simple sentiment analysis
        return simple_analyze_sentiment(text)


def simple_analyze_sentiment(text):
    """
    Simple sentiment analysis using keyword matching.
    Used as fallback when AI sentiment analysis is not available.
    
    Args:
        text (str): Text to analyze
    
    Returns:
        dict: Sentiment analysis result
    """
    try:
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'awesome',
            'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied', 'perfect', 'best',
            'beautiful', 'brilliant', 'outstanding', 'superb', 'marvelous', 'delightful'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'disgusting', 'hate', 'dislike',
            'angry', 'sad', 'disappointed', 'frustrated', 'annoyed', 'upset', 'worst',
            'ugly', 'stupid', 'dumb', 'boring', 'useless', 'pathetic', 'disgusting'
        }
        
        text_lower = text.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.8, positive_count / 10)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.8, negative_count / 10)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        logger.info(f"Simple sentiment analysis: {sentiment} (confidence: {confidence})")
        return {'sentiment': sentiment, 'confidence': confidence}
        
    except Exception as e:
        logger.error(f"Simple sentiment analysis failed: {str(e)}")
        return {'sentiment': 'neutral', 'confidence': 0.0}
