@echo off
echo 🎬 Installing Video Summarization Dependencies
echo ================================================

echo.
echo 📦 Installing Python packages...
pip install openai-whisper==20231117
pip install transformers==4.35.2
pip install torch==2.1.0
pip install nltk==3.8.1
pip install numpy==1.24.3

echo.
echo 🧪 Testing installation...
python -c "import whisper; import transformers; import torch; import nltk; print('✅ All packages imported successfully')"

echo.
echo 🎥 Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ FFmpeg is available
) else (
    echo ❌ FFmpeg not found!
    echo.
    echo 📋 FFmpeg Installation Instructions:
    echo 1. Download FFmpeg from: https://ffmpeg.org/download.html
    echo 2. Extract to C:\ffmpeg
    echo 3. Add C:\ffmpeg\bin to your PATH environment variable
    echo 4. Restart your command prompt
)

echo.
echo 🎉 Installation completed!
echo.
echo 📋 Next steps:
echo 1. Make sure FFmpeg is installed and in your PATH
echo 2. Run: python manage.py runserver
echo 3. Visit: http://localhost:8000
echo 4. Click on 'Video Summarizer' in the dashboard

pause
