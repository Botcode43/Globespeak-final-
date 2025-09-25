# 🚀 GlobeSpeak Setup Guide

## 📋 Prerequisites

### System Requirements
- **Operating System:** Windows 10/11 (64-bit)
- **Python:** 3.12 or higher
- **RAM:** Minimum 8GB (16GB recommended for video processing)
- **Storage:** At least 5GB free space
- **Internet:** Required for downloading AI models

### External Dependencies
1. **FFmpeg** (Required for video processing)
2. **Tesseract OCR** (Required for image text extraction)

---

## 🛠️ Installation Steps

### Step 1: Install Python
1. Download Python 3.12+ from [python.org](https://www.python.org/downloads/)
2. **Important:** Check "Add Python to PATH" during installation
3. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### Step 2: Install FFmpeg
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg\`
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Add `C:\ffmpeg\bin` to PATH
4. Verify installation:
   ```bash
   ffmpeg -version
   ```

### Step 3: Install Tesseract OCR
1. Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install to default location: `C:\Program Files\Tesseract-OCR`
3. Add to PATH:
   - Add `C:\Program Files\Tesseract-OCR` to PATH
4. Verify installation:
   ```bash
   tesseract --version
   ```

### Step 4: Clone/Download Project
```bash
# If using Git
git clone <repository-url>
cd globe_speak/bhashini_project

# Or download and extract ZIP file
```

### Step 5: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
```

### Step 6: Install Python Dependencies
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt
```

### Step 7: Environment Configuration
1. Copy `env_template.txt` to `.env`:
   ```bash
   copy env_template.txt .env
   ```
2. Edit `.env` file and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```

### Step 8: Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 9: Collect Static Files
```bash
python manage.py collectstatic
```

### Step 10: Run the Application
```bash
python manage.py runserver
```

Visit: http://localhost:8000

---

## 🔧 Troubleshooting

### Common Issues

#### 1. "FFmpeg not found"
- **Solution:** Ensure FFmpeg is installed and added to PATH
- **Test:** Run `ffmpeg -version` in command prompt

#### 2. "Tesseract not found"
- **Solution:** Install Tesseract OCR and add to PATH
- **Test:** Run `tesseract --version` in command prompt

#### 3. "Module not found" errors
- **Solution:** Ensure virtual environment is activated
- **Test:** Run `pip list` to see installed packages

#### 4. "Permission denied" errors
- **Solution:** Run command prompt as Administrator
- **Alternative:** Use PowerShell with execution policy

#### 5. Video processing fails
- **Solution:** Check FFmpeg installation and internet connection
- **Note:** First-time model download takes 5-10 minutes

#### 6. Clipboard copy fails
- **Solution:** Use HTTPS or localhost (not file://)
- **Note:** Fallback method should work in most cases

### Performance Optimization

#### For Better Video Processing:
1. **GPU Support:** Install CUDA for faster processing
2. **RAM:** Increase virtual memory if needed
3. **Storage:** Use SSD for better I/O performance

#### For Development:
```bash
# Install development tools
pip install django-debug-toolbar django-extensions

# Enable debug toolbar in settings.py
```

---

## 📁 Project Structure

```
bhashini_project/
├── globespeak/           # Django project settings
├── translation/          # Main app
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── services/        # AI services
│   └── templates/       # HTML templates
├── static/              # Static files (CSS, JS)
├── media/               # User uploads
├── templates/           # Base templates
├── requirements.txt     # Python dependencies
├── manage.py           # Django management
└── .env                # Environment variables
```

---

## 🎯 Features Overview

### Core Features:
- **Text Translation:** 100+ languages
- **Image Translation:** OCR + Translation
- **Video Summarization:** AI-powered summaries
- **Real-time Conversation:** Voice translation
- **Text Summarization:** AI summarization

### AI Models Used:
- **Whisper:** Speech-to-text
- **BART:** Text summarization
- **Google Translate:** Translation
- **Tesseract:** OCR
- **Gemini:** AI processing

---

## 🔐 Security Notes

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** in production
3. **Set DEBUG=False** in production
4. **Use HTTPS** in production
5. **Regular updates** for security patches

---

## 📞 Support

### Getting Help:
1. Check this setup guide first
2. Review error messages carefully
3. Check Django logs in `logs/django.log`
4. Ensure all prerequisites are installed

### Common Commands:
```bash
# Check Django status
python manage.py check

# View installed packages
pip list

# Update packages
pip install --upgrade package_name

# Deactivate virtual environment
deactivate
```

---

## 🎉 Success!

If everything is working correctly, you should see:
- ✅ Django server running on http://localhost:8000
- ✅ All features accessible from dashboard
- ✅ Video processing working (may take time on first use)
- ✅ Translation features working
- ✅ No error messages in console

**Happy translating! 🌍**
