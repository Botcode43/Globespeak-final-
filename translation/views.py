"""
Views for the translation app
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import os
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
from .models import TranslationHistory, Video, VideoSummary
from .services.translate import translate_text, get_supported_languages
from .services.stt import speech_to_text_from_file, speech_to_text_from_bytes, get_supported_stt_languages

def limit_translation_history(user, max_entries=5):
    """
    Keep only the last max_entries translations for a user
    """
    try:
        # Get all translations for the user, ordered by creation date (newest first)
        all_translations = TranslationHistory.objects.filter(user=user).order_by('-created_at')
        
        # If we have more than max_entries, delete the oldest ones
        if all_translations.count() > max_entries:
            translations_to_delete = all_translations[max_entries:]
            for translation in translations_to_delete:
                translation.delete()
            logger.info(f"Deleted {len(translations_to_delete)} old translations for user {user.username}")
    except Exception as e:
        logger.error(f"Error limiting translation history: {str(e)}")

def convert_to_stt_language_code(lang_code):
    """
    Convert language code to speech recognition format (with country codes)
    """
    stt_mapping = {
        'en': 'en-US',
        'hi': 'hi-IN',
        'es': 'es-ES',
        'fr': 'fr-FR',
        'de': 'de-DE',
        'it': 'it-IT',
        'pt': 'pt-PT',
        'ru': 'ru-RU',
        'ja': 'ja-JP',
        'ko': 'ko-KR',
        'zh': 'zh-CN',
        'ar': 'ar-SA',
        'bn': 'bn-BD',
        'gu': 'gu-IN',
        'kn': 'kn-IN',
        'ml': 'ml-IN',
        'mr': 'mr-IN',
        'ne': 'ne-NP',
        'pa': 'pa-IN',
        'ta': 'ta-IN',
        'te': 'te-IN',
        'ur': 'ur-PK',
        'th': 'th-TH',
        'vi': 'vi-VN',
        'tr': 'tr-TR',
        'pl': 'pl-PL',
        'nl': 'nl-NL',
        'sv': 'sv-SE',
        'da': 'da-DK',
        'no': 'no-NO',
        'fi': 'fi-FI',
        'cs': 'cs-CZ',
        'hu': 'hu-HU',
        'ro': 'ro-RO',
        'bg': 'bg-BG',
        'hr': 'hr-HR',
        'sk': 'sk-SK',
        'sl': 'sl-SI',
        'et': 'et-EE',
        'lv': 'lv-LV',
        'lt': 'lt-LT',
        'mt': 'mt-MT',
        'cy': 'cy-GB',
        'ga': 'ga-IE',
        'is': 'is-IS',
        'mk': 'mk-MK',
        'sq': 'sq-AL',
        'sr': 'sr-RS',
        'bs': 'bs-BA',
        'uk': 'uk-UA',
        'be': 'be-BY',
        'ka': 'ka-GE',
        'hy': 'hy-AM',
        'az': 'az-AZ',
        'kk': 'kk-KZ',
        'ky': 'ky-KG',
        'uz': 'uz-UZ',
        'tg': 'tg-TJ',
        'mn': 'mn-MN',
        'my': 'my-MM',
        'km': 'km-KH',
        'lo': 'lo-LA',
        'si': 'si-LK',
        'dz': 'dz-BT',
        'bo': 'bo-CN',
        'am': 'am-ET',
        'sw': 'sw-KE',
        'zu': 'zu-ZA',
        'af': 'af-ZA',
        'eu': 'eu-ES',
        'ca': 'ca-ES',
        'gl': 'gl-ES',
        'he': 'he-IL',
        'fa': 'fa-IR',
        'ps': 'ps-AF',
        'sd': 'sd-PK',
        'or': 'or-IN',
        'as': 'as-IN',
        'sa': 'sa-IN',
    }
    return stt_mapping.get(lang_code, 'en-US')
from .services.tts import text_to_speech, get_supported_tts_languages
from .services.ocr import extract_text_from_image, get_supported_ocr_languages
from .services.summarize import summarize_text, extract_keywords, analyze_sentiment
from .services.ai_partner import generate_partner_reply
from .services.video_summarize import process_video_for_summarization, process_video_url_for_summarization, is_valid_video_url
from django.db import models


def home(request):
    """Home page - redirect to dashboard if authenticated, otherwise to login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires when browser closes
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'translation/login.html')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not all([username, email, password, confirm_password]):
            messages.error(request, 'Please fill in all fields.')
        elif password != confirm_password:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        else:
            from django.contrib.auth.models import User
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                login(request, user)
                messages.success(request, f'Account created successfully! Welcome, {username}!')
                return redirect('dashboard')
    
    return render(request, 'translation/register.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get recent translation history
    recent_translations = TranslationHistory.objects.filter(user=request.user)[:5]
    
    # Conversation rooms removed - feature deleted
    
    context = {
        'recent_translations': recent_translations,
        'supported_languages': get_supported_languages(),
    }
    
    return render(request, 'translation/dashboard.html', context)


@login_required
def text_translation(request):
    """Text translation view"""
    if request.method == 'POST':
        text = request.POST.get('text')
        source_lang = request.POST.get('source_lang', 'en')
        target_lang = request.POST.get('target_lang', 'hi')
        
        if text and text.strip():
            try:
                # Translate text
                translated_text = translate_text(text, source_lang, target_lang)
                
                # Generate TTS if requested
                audio_url = None
                if request.POST.get('generate_audio') == 'on':
                    try:
                        filepath = text_to_speech(translated_text, target_lang)
                        audio_url = f"/media/audio/{os.path.basename(filepath)}"
                    except Exception as e:
                        messages.warning(request, f'Audio generation failed: {str(e)}')
                
                # Save to history
                TranslationHistory.objects.create(
                    user=request.user,
                    translation_type='text',
                    source_language=source_lang,
                    target_language=target_lang,
                    original_text=text,
                    translated_text=translated_text,
                    audio_file=audio_url
                )
                
                # Limit translation history to last 5 entries
                limit_translation_history(request.user)
                
                context = {
                    'original_text': text,
                    'translated_text': translated_text,
                    'source_lang': source_lang,
                    'target_lang': target_lang,
                    'audio_url': audio_url,
                    'supported_languages': get_supported_languages(),
                }
                
                return render(request, 'translation/text_translation.html', context)
                
            except Exception as e:
                messages.error(request, f'Translation failed: {str(e)}')
        else:
            messages.error(request, 'Please enter text to translate.')
    
    context = {
        'supported_languages': get_supported_languages(),
    }
    
    return render(request, 'translation/text_translation.html', context)




@login_required
def simple_conversation(request):
    """Simple Google Translate-style conversation"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'supported_languages': get_supported_languages(),
    }
    
    return render(request, 'translation/simple_conversation.html', context)





# All conversation API functions removed


@login_required
def image_translation(request):
    """Image translation (OCR) view"""
    if request.method == 'POST':
        if 'image' in request.FILES:
            image_file = request.FILES['image']
            target_lang = request.POST.get('target_lang', 'en')
            
            try:
                # Save uploaded image
                filename = f"ocr_{uuid.uuid4().hex[:8]}_{image_file.name}"
                filepath = default_storage.save(f'images/{filename}', ContentFile(image_file.read()))
                full_path = os.path.join(settings.MEDIA_ROOT, filepath)
                
                # Extract text from image
                extracted_text = extract_text_from_image(full_path)
                
                if extracted_text and extracted_text.strip():
                    # Translate extracted text
                    translated_text = translate_text(extracted_text, 'auto', target_lang)
                    
                    # Save to history
                    TranslationHistory.objects.create(
                        user=request.user,
                        translation_type='image',
                        source_language='auto',
                        target_language=target_lang,
                        original_text=extracted_text,
                        translated_text=translated_text,
                        image_file=filepath
                    )
                    
                    # Limit translation history to last 5 entries
                    limit_translation_history(request.user)
                    
                    context = {
                        'extracted_text': extracted_text,
                        'translated_text': translated_text,
                        'target_lang': target_lang,
                        'image_url': f"/media/{filepath}",
                        'supported_languages': get_supported_languages(),
                        'supported_ocr_languages': get_supported_ocr_languages(),
                    }
                    
                    return render(request, 'translation/image_translation.html', context)
                else:
                    messages.error(request, 'No text could be extracted from the image.')
                    
            except Exception as e:
                messages.error(request, f'Image processing failed: {str(e)}')
        else:
            messages.error(request, 'Please select an image file.')
    
    context = {
        'supported_languages': get_supported_languages(),
        'supported_ocr_languages': get_supported_ocr_languages(),
    }
    
    return render(request, 'translation/image_translation.html', context)


@login_required
def history(request):
    """Translation history view"""
    translations = TranslationHistory.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by type if specified
    translation_type = request.GET.get('type')
    if translation_type:
        translations = translations.filter(translation_type=translation_type)
    
    context = {
        'translations': translations,
        'selected_type': translation_type,
    }
    
    return render(request, 'translation/history.html', context)


@login_required
def summarize(request):
    """Text summarization view"""
    if request.method == 'POST':
        text = request.POST.get('text')
        max_length = int(request.POST.get('max_length', 150))
        
        if text and text.strip():
            try:
                # Summarize text
                summary = summarize_text(text, max_length)
                
                # Extract keywords
                keywords = extract_keywords(text, 10)
                
                # Analyze sentiment
                sentiment = analyze_sentiment(text)
                
                # Save to history
                TranslationHistory.objects.create(
                    user=request.user,
                    translation_type='summarize',
                    source_language='en',
                    target_language='en',
                    original_text=text,
                    translated_text=summary,
                    summary=f"Keywords: {', '.join(keywords)} | Sentiment: {sentiment['sentiment']}"
                )
                
                # Limit translation history to last 5 entries
                limit_translation_history(request.user)
                
                context = {
                    'original_text': text,
                    'summary': summary,
                    'keywords': keywords,
                    'sentiment': sentiment,
                    'max_length': max_length,
                }
                
                return render(request, 'translation/summarize.html', context)
                
            except Exception as e:
                messages.error(request, f'Summarization failed: {str(e)}')
        else:
            messages.error(request, 'Please enter text to summarize.')
    
    return render(request, 'translation/summarize.html')




# API Views for AJAX requests
@login_required
@require_http_methods(["POST"])
def api_translate(request):
    """API endpoint for text translation"""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        source_lang = data.get('source_lang', 'en')
        target_lang = data.get('target_lang', 'hi')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        translated_text = translate_text(text, source_lang, target_lang)
        
        return JsonResponse({
            'original_text': text,
            'translated_text': translated_text,
            'source_lang': source_lang,
            'target_lang': target_lang
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_tts(request):
    """API endpoint for text-to-speech"""
    try:
        data = json.loads(request.body)
        text = data.get('text')
        language = data.get('language', 'en')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        filepath = text_to_speech(text, language)
        audio_url = f"/media/audio/{os.path.basename(filepath)}"
        
        return JsonResponse({
            'audio_url': audio_url,
            'text': text,
            'language': language
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_process_conversation_audio(request):
    """API endpoint for processing conversation audio"""
    try:
        data = json.loads(request.body)
        audio_data = data.get('audio_data')
        source_language = data.get('source_language', 'en')
        target_language = data.get('target_language', 'hi')
        speaker = data.get('speaker', 'me')
        
        if not audio_data:
            return JsonResponse({'success': False, 'error': 'No audio data provided'}, status=400)
        
        # Decode audio
        import base64
        
        audio_bytes = base64.b64decode(audio_data.split(',')[1])
        
        # Convert language codes for speech recognition (needs country codes)
        stt_source_lang = convert_to_stt_language_code(source_language)
        
        # Speech to text (the improved function will handle format conversion)
        transcribed_text = speech_to_text_from_bytes(audio_bytes, stt_source_lang)
        
        if not transcribed_text:
            return JsonResponse({'success': False, 'error': 'No speech detected'}, status=400)
        
        # Log the transcription for debugging
        logger.info(f"Transcribed: '{transcribed_text}' (from {stt_source_lang})")
        
        # Translate text (use original language codes for translation)
        translated_text = translate_text(transcribed_text, source_language, target_language)
        
        # Log the translation for debugging
        logger.info(f"Translated: '{translated_text}' ({source_language} -> {target_language})")
        
        # Generate TTS for translated text
        tts_filepath = text_to_speech(translated_text, target_language)
        audio_url = f"/media/audio/{os.path.basename(tts_filepath)}"
        
        # Save to history
        TranslationHistory.objects.create(
            user=request.user,
            translation_type='conversation',
            source_language=source_language,
            target_language=target_language,
            original_text=transcribed_text,
            translated_text=translated_text,
            audio_file=audio_url
        )
        
        # Limit translation history to last 5 entries
        limit_translation_history(request.user)
        
        return JsonResponse({
            'success': True,
            'transcribed_text': transcribed_text,
            'translated_text': translated_text,
            'audio_url': audio_url,
            'source_language': source_language,
            'target_language': target_language,
            'speaker': speaker
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def serve_audio(request, filename):
    """Serve audio files"""
    try:
        filepath = os.path.join(settings.MEDIA_ROOT, 'audio', filename)
        
        if os.path.exists(filepath):
            return FileResponse(open(filepath, 'rb'), content_type='audio/mpeg')
        else:
            return JsonResponse({'error': 'Audio file not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def serve_image(request, filename):
    """Serve image files"""
    try:
        filepath = os.path.join(settings.MEDIA_ROOT, 'images', filename)
        
        if os.path.exists(filepath):
            return FileResponse(open(filepath, 'rb'), content_type='image/jpeg')
        else:
            return JsonResponse({'error': 'Image file not found'}, status=404)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Video Summarization Views
@login_required
def video_upload(request):
    """Video upload view"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        video_file = request.FILES.get('video_file')
        video_url = request.POST.get('video_url', '').strip()
        source_type = request.POST.get('source_type', 'upload')
        
        
        if source_type == 'url':
            # Process URL-based video
            if title and video_url:
                if not is_valid_video_url(video_url):
                    messages.error(request, 'Please provide a valid video URL (YouTube, Vimeo, etc.)')
                    return render(request, 'translation/video_upload.html')
                
                try:
                    # Create video object for URL
                    video = Video.objects.create(
                        user=request.user,
                        title=title,
                        description=description,
                        source_type='url',
                        video_url=video_url
                    )
                    
                    messages.success(request, f'Video URL "{title}" added successfully!')
                    return redirect('video_summarize_url', video_id=video.id)
                    
                except Exception as e:
                    messages.error(request, f'URL processing failed: {str(e)}')
            else:
                messages.error(request, 'Please provide both title and video URL.')
        else:
            # Process file upload
            if title and video_file:
                try:
                    # Create video object
                    video = Video.objects.create(
                        user=request.user,
                        title=title,
                        description=description,
                        source_type='upload',
                        video_file=video_file
                    )
                    
                    messages.success(request, f'Video "{title}" uploaded successfully!')
                    return redirect('video_summarize', video_id=video.id)
                    
                except Exception as e:
                    messages.error(request, f'Upload failed: {str(e)}')
            else:
                messages.error(request, 'Please provide both title and video file.')
    
    return render(request, 'translation/video_upload.html')


@login_required
def video_summarize(request, video_id):
    """Video summarization view"""
    try:
        video = Video.objects.get(id=video_id, user=request.user)
    except Video.DoesNotExist:
        messages.error(request, 'Video not found.')
        return redirect('video_upload')
    
    # Check if summary already exists
    existing_summary = VideoSummary.objects.filter(video=video).first()
    if existing_summary:
        # Calculate compression ratio
        compression_ratio = None
        if existing_summary.transcript_words and existing_summary.summary_words:
            compression_ratio = round((existing_summary.summary_words / existing_summary.transcript_words) * 100, 1)
        
        context = {
            'video': video,
            'summary': existing_summary,
            'existing': True,
            'compression_ratio': compression_ratio,
        }
        return render(request, 'translation/video_summary.html', context)
    
    # Process video for summarization
    try:
        video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
        
        if not os.path.exists(video_path):
            messages.error(request, 'Video file not found.')
            return redirect('video_upload')
        
        # Process video
        result = process_video_for_summarization(video_path)
        
        if result is None:
            messages.error(request, 'Video processing dependencies are not installed. Please install the required packages.')
            return redirect('video_upload')
        elif result:
            # Create video summary
            video_summary = VideoSummary.objects.create(
                user=request.user,
                video=video,
                summary_text=result['summary'],
                transcript_text=result['transcript'],
                summary_words=result['summary_words'],
                transcript_words=result['transcript_words'],
                duration=result['duration']
            )
            
            # Save to translation history
            TranslationHistory.objects.create(
                user=request.user,
                translation_type='video',
                source_language='auto',
                target_language='en',
                original_text=result['transcript'],
                translated_text=result['summary'],
                summary=f"Duration: {result['duration']} | Words: {result['transcript_words']} -> {result['summary_words']}"
            )
            
            # Limit translation history to last 5 entries
            limit_translation_history(request.user)
            
            # Calculate compression ratio
            compression_ratio = None
            if video_summary.transcript_words and video_summary.summary_words:
                compression_ratio = round((video_summary.summary_words / video_summary.transcript_words) * 100, 1)
            
            context = {
                'video': video,
                'summary': video_summary,
                'existing': False,
                'compression_ratio': compression_ratio,
            }
            
            messages.success(request, 'Video summarized successfully!')
            return render(request, 'translation/video_summary.html', context)
        else:
            messages.error(request, 'Video processing failed. Please try again.')
            
    except Exception as e:
        logger.error(f"Video summarization failed: {str(e)}")
        messages.error(request, f'Summarization failed: {str(e)}')
    
    return redirect('video_upload')


@login_required
def video_summarize_url(request, video_id):
    """URL-based video summarization view - shows processing page"""
    try:
        video = Video.objects.get(id=video_id, user=request.user, source_type='url')
    except Video.DoesNotExist:
        messages.error(request, 'Video not found.')
        return redirect('video_upload')
    
    # Check if summary already exists
    existing_summary = VideoSummary.objects.filter(video=video).first()
    if existing_summary:
        # Calculate compression ratio
        compression_ratio = None
        if existing_summary.transcript_words and existing_summary.summary_words:
            compression_ratio = round((existing_summary.summary_words / existing_summary.transcript_words) * 100, 1)
        
        context = {
            'video': video,
            'summary': existing_summary,
            'existing': True,
            'compression_ratio': compression_ratio,
        }
        return render(request, 'translation/video_summary.html', context)
    
    # Show processing page
    context = {
        'video': video,
    }
    return render(request, 'translation/video_processing.html', context)

@login_required
def video_process_url(request, video_id):
    """Actually process the video URL - called via AJAX or redirect"""
    try:
        video = Video.objects.get(id=video_id, user=request.user, source_type='url')
    except Video.DoesNotExist:
        messages.error(request, 'Video not found.')
        return redirect('video_upload')
    
    # Process video URL for summarization
    try:
        if not video.video_url:
            messages.error(request, 'Video URL not found.')
            return redirect('video_upload')
        
        # Process video URL
        result = process_video_url_for_summarization(video.video_url)
        
        if result is None:
            messages.error(request, 'Video processing failed. This might be due to a long video or network issues. Please try with a shorter video or check your internet connection.')
            return redirect('video_upload')
        elif result:
            # Create video summary
            video_summary = VideoSummary.objects.create(
                user=request.user,
                video=video,
                summary_text=result['summary'],
                transcript_text=result['transcript'],
                summary_words=result['summary_words'],
                transcript_words=result['transcript_words'],
                duration=result['duration']
            )
            
            # Save to translation history
            TranslationHistory.objects.create(
                user=request.user,
                translation_type='video',
                source_language='auto',
                target_language='en',
                original_text=result['transcript'],
                translated_text=result['summary'],
                summary=f"Duration: {result['duration']} | Words: {result['transcript_words']} -> {result['summary_words']} | URL: {result['source_url']}"
            )
            
            # Limit translation history to last 5 entries
            limit_translation_history(request.user)
            
            # Calculate compression ratio
            compression_ratio = None
            if video_summary.transcript_words and video_summary.summary_words:
                compression_ratio = round((video_summary.summary_words / video_summary.transcript_words) * 100, 1)
            
            context = {
                'video': video,
                'summary': video_summary,
                'existing': False,
                'compression_ratio': compression_ratio,
            }
            
            messages.success(request, 'Video URL summarized successfully!')
            return render(request, 'translation/video_summary.html', context)
        else:
            messages.error(request, 'Video URL processing failed. Please try again.')
            
    except Exception as e:
        logger.error(f"Video URL summarization failed: {str(e)}")
        messages.error(request, f'Summarization failed: {str(e)}')
    
    return redirect('video_upload')


@login_required
def video_history(request):
    """Video summarization history view"""
    videos = Video.objects.filter(user=request.user).order_by('-upload_date')
    
    # Calculate stats
    total_videos = videos.count()
    processed_videos = sum(1 for video in videos if video.summaries.exists())
    pending_videos = total_videos - processed_videos
    url_videos = sum(1 for video in videos if video.source_type == 'url')
    
    context = {
        'videos': videos,
        'total_videos': total_videos,
        'processed_videos': processed_videos,
        'pending_videos': pending_videos,
        'url_videos': url_videos,
    }
    
    return render(request, 'translation/video_history.html', context)


@login_required
def video_detail(request, video_id):
    """Video detail view with summary"""
    try:
        video = Video.objects.get(id=video_id, user=request.user)
        summary = VideoSummary.objects.filter(video=video).first()
        
        # Calculate compression ratio
        compression_ratio = None
        if summary and summary.transcript_words and summary.summary_words:
            compression_ratio = round((summary.summary_words / summary.transcript_words) * 100, 1)
        
        context = {
            'video': video,
            'summary': summary,
            'compression_ratio': compression_ratio,
        }
        
        return render(request, 'translation/video_detail.html', context)
        
    except Video.DoesNotExist:
        messages.error(request, 'Video not found.')
        return redirect('video_history')

@login_required
def delete_video(request, video_id):
    """Delete video view"""
    if request.method == 'POST':
        try:
            video = Video.objects.get(id=video_id, user=request.user)
            video_title = video.title
            video.delete()
            messages.success(request, f'Video "{video_title}" deleted successfully.')
        except Video.DoesNotExist:
            messages.error(request, 'Video not found.')
        except Exception as e:
            messages.error(request, f'Failed to delete video: {str(e)}')
    
    return redirect('video_history')