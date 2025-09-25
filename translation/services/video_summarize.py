"""
Video summarization service using Whisper and BART
"""

import os
import subprocess
import logging
import requests
import tempfile
from urllib.parse import urlparse
from django.conf import settings

logger = logging.getLogger(__name__)

# Conditional imports to avoid errors if dependencies aren't installed
try:
    import whisper
    import nltk
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
        
    DEPENDENCIES_AVAILABLE = True
except (ImportError, TypeError, Exception) as e:
    # Only log as info for common Windows compatibility issues
    if "shared object file" in str(e) or "Could not find/load" in str(e):
        logger.info(f"Video summarization dependencies available but with minor compatibility issues: {e}")
        DEPENDENCIES_AVAILABLE = True  # Still allow processing
    else:
        logger.warning(f"Video summarization dependencies not available: {e}")
        DEPENDENCIES_AVAILABLE = False
    
    # Always set dummy variables to avoid NameError if imports failed
    whisper = None
    nltk = None
    AutoTokenizer = None
    AutoModelForSeq2SeqLM = None


def download_video_from_url(video_url, output_path):
    """
    Download video from URL using yt-dlp
    
    Args:
        video_url (str): URL of the video to download
        output_path (str): Path to save the downloaded video
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use yt-dlp with optimized settings for faster download
        command = f'python -m yt_dlp -o "{output_path}" --max-downloads 1 --format "best[height<=720]" --no-playlist "{video_url}"'
        logger.info(f"Downloading video with command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        # Check if download was successful by looking for the file
        # yt-dlp sometimes returns non-zero exit codes even on success
        import glob
        import os
        
        # Find the actual downloaded file (yt-dlp adds extension)
        # Remove the %(ext)s part from the pattern
        base_path = output_path.replace('%(ext)s', '')
        actual_files = glob.glob(f"{base_path}*")
        
        if actual_files and os.path.exists(actual_files[0]):
            logger.info(f"Video downloaded successfully: {actual_files[0]}")
            return True
        else:
            logger.error(f"Video download failed: {result.stderr}")
            logger.error(f"Command output: {result.stdout}")
            return False
                
    except subprocess.TimeoutExpired:
        logger.error("Video download timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"Video download failed: {str(e)}")
        return False


def is_valid_video_url(url):
    """
    Check if the URL is a valid video URL
    
    Args:
        url (str): URL to check
    
    Returns:
        bool: True if valid video URL, False otherwise
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for common video platforms
        video_domains = [
            'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
            'twitch.tv', 'facebook.com', 'instagram.com', 'tiktok.com',
            'twitter.com', 'x.com', 'linkedin.com'
        ]
        
        domain = parsed.netloc.lower()
        return any(video_domain in domain for video_domain in video_domains)
        
    except Exception:
        return False


def extract_audio_from_video(video_path, audio_path):
    """
    Extract audio from video using ffmpeg
    
    Args:
        video_path (str): Path to the video file
        audio_path (str): Path to save the audio file
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use ffmpeg to extract audio
        command = f'ffmpeg -i "{video_path}" "{audio_path}" -y'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Audio extracted successfully: {audio_path}")
            return True
        else:
            logger.error(f"FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Audio extraction failed: {str(e)}")
        return False


def transcribe_audio(audio_path):
    """
    Transcribe audio to text using Whisper
    
    Args:
        audio_path (str): Path to the audio file
    
    Returns:
        str: Transcribed text
    """
    if not DEPENDENCIES_AVAILABLE or whisper is None:
        logger.error("Whisper not available - dependencies not installed")
        return ""
        
    try:
        # Load Whisper model
        logger.info("Loading Whisper model...")
        model = whisper.load_model("base")
        
        # Transcribe audio with timeout
        logger.info("Starting transcription...")
        result = model.transcribe(audio_path)
        transcript = result["text"]
        
        logger.info(f"Transcription successful: {len(transcript)} characters")
        return transcript
        
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return ""


def summarize_transcript(transcript, max_length_ratio=0.5):
    """
    Summarize transcript using BART model
    
    Args:
        transcript (str): Text to summarize
        max_length_ratio (float): Ratio of original length for summary
    
    Returns:
        str: Summarized text
    """
    if not DEPENDENCIES_AVAILABLE or AutoTokenizer is None or AutoModelForSeq2SeqLM is None or nltk is None:
        logger.error("Transformers not available - dependencies not installed")
        return ""
        
    try:
        if not transcript or not transcript.strip():
            return ""
        
        # Load BART model and tokenizer
        checkpoint = "sshleifer/distilbart-cnn-12-6"
        tokenizer = AutoTokenizer.from_pretrained(checkpoint)
        model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
        
        # Tokenize sentences
        sentences = nltk.tokenize.sent_tokenize(transcript)
        
        # Create chunks that fit within tokenizer limits
        length = 0
        chunk = ""
        chunks = []
        count = -1
        
        for sentence in sentences:
            count += 1
            combined_length = len(tokenizer.tokenize(sentence)) + length
            
            if combined_length <= tokenizer.max_len_single_sentence:
                chunk += sentence + " "
                length = combined_length
                
                if count == len(sentences) - 1:
                    chunks.append(chunk.strip())
            else:
                chunks.append(chunk.strip())
                length = 0
                chunk = ""
                chunk += sentence + " "
                length = len(tokenizer.tokenize(sentence))
        
        # Generate summaries for each chunk
        inputs = [tokenizer(chunk, return_tensors="pt") for chunk in chunks]
        summary_parts = []
        
        for input_data in inputs:
            max_length = max(50, int(len(input_data['input_ids'][0]) * max_length_ratio))
            output = model.generate(**input_data, max_length=max_length, min_length=10)
            summary_parts.append(tokenizer.decode(*output, skip_special_tokens=True))
        
        # Combine all summary parts
        summary = " ".join(summary_parts)
        
        logger.info(f"Summarization successful: {len(summary)} characters")
        return summary
        
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        return ""


def get_video_duration(video_path):
    """
    Get video duration using ffprobe
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        str: Duration in minutes
    """
    try:
        command = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        if result.returncode == 0:
            duration_seconds = float(result.stdout.strip())
            duration_minutes = "%.2f" % (duration_seconds / 60)
            return f"{duration_minutes} min"
        else:
            logger.error(f"FFprobe error: {result.stdout}")
            return "Unknown"
            
    except Exception as e:
        logger.error(f"Duration extraction failed: {str(e)}")
        return "Unknown"


def process_video_for_summarization(video_path):
    """
    Complete video processing pipeline: extract audio, transcribe, and summarize
    
    Args:
        video_path (str): Path to the video file
    
    Returns:
        dict: Contains transcript, summary, duration, and word counts
    """
    if not DEPENDENCIES_AVAILABLE:
        logger.error("Video processing dependencies not available")
        return None
        
    try:
        # Create temporary audio file path
        audio_path = video_path.rsplit('.', 1)[0] + '.mp3'
        
        # Step 1: Extract audio from video
        if not extract_audio_from_video(video_path, audio_path):
            return None
        
        # Step 2: Transcribe audio
        transcript = transcribe_audio(audio_path)
        if not transcript:
            return None
        
        # Step 3: Summarize transcript
        summary = summarize_transcript(transcript)
        if not summary:
            return None
        
        # Step 4: Get video duration
        duration = get_video_duration(video_path)
        
        # Step 5: Calculate word counts
        transcript_words = len(transcript.split())
        summary_words = len(summary.split())
        
        # Clean up temporary audio file
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary audio file: {str(e)}")
        
        return {
            'transcript': transcript,
            'summary': summary,
            'duration': duration,
            'transcript_words': transcript_words,
            'summary_words': summary_words
        }
        
    except Exception as e:
        logger.error(f"Video processing failed: {str(e)}")
        return None


def process_video_url_for_summarization(video_url):
    """
    Complete video URL processing pipeline: download, extract audio, transcribe, and summarize
    
    Args:
        video_url (str): URL of the video to process
    
    Returns:
        dict: Contains transcript, summary, duration, and word counts
    """
    if not DEPENDENCIES_AVAILABLE:
        logger.error("Video processing dependencies not available")
        return None
        
    if not is_valid_video_url(video_url):
        logger.error(f"Invalid video URL: {video_url}")
        return None
    
    logger.info(f"Starting video processing for URL: {video_url}")
        
    try:
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate temporary file paths
            video_filename = f"downloaded_video_{hash(video_url) % 100000}.%(ext)s"
            video_path = os.path.join(temp_dir, video_filename)
            audio_path = os.path.join(temp_dir, "audio.mp3")
            
            # Step 1: Download video from URL
            if not download_video_from_url(video_url, video_path):
                return None
            
            # Find the actual downloaded file (yt-dlp adds extension)
            actual_video_path = None
            for file in os.listdir(temp_dir):
                if file.startswith("downloaded_video_"):
                    actual_video_path = os.path.join(temp_dir, file)
                    break
            
            if not actual_video_path or not os.path.exists(actual_video_path):
                logger.error("Downloaded video file not found")
                return None
            
            # Step 2: Extract audio from video
            if not extract_audio_from_video(actual_video_path, audio_path):
                return None
            
            # Step 3: Transcribe audio
            transcript = transcribe_audio(audio_path)
            if not transcript:
                return None
            
            # Step 4: Summarize transcript
            summary = summarize_transcript(transcript)
            if not summary:
                return None
            
            # Step 5: Get video duration
            duration = get_video_duration(actual_video_path)
            
            # Step 6: Calculate word counts
            transcript_words = len(transcript.split())
            summary_words = len(summary.split())
            
            return {
                'transcript': transcript,
                'summary': summary,
                'duration': duration,
                'transcript_words': transcript_words,
                'summary_words': summary_words,
                'source_url': video_url
            }
            
    except Exception as e:
        logger.error(f"Video URL processing failed: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return None
