from django.contrib import admin
from .models import TranslationHistory, Video, VideoSummary


@admin.register(TranslationHistory)
class TranslationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'translation_type', 'source_language', 'target_language', 'created_at']
    list_filter = ['translation_type', 'source_language', 'target_language', 'created_at']
    search_fields = ['user__username', 'original_text', 'translated_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'translation_type', 'created_at')
        }),
        ('Languages', {
            'fields': ('source_language', 'target_language')
        }),
        ('Content', {
            'fields': ('original_text', 'translated_text', 'summary')
        }),
        ('Media Files', {
            'fields': ('audio_file', 'image_file'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'upload_date', 'video_file']
    list_filter = ['upload_date', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['upload_date']
    ordering = ['-upload_date']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'description', 'upload_date')
        }),
        ('Video File', {
            'fields': ('video_file',)
        }),
    )


@admin.register(VideoSummary)
class VideoSummaryAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'video', 'summary_words', 'transcript_words', 'duration', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'user__username', 'video__title', 'summary_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'video', 'title', 'created_at')
        }),
        ('Statistics', {
            'fields': ('duration', 'transcript_words', 'summary_words')
        }),
        ('Content', {
            'fields': ('transcript_text', 'summary_text'),
            'classes': ('collapse',)
        }),
    )

