#!/usr/bin/env python3
"""
MAYA Advanced - My Advanced Yielding Assistant
Enhanced Indian female voice assistant for Raspberry Pi robot
Optimized for speed, reduced latency, humor, and seamless integration
"""

import os
import sys

# Add virtual environment packages to path FIRST
venv_site_packages = "/home/pragyan/Robot/.venv/lib/python3.11/site-packages"
if os.path.exists(venv_site_packages) and venv_site_packages not in sys.path:
    sys.path.insert(0, venv_site_packages)

# Add project root to path
project_root = "/home/pragyan/Robot"
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import after path setup
import time
import random
import json
import requests
import datetime
import subprocess
import threading
import speech_recognition as sr
from gtts import gTTS  # Better voice quality
import pygame
import logging
import wikipedia
import pyjokes
from PIL import Image
import base64
from io import BytesIO
import google.generativeai as genai  # Google Gemini AI
from features.maya.movement_helper import MovementHelper
from features.maya.config import *
from hardware.motors import MotorController

# Configure logging
logging.basicConfig(
    level=logging.INFO if DEBUG_MODE else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOGS_FILE), logging.StreamHandler()]
)
logger = logging.getLogger("MAYA")

class MAYAAssistant:
    def __init__(self):
        logger.info("🚀 Initializing Enhanced MAYA Assistant...")
        
        # Core state
        self.running = False
        self.listening = False
        self.speaking = False
        
        # Initialize pygame for better audio
        pygame.mixer.init()
        
        # Initialize speech recognition with optimized settings for Pi
        self.recognizer = sr.Recognizer()
        
        # Configure for USB microphone
        try:
            self.microphone = sr.Microphone(device_index=MICROPHONE_DEVICE_INDEX)
            logger.info(f"✅ USB Microphone initialized (device index: {MICROPHONE_DEVICE_INDEX})")
        except Exception:
            # Fallback to default microphone
            self.microphone = sr.Microphone()
            logger.warning("⚠️ Using default microphone as fallback")
        
        # Optimize recognition settings for Pi
        self.recognizer.energy_threshold = ENERGY_THRESHOLD
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5  # Shorter pause detection
        self.recognizer.non_speaking_duration = 0.3  # Quick silence detection
        self._setup_speech_recognition()
        
        # Initialize movement systems - both HTTP and direct motor control
        self.movement = MovementHelper(ROBOT_API_URL)
        
        # Initialize direct motor control for better performance
        try:
            self.motors = MotorController()
            self.direct_motor_control = True
            logger.info("✅ Direct motor control initialized")
        except Exception as e:
            logger.warning(f"⚠️ Direct motor control failed, using HTTP fallback: {e}")
            self.motors = None
            self.direct_motor_control = False
        
        # Enhanced personality and responses
        self._init_enhanced_personality()
        
        # Quick command cache for faster processing
        self.command_cache = {}
        
        # AI clients (optional for complex queries)
        self.ai_available = self._check_ai_availability()
        
        logger.info("✨ Enhanced MAYA is ready!")

    def _setup_speech_recognition(self):
        """Setup speech recognition using the proven working test method"""
        try:
            with self.microphone as source:
                logger.info("🎤 Calibrating microphone using proven test method...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                logger.info(f"✅ Microphone ready. Energy threshold: {self.recognizer.energy_threshold}")
            
            # Use exact settings from working test
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.0  # Longer pause for complete sentences
            self.recognizer.non_speaking_duration = 0.8  # Allow pauses within sentences
            self.recognizer.phrase_threshold = 0.3
            
            logger.info("✅ Speech recognition configured like working test")
            
        except Exception as e:
            logger.error(f"❌ Speech recognition setup failed: {e}")

    def _init_enhanced_personality(self):
        """Initialize MAYA's enhanced Indian personality with humor"""
        # Quick greetings for wake-up
        self.quick_greetings = [
            "Haan ji!", "Bilkul!", "Zaroor!", "Present!", "Ready!"
        ]
        
        # Expanded greetings with Indian flavor
        self.greetings = [
            "Namaste! MAYA is here, ready to help with everything! 🙏",
            "Hello ji! MAYA is at your service, just like a good dost! 😊",
            "Arey wah! MAYA is active and excited to assist! 🌟",
            "Namaste from your tech-savvy saheli MAYA! Kaise ho? 💫",
            "Hello there! MAYA is fully charged and ready for action! ⚡"
        ]
        
        # Enhanced humor with more Indian references
        self.humor_responses = [
            "MAYA thinks you're more entertaining than a cricket match! 🏏",
            "Even MAYA needs chai breaks, but I'm always energized for you! ☕",
            "MAYA wonders if robots can enjoy gol gappa! Life's mysteries! 🤔",
            "If MAYA could dance, I'd be doing bhangra right now! 💃",
            "MAYA's excitement level is higher than Mumbai traffic! 🚗",
            "MAYA thinks your questions are spicier than masala chai! 🌶️",
            "Even Google would be impressed by MAYA's desi knowledge! 😄"
        ]
        
        # Movement confirmations with personality
        self.movement_confirmations = {
            "F": ["Aage chalo!", "Forward march!", "Chaliye aage!", "Moving ahead ji!"],
            "B": ["Peeche jao!", "Reverse gear!", "Back karte hain!", "Going back!"],
            "L": ["Left turn!", "Bayi taraf!", "Left ho jao!", "Turning left!"],
            "R": ["Right turn!", "Dayi taraf!", "Right ho jao!", "Turning right!"],
            "S": ["Ruk jao!", "Full stop!", "Brake maar!", "Stopping now!"]
        }
        
        # Quick acknowledgments for speed
        self.quick_acks = self.quick_greetings
        
        # Voice command mappings (expanded)
        self.movement_commands = {
            # Forward
            "forward": "F", "move forward": "F", "go forward": "F", "ahead": "F",
            "go straight": "F", "aage": "F", "aage chalo": "F", "aage jao": "F",
            
            # Backward
            "backward": "B", "move backward": "B", "go backward": "B", "reverse": "B",
            "go back": "B", "peeche": "B", "peeche jao": "B", "back karo": "B",
            
            # Left
            "left": "L", "turn left": "L", "go left": "L", "move left": "L",
            "bayi": "L", "bayan": "L", "left turn": "L",
            
            # Right
            "right": "R", "turn right": "R", "go right": "R", "move right": "R",
            "dayi": "R", "dayan": "R", "right turn": "R",
            
            # Stop
            "stop": "S", "halt": "S", "brake": "S", "ruk": "S", "ruk jao": "S",
            "pause": "S", "freeze": "S"
        }

    def _check_ai_availability(self):
        """Check which AI services are available"""
        available = {}
        
        # Check Google Gemini (Primary - Free and Fast)
        if GEMINI_API_KEY and GEMINI_API_KEY != "your-gemini-api-key-here":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                available['gemini'] = True
                logger.info("✅ Google Gemini AI available")
            except Exception as e:
                logger.error(f"Gemini setup failed: {e}")
                available['gemini'] = False
        
        # Check OpenAI
        if OPENAI_API_KEY and OPENAI_API_KEY != "ddc-a4f-168661602ce443ce97fbb1d884cd2f10":
            try:
                available['openai'] = True
                logger.info("✅ OpenAI API available")
            except:
                available['openai'] = False
        
        return available

    def speak(self, text, priority='normal'):
        """Simplified speak method that doesn't block listening"""
        if not text:
            return
            
        logger.info(f"🗣️ MAYA: {text}")
        
        # For quick responses, use direct speech without threading complications
        if priority == 'high' or len(text.split()) < 5:
            self._speak_direct_simple(text)
        else:
            # For longer responses, use background thread but don't wait
            threading.Thread(target=self._speak_direct_simple, args=(text,), daemon=True).start()

    def _speak_direct_simple(self, text):
        """Simplified direct speech method that's faster and doesn't block"""
        self.speaking = True
        
        try:
            # Create temporary file for speech
            temp_file = f"/tmp/maya_speech_{int(time.time())}.mp3"
            
            # Generate speech with Indian accent
            tts = gTTS(text=text, lang=VOICE_LANG, tld=VOICE_TLD, slow=VOICE_SLOW)
            tts.save(temp_file)
            
            # Play the speech
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for speech to complete with shorter checks
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(20)  # Faster checks
            
            # Clean up temp file
            try:
                os.remove(temp_file)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Speech error: {e}")
            # Quick fallback - just print the text
            print(f"MAYA: {text}")
        finally:
            self.speaking = False

    def listen_for_wake_word(self):
        """Continuous listening using EXACT method from test_maya_continuous.py"""
        logger.info("👂 MAYA listening using proven test method...")
        
        # Initial message
        self.speak("I'm ready! Say Hey Maya to talk to me!", priority='high')
        time.sleep(1)
        
        while self.running:
            try:
                if self.speaking:
                    time.sleep(0.05)
                    continue
                
                logger.info("🔍 LISTENING FOR WAKE WORD...")
                
                with self.microphone as source:
                    logger.info("🔇 ADJUSTING FOR AMBIENT NOISE (1.5 seconds)...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
                    logger.info(f"✅ ENERGY THRESHOLD: {self.recognizer.energy_threshold}")
                    
                    logger.info("🎙️ READY! LISTENING FOR COMPLETE SENTENCE (17 seconds for better capture)...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=17)
                
                try:
                    logger.info("⏹️ PROCESSING SPEECH...")
                    text = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"✅ SPEECH RECOGNIZED ({len(text)} chars): '{text}'")
                    
                    word_count = len(text.split())
                    logger.info(f"📊 WORD COUNT: {word_count} words")
                    
                    # Wake word detection using exact test method
                    wake_words = ["maya", "hey maya", "ok maya", "maya ji"]
                    wake_word_detected = False
                    wake_word_used = None
                    
                    for wake_word in wake_words:
                        if wake_word in text:
                            wake_word_detected = True
                            wake_word_used = wake_word
                            break
                    
                    if wake_word_detected:
                        logger.info(f"🔥 WAKE WORD DETECTED: '{wake_word_used}'")
                        
                        command_part = text.replace(wake_word_used, "").strip()
                        command_part = command_part.lstrip(",").strip()
                        
                        if len(command_part) > 3:
                            logger.info(f"💡 COMPLETE COMMAND EXTRACTED: '{command_part}'")
                            logger.info(f"⚡ PROCESSING COMMAND: '{command_part}'")
                            
                            # Quick acknowledgment in background
                            ack = self.quick_acks[0] if self.quick_acks else "Yes!"
                            threading.Thread(target=self._speak_direct_simple, args=(ack,), daemon=True).start()
                            
                            # Process command in background
                            threading.Thread(target=self._process_command_with_logging, args=(command_part,), daemon=True).start()
                            
                            logger.info("⏭️ RETURNING TO LISTENING IMMEDIATELY")
                            time.sleep(0.2)
                            continue
                            
                        else:
                            logger.info("⚠️ ONLY WAKE WORD, LISTENING FOR COMMAND...")
                            
                            ack = self.quick_acks[0] if self.quick_acks else "Yes!"
                            threading.Thread(target=self._speak_direct_simple, args=(ack,), daemon=True).start()
                            
                            time.sleep(0.3)
                            
                            command = self._listen_for_command_working_method()
                            if command:
                                logger.info(f"⚡ PROCESSING COMMAND: '{command}'")
                                threading.Thread(target=self._process_command_with_logging, args=(command,), daemon=True).start()
                            else:
                                threading.Thread(target=self._speak_direct_simple, args=("Could you repeat that?",), daemon=True).start()
                            
                            logger.info("⏭️ RETURNING TO LISTENING")
                            time.sleep(0.2)
                            continue
                    else:
                        logger.info(f"❌ NO WAKE WORD IN: '{text}'")
                
                except sr.UnknownValueError:
                    logger.info("🤔 COULD NOT UNDERSTAND SPEECH - try speaking more clearly")
                except sr.RequestError as e:
                    logger.error(f"🌐 SPEECH SERVICE ERROR: {e}")
                except Exception as e:
                    logger.error(f"🤔 SPEECH RECOGNITION ERROR: {e}")
                    
            except sr.WaitTimeoutError:
                logger.debug("⏰ LISTENING TIMEOUT - no speech detected in 10 seconds")
            except Exception as e:
                logger.error(f"⏰ LISTENING ERROR: {e}")
                time.sleep(0.5)

    def _process_command_with_logging(self, command):
        """Process command with logging like test_maya_continuous.py"""
        logger.info(f"⚡ PROCESSING: {command}")
        result = self._process_command_fast(command)
        logger.info(f"✅ COMMAND PROCESSED: '{command}'")
        return result

    def _listen_for_command_working_method(self):
        """Listen for command using exact method from working test"""
        try:
            logger.info("🎧 LISTENING FOR COMMAND...")
            
            with self.microphone as source:
                logger.info("🔇 ADJUSTING FOR AMBIENT NOISE (1.8 seconds)...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.8)
                logger.info("🎙️ LISTENING FOR COMMAND (17 seconds timeout)...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=17)
            
            command = self.recognizer.recognize_google(audio).lower()
            logger.info(f"💭 COMMAND RECEIVED: '{command}'")
            return command
            
        except sr.UnknownValueError:
            logger.info("🤔 COULD NOT UNDERSTAND COMMAND")
            return None
        except sr.RequestError as e:
            logger.error(f"🌐 SPEECH SERVICE ERROR: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ COMMAND LISTENING ERROR: {e}")
            return None

    def _listen_for_command(self):
        """Legacy method - now redirects to working method"""
        return self._listen_for_command_working_method()

    def _process_command_fast(self, command):
        """Fast command processing with priority-based responses"""
        logger.info(f"⚡ Processing: {command}")
        
        # Movement commands get highest priority
        if self._handle_movement_command_fast(command):
            return
        
        # Quick responses for common commands
        if 'time' in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"Time is {current_time}")
            return
            
        elif 'date' in command:
            current_date = datetime.datetime.now().strftime("%A, %B %d")
            self.speak(f"Today is {current_date}")
            return
            
        elif any(word in command for word in ['hello', 'hi', 'namaste', 'hey']):
            self.speak(random.choice(self.greetings))
            return
            
        elif 'joke' in command:
            self._tell_quick_joke()
            return
            
        elif 'weather' in command:
            self._get_weather_quick()
            return
            
        elif any(phrase in command for phrase in ['what do you see', 'what is in front', 'what can you see', 'describe this']):
            self._handle_vision_quick()
            return
            
        elif 'status' in command:
            self._robot_status_quick()
            return
            
        elif any(word in command for word in ['bye', 'goodbye', 'exit', 'stop maya']):
            self._goodbye()
            return
            
        # Check for questions that should go to AI
        elif any(word in command for word in ['how', 'what', 'why', 'where', 'when', 'who', 'explain', 'tell me']):
            # This is likely a question, send to AI
            self._handle_ai_query_quick(command)
            return
            
        # If no quick match and it's a longer query, try AI processing
        elif len(command.split()) > 2:  # Complex query
            self._handle_ai_query_quick(command)
        else:
            # Random humor for unrecognized commands
            if random.random() < 0.3:
                self.speak(random.choice(self.humor_responses))
            else:
                self.speak("MAYA didn't understand that. Try asking a question or giving a command!")

    def _handle_movement_command_fast(self, command):
        """Fast movement command processing with direct motor control"""
        for phrase, cmd in self.movement_commands.items():
            if phrase in command.lower():
                logger.info(f"🚗 MOVEMENT COMMAND DETECTED: {phrase} -> {cmd}")
                
                # Try direct motor control first, then fallback to API
                try:
                    if self.direct_motor_control and self.motors:
                        # Use direct motor control for instant response
                        logger.info(f"🔌 USING DIRECT MOTOR CONTROL: {cmd}")
                        
                        # Execute movement command directly
                        self.motors.send_command(cmd)
                        success = True
                    else:
                        # Fallback to HTTP API
                        logger.info(f"🌐 USING HTTP API: {cmd}")
                        success = self.movement.send_command(cmd)
                    
                    if success:
                        # Quick confirmation
                        confirmation = random.choice(self.movement_confirmations[cmd])
                        threading.Thread(target=self._speak_direct_simple, args=(confirmation,), daemon=True).start()
                        logger.info(f"✅ MOVEMENT EXECUTED: {cmd}")
                    else:
                        error_msg = "Movement command failed! Robot may not be connected."
                        threading.Thread(target=self._speak_direct_simple, args=(error_msg,), daemon=True).start()
                        logger.error(f"❌ MOVEMENT FAILED: {cmd}")
                        
                except Exception as e:
                    error_msg = f"Robot control error! Check the connection."
                    threading.Thread(target=self._speak_direct_simple, args=(error_msg,), daemon=True).start()
                    logger.error(f"❌ MOVEMENT EXCEPTION: {e}")
                
                return True
        
        return False

    def _tell_quick_joke(self):
        """Quick joke responses"""
        quick_jokes = [
            "Why don't robots eat spicy food? They can't handle the bytes!",
            "What's a robot's favorite music? Heavy metal!",
            "Why did the robot go to therapy? Too many bugs!",
            "What do you call a robot who takes the long way? R2-Detour!",
            "Why don't robots ever panic? They have stable connections!"
        ]
        
        joke = random.choice(quick_jokes)
        self.speak(joke)

    def _get_weather_quick(self):
        """Quick weather using free API"""
        try:
            # Use wttr.in for instant weather (no API key needed)
            url = f"http://wttr.in/{DEFAULT_LOCATION}?format=3"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                weather = response.text.strip()
                self.speak(f"Weather in {DEFAULT_LOCATION}: {weather}")
            else:
                self.speak("Weather service is busy right now!")
        except:
            self.speak("Can't get weather at the moment!")

    def _handle_vision_quick(self):
        """Quick vision processing"""
        self.speak("MAYA taking a picture!")
        
        def vision_task():
            image_path = self._capture_image_fast()
            if image_path:
                self._describe_image_simple(image_path)
        
        # Run in background to avoid blocking
        threading.Thread(target=vision_task, daemon=True).start()

    def _capture_image_fast(self):
        """Fast image capture with reduced quality for speed"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = f"/tmp/maya_quick_{timestamp}.jpg"
            
            # Quick capture with lower resolution for speed
            cmd = ["libcamera-still", "-n", "--immediate", "-o", image_path, 
                   "--width", "640", "--height", "480", "--quality", "70"]
            
            result = subprocess.run(cmd, capture_output=True, timeout=3)
            
            if result.returncode == 0 and os.path.exists(image_path):
                return image_path
            else:
                self.speak("Camera not working!")
                return None
                
        except Exception as e:
            logger.error(f"Fast capture error: {e}")
            self.speak("Camera error!")
            return None

    def _describe_image_simple(self, image_path):
        """Simple image description without complex AI"""
        try:
            # For now, just confirm image was taken
            # TODO: Add simple object detection or AI vision when API is configured
            self.speak("MAYA captured the image! For detailed analysis, configure AI vision APIs.")
            
            # Clean up
            os.remove(image_path)
            
        except Exception as e:
            logger.error(f"Image description error: {e}")

    def _robot_status_quick(self):
        """Quick robot status check"""
        try:
            if self.movement.test_connection():
                self.speak("Robot is connected and ready!")
            else:
                self.speak("Robot connection needs attention!")
        except:
            self.speak("Cannot check robot status!")

    def _handle_ai_query_quick(self, query):
        """Handle AI queries using Gemini - completely non-blocking"""
        if self.ai_available.get('gemini'):
            # Give immediate feedback but don't wait
            self.speak("Let me think about that...", priority='high')
            
            def ai_process():
                try:
                    # Create a prompt for MAYA's personality
                    prompt = f"""You are MAYA, an intelligent Indian female virtual assistant for a robot. 
                    Respond in a friendly, helpful way with slight Indian context. Keep responses under 50 words.
                    Be conversational and warm.
                    
                    User question: {query}
                    
                    Respond as MAYA:"""
                    
                    # Generate response using Gemini
                    response = self.gemini_model.generate_content(prompt)
                    ai_answer = response.text.strip()
                    
                    # Clean up the response for better speech output
                    # Remove asterisks and other markdown formatting that affects speech
                    ai_answer = ai_answer.replace('*', '')
                    ai_answer = ai_answer.replace('#', '')
                    ai_answer = ai_answer.replace('_', '')
                    ai_answer = ai_answer.replace('`', '')
                    ai_answer = ai_answer.replace('[', '')
                    ai_answer = ai_answer.replace(']', '')
                    
                    # Remove extra spaces and normalize
                    ai_answer = ' '.join(ai_answer.split())
                    
                    # Make sure response is not too long
                    if len(ai_answer) > 200:
                        ai_answer = ai_answer[:200] + "..."
                    
                    logger.info(f"🧠 Gemini response: {ai_answer}")
                    
                    # Speak the response in background
                    threading.Thread(target=self._speak_direct_simple, args=(ai_answer,), daemon=True).start()
                    
                except Exception as e:
                    logger.error(f"Gemini error: {e}")
                    fallback_response = "MAYA's AI is having trouble with that question right now!"
                    threading.Thread(target=self._speak_direct_simple, args=(fallback_response,), daemon=True).start()
            
            # Run AI processing in background - completely separate from listening
            threading.Thread(target=ai_process, daemon=True).start()
            
        else:
            response = "MAYA would love to answer that! AI features are ready with Gemini!"
            self.speak(response, priority='high')

    def _goodbye(self):
        """Quick goodbye"""
        goodbyes = [
            "MAYA going to sleep! Namaste! 👋",
            "Alvida from MAYA! Take care! 🙏",
            "Bye bye! MAYA will miss you! 💫"
        ]
        self.speak(random.choice(goodbyes))
        self.running = False

    # Additional utility methods can be added here as needed
    
    def get_system_info_quick(self):
        """Quick system info for debugging"""
        try:
            # Get basic system info quickly
            uptime = subprocess.check_output("uptime -p", shell=True).decode().strip()
            self.speak(f"System {uptime}")
        except:
            self.speak("System info not available!")

    def start(self):
        """Start Enhanced MAYA Assistant"""
        self.running = True
        
        # Welcome message
        welcome_msg = "Namaste! Enhanced MAYA is now ready! Say 'Hey MAYA' to wake me up!"
        self.speak(welcome_msg)
        
        try:
            # Start continuous wake word listening
            self.listen_for_wake_word()
            
        except KeyboardInterrupt:
            logger.info("MAYA stopped by user")
        except Exception as e:
            logger.error(f"MAYA runtime error: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources when shutting down"""
        logger.info("🧹 MAYA cleanup starting...")
        
        self.running = False
        
        # Stop pygame mixer
        try:
            pygame.mixer.quit()
        except:
            pass
        
        # Clean up motor controller
        if hasattr(self, 'motors') and self.motors:
            try:
                self.motors.cleanup()
            except:
                pass
        
        # Clean up any temporary files
        try:
            import glob
            temp_files = glob.glob("/tmp/maya_speech_*.mp3")
            for file in temp_files:
                os.remove(file)
        except:
            pass
        
        logger.info("✅ MAYA cleanup completed")

def main():
    """Main function to run Enhanced MAYA Assistant"""
    try:
        maya = MAYAAssistant()
        maya.start()
    except KeyboardInterrupt:
        print("\n👋 Enhanced MAYA shutting down...")
    except Exception as e:
        print(f"❌ MAYA Critical Error: {e}")
        logger.error(f"Critical error: {e}")

if __name__ == "__main__":
    main()
