"""
MAYA Configuration File
Store all API keys and settings here
"""

# OpenAI API Configuration
OPENAI_API_KEY = "ddc-a4f-168661602ce443ce97fbb1d884cd2f10"  # Replace with your actual OpenAI API key

# Alternative AI APIs (for fallback and cost efficiency)
GEMINI_API_KEY = "AIzaSyCTlNHDgfFJf8kygz31M3eIn0fOFh3WWjE"  # Google Gemini API
GROQ_API_KEY = "your-groq-api-key-here"  # Fast inference API

# Weather API Configuration
OWM_API_KEY = "YOUR_OWM_API_KEY_HERE"  # Replace with your OpenWeatherMap API key

# News API Configuration  
NEWS_API_KEY = "YOUR_NEWSAPI_KEY_HERE"  # Replace with your NewsAPI key

# Robot API Configuration
ROBOT_API_URL = "http://localhost:5001/command"

# Camera Settings
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_QUALITY = 85

# Voice Recognition Settings (Optimized for Raspberry Pi direct access)
SPEECH_TIMEOUT = 2  # Very fast timeout for responsive interaction
PHRASE_TIME_LIMIT = 3  # Quick command processing
ENERGY_THRESHOLD = 2500  # Adjusted for USB microphone sensitivity
CALIBRATION_DURATION = 0.2  # Minimal calibration time
MICROPHONE_DEVICE_INDEX = 1  # USB PnP Sound Device (hw:3,0) - correct index
SAMPLE_RATE = 16000  # Optimal for speech recognition
CHANNELS = 1  # Mono recording for better compatibility

# Voice Settings (Enhanced for better Indian female voice)
VOICE_ENGINE = "gtts"  # Use gTTS for better voice quality
VOICE_LANG = "en"  # English with Indian accent
VOICE_TLD = "co.in"  # Indian domain for better accent
VOICE_RATE = 180  # Speaking speed (words per minute)
VOICE_PITCH = 0.8  # Higher pitch for female voice
VOICE_VOLUME = 0.9  # Volume level
VOICE_SLOW = False  # Normal speed

# AI Model Settings (Optimized for speed and cost)
PRIMARY_AI = "groq"  # Primary AI (groq is faster)
FALLBACK_AI = "openai"  # Fallback to OpenAI
OPENAI_MODEL = "provider-3/gpt-4"  # Faster and cheaper than GPT-4
GROQ_MODEL = "llama3-8b-8192"  # Fast Groq model
GEMINI_MODEL = "gemini-2.0-flash"  # Google's model
OPENAI_VISION_MODEL = "gpt-4-vision-preview"
AI_MAX_TOKENS = 120  # Shorter responses for speed
AI_TEMPERATURE = 0.7

# Wake Word Settings
WAKE_WORDS = ["maya", "hey maya", "ok maya", "maya ji"]
CONTINUOUS_LISTENING = True  # Keep listening in background

# Paths
IMAGES_DIR = "~/maya_images"
LOGS_FILE = "/home/pragyan/Robot/maya_logs.log"
AUDIO_CACHE_DIR = "~/maya_audio_cache"  # Cache for faster TTS

# System Settings
DEFAULT_LOCATION = "Delhi"  # Default city for weather
DEBUG_MODE = False  # Disable for production use
ENABLE_HUMOR = True  # Indian humor and personality
RESPONSE_SPEED_MODE = True  # Prioritize speed over complex responses

# Hardware Settings
USE_GPIO_LED = True  # LED indicators during listening/speaking
LED_PIN = 18  # GPIO pin for status LED

# Advanced Features
ENABLE_OBJECT_DETECTION = True  # Enable vision analysis
ENABLE_GESTURE_CONTROL = False  # Future feature
ENABLE_LEARNING_MODE = True  # Learn user preferences
SAVE_CONVERSATIONS = True  # Save for learning
