# 🌍 Globespeak - Multilingual Communication Platform

A modern, real-time multilingual communication platform that enables seamless translation between different languages using AI-powered speech-to-text, translation, and text-to-speech services. Built with Django, HTML5, and Tailwind CSS.

## ✨ Features

### 🎤 Real-time Conversation Translation
- **Speech-to-Text**: Convert spoken language to text using Google Speech Recognition
- **Text Translation**: Translate text between 100+ languages using Google Translate
- **Text-to-Speech**: Convert translated text to audio using Google Text-to-Speech
- **WebSocket Support**: Live communication with instant translation
- **Multi-user Rooms**: Create and join conversation rooms for group translations

### 📝 Text Translation
- Translate text between any supported languages
- Copy translated text to clipboard
- Audio playback of translations
- Language auto-detection
- Real-time translation with instant results

### 🖼️ Image Translation (OCR)
- Extract text from images using Tesseract OCR
- Support for 50+ languages including Indian languages
- Translate extracted text to target language
- Mobile-friendly with drag-and-drop support
- High-quality image processing

### 📄 Text Summarization
- AI-powered text summarization using Google Gemini
- Keyword extraction
- Sentiment analysis
- Customizable summary length
- Smart text processing


### 📜 History & User Management
- Complete user authentication system
- Translation history tracking
- Session management with "Remember Me" functionality
- Account management
- Export and manage past translations

## 🚀 Technology Stack

### Backend
- **Django 4.2.7** - Modern web framework
- **Django REST Framework** - API development
- **Django Channels** - WebSocket support for real-time communication
- **Redis** - Message broker for WebSocket channels
- **SQLite3** - Database (development)

### Frontend
- **HTML5** - Modern markup
- **Tailwind CSS** - Utility-first CSS framework
- **Alpine.js** - Lightweight JavaScript framework
- **WebSocket API** - Real-time communication
- **Responsive Design** - Mobile-first approach

### AI/ML Services
- **Google Translate API** (via deep_translator) - Text translation
- **Tesseract OCR** - Image text extraction
- **Google Speech Recognition** - Speech-to-text
- **Google Text-to-Speech (gTTS)** - Text-to-speech
- **Google Gemini AI** - Text summarization

## 📦 Installation & Setup

### Prerequisites
- **Python 3.12+** (Required)
- **FFmpeg** (Required for video processing)
- **Tesseract OCR** (Required for image text extraction)

### 🛠️ Easy Installation (Windows)

**Option 1: Automated Installation**
```bash
# Run the installation script
install.bat
```

**Option 2: Manual Installation**
```bash
# 1. Clone repository
git clone <repository-url>
cd bhashini_project

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py makemigrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic

# 6. Start server
python manage.py runserver
```

### 📋 External Dependencies

**FFmpeg Installation:**
1. Download from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to PATH

**Tesseract OCR Installation:**
- **Windows**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

### ✅ Verification
```bash
# Check if everything is installed correctly
python verify_installation.py
```

### 📖 Detailed Setup
For complete setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

### 5. Environment Configuration
Create a `.env` file in the project root:
```bash
# Copy the template
cp env_template.txt .env
```

Edit `.env` file with your configuration:
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Gemini AI API Key (for text summarization)
GEMINI_API_KEY=your-gemini-api-key-here

# Redis (for WebSocket channels)
REDIS_URL=redis://localhost:6379/0
```

### 6. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Start Redis Server
```bash
# On Windows (if installed via installer)
redis-server

# On macOS (if installed via Homebrew)
brew services start redis

# On Ubuntu/Debian
sudo systemctl start redis
```

### 8. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`


## 🎯 Usage

### Real-time Conversation Translation

1. **Access the application**: Open http://localhost:8000
2. **Login/Register**: Create an account or login
3. **Start Conversation**: Click on "Real-time Chat"
4. **Configure Languages**: Set your language and target language
5. **Start Speaking**: Click the microphone button and speak
6. **Real-time Translation**: Your speech will be converted to text, translated, and played as audio

### Text Translation

1. Navigate to "Text Translation"
2. Select source and target languages
3. Enter text to translate
4. Click "Translate Text"
5. Copy or play audio of the translation

### Image Translation

1. Go to "Image Translation"
2. Upload an image or drag and drop
3. Select target language
4. Click "Extract & Translate Text"
5. View extracted and translated text

### Text Summarization

1. Visit "Summarize" page
2. Enter text to summarize
3. Choose summary length
4. Click "Summarize Text"
5. View summary, keywords, and sentiment analysis

## 🌐 Language Support

The platform supports 100+ languages including:

### Indian Languages
Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Gujarati, Punjabi, Marathi, Assamese, Odia, Urdu, Sanskrit, Nepali, Sindhi

### International Languages
English, Spanish, French, German, Japanese, Korean, Chinese, Arabic, Portuguese, Russian, Italian, Dutch, Swedish, Danish, Norwegian, Finnish, and many more

## 🔧 API Endpoints

### Authentication
- `POST /login/` - User login
- `POST /register/` - User registration
- `POST /logout/` - User logout

### Translation Services
- `POST /translate/` - Text translation
- `POST /conversation/` - Real-time conversation
- `POST /image/` - Image OCR and translation
- `POST /summarize/` - Text summarization

### Data Management
- `GET /history/` - Get translation history
- `GET /dashboard/` - User dashboard

### WebSocket
- `ws://localhost:8000/ws/translation/<room_name>/` - Real-time communication

## 🏗️ Project Structure

```
bhashini_project/
├── globespeak/              # Django project settings
│   ├── settings.py         # Main settings
│   ├── urls.py            # URL configuration
│   └── asgi.py            # ASGI configuration
├── translation/            # Main Django app
│   ├── models.py          # Database models
│   ├── views.py           # View functions
│   ├── urls.py            # App URL patterns
│   ├── consumers.py       # WebSocket consumers
│   ├── routing.py         # WebSocket routing
│   ├── admin.py           # Admin configuration
│   └── services/          # AI/ML services
│       ├── translate.py   # Translation service
│       ├── stt.py         # Speech-to-text
│       ├── tts.py         # Text-to-speech
│       ├── ocr.py         # OCR service
│       └── summarize.py   # Summarization service
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   └── translation/      # App templates
├── static/               # Static files
├── media/                # Media files
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🔒 Security Features

- User authentication and authorization
- CSRF protection
- Secure session management
- Input validation and sanitization
- File upload security
- Environment variable configuration

## 🎨 UI/UX Features

- **Modern Design**: Clean, professional interface with Tailwind CSS
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Dark/Light Theme**: Automatic theme detection
- **Smooth Animations**: Engaging user interactions
- **Accessibility**: WCAG compliant design
- **Progressive Web App**: Installable and offline-capable

## 🚀 Deployment

### Production Settings

1. **Environment Variables**:
   ```bash
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Database**: Configure PostgreSQL or MySQL for production

3. **Static Files**: Use WhiteNoise or AWS S3 for static file serving

4. **Web Server**: Deploy with Gunicorn and Nginx

5. **Redis**: Use Redis Cloud or AWS ElastiCache

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn", "globespeak.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Contact the development team

## 🙏 Acknowledgments

- Google for providing excellent AI/ML APIs
- Django community for the amazing framework
- Tailwind CSS for the beautiful design system
- All contributors and users

---

**Globespeak** - Breaking down language barriers, one conversation at a time. 🌍

Made with ❤️ using Django, HTML5, and Tailwind CSS
# GlobeSpeak
