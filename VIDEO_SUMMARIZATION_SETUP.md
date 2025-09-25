# 🎬 Video Summarization Setup Guide

This guide will help you set up the video summarization feature that has been integrated from the Brefify project.

## ✅ What's Already Done

The integration is complete! The following has been added to your Bhashini project:

- ✅ New database models for videos and summaries
- ✅ Video upload and processing views
- ✅ AI-powered transcription using Whisper
- ✅ AI-powered summarization using BART
- ✅ Beautiful templates for video management
- ✅ Integration with existing user system
- ✅ Database migrations applied

## 🚀 Quick Setup

### Option 1: Automated Installation (Recommended)

**For Windows:**
```bash
# Run the batch file
install_video_deps.bat
```

**For macOS/Linux:**
```bash
# Run the Python script
python install_video_deps.py
```

### Option 2: Manual Installation

1. **Install Python Dependencies:**
```bash
pip install openai-whisper==20231117
pip install transformers==4.35.2
pip install torch==2.1.0
pip install nltk==3.8.1
pip install numpy==1.24.3
```

2. **Install FFmpeg:**

**Windows:**
- Download from: https://ffmpeg.org/download.html
- Extract to `C:\ffmpeg`
- Add `C:\ffmpeg\bin` to your PATH environment variable
- Restart your command prompt

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

3. **Download NLTK Data:**
```python
python -c "import nltk; nltk.download('punkt')"
```

## 🧪 Testing the Installation

1. **Start the server:**
```bash
python manage.py runserver
```

2. **Visit the application:**
   - Go to: http://localhost:8000
   - Login to your account
   - Click on "Video Summarizer" in the dashboard

3. **Test video upload:**
   - Upload a video file (MP4, AVI, MOV, etc.)
   - Wait for processing to complete
   - View the generated transcript and summary

## 🎯 Features Available

### Video Upload
- Support for MP4, AVI, MOV, WMV, FLV, WebM formats
- Maximum file size: 100MB
- Automatic title generation from filename

### AI Processing
- **Speech Recognition:** OpenAI Whisper extracts accurate transcripts
- **AI Summarization:** BART model generates concise summaries
- **Analytics:** Duration, word counts, compression ratios

### Management Features
- View all uploaded videos
- Access detailed summaries and transcripts
- Copy, translate, or download content
- Video playback in browser

## 🔧 Technical Details

### Models Used
- **Whisper Base Model:** For speech-to-text conversion
- **BART CNN 12-6:** For text summarization
- **FFmpeg:** For video/audio processing

### File Structure
```
bhashini_project/
├── translation/
│   ├── models.py          # Video and VideoSummary models
│   ├── views.py           # Video processing views
│   ├── services/
│   │   └── video_summarize.py  # Core processing logic
│   └── templates/translation/
│       ├── video_upload.html
│       ├── video_summary.html
│       ├── video_history.html
│       └── video_detail.html
```

### Database Tables
- `translation_video`: Stores uploaded video files
- `translation_videosummary`: Stores transcripts and summaries
- `translation_translationhistory`: Updated to include video type

## 🚨 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'whisper'"**
   - Run: `pip install openai-whisper==20231117`

2. **"FFmpeg not found"**
   - Install FFmpeg and add it to your PATH
   - Restart your command prompt/terminal

3. **"Video processing dependencies not available"**
   - Install all required packages: `pip install -r requirements.txt`
   - Make sure FFmpeg is installed

4. **"No speech detected"**
   - Check if the video has clear audio
   - Try with a different video file
   - Ensure the video is not corrupted

### Performance Tips

- **Smaller videos process faster:** Consider compressing large videos
- **Clear audio works better:** Videos with background noise may have lower accuracy
- **English content:** Whisper works best with English, but supports many languages

## 📊 Usage Statistics

The system tracks:
- Video duration
- Transcript word count
- Summary word count
- Compression ratio
- Processing time

## 🔒 Security Notes

- Videos are stored in the `media/videos/` directory
- Only authenticated users can upload videos
- Users can only access their own videos
- Temporary audio files are automatically cleaned up

## 🆘 Support

If you encounter issues:

1. Check the Django logs in `logs/django.log`
2. Verify all dependencies are installed
3. Ensure FFmpeg is in your PATH
4. Try with a small test video first

## 🎉 You're All Set!

The video summarization feature is now fully integrated into your Bhashini project. Users can upload videos, get AI-generated transcripts and summaries, and manage their video library through a beautiful web interface.

Enjoy your new video summarization capabilities! 🎬✨
