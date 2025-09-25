from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Video(models.Model):
    """Model to store uploaded videos for summarization"""
    VIDEO_SOURCE_CHOICES = [
        ('upload', 'File Upload'),
        ('url', 'Video URL'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='videos')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    source_type = models.CharField(max_length=10, choices=VIDEO_SOURCE_CHOICES, default='upload')
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class VideoSummary(models.Model):
    """Model to store video summaries"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_summaries')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='summaries')
    title = models.CharField(max_length=100, default='')
    summary_text = models.TextField()
    transcript_text = models.TextField(blank=True)
    summary_words = models.IntegerField(default=0)
    transcript_words = models.IntegerField(default=0)
    duration = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Video Summary'
        verbose_name_plural = 'Video Summaries'
    
    def __str__(self):
        return f"{self.user.username} - {self.video.title} Summary"
    
    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.video.title
        super().save(*args, **kwargs)


class TranslationHistory(models.Model):
    """Model to store translation history for users"""
    
    TRANSLATION_TYPES = [
        ('text', 'Text Translation'),
        ('conversation', 'Real-time Conversation'),
        ('image', 'Image Translation'),
        ('summarize', 'Text Summarization'),
        ('video', 'Video Summarization'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='translation_history')
    translation_type = models.CharField(max_length=20, choices=TRANSLATION_TYPES)
    source_language = models.CharField(max_length=10, default='en')
    target_language = models.CharField(max_length=10, default='hi')
    original_text = models.TextField()
    translated_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    conversation_summary = models.TextField(blank=True)  # For conversation mode summaries
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    image_file = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Translation History'
        verbose_name_plural = 'Translation Histories'
    
    def __str__(self):
        return f"{self.user.username} - {self.translation_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

