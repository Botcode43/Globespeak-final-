#!/usr/bin/env python3
"""
Installation script for video summarization dependencies
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🎬 Installing Video Summarization Dependencies")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Please run this script from the bhashini_project directory")
        sys.exit(1)
    
    # Install Python packages
    packages = [
        "openai-whisper==20231117",
        "transformers==4.35.2", 
        "torch==2.1.0",
        "nltk==3.8.1",
        "numpy==1.24.3"
    ]
    
    print("\n📦 Installing Python packages...")
    for package in packages:
        if not run_command(f"pip install {package}", f"Installing {package}"):
            print(f"⚠️  Failed to install {package}, continuing with others...")
    
    # Download NLTK data
    print("\n📚 Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        print("✅ NLTK punkt data downloaded")
    except Exception as e:
        print(f"⚠️  NLTK data download failed: {e}")
    
    # Check FFmpeg
    print("\n🎥 Checking FFmpeg installation...")
    if run_command("ffmpeg -version", "Checking FFmpeg"):
        print("✅ FFmpeg is available")
    else:
        print("❌ FFmpeg not found!")
        print("\n📋 FFmpeg Installation Instructions:")
        print("Windows:")
        print("1. Download FFmpeg from: https://ffmpeg.org/download.html")
        print("2. Extract to C:\\ffmpeg")
        print("3. Add C:\\ffmpeg\\bin to your PATH environment variable")
        print("\nmacOS:")
        print("brew install ffmpeg")
        print("\nUbuntu/Debian:")
        print("sudo apt install ffmpeg")
    
    # Test the installation
    print("\n🧪 Testing installation...")
    try:
        import whisper
        import transformers
        import torch
        import nltk
        print("✅ All Python packages imported successfully")
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("\n🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Make sure FFmpeg is installed and in your PATH")
    print("2. Run: python manage.py runserver")
    print("3. Visit: http://localhost:8000")
    print("4. Click on 'Video Summarizer' in the dashboard")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
