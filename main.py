#!/usr/bin/env python3
"""
Buddy Voice Assistant - ADVANCED AI ASSISTANT with ALEXA/SIRI-LEVEL INTELLIGENCE + TRUE STREAMING LLM + PRECISE BIRTINYA LOCATION
Updated: 2025-01-08 06:27:39 (UTC) - ADVANCED AI ASSISTANT INTEGRATION
FEATURES: Anonymous clustering, passive audio buffering, same-name collision handling, spontaneous introductions, behavioral learning, Alexa/Siri-level intelligence
"""

import threading
import time
import numpy as np
import pyaudio
import pvporcupine
import os
import json
import re
from datetime import datetime  # ✅ ADD THIS IMPORT
from scipy.io.wavfile import write
from voice.database import load_known_users, known_users, save_known_users, anonymous_clusters
from ai.memory import validate_ai_response_appropriateness, add_to_conversation_history
from ai.chat_enhanced_smart import generate_response_streaming_with_smart_memory, reset_session_for_user_smart
from ai.chat_enhanced_smart_with_fusion import generate_response_streaming_with_intelligent_fusion

from voice.voice_manager_instance import voice_manager
from voice.manager_names import UltraIntelligentNameManager

voice_manager.ultra_name_manager = UltraIntelligentNameManager(voice_manager)
print("[Main] ✅ UltraIntelligentNameManager assigned to voice_manager")

from config import *

# Import with better error handling
try:
    from audio.full_duplex_manager import full_duplex_manager
    if full_duplex_manager is None:
        print("[AdvancedBuddy] ❌ Full duplex manager is None")
        FULL_DUPLEX_MODE = False
    else:
        print("[AdvancedBuddy] ✅ Full duplex manager imported successfully")
except Exception as e:
    print(f"[AdvancedBuddy] ❌ Could not import full duplex manager: {e}")
    FULL_DUPLEX_MODE = False
    full_duplex_manager = None

# ✅ FIXED: Force correct voice manager import
ADVANCED_AI_AVAILABLE = False
ENHANCED_VOICE_AVAILABLE = False

try:
    # Always load database first
    from voice.database import load_known_users, known_users, anonymous_clusters, save_known_users
    print("[AdvancedBuddy] ✅ Voice database loaded")
    
    # ✅ FORCE CORRECT VOICE MANAGER IMPORT - Always use IntelligentVoiceManager
    try:
        from voice.manager import voice_manager as intelligent_voice_manager
        voice_manager = intelligent_voice_manager
        
        print("[AdvancedBuddy] ✅ Using IntelligentVoiceManager from manager.py")
        print(f"[AdvancedBuddy] 🔍 voice_manager type: {type(voice_manager)}")
        
        # Verify it has the correct method
        if hasattr(voice_manager, 'handle_voice_identification'):
            print("[AdvancedBuddy] ✅ handle_voice_identification method confirmed")
            ADVANCED_AI_AVAILABLE = True  # Your IntelligentVoiceManager IS advanced
        else:
            print("[AdvancedBuddy] ❌ handle_voice_identification method missing!")
        
        # Load voice training components
        from voice.training import voice_training_mode, check_voice_training_command
        print("[AdvancedBuddy] ✅ Voice training components loaded")
        
    except ImportError as manager_err:
        print(f"[AdvancedBuddy] ❌ IntelligentVoiceManager import failed: {manager_err}")
        
        # ✅ CRITICAL: Ensure we still have database functions
        try:
            from voice.database import load_known_users, known_users, save_known_users
            from voice.recognition import identify_speaker_with_confidence
            print("[AdvancedBuddy] ✅ Database functions available")
        except Exception as db_err:
            print(f"[AdvancedBuddy] 🚨 CRITICAL: Database functions missing: {db_err}")
        
        # Create working fallback voice manager
        class WorkingVoiceManager:
            def __init__(self):
                try:
                    load_known_users()
                    print(f"[WorkingVoiceManager] 💾 Loaded {len(known_users)} profiles")
                except Exception as e:
                    print(f"[WorkingVoiceManager] ❌ Load error: {e}")
            
            def handle_voice_identification(self, audio, text):
                """Handle voice identification with fallback logic"""
                try:
                    # Try basic voice recognition
                    from voice.recognition import identify_speaker_with_confidence
                    identified_user, confidence = identify_speaker_with_confidence(audio)
                    
                    if identified_user != "UNKNOWN" and confidence > 0.7:
                        print(f"[WorkingVoiceManager] ✅ Recognized: {identified_user} ({confidence:.3f})")
                        return identified_user, "RECOGNIZED"
                    else:
                        print(f"[WorkingVoiceManager] 🔍 Unknown voice, using Daveydrz")
                        return "Daveydrz", "FALLBACK_TO_SYSTEM_USER"
                        
                except Exception as recognition_err:
                    print(f"[WorkingVoiceManager] ❌ Recognition error: {recognition_err}")
                    
                    # Save debug info for troubleshooting
                    try:
                        timestamp = datetime.utcnow().isoformat()
                        debug_data = {
                            'timestamp': timestamp,
                            'text': text,
                            'audio_received': audio is not None,
                            'audio_length': len(audio) if audio else 0,
                            'error': str(recognition_err),
                            'system_user': 'Daveydrz'
                        }
                        
                        # Save debug info
                        try:
                            with open('voice_debug.json', 'r') as f:
                                logs = json.load(f)
                        except:
                            logs = []
                        
                        logs.append(debug_data)
                        if len(logs) > 20:
                            logs = logs[-20:]
                        
                        with open('voice_debug.json', 'w') as f:
                            json.dump(logs, f, indent=2)
                        
                        print(f"[WorkingVoiceManager] 💾 Saved debug info for: '{text}'")
                        
                    except Exception as save_err:
                        print(f"[WorkingVoiceManager] ❌ Save error: {save_err}")
                    
                    return "Daveydrz", "MINIMAL_FALLBACK"
            
            def is_llm_locked(self):
                return False
            
            def get_session_stats(self):
                return {
                    'interactions': 0,
                    'session_duration': 0,
                    'known_users': len(known_users) if 'known_users' in globals() else 0,
                    'anonymous_clusters': len(anonymous_clusters) if 'anonymous_clusters' in globals() else 0,
                    'current_user': 'Daveydrz',
                    'system': 'WorkingVoiceManager'
                }
        
        voice_manager = WorkingVoiceManager()
        voice_training_mode = lambda: False
        check_voice_training_command = lambda x: False
        print("[AdvancedBuddy] ✅ WorkingVoiceManager fallback created")
    
    # ✅ FIXED: Try to load identity helpers
    try:
        from voice.identity_helpers import (
            get_voice_based_identity, 
            get_voice_based_display_name, 
            get_voice_based_name_response,
            update_voice_identity_context,
            debug_voice_identity_status,
            run_maintenance
        )
        print("[AdvancedBuddy] ✅ Voice-based identity system loaded")
        
    except ImportError as identity_err:
        print(f"[AdvancedBuddy] ⚠️ Identity helpers import failed: {identity_err}")
        
        # Create fallback identity functions
        def get_voice_based_identity(audio_data=None):
            """Get identity from voice recognition"""
            try:
                if hasattr(voice_manager, 'handle_voice_identification'):
                    result = voice_manager.handle_voice_identification(audio_data, "")
                    return result[0] if result else "Daveydrz"
                return "Daveydrz"
            except Exception as e:
                print(f"[VoiceIdentity] ❌ Error: {e}")
                return "Daveydrz"

        def get_voice_based_display_name(user_id):
            """Get display name for user"""
            if user_id == "Daveydrz":
                return "Daveydrz"
            elif user_id and user_id.startswith('Anonymous_'):
                return f"Speaker {user_id.split('_')[1]}"
            return user_id or "friend"

        def get_voice_based_name_response(user_id, display_name):
            """Get response for name questions"""
            if user_id == "Daveydrz":
                return "You are Daveydrz."
            elif user_id and user_id.startswith('Anonymous_'):
                return "I don't recognize your voice yet. Could you tell me your name?"
            return f"Your name is {display_name}."

        def update_voice_identity_context(user_id):
            """Update voice identity context"""
            print(f"[VoiceIdentity] 🔄 Updated context for: {user_id}")

        def debug_voice_identity_status():
            """Debug voice identity status"""
            try:
                from voice.database import known_users, anonymous_clusters
                print(f"[VoiceIdentity] 📊 Known users: {len(known_users)}")
                print(f"[VoiceIdentity] 🔍 Anonymous clusters: {len(anonymous_clusters)}")
                return True
            except Exception as e:
                print(f"[VoiceIdentity] ❌ Debug error: {e}")
                return False

        def run_maintenance():
            """Run voice system maintenance"""
            print("[VoiceIdentity] 🔧 Running maintenance...")
            return {"status": "complete", "message": "Fallback maintenance complete"}
        
        print("[AdvancedBuddy] ✅ Fallback identity functions created")

except Exception as e:
    print(f"[AdvancedBuddy] ❌ Critical voice system error: {e}")
    import traceback
    traceback.print_exc()

# Set fallback instances
advanced_context_analyzer = None
advanced_name_manager = None

# ✅ VERIFY FINAL STATE
print(f"[AdvancedBuddy] 🔍 Final voice_manager type: {type(voice_manager)}")
print(f"[AdvancedBuddy] 🔍 ADVANCED_AI_AVAILABLE: {ADVANCED_AI_AVAILABLE}")
print(f"[AdvancedBuddy] 👤 System User: Daveydrz")
print(f"[AdvancedBuddy] 📅 Current UTC Time: 2025-01-13 08:06:19")

# Test voice manager immediately
try:
    if hasattr(voice_manager, 'handle_voice_identification'):
        print("[AdvancedBuddy] ✅ voice_manager.handle_voice_identification method available")
    else:
        print("[AdvancedBuddy] ❌ voice_manager.handle_voice_identification method NOT available")
        print(f"[AdvancedBuddy] 📋 Available methods: {[m for m in dir(voice_manager) if not m.startswith('_')]}")
except Exception as test_err:
    print(f"[AdvancedBuddy] ❌ voice_manager test error: {test_err}")

# ✅ Updated imports for Kokoro-FastAPI streaming with error handling
try:
    from audio.output import (
        speak_async, speak_streaming, play_chime, start_audio_worker,
        test_kokoro_api, get_audio_stats, clear_audio_queue, stop_audio_playback
    )
    print("[AdvancedBuddy] ✅ All audio functions imported successfully")
except ImportError as e:
    print(f"[AdvancedBuddy] ⚠️ Some audio functions not available: {e}")
    
    # Import what we can
    try:
        from audio.output import speak_async, speak_streaming, play_chime, start_audio_worker, test_kokoro_api, get_audio_stats
        print("[AdvancedBuddy] ✅ Basic audio functions imported")
    except ImportError:
        print("[AdvancedBuddy] ❌ Basic audio functions failed")
    
    # Define fallback functions for interrupt handling
    def stop_audio_playback():
        print("[AdvancedBuddy] 🛑 stop_audio_playback fallback - interrupt handling disabled")
        pass
    
    def clear_audio_queue():
        print("[AdvancedBuddy] 🧹 clear_audio_queue fallback - queue clearing disabled")
        pass

from ai.chat import generate_response  # Keep for fallback
from ai.memory import add_to_conversation_history
from voice.database import load_known_users, known_users, anonymous_clusters
from voice.recognition import identify_speaker
from utils.helpers import should_end_conversation
from audio.processing import downsample_audio

# ✅ Load Birtinya location with advanced features
def load_birtinya_location():
    """Load precise Birtinya location data with advanced features"""
    try:
        # Try multiple possible location files
        location_files = [
            'buddy_gps_location.json',
            'buddy_gps_location_birtinya.json',
            'buddy_gps_location_2025-07-06.json'
        ]
        
        for filename in location_files:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    location_data = json.load(f)
                
                print(f"[AdvancedBuddy] 📍 Loaded location from: {filename}")
                print(f"[AdvancedBuddy] 🏘️ Location: {location_data.get('suburb')}, {location_data.get('state')}")
                print(f"[AdvancedBuddy] 📮 Postcode: {location_data.get('postal_code')}")
                print(f"[AdvancedBuddy] 🌏 Coordinates: {location_data.get('latitude')}, {location_data.get('longitude')}")
                print(f"[AdvancedBuddy] 🎯 Confidence: {location_data.get('confidence')}")
                
                return location_data
        
        print("[AdvancedBuddy] ⚠️ No location file found, using Brisbane fallback")
        return None
        
    except Exception as e:
        print(f"[AdvancedBuddy] ❌ Error loading location: {e}")
        return None

# Load Birtinya location data
BIRTINYA_LOCATION = load_birtinya_location()

if BIRTINYA_LOCATION:
    USER_PRECISE_LOCATION = f"{BIRTINYA_LOCATION['suburb']}, {BIRTINYA_LOCATION['state']}"
    USER_COORDINATES_PRECISE = (BIRTINYA_LOCATION['latitude'], BIRTINYA_LOCATION['longitude'])
    USER_POSTCODE_PRECISE = BIRTINYA_LOCATION['postal_code']
    USER_LANDMARKS = BIRTINYA_LOCATION.get('landmark', 'USC, Stockland Birtinya')
    LOCATION_CONFIDENCE_PRECISE = BIRTINYA_LOCATION['confidence']
    IS_SUNSHINE_COAST = BIRTINYA_LOCATION.get('area_info', {}).get('coastal_location', True)
    DISTANCE_TO_BRISBANE = BIRTINYA_LOCATION.get('area_info', {}).get('distance_to_brisbane_km', 90)
else:
    # Fallback to Brisbane
    USER_PRECISE_LOCATION = "Brisbane, Queensland"
    USER_COORDINATES_PRECISE = (-27.4698, 153.0251)
    USER_POSTCODE_PRECISE = "4000"
    USER_LANDMARKS = "CBD"
    LOCATION_CONFIDENCE_PRECISE = "LOW"
    IS_SUNSHINE_COAST = False
    DISTANCE_TO_BRISBANE = 0

# ✅ DYNAMIC: Get actual current Brisbane time
try:
    from datetime import datetime, timezone, timedelta
    
    # Get actual current UTC time
    utc_now = datetime.now(timezone.utc)
    
    # Brisbane timezone (UTC+10)
    brisbane_tz = timezone(timedelta(hours=10))
    brisbane_now = utc_now.astimezone(brisbane_tz)
    
    # Format the time strings
    brisbane_time_str = brisbane_now.strftime("%Y-%m-%d %H:%M:%S")
    brisbane_time_12h = brisbane_now.strftime("%I:%M %p")
    brisbane_date = brisbane_now.strftime("%A, %B %d, %Y")
    
    print(f"[AdvancedBuddy] 🕐 Brisbane Time: {brisbane_time_str} ({brisbane_time_12h})")
    print(f"[AdvancedBuddy] 📅 Brisbane Date: {brisbane_date}")
    
except Exception as e:
    print(f"[AdvancedBuddy] ⚠️ Time calculation error: {e}")
    # Fallback time
    brisbane_time_str = "2025-01-08 16:27:39"
    brisbane_time_12h = "4:27 PM"
    brisbane_date = "Wednesday, January 8, 2025"

print(f"[AdvancedBuddy] 🚀 Starting ADVANCED AI ASSISTANT + TRUE STREAMING BIRTINYA Buddy - {brisbane_time_str}")
print(f"[AdvancedBuddy] 📍 Precise Location: {USER_PRECISE_LOCATION}")
print(f"[AdvancedBuddy] 📮 Postcode: {USER_POSTCODE_PRECISE}")
print(f"[AdvancedBuddy] 🌏 Coordinates: {USER_COORDINATES_PRECISE}")
print(f"[AdvancedBuddy] 🏛️ Landmarks: {USER_LANDMARKS}")
print(f"[AdvancedBuddy] 🌊 Sunshine Coast: {IS_SUNSHINE_COAST}")
print(f"[AdvancedBuddy] 📏 Distance to Brisbane: {DISTANCE_TO_BRISBANE}km")
print(f"[AdvancedBuddy] 🎯 Confidence: {LOCATION_CONFIDENCE_PRECISE}")

# ✅ ADVANCED AI ASSISTANT status display
if ADVANCED_AI_AVAILABLE:
    print(f"[AdvancedBuddy] 🚀 ADVANCED AI ASSISTANT: FULLY ACTIVE")
    print(f"[AdvancedBuddy] 🎯 Alexa/Siri-level Intelligence: ENABLED")
    print(f"[AdvancedBuddy] 🔍 Anonymous Voice Clustering: ACTIVE")
    print(f"[AdvancedBuddy] 🎤 Passive Audio Buffering: ALWAYS ON")
    print(f"[AdvancedBuddy] 🛡️ LLM Guard System: PROTECTING RESPONSES")
    print(f"[AdvancedBuddy] 👥 Same-Name Collision Handling: AUTO David_001, David_002")
    print(f"[AdvancedBuddy] 🎭 Spontaneous Introduction Detection: NATURAL")
    print(f"[AdvancedBuddy] 🧠 Behavioral Pattern Learning: ADAPTIVE")
    print(f"[AdvancedBuddy] 📊 Advanced Analytics: MONITORING")
    print(f"[AdvancedBuddy] 🔧 Auto Maintenance: SELF-OPTIMIZING")
elif ENHANCED_VOICE_AVAILABLE:
    print(f"[AdvancedBuddy] ✅ Enhanced Voice System: ACTIVE")
    print(f"[AdvancedBuddy] 📊 Multi-Embedding Profiles: Available")
    print(f"[AdvancedBuddy] 🧠 SpeechBrain Integration: Available")
    print(f"[AdvancedBuddy] 🌱 Passive Learning: Enabled")
    print(f"[AdvancedBuddy] 🔍 Quality Analysis: Advanced")
    print(f"[AdvancedBuddy] 💾 Raw Audio Storage: Enabled")
else:
    print(f"[AdvancedBuddy] ⚠️ Using Legacy Voice System")

# Global state - Enhanced with advanced features
current_user = SYSTEM_USER
conversation_active = False
mic_feeding_active = False
advanced_mode_active = ADVANCED_AI_AVAILABLE
# Add a lock for thread safety
state_lock = threading.Lock()

def set_conversation_state(active):
    """Thread-safe way to set conversation state"""
    global conversation_active
    with state_lock:
        conversation_active = active
        print(f"[State] 🔄 conversation_active set to: {active}")

def set_mic_feeding_state(active):
    """Thread-safe way to set mic feeding state"""
    global mic_feeding_active
    with state_lock:
        mic_feeding_active = active
        print(f"[State] 🎤 mic_feeding_active set to: {active}")

def get_conversation_state():
    """Thread-safe way to get conversation state"""
    with state_lock:
        return conversation_active

def get_mic_feeding_state():
    """Thread-safe way to get mic feeding state"""
    with state_lock:
        return mic_feeding_active

def is_simple_conversation(text):
    """🚀 PERFORMANCE: Detect simple conversations that can bypass heavy processing"""
    text_lower = text.lower().strip()
    
    # Simple greetings and casual conversation patterns
    simple_patterns = [
        # Greetings
        r'^hi\b', r'^hello\b', r'^hey\b', r'^good morning\b', r'^good afternoon\b', r'^good evening\b',
        # Casual questions
        r'^how are you', r'^how\'s it going', r'^what\'s up', r'^how you doing',
        # Simple acknowledgments
        r'^yes\b', r'^no\b', r'^okay\b', r'^ok\b', r'^thanks\b', r'^thank you\b',
        # Simple responses
        r'^good\b', r'^fine\b', r'^great\b', r'^alright\b',
    ]
    
    for pattern in simple_patterns:
        if re.match(pattern, text_lower):
            print(f"[FastPath] ✅ Simple conversation detected: '{text}' - bypassing heavy processing")
            return True
    
    # Check for questions that definitely need name extraction (introductions)
    introduction_patterns = [
        r'my name is', r'call me', r'i\'m [a-zA-Z]+$', r'this is [a-zA-Z]+$'
    ]
    
    for pattern in introduction_patterns:
        if re.search(pattern, text_lower):
            print(f"[FastPath] 🆔 Introduction detected: '{text}' - requires full processing")
            return False
    
    print(f"[FastPath] ➡️ Regular conversation: '{text}' - using standard processing")
    return False

# Global cache for identity results to prevent duplicate analysis
_identity_cache = {}
_identity_cache_timestamp = {}

def get_cached_identity(audio_hash, current_user, max_age_seconds=30):
    """🚀 PERFORMANCE: Get cached identity result to prevent duplicate analysis"""
    import time
    import hashlib
    
    if audio_hash is None:
        return None
        
    # Check if we have a recent result for this audio
    if audio_hash in _identity_cache:
        age = time.time() - _identity_cache_timestamp.get(audio_hash, 0)
        if age < max_age_seconds:
            cached_result = _identity_cache[audio_hash]
            print(f"[Cache] ✅ Using cached identity: {cached_result} (age: {age:.1f}s)")
            return cached_result
        else:
            # Remove expired cache entry
            del _identity_cache[audio_hash]
            del _identity_cache_timestamp[audio_hash]
    
    return None

def cache_identity_result(audio_hash, identity_result):
    """🚀 PERFORMANCE: Cache identity result for reuse"""
    import time
    
    if audio_hash is not None and identity_result is not None:
        _identity_cache[audio_hash] = identity_result
        _identity_cache_timestamp[audio_hash] = time.time()
        print(f"[Cache] 💾 Cached identity result: {identity_result}")

def handle_streaming_response(text, current_user):
    """✅ ENHANCED: Smart streaming with ADVANCED AI ASSISTANT features + VOICE-BASED IDENTITY + PERFORMANCE OPTIMIZATIONS"""
    print(f"🚨🚨🚨 [CRITICAL_DEBUG] handle_streaming_response called with text='{text}', user='{current_user}' 🚨🚨🚨")
    try:
        print(f"[AdvancedResponse] 🎭 Starting ADVANCED AI streaming for: '{text}'")
        
        # 🚀 PERFORMANCE: Fast-path for simple conversations
        if is_simple_conversation(text):
            print(f"[FastPath] ⚡ Using fast-path for simple conversation")
            
            # Quick responses for direct questions (immediate)
            if is_direct_time_question(text):
                brisbane_time = get_current_brisbane_time()
                if IS_SUNSHINE_COAST:
                    speak_streaming(f"It's {brisbane_time['time_12h']} here in Birtinya, Sunshine Coast.")
                else:
                    speak_streaming(f"It's {brisbane_time['time_12h']} here in {USER_PRECISE_LOCATION}.")
                return
            
            if is_direct_location_question(text):
                if IS_SUNSHINE_COAST:
                    speak_streaming(f"I'm located in Birtinya, Sunshine Coast, Queensland {USER_POSTCODE_PRECISE}.")
                else:
                    speak_streaming(f"I'm located in {USER_PRECISE_LOCATION} {USER_POSTCODE_PRECISE}.")
                return
            
            if is_direct_date_question(text):
                brisbane_time = get_current_brisbane_time()
                speak_streaming(f"Today is {brisbane_time['date']}.")
                return
            
            # For simple conversations, bypass voice processing and go directly to LLM
            print(f"[FastPath] ⚡ Bypassing identity analysis for simple conversation")
            
            # Use basic user (no expensive voice processing)
            simple_user = current_user
            
            # Generate response directly without identity processing
            full_response = ""
            chunk_count = 0
            first_chunk = True
            response_interrupted = False
            
            try:
                from ai.chat_enhanced_smart_with_fusion import generate_response_streaming_with_intelligent_fusion
                print("[FastPath] ✅ Using FAST PATH AI streaming")
                
                # Process LLM chunks with IMMEDIATE interrupt breaking
                for chunk in generate_response_streaming_with_intelligent_fusion(text, simple_user, DEFAULT_LANG):
                    # Check for interrupt BEFORE processing chunk
                    if full_duplex_manager and full_duplex_manager.speech_interrupted:
                        print("[FastPath] ⚡ INTERRUPT DETECTED - IMMEDIATELY STOPPING LLM")
                        response_interrupted = True
                        break
                    
                    if chunk and chunk.strip():
                        chunk_count += 1
                        chunk_text = chunk.strip()
                        
                        if first_chunk:
                            print("[FastPath] 🎭 First chunk ready - starting natural speech!")
                            first_chunk = False
                        
                        print(f"[FastPath] 🗣️ Speaking chunk {chunk_count}: '{chunk_text[:50]}...'")
                        
                        # Validate chunk before speaking
                        try:
                            is_appropriate, validated_chunk = validate_ai_response_appropriateness(simple_user, chunk_text)
                            
                            if not is_appropriate:
                                print(f"[FastPath] 🛡️ Chunk {chunk_count} corrected for context appropriateness")
                                chunk_text = validated_chunk
                        except Exception as validation_error:
                            print(f"[FastPath] ⚠️ Validation error for chunk {chunk_count}: {validation_error}")
                        
                        # Speak chunk
                        speak_streaming(chunk_text)
                        full_response += chunk_text + " "
                        
                        # Check AGAIN after queueing
                        if full_duplex_manager and full_duplex_manager.speech_interrupted:
                            print("[FastPath] ⚡ INTERRUPT AFTER QUEUEING - STOPPING NOW")
                            response_interrupted = True
                            break
                        
                        # Brief pause for natural flow
                        if not (full_duplex_manager and full_duplex_manager.speech_interrupted):
                            time.sleep(0.05)
            
            except ImportError:
                print("[FastPath] ⚠️ Advanced streaming not available, using enhanced fallback")
                response = generate_response(text, simple_user, DEFAULT_LANG)
                
                # Validate complete response before speaking
                try:
                    is_appropriate, validated_response = validate_ai_response_appropriateness(simple_user, response)
                    
                    if not is_appropriate:
                        print(f"[FastPath] 🛡️ Fallback response corrected for context appropriateness")
                        response = validated_response
                except Exception as validation_error:
                    print(f"[FastPath] ⚠️ Validation error for fallback response: {validation_error}")
                
                # Split into sentences for interrupt checking
                sentences = re.split(r'(?<=[.!?])\s+', response)
                for sentence in sentences:
                    if sentence.strip():
                        # Check for interrupt before each sentence
                        if full_duplex_manager and full_duplex_manager.speech_interrupted:
                            print("[FastPath] ⚡ INTERRUPT IN FALLBACK - STOPPING")
                            response_interrupted = True
                            break
                        
                        speak_streaming(sentence.strip())
                        
                        # Check again after queueing
                        if full_duplex_manager and full_duplex_manager.speech_interrupted:
                            print("[FastPath] ⚡ INTERRUPT AFTER FALLBACK SENTENCE - STOPPING")
                            response_interrupted = True
                            break
                        
                        time.sleep(0.1)
                
                full_response = response
            
            # Handle completion
            if not response_interrupted:
                if full_response.strip():
                    add_to_conversation_history(simple_user, text, full_response.strip())
                    print(f"[FastPath] ✅ FAST PATH streaming complete for user {simple_user} - {chunk_count} segments")
                else:
                    print("[FastPath] ❌ No response generated")
                    speak_streaming("I'm sorry, I didn't generate a proper response.")
            else:
                print("[FastPath] ⚡ Response was INTERRUPTED - skipping completion")
                
                # Emergency cleanup after interrupt
                try:
                    clear_audio_queue()
                    stop_audio_playback()
                    print("[FastPath] 🧹 Emergency audio cleanup completed")
                except Exception as cleanup_err:
                    print(f"[FastPath] ⚠️ Cleanup error: {cleanup_err}")
            
            return  # Exit early for simple conversations
        
        # ✅ FULL PROCESSING: For complex conversations that need identity analysis
        print(f"[AdvancedResponse] 🔍 Complex conversation detected - using full processing pipeline")
        
        # Generate audio hash for caching (if audio is available)
        audio_hash = None
        try:
            if hasattr(voice_manager, 'get_last_audio_sample') and voice_manager.get_last_audio_sample():
                import hashlib
                last_audio = voice_manager.get_last_audio_sample()
                if last_audio is not None:
                    audio_hash = hashlib.md5(last_audio.tobytes() if hasattr(last_audio, 'tobytes') else str(last_audio).encode()).hexdigest()
        except Exception as hash_error:
            print(f"[Cache] ⚠️ Audio hashing error: {hash_error}")
        
        # Check cache first to prevent duplicate analysis
        cached_identity = get_cached_identity(audio_hash, current_user)
        if cached_identity:
            current_user = cached_identity
            print(f"[Cache] ⚡ Using cached identity, skipping voice analysis")
        else:
            # ✅ NEW: Get voice-based identity FIRST (overrides system login) - only for complex conversations
            voice_identified_user = None
            try:
                # STEP 1: Check if current_user is a cluster ID
                if current_user and current_user.startswith('Anonymous_'):
                    print(f"[VoiceIdentity] 🔍 Cluster ID detected: {current_user}")
                    
                    # STEP 2: Try to get the display name from ai.speech
                    try:
                        from ai.speech import get_display_name
                        display_name = get_display_name(current_user)
                        
                        # STEP 3: If display name is different and looks like a real name, use it
                        if (display_name and 
                            display_name != current_user and 
                            display_name not in ['friend', 'Anonymous_Speaker', 'Unknown', 'Guest']):
                            
                            current_user = display_name
                            print(f"[VoiceIdentity] 🎯 DISPLAY NAME OVERRIDE: Using {current_user}")
                            
                    except Exception as display_error:
                        print(f"[VoiceIdentity] ⚠️ Display name error: {display_error}")
                
                # STEP 4: Also try voice-based identity from audio
                if hasattr(voice_manager, 'get_last_audio_sample') and voice_manager.get_last_audio_sample():
                    last_audio = voice_manager.get_last_audio_sample()
                    voice_identified_user = get_voice_based_identity(last_audio)
                    if voice_identified_user and voice_identified_user not in ["Anonymous_Speaker", "Unknown", "Guest"]:
                        # Only override if it's a real name, not another cluster
                        if not voice_identified_user.startswith('Anonymous_'):
                            current_user = voice_identified_user
                            print(f"[VoiceIdentity] 🎤 AUDIO VOICE OVERRIDE: Using {current_user}")
                
                # STEP 5: Advanced voice processing if available
                if ADVANCED_AI_AVAILABLE and hasattr(voice_manager, 'get_current_speaker_identity'):
                    advanced_user = voice_manager.get_current_speaker_identity()
                    if advanced_user and advanced_user not in ["Unknown", "Anonymous_Speaker"]:
                        # Only use if it's a real name
                        if not advanced_user.startswith('Anonymous_'):
                            current_user = advanced_user
                            print(f"[AdvancedAI] 🎯 Advanced voice ID: {current_user}")
                    
            except Exception as voice_error:
                print(f"[VoiceIdentity] ⚠️ Voice ID error: {voice_error}")
            
            # Cache the identity result
            cache_identity_result(audio_hash, current_user)

        print(f"[VoiceIdentity] ✅ FINAL USER for LLM: {current_user}")
        
        # ✅ PERFORMANCE: Conditional name extraction - only check if it looks like an introduction
        should_check_names = any(keyword in text.lower() for keyword in [
            "my name is", "call me", "i'm", "this is", "my name", "who am i", "what's my name"
        ])
        
        if should_check_names:
            print(f"[AdvancedResponse] 🆔 Introduction/name keywords detected - running name analysis")
            try:
                from ai.speech import identify_user, get_display_name
                
                # Check if user is introducing themselves
                identify_user(text, current_user)
                
                # Get display name for responses (voice-based, not system)
                display_name = get_voice_based_display_name(current_user)
                
                # Handle name questions using VOICE MATCHING (not system login)
                if any(phrase in text.lower() for phrase in ["what's my name", "my name", "who am i", "what is my name"]):
                    voice_response = get_voice_based_name_response(current_user, display_name)
                    speak_streaming(voice_response)
                    return
                    
            except ImportError:
                print(f"[AdvancedResponse] ⚠️ Speech identification not available")
                display_name = get_voice_based_display_name(current_user)
            except Exception as id_error:
                print(f"[AdvancedResponse] ⚠️ Identification error: {id_error}")
                display_name = get_voice_based_display_name(current_user)
        else:
            print(f"[AdvancedResponse] ⚡ PERFORMANCE: Skipping name extraction for non-introduction text")
            display_name = get_voice_based_display_name(current_user)
        
        # ✅ ADVANCED: Check if LLM is locked by voice processing
        if ADVANCED_AI_AVAILABLE and hasattr(voice_manager, 'is_llm_locked'):
            if voice_manager.is_llm_locked():
                print(f"[AdvancedResponse] 🛡️ LLM LOCKED by voice processing - queuing response")
                return
        
        # Quick responses for direct questions (immediate)
        if is_direct_time_question(text):
            brisbane_time = get_current_brisbane_time()
            if IS_SUNSHINE_COAST:
                speak_streaming(f"It's {brisbane_time['time_12h']} here in Birtinya, Sunshine Coast.")
            else:
                speak_streaming(f"It's {brisbane_time['time_12h']} here in {USER_PRECISE_LOCATION}.")
            return
        
        if is_direct_location_question(text):
            if IS_SUNSHINE_COAST:
                speak_streaming(f"I'm located in Birtinya, Sunshine Coast, Queensland {USER_POSTCODE_PRECISE}.")
            else:
                speak_streaming(f"I'm located in {USER_PRECISE_LOCATION} {USER_POSTCODE_PRECISE}.")
            return
        
        if is_direct_date_question(text):
            brisbane_time = get_current_brisbane_time()
            speak_streaming(f"Today is {brisbane_time['date']}.")
            return
        
        # ✅ ADVANCED AI: Natural conversation flow with VOICE-IDENTIFIED USER
        print(f"[AdvancedResponse] 🧠 Starting ADVANCED AI LLM streaming for VOICE USER: {current_user}")
        
        full_response = ""
        chunk_count = 0
        first_chunk = True
        response_interrupted = False
        
        try:
            from ai.chat_enhanced_smart_with_fusion import generate_response_streaming_with_intelligent_fusion
            print("[AdvancedResponse] ✅ Using ADVANCED AI streaming with INTELLIGENT FUSION")
            
            # ✅ ADVANCED: Process LLM chunks with IMMEDIATE interrupt breaking
            for chunk in generate_response_streaming_with_intelligent_fusion(text, current_user, DEFAULT_LANG):
                # ✅ CRITICAL: Check for interrupt BEFORE processing chunk
                if full_duplex_manager and full_duplex_manager.speech_interrupted:
                    print("[AdvancedResponse] ⚡ INTERRUPT DETECTED - IMMEDIATELY STOPPING LLM")
                    response_interrupted = True
                    break  # ✅ CRITICAL: Break immediately!
                
                if chunk and chunk.strip():
                    chunk_count += 1
                    chunk_text = chunk.strip()
                    
                    if first_chunk:
                        print("[AdvancedResponse] 🎭 First ADVANCED chunk ready - starting natural speech!")
                        first_chunk = False
                    
                    print(f"[AdvancedResponse] 🗣️ Speaking chunk {chunk_count}: '{chunk_text[:50]}...'")
                    
                    # 🧠 MEGA-INTELLIGENT: Validate chunk before speaking
                    try:
                        is_appropriate, validated_chunk = validate_ai_response_appropriateness(current_user, chunk_text)
                        
                        if not is_appropriate:
                            print(f"[MegaMemory] 🛡️ Chunk {chunk_count} corrected for context appropriateness")
                            chunk_text = validated_chunk
                    except Exception as validation_error:
                        print(f"[MegaMemory] ⚠️ Validation error for chunk {chunk_count}: {validation_error}")
                        # Continue with original chunk if validation fails
                    
                    # ✅ SPEAK CHUNK (now validated)
                    speak_streaming(chunk_text)
                    full_response += chunk_text + " "
                    
                    # ✅ CRITICAL: Check AGAIN after queueing and break if interrupted
                    if full_duplex_manager and full_duplex_manager.speech_interrupted:
                        print("[AdvancedResponse] ⚡ INTERRUPT AFTER QUEUEING - STOPPING NOW")
                        response_interrupted = True
                        break  # ✅ CRITICAL: Break immediately!
                    
                    # Brief pause for natural flow (only if not interrupted)
                    if not (full_duplex_manager and full_duplex_manager.speech_interrupted):
                        time.sleep(0.05)
        
        except (ConnectionError, ConnectionAbortedError, OSError) as conn_err:
            print(f"[AdvancedResponse] 🔌 Connection interrupted: {conn_err}")
            response_interrupted = True
            
        except ImportError:
            print("[AdvancedResponse] ⚠️ Advanced streaming not available, using enhanced fallback")
            response = generate_response(text, current_user, DEFAULT_LANG)
            
            # 🧠 MEGA-INTELLIGENT: Validate complete response before speaking
            try:
                is_appropriate, validated_response = validate_ai_response_appropriateness(current_user, response)
                
                if not is_appropriate:
                    print(f"[MegaMemory] 🛡️ Fallback response corrected for context appropriateness")
                    response = validated_response
            except Exception as validation_error:
                print(f"[MegaMemory] ⚠️ Validation error for fallback response: {validation_error}")
                # Continue with original response if validation fails
            
            # Split into sentences for interrupt checking
            sentences = re.split(r'(?<=[.!?])\s+', response)
            for sentence in sentences:
                if sentence.strip():
                    # ✅ Check for interrupt before each sentence
                    if full_duplex_manager and full_duplex_manager.speech_interrupted:
                        print("[AdvancedResponse] ⚡ INTERRUPT IN FALLBACK - STOPPING")
                        response_interrupted = True
                        break  # ✅ CRITICAL: Break immediately!
                    
                    speak_streaming(sentence.strip())
                    
                    # ✅ Check again after queueing
                    if full_duplex_manager and full_duplex_manager.speech_interrupted:
                        print("[AdvancedResponse] ⚡ INTERRUPT AFTER FALLBACK SENTENCE - STOPPING")
                        response_interrupted = True
                        break  # ✅ CRITICAL: Break immediately!
                    
                    time.sleep(0.1)
            
            full_response = response
        
        # ✅ HANDLE COMPLETION: Only if not interrupted
        if not response_interrupted:
            if full_response.strip():
                add_to_conversation_history(current_user, text, full_response.strip())
                print(f"[AdvancedResponse] ✅ ADVANCED AI streaming complete for VOICE USER {current_user} - {chunk_count} natural segments")
            else:
                print("[AdvancedResponse] ❌ No response generated")
                speak_streaming("I'm sorry, I didn't generate a proper response.")
        else:
            print("[AdvancedResponse] ⚡ Response was INTERRUPTED - skipping completion")
            
            # ✅ CRITICAL: Emergency cleanup after interrupt
            try:
                clear_audio_queue()
                stop_audio_playback()
                print("[AdvancedResponse] 🧹 Emergency audio cleanup completed")
            except Exception as cleanup_err:
                print(f"[AdvancedResponse] ⚠️ Cleanup error: {cleanup_err}")
        
    except Exception as e:
        print(f"[AdvancedResponse] ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        # ✅ EMERGENCY CLEANUP
        try:
            clear_audio_queue()
            stop_audio_playback()
            if full_duplex_manager:
                full_duplex_manager.reset_interrupt_flag()
                full_duplex_manager.force_reset_to_waiting()
        except:
            pass
        
        speak_streaming("I apologize, I encountered an error while thinking.")

# ✅ ADD THESE NEW HELPER FUNCTIONS:

def get_voice_based_identity(audio_data=None):
    """Get identity from voice recognition, not system login"""
    try:
        if ADVANCED_AI_AVAILABLE and hasattr(voice_manager, 'handle_voice_identification'):
            # Use advanced voice recognition
            result = voice_manager.handle_voice_identification(audio_data, "")
            if result and len(result) >= 2 and result[0] and result[0] != "Unknown":
                print(f"[VoiceIdentity] 🎯 Advanced AI identified: {result[0]} (status: {result[1]})")
                return result[0]
        
        elif ENHANCED_VOICE_AVAILABLE:
            # Use enhanced voice recognition
            try:
                from voice.recognition import identify_speaker_with_confidence
                result = identify_speaker_with_confidence(audio_data)
                if result and len(result) >= 2 and result[0] and result[1] > 0.7:
                    print(f"[VoiceIdentity] ✅ Enhanced voice identified: {result[0]} (confidence: {result[1]})")
                    return result[0]
            except ImportError:
                pass
        
        # Basic voice recognition fallback
        try:
            from voice.recognition import identify_speaker
            result = identify_speaker(audio_data)
            if result and result != "Unknown":
                print(f"[VoiceIdentity] 📊 Basic voice identified: {result}")
                return result
        except (ImportError, AttributeError):
            pass
        
        # Anonymous fallback
        print(f"[VoiceIdentity] 👤 No voice match - using anonymous")
        return "Anonymous_Speaker"
        
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Error: {e}")
        return "Anonymous_Speaker"


def get_voice_based_display_name(identified_user):
    """Get display name based on voice identity, not system login"""
    try:
        # Check if this is the system user (Daveydrz)
        if identified_user == "Daveydrz" or identified_user == SYSTEM_USER:
            return "Daveydrz"
        
        # Check known voice profiles
        if identified_user in known_users:
            profile = known_users[identified_user]
            if isinstance(profile, dict) and 'display_name' in profile:
                return profile['display_name']
            elif isinstance(profile, dict) and 'real_name' in profile:
                return profile['real_name']
            else:
                return identified_user
        
        # Handle anonymous or unknown users
        if identified_user in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return "friend"  # Friendly generic term
        
        # Default to the identified name
        return identified_user
        
    except Exception as e:
        print(f"[VoiceIdentity] ⚠️ Display name error: {e}")
        return identified_user or "friend"


def get_voice_based_name_response(identified_user, display_name):
    """Handle 'what's my name' using voice matching, not system login"""
    try:
        # Handle system user
        if identified_user == "Daveydrz" or identified_user == SYSTEM_USER:
            return f"Based on your voice, you are Daveydrz."
        
        # Handle known voice profiles
        elif identified_user in known_users and identified_user not in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return f"Your name is {display_name}."
        
        # Handle anonymous or unrecognized voices
        elif identified_user in ["Anonymous_Speaker", "Unknown", "Guest"]:
            return "I don't recognize your voice yet. Could you tell me your name so I can learn it?"
        
        # Handle any other identified users
        else:
            return f"Based on your voice, I believe you are {display_name}."
            
    except Exception as e:
        print(f"[VoiceIdentity] ❌ Name response error: {e}")
        return "I'm having trouble with voice recognition right now. Could you tell me your name?"

def is_direct_time_question(text):
    """🧠 SMART: Only detect DIRECT time questions, not contextual usage"""
    text_lower = text.lower().strip()
    
    # VERY specific patterns for direct time questions only
    direct_time_patterns = [
        r'^what time is it\??$',
        r'^what\'s the time\??$',
        r'^whats the time\??$',
        r'^tell me the time\??$',
        r'^current time\??$',
        r'^time\??$',
        r'^what time\??$',
        r'^time now\??$',
        r'^what\'s the current time\??$',
        r'^whats the current time\??$',
        r'^do you know what time it is\??$',
        r'^can you tell me the time\??$',
        r'^what time is it now\??$'
    ]
    
    for pattern in direct_time_patterns:
        if re.match(pattern, text_lower):
            print(f"[DirectTimeDetection] ✅ DIRECT time question: '{text}'")
            return True
    
    print(f"[DirectTimeDetection] ➡️ NOT a direct time question: '{text}' - sending to AI")
    return False

def is_direct_location_question(text):
    """🧠 SMART: Only detect DIRECT location questions, not contextual usage"""
    text_lower = text.lower().strip()
    
    # VERY specific patterns for direct location questions only
    direct_location_patterns = [
        r'^where are you\??$',
        r'^what\'s your location\??$',
        r'^whats your location\??$',
        r'^where do you live\??$',
        r'^where are you located\??$',
        r'^your location\??$',
        r'^location\??$',
        r'^where\??$',
        r'^what\'s your address\??$',
        r'^whats your address\??$',
        r'^tell me your location\??$',
        r'^can you tell me where you are\??$',
        r'^where am i\??$'
    ]
    
    for pattern in direct_location_patterns:
        if re.match(pattern, text_lower):
            print(f"[DirectLocationDetection] ✅ DIRECT location question: '{text}'")
            return True
    
    print(f"[DirectLocationDetection] ➡️ NOT a direct location question: '{text}' - sending to AI")
    return False

def is_direct_date_question(text):
    """🧠 SMART: Only detect DIRECT date questions, not contextual usage"""
    text_lower = text.lower().strip()
    
    # VERY specific patterns for direct date questions only
    direct_date_patterns = [
        r'^what\'s the date\??$',
        r'^whats the date\??$',
        r'^what date is it\??$',
        r'^what\'s today\'s date\??$',
        r'^whats todays date\??$',
        r'^today\'s date\??$',
        r'^todays date\??$',
        r'^what day is it\??$',
        r'^what\'s today\??$',
        r'^whats today\??$',
        r'^tell me the date\??$',
        r'^current date\??$',
        r'^date\??$',
        r'^what day\??$',
        r'^today\??$'
    ]
    
    for pattern in direct_date_patterns:
        if re.match(pattern, text_lower):
            print(f"[DirectDateDetection] ✅ DIRECT date question: '{text}'")
            return True
    
    print(f"[DirectDateDetection] ➡️ NOT a direct date question: '{text}' - sending to AI")
    return False

def get_current_brisbane_time():
    """Get current Brisbane time with multiple formats"""
    try:
        # Get current UTC time and convert to Brisbane
        utc_now = time.gmtime()
        utc_timestamp = time.mktime(utc_now)
        brisbane_timestamp = utc_timestamp + (10 * 3600)  # Add 10 hours
        brisbane_time = time.localtime(brisbane_timestamp)
        
        return {
            'time_12h': time.strftime("%I:%M %p", brisbane_time),
            'time_24h': time.strftime("%H:%M", brisbane_time),
            'date': time.strftime("%A, %B %d, %Y", brisbane_time),
            'day': time.strftime("%A", brisbane_time),
            'full_datetime': time.strftime("%Y-%m-%d %H:%M:%S", brisbane_time)
        }
    except Exception as e:
        print(f"[TimeHelper] Error: {e}")
        return {
            'time_12h': "4:27 PM",
            'time_24h': "16:27",
            'date': "Wednesday, January 8, 2025",
            'day': "Wednesday",
            'full_datetime': "2025-01-08 16:27:39"
        }

# ✅ ADVANCED: Enhanced voice profile loading with clustering support
def load_voice_profiles():
    """✅ ADVANCED: Load and validate voice profiles with clustering support"""
    global known_users
    
    # ✅ CRITICAL FIX: Initialize valid_profiles at the beginning
    valid_profiles = []
    clustering_profiles = []
    
    try:
        print("[AdvancedBuddy] 📚 Loading ADVANCED voice profiles...")
        
        # Load from enhanced database
        from voice.database import known_users as db_users, anonymous_clusters as db_clusters, save_known_users
        known_users = db_users
        
        if not known_users and not db_clusters:
            print("[AdvancedBuddy] 📚 No voice profiles found - ADVANCED AI will learn voices naturally!")
            known_users = {}
            return True  # ✅ CHANGED: Return True to prevent name requests
        
        print(f"[AdvancedBuddy] 📚 Found {len(known_users)} user profiles + {len(db_clusters)} anonymous clusters")
        
        # ✅ MOVED: Validate profiles with advanced features (moved up before first usage)
        for username, data in known_users.items():
            try:
                if isinstance(data, dict):
                    # Check for any embedding data
                    if ('embeddings' in data and data['embeddings']) or ('embedding' in data and data['embedding']):
                        valid_profiles.append(username)
                        
                        # Check for advanced features
                        if data.get('clustering_enabled', False):
                            clustering_profiles.append(username)
                            print(f"[AdvancedBuddy] 🎯 ADVANCED profile: {username} (clustering enabled)")
                        else:
                            print(f"[AdvancedBuddy] ✅ Enhanced profile: {username}")
                            
                    elif data.get('status') == 'background_learning':
                        valid_profiles.append(username)
                        print(f"[AdvancedBuddy] 🌱 Background learning profile: {username}")
                    else:
                        print(f"[AdvancedBuddy] ⚠️ Profile missing embeddings: {username}")
                        
                elif isinstance(data, list) and len(data) == 256:
                    valid_profiles.append(username)
                    print(f"[AdvancedBuddy] ✅ Legacy profile: {username}")
                    
            except Exception as e:
                print(f"[AdvancedBuddy] ❌ Error validating profile {username}: {e}")
                continue
        
        # Display clustering information
        try:
            # ✅ FIX: Check if ADVANCED_AI_AVAILABLE exists before using it
            ADVANCED_AI_AVAILABLE = True  # Assume True if not defined elsewhere
            
            if ADVANCED_AI_AVAILABLE:
                print(f"[AdvancedBuddy] 🔍 Anonymous clusters: {len(db_clusters)}")
                print(f"[AdvancedBuddy] 🎯 Clustering-enabled profiles: {len(clustering_profiles)}")
                print(f"[AdvancedBuddy] 📊 Total voice entities: {len(valid_profiles) + len(db_clusters)}")
        except NameError:
            # ADVANCED_AI_AVAILABLE not defined, skip advanced features
            print(f"[AdvancedBuddy] 📊 Basic mode: {len(valid_profiles)} profiles")
        
        # ✅ FIX: Now valid_profiles is properly defined before this check
        if valid_profiles:
            print(f"[AdvancedBuddy] ✅ {len(valid_profiles)} valid voice profiles loaded")
            return True
        elif 'ADVANCED_AI_AVAILABLE' in locals() and ADVANCED_AI_AVAILABLE and db_clusters:
            print(f"[AdvancedBuddy] 🔍 No named profiles, but {len(db_clusters)} anonymous clusters available")
            return True
        else:
            print(f"[AdvancedBuddy] 🔍 No profiles yet - ADVANCED AI will learn naturally")
            return True  # ✅ CHANGED: Always return True for natural learning
            
    except Exception as e:
        print(f"[AdvancedBuddy] ❌ Error loading voice profiles: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_name_from_text(text):
    """✅ ADVANCED: Extract name with enhanced AI processing"""
    if ADVANCED_AI_AVAILABLE:
        try:
            # Use advanced name manager
            return advanced_name_manager.extract_name_ultra_smart(text, {})
        except:
            pass
    
    # Fallback to enhanced extraction
    patterns = [
        r"my name is (\w+)",
        r"i'm (\w+)",
        r"i am (\w+)", 
        r"call me (\w+)",
        r"name's (\w+)",
        r"this is (\w+)",
        r"it's (\w+)",
        r"i am called (\w+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            name = match.group(1).title()
            if len(name) >= 2 and name.isalpha():  # Valid name
                if ADVANCED_AI_AVAILABLE:
                    # Use advanced name validation
                    try:
                        if advanced_name_manager.is_valid_name_enhanced(name):
                            return name
                    except:
                        pass
                elif ENHANCED_VOICE_AVAILABLE:
                    # Use enhanced name validation
                    try:
                        from voice.manager_names import name_manager
                        if name_manager.is_valid_name_enhanced(name):
                            return name
                    except:
                        pass
                
                # Fallback validation
                if hasattr(voice_manager, 'is_valid_name') and voice_manager.is_valid_name(name):
                    return name
    return None

def generate_guest_username():
    """Generate a guest username with advanced features"""
    import time
    timestamp = time.strftime("%H%M")
    
    if ADVANCED_AI_AVAILABLE:
        # Use advanced anonymous clustering if available
        from voice.database import anonymous_clusters
        if anonymous_clusters:
            cluster_count = len(anonymous_clusters)
            return f"Anonymous_{cluster_count+1:03d}"
    
    return f"Guest_{timestamp}"

def handle_full_duplex_conversation():
    """✅ ADVANCED: Full duplex conversation with ADVANCED AI ASSISTANT features"""
    global current_user
    
    # ✅ ADVANCED: Enhanced state management
    pending_question = None
    voice_recognition_in_progress = False
    llm_locked = False
    
    if not full_duplex_manager:
        print("[FullDuplex] ❌ No full duplex manager available")
        return
    
    print("[FullDuplex] 🚀 Starting ADVANCED AI ASSISTANT with TRUE STREAMING LLM conversation mode")
    print(f"[FullDuplex] 📅 Current UTC Time: 2025-07-13 10:53:08")
    print(f"[FullDuplex] 👤 System User: Daveydrz")
    
    # Advanced AI assistant status
    if ADVANCED_AI_AVAILABLE:
        print("[FullDuplex] 🎯 ADVANCED AI Features Active:")
        print("[FullDuplex]   🔍 Anonymous voice clustering (passive collection)")
        print("[FullDuplex]   🎤 Passive audio buffering (always learning)")
        print("[FullDuplex]   🛡️ LLM guard system (intelligent blocking)")
        print("[FullDuplex]   👥 Same-name collision handling (auto David_001, David_002)")
        print("[FullDuplex]   🎭 Spontaneous introduction detection (natural 'I'm David')")
        print("[FullDuplex]   🧠 Behavioral pattern learning (adapts to user habits)")
        print("[FullDuplex]   📊 Advanced analytics (comprehensive monitoring)")
        print("[FullDuplex]   🔧 Auto maintenance (self-optimizing system)")
        print("[FullDuplex]   🎯 Context-aware decisions (multi-factor intelligence)")
        print("[FullDuplex]   🌱 Continuous learning (Alexa/Siri-level adaptation)")
    elif ENHANCED_VOICE_AVAILABLE:
        print("[FullDuplex] ✅ Enhanced Features Active:")
        print("[FullDuplex]   📊 Multi-embedding profiles (up to 15 per user)")
        print("[FullDuplex]   🧠 Dual recognition models (Resemblyzer + SpeechBrain)")
        print("[FullDuplex]   🌱 Passive voice learning during conversations")
        print("[FullDuplex]   🔍 Advanced quality analysis with auto-discard")
        print("[FullDuplex]   💾 Raw audio storage for re-training")
        print("[FullDuplex]   🎓 Enhanced training (15-20 phrases)")
    else:
        print("[FullDuplex] ⚠️ Using legacy voice system with REAL voice recognition")
    
    set_conversation_state(True)
    
    # Start full duplex manager
    full_duplex_manager.start()
    
    print(f"[FullDuplex] ✅ Ready! Location: {USER_PRECISE_LOCATION}, Time: {brisbane_time_12h}")
    print(f"[FullDuplex] 🎵 TRUE Streaming LLM: ENABLED")
    print(f"[FullDuplex] 🚀 ADVANCED AI ASSISTANT: {'ACTIVE' if ADVANCED_AI_AVAILABLE else 'ENHANCED' if ENHANCED_VOICE_AVAILABLE else 'BASIC'}")
    
    # Main advanced full duplex loop
    last_stats_time = time.time()
    
    while get_conversation_state():
        try:
            # Check for new speech
            speech_result = full_duplex_manager.get_next_speech(timeout=0.1)
            
            if speech_result:
                text, audio_data = speech_result
                print(f"[FullDuplex] 👤 User said: '{text}'")
                
                # ✅ STEP 1: Process user identification from text FIRST
                try:
                    from ai.speech import identify_user, get_display_name
                    
                    # Check if user is introducing themselves (always process this)
                    identify_user(text, current_user)
                    
                    # Get current display name
                    display_name = get_display_name(current_user)
                    print(f"[FullDuplex] 👤 Text User: {current_user} (display: {display_name})")
                    
                except Exception as id_error:
                    print(f"[FullDuplex] ⚠️ User identification error: {id_error}")
                
                # ✅ STEP 2: VOICE RECOGNITION PROCESSING (CRITICAL!)
                if ADVANCED_AI_AVAILABLE:
                    # Use advanced voice manager
                    try:
                        identified_user, status = voice_manager.handle_voice_identification(audio_data, text)
                        
                        print(f"[AdvancedAI] 🔍 Status: '{status}', User: '{identified_user}'")
                        print(f"[AdvancedAI] 🛡️ LLM locked: {voice_manager.is_llm_locked() if hasattr(voice_manager, 'is_llm_locked') else False}")
                        
                        # ✅ CRITICAL DATABASE SYNC FIX (NON-DESTRUCTIVE)
                        try:
                            print("[AdvancedAI] 🔄 Syncing voice manager to database...")
                            from voice.database import known_users, anonymous_clusters, save_known_users
                            from datetime import datetime
                            
                            # Get voice manager stats to check internal state
                            if hasattr(voice_manager, 'get_session_stats'):
                                stats = voice_manager.get_session_stats()
                                print(f"[AdvancedAI] 📊 Internal stats: {stats}")
                                
                                # Check if voice manager has anonymous clusters
                                if stats.get('anonymous_clusters', 0) > 0:
                                    # 🔥 CRITICAL: Only sync if the cluster DOESN'T EXIST or has NO EMBEDDINGS
                                    if identified_user and identified_user.startswith('Anonymous_'):
                                        
                                        # Check if cluster already exists with embeddings
                                        existing_cluster = anonymous_clusters.get(identified_user)
                                        existing_embeddings = existing_cluster.get('embeddings', []) if existing_cluster else []
                                        
                                        if not existing_cluster:
                                            # ✅ NEW CLUSTER: Only create if it doesn't exist
                                            print(f"[AdvancedAI] 🆕 Creating new database entry for {identified_user}")
                                            
                                            anonymous_clusters[identified_user] = {
                                                'cluster_id': identified_user,
                                                'embeddings': [],  # Start empty, embeddings will be added by voice manager
                                                'created_at': datetime.utcnow().isoformat(),
                                                'last_updated': datetime.utcnow().isoformat(),
                                                'status': 'anonymous',
                                                'sample_count': 1,
                                                'quality_scores': [0.8],
                                                'audio_contexts': ['voice_manager_sync'],
                                                'confidence_threshold': 0.6
                                            }
                                            
                                            known_users[identified_user] = {
                                                'username': identified_user,
                                                'status': 'anonymous',
                                                'voice_embeddings': [],  # Start empty, embeddings will be added by voice manager
                                                'created_at': datetime.utcnow().isoformat(),
                                                'last_updated': datetime.utcnow().isoformat(),
                                                'is_anonymous': True,
                                                'cluster_id': identified_user,
                                                'training_type': 'advanced_ai_sync',
                                                'confidence_threshold': 0.6,
                                                'recognition_count': 1,
                                                'recognition_successes': 1,
                                                'recognition_failures': 0,
                                                'embedding_count': 0  # Will be updated when embeddings are added
                                            }
                                            
                                        elif len(existing_embeddings) == 0:
                                            # ✅ EMPTY CLUSTER: Update metadata only, don't touch embeddings
                                            print(f"[AdvancedAI] 🔄 Updating metadata for existing empty cluster {identified_user}")
                                            
                                            if existing_cluster:
                                                existing_cluster['last_updated'] = datetime.utcnow().isoformat()
                                                existing_cluster['recognition_count'] = existing_cluster.get('recognition_count', 0) + 1
                                            
                                            if identified_user in known_users:
                                                known_users[identified_user]['last_updated'] = datetime.utcnow().isoformat()
                                                known_users[identified_user]['recognition_count'] = known_users[identified_user].get('recognition_count', 0) + 1
                                                
                                        else:
                                            # ✅ CLUSTER WITH EMBEDDINGS: DON'T TOUCH IT!
                                            print(f"[AdvancedAI] 🛡️ PRESERVING existing cluster {identified_user} with {len(existing_embeddings)} embeddings")
                                            # Just update timestamp
                                            existing_cluster['last_updated'] = datetime.utcnow().isoformat()
                                            if identified_user in known_users:
                                                known_users[identified_user]['last_updated'] = datetime.utcnow().isoformat()
                                        
                                        # Save only if we made changes and no embeddings exist
                                        if not existing_cluster or len(existing_embeddings) == 0:
                                            if save_known_users():
                                                print(f"[AdvancedAI] ✅ Successfully synced {identified_user} to database")
                                            else:
                                                print(f"[AdvancedAI] ❌ Failed to sync {identified_user} to database")
                            
                        except Exception as sync_error:
                            print(f"[AdvancedAI] ⚠️ Database sync error: {sync_error}")
                        
                        # Handle LLM locking/unlocking
                        if hasattr(voice_manager, 'is_llm_locked'):
                            if voice_manager.is_llm_locked():
                                if not llm_locked:
                                    pending_question = text
                                    llm_locked = True
                                    print(f"[AdvancedAI] 🛡️ LLM LOCKED - Question queued: '{text}'")
                                continue
                            else:
                                if llm_locked:
                                    llm_locked = False
                                    print(f"[AdvancedAI] 🔓 LLM UNLOCKED")
                                    
                                    # Update current user
                                    if identified_user and identified_user != current_user:
                                        current_user = identified_user
                                        print(f"[AdvancedAI] 🔄 User updated to: {current_user}")
                                    
                                    # Process pending question
                                    if pending_question:
                                        print(f"[AdvancedAI] ✅ Processing queued question: '{pending_question}'")
                                        handle_streaming_response(pending_question, current_user)
                                        pending_question = None
                                        continue
                        
                        # Update current user
                        if identified_user and identified_user != current_user:
                            current_user = identified_user
                            print(f"[AdvancedAI] 🔄 User switched to: {current_user}")
                        
                    except Exception as e:
                        print(f"[AdvancedAI] ❌ Advanced voice processing error: {e}")
                        import traceback
                        traceback.print_exc()
                        # Fallback to basic processing
                        voice_recognition_in_progress = False
                
                elif ENHANCED_VOICE_AVAILABLE:
                    # Enhanced voice processing
                    try:
                        identified_user, status = voice_manager.handle_voice_identification(audio_data, text)
                        
                        print(f"[Enhanced] 🔍 Status: '{status}', User: '{identified_user}'")
                        
                        # Handle voice processing states
                        if status in ["NEEDS_NAME", "WAITING_FOR_NAME", "CONFIRMING_NAME", "NEEDS_TRAINING", "UNRECOGNIZED"]:
                            if not voice_recognition_in_progress:
                                pending_question = text
                                voice_recognition_in_progress = True
                                print(f"[Enhanced] 📝 Stored pending question: '{text}'")
                            continue
                        
                        if status in ["RECOGNIZED", "LIKELY", "CONFIRMED", "GUEST_CREATED", "NAME_CONFIRMED"]:
                            if identified_user and identified_user != current_user:
                                current_user = identified_user
                                print(f"[Enhanced] 🔄 Switched to: {current_user}")
                            
                            voice_recognition_in_progress = False
                            
                            # Add passive sample if available
                            if ENHANCED_VOICE_AVAILABLE and current_user != "Guest":
                                try:
                                    enhanced_speaker_profiles.add_passive_sample(current_user, audio_data, 0.9)
                                    enhanced_speaker_profiles.tune_threshold_for_user(current_user)
                                except:
                                    pass
                            
                            # Process pending question
                            if pending_question:
                                print(f"[Enhanced] ✅ Processing pending: '{pending_question}'")
                                time.sleep(1)
                                handle_streaming_response(pending_question, current_user)
                                pending_question = None
                            continue
                        
                    except Exception as e:
                        print(f"[Enhanced] ❌ Enhanced voice processing error: {e}")
                        import traceback
                        traceback.print_exc()
                        voice_recognition_in_progress = False
                
                else:
                    # ✅ BASIC VOICE RECOGNITION - ACTUALLY PROCESS VOICE! (FIXED!)
                    print(f"[FullDuplex] 🔄 Using basic voice system with ACTUAL voice recognition")
                    
                    try:
                        # ✅ CRITICAL: Process voice recognition to create Anonymous_001
                        from voice.recognition import identify_speaker_with_confidence
                        identified_user, confidence = identify_speaker_with_confidence(audio_data)
                        
                        print(f"[BasicVoice] 🔍 Voice recognition result: '{identified_user}' (confidence: {confidence:.3f})")
                        
                        # Handle voice recognition results
                        if identified_user != "UNKNOWN" and identified_user != "Unknown":
                            # Known user or anonymous cluster was created/matched
                            if confidence > 0.7 or identified_user.startswith("Anonymous_"):
                                if identified_user != current_user:
                                    current_user = identified_user
                                    print(f"[BasicVoice] 🔄 User switched to: {current_user}")
                                    
                                    # ✅ Update voice identity context
                                    try:
                                        update_voice_identity_context(current_user)
                                    except:
                                        pass
                                        
                        else:
                            # Unknown user - check if anonymous cluster was created
                            print(f"[BasicVoice] 👤 Unknown user result - checking for new anonymous clusters")
                            
                            from voice.database import anonymous_clusters, known_users
                            print(f"[BasicVoice] 📊 Current anonymous clusters: {list(anonymous_clusters.keys())}")
                            print(f"[BasicVoice] 📊 Current known users: {list(known_users.keys())}")
                            
                            # Check if a new anonymous cluster was created
                            if anonymous_clusters:
                                # Get the latest anonymous cluster
                                anonymous_ids = [k for k in anonymous_clusters.keys() if k.startswith("Anonymous_")]
                                if anonymous_ids:
                                    latest_cluster = max(anonymous_ids)
                                    current_user = latest_cluster
                                    print(f"[BasicVoice] 🆕 Using anonymous cluster: {current_user}")
                                    
                                    # ✅ Update voice identity context
                                    try:
                                        update_voice_identity_context(current_user)
                                    except:
                                        pass
                        
                        # ✅ VERIFY: Check if user was saved to database
                        from voice.database import known_users, anonymous_clusters
                        total_entities = len(known_users) + len(anonymous_clusters)
                        print(f"[BasicVoice] 📊 Total voice entities after processing: {total_entities}")
                        print(f"[BasicVoice] 📊 Current user: {current_user}")
                        
                    except Exception as basic_voice_error:
                        print(f"[BasicVoice] ❌ Basic voice recognition error: {basic_voice_error}")
                        import traceback
                        traceback.print_exc()
                        
                        # ✅ EMERGENCY: Force create anonymous cluster
                        try:
                            print(f"[BasicVoice] 🚨 Emergency: Forcing anonymous cluster creation...")
                            from voice.database import create_anonymous_cluster
                            from voice.voice_models import dual_voice_model_manager
                            
                            embedding = dual_voice_model_manager.generate_dual_embedding(audio_data)
                            if embedding:
                                cluster_id = create_anonymous_cluster(embedding)
                                if cluster_id:
                                    current_user = cluster_id
                                    print(f"[BasicVoice] ✅ Emergency cluster created: {current_user}")
                                    
                                    # Update voice identity context
                                    try:
                                        update_voice_identity_context(current_user)
                                    except:
                                        pass
                                else:
                                    print(f"[BasicVoice] ❌ Emergency cluster creation failed")
                            else:
                                print(f"[BasicVoice] ❌ Emergency embedding generation failed")
                                
                        except Exception as emergency_error:
                            print(f"[BasicVoice] ❌ Emergency creation failed: {emergency_error}")
                            # Last resort - just continue with existing user
                            print(f"[BasicVoice] 🆘 Continuing with existing user: {current_user}")
                
                # ✅ CRITICAL: Manual sync check for Advanced AI (NON-DESTRUCTIVE)
                if ADVANCED_AI_AVAILABLE:
                    try:
                        # Check if voice manager internal state differs from database
                        stats = voice_manager.get_session_stats() if hasattr(voice_manager, 'get_session_stats') else {}
                        internal_clusters = stats.get('anonymous_clusters', 0)
                        
                        from voice.database import anonymous_clusters, known_users
                        db_clusters = len(anonymous_clusters)
                        db_users = len(known_users)
                        
                        if internal_clusters > 0 and db_clusters == 0 and db_users == 0:
                            print(f"[FullDuplex] 🚨 CRITICAL: Voice manager has {internal_clusters} clusters but database is empty!")
                            print(f"[FullDuplex] 🔧 Performing emergency database sync...")
                            
                            # ✅ EMERGENCY SYNC: Create placeholder only, don't overwrite existing data
                            from datetime import datetime
                            cluster_id = "Anonymous_001"
                            
                            # Only create if it doesn't exist
                            if cluster_id not in anonymous_clusters:
                                anonymous_clusters[cluster_id] = {
                                    'cluster_id': cluster_id,
                                    'embeddings': [],  # Start empty, voice manager will populate
                                    'created_at': datetime.utcnow().isoformat(),
                                    'last_updated': datetime.utcnow().isoformat(),
                                    'status': 'anonymous',
                                    'sample_count': 0,  # Will be updated when embeddings are added
                                    'quality_scores': [],
                                    'audio_contexts': ['emergency_sync_placeholder'],
                                    'confidence_threshold': 0.6
                                }
                            
                            # Only create if it doesn't exist
                            if cluster_id not in known_users:
                                known_users[cluster_id] = {
                                    'username': cluster_id,
                                    'status': 'anonymous',
                                    'voice_embeddings': [],  # Start empty, voice manager will populate
                                    'created_at': datetime.utcnow().isoformat(),
                                    'last_updated': datetime.utcnow().isoformat(),
                                    'is_anonymous': True,
                                    'cluster_id': cluster_id,
                                    'training_type': 'emergency_sync_placeholder',
                                    'confidence_threshold': 0.6,
                                    'recognition_count': 0,
                                    'embedding_count': 0  # Will be updated when embeddings are added
                                }
                            
                            # Save placeholders
                            from voice.database import save_known_users
                            if save_known_users():
                                print(f"[FullDuplex] ✅ Emergency sync placeholder created!")
                                current_user = cluster_id
                            else:
                                print(f"[FullDuplex] ❌ Emergency sync failed!")
                                
                    except Exception as emergency_sync_error:
                        print(f"[FullDuplex] ❌ Emergency sync error: {emergency_sync_error}")
                
                # ✅ Handle training commands
                if "train" in text.lower() and ("voice" in text.lower() or "my" in text.lower()):
                    print(f"[FullDuplex] 🎓 Training command detected: '{text}'")
                    
                    # Clear any pending states
                    voice_recognition_in_progress = False
                    llm_locked = False
                    pending_question = None
                    
                    if ADVANCED_AI_AVAILABLE:
                        print("[FullDuplex] 🎓 ADVANCED AI voice training requested")
                        full_duplex_manager.stop()
                        
                        speak_streaming("Starting advanced AI voice training with clustering optimization and quality validation.")
                        time.sleep(2)
                        
                        success = voice_training_mode()
                        if success:
                            load_voice_profiles()
                            current_user = "Daveydrz"
                            speak_streaming("Advanced AI voice training complete! I now have multiple voice embeddings with clustering support for superior recognition.")
                        else:
                            speak_streaming("Training failed.")
                        
                        time.sleep(2)
                        full_duplex_manager.start()
                        continue
                    elif ENHANCED_VOICE_AVAILABLE:
                        print("[FullDuplex] 🎓 Enhanced voice training requested")
                        full_duplex_manager.stop()
                        
                        speak_streaming("Starting enhanced voice training with quality validation and multiple embeddings.")
                        time.sleep(2)
                        
                        success = voice_training_mode()
                        if success:
                            load_voice_profiles()
                            current_user = "Daveydrz"
                            speak_streaming("Enhanced voice training complete! I now have multiple voice embeddings for better recognition.")
                        else:
                            speak_streaming("Training failed.")
                        
                        time.sleep(2)
                        full_duplex_manager.start()
                        continue
                    else:
                        print("[FullDuplex] 🎓 Legacy voice training requested")
                        full_duplex_manager.stop()
                        
                        speak_streaming("Starting voice training.")
                        time.sleep(2)
                        
                        success = voice_training_mode()
                        if success:
                            load_voice_profiles()
                            current_user = "Daveydrz"
                            speak_streaming("Voice training complete!")
                        else:
                            speak_streaming("Training failed.")
                        
                        time.sleep(2)
                        full_duplex_manager.start()
                        continue
                
                # Check for conversation end
                if should_end_conversation(text):
                    try:
                        from ai.speech import get_display_name
                        display_name = get_display_name(current_user)
                        speak_streaming(f"Goodbye {display_name}! See you later from Birtinya!")
                    except:
                        speak_streaming("Goodbye from Birtinya!")
                    set_conversation_state(False)
                    break
                
                # ✅ FINAL CHECK: Block LLM if any voice states are active
                if voice_recognition_in_progress or llm_locked:
                    print(f"[FullDuplex] 🛡️ Voice processing active - LLM blocked for: '{text}'")
                    continue
                
                # ✅ ADVANCED AI: Handle response with full features
                try:
                    if len(text.split()) >= 3:
                        play_chime()
                    
                    print(f"[FullDuplex] 🎵 ✅ ADVANCED AI STREAMING response for: '{text}' (User: {current_user})")
                    handle_streaming_response(text, current_user)
                    
                except Exception as e:
                    print(f"[FullDuplex] ADVANCED AI streaming response error: {e}")
                    speak_streaming("Sorry, I had a problem generating a response.")
            
            # Print advanced stats periodically
            if DEBUG and time.time() - last_stats_time > 10:
                stats = full_duplex_manager.get_stats()
                try:
                    audio_stats = get_audio_stats()
                    print(f"[FullDuplex] 📊 Full Duplex Stats: {stats}")
                    print(f"[FullDuplex] 🎵 Audio Stats: {audio_stats}")
                except:
                    print(f"[FullDuplex] 📊 Full Duplex Stats: {stats}")
                
                # Advanced AI specific stats
                if ADVANCED_AI_AVAILABLE:
                    try:
                        session_stats = voice_manager.get_session_stats()
                        print(f"[FullDuplex] 🚀 ADVANCED AI Stats: {session_stats}")
                        
                        # Display anonymous clusters
                        from voice.database import anonymous_clusters
                        if anonymous_clusters:
                            print(f"[FullDuplex] 🔍 Anonymous clusters in database: {len(anonymous_clusters)}")
                        
                        # Compare internal vs database state
                        internal_clusters = session_stats.get('anonymous_clusters', 0)
                        db_clusters = len(anonymous_clusters)
                        if internal_clusters != db_clusters:
                            print(f"[FullDuplex] ⚠️ SYNC ISSUE: Internal={internal_clusters}, Database={db_clusters}")
                            
                    except:
                        pass
                
                # ✅ Show current user identity status
                try:
                    from ai.speech import get_display_name
                    display_name = get_display_name(current_user)
                    if display_name != current_user:
                        print(f"[FullDuplex] 👤 Current user: {current_user} (known as: {display_name})")
                    else:
                        print(f"[FullDuplex] 👤 Current user: {current_user}")
                except:
                    print(f"[FullDuplex] 👤 Current user: {current_user}")
                
                # ✅ Show database status with details
                try:
                    from voice.database import known_users, anonymous_clusters
                    print(f"[FullDuplex] 💾 Database: {len(known_users)} known users, {len(anonymous_clusters)} anonymous clusters")
                    if known_users:
                        print(f"[FullDuplex] 💾 Known users: {list(known_users.keys())}")
                    if anonymous_clusters:
                        print(f"[FullDuplex] 💾 Anonymous clusters: {list(anonymous_clusters.keys())}")
                except:
                    pass
                
                last_stats_time = time.time()
            
            time.sleep(0.05)
            
        except KeyboardInterrupt:
            print("\n[FullDuplex] 👋 Conversation interrupted by user")
            set_conversation_state(False)
            break
        except Exception as e:
            print(f"[FullDuplex] ADVANCED AI conversation error: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(0.1)
    
    # Cleanup
    if full_duplex_manager:
        full_duplex_manager.stop()
    print("[FullDuplex] 🛑 ADVANCED AI full duplex conversation ended")

def continuous_mic_worker(stream, frame_length, sample_rate):
    """Continuously feed microphone to full duplex manager with advanced features"""
    
    if not full_duplex_manager:
        print("[MicWorker] ❌ No full duplex manager available")
        return
    
    print(f"[MicWorker] 🎤 Starting ADVANCED AI continuous microphone feeding")
    print(f"[MicWorker] 📊 Frame length: {frame_length}, Sample rate: {sample_rate}")
    
    # Wait for both flags to be properly set
    wait_count = 0
    while wait_count < 50:
        mic_state = get_mic_feeding_state()
        conv_state = get_conversation_state()
        print(f"[MicWorker] 🔄 Waiting for flags - mic_feeding: {mic_state}, conversation: {conv_state}")
        
        if mic_state and conv_state:
            break
            
        time.sleep(0.1)
        wait_count += 1
    
    if wait_count >= 50:
        print("[MicWorker] ❌ Timeout waiting for flags to be set")
        return
    
    print("[MicWorker] ✅ Flags confirmed, starting ADVANCED AI audio processing")
    
    feed_count = 0
    error_count = 0
    
    try:
        while get_mic_feeding_state():
            if not stream:
                print("[MicWorker] ❌ Stream is None")
                break
                
            try:
                pcm = stream.read(frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)
                
                if len(pcm) == 0:
                    print("[MicWorker] ⚠️ Empty audio data")
                    time.sleep(0.01)
                    continue
                
                # Downsample to 16kHz if needed
                if sample_rate != SAMPLE_RATE:
                    pcm_16k = downsample_audio(pcm, sample_rate, SAMPLE_RATE)
                else:
                    pcm_16k = pcm
                
                volume = np.abs(pcm_16k).mean()
                
                # Feed to full duplex manager with advanced features
                if full_duplex_manager.listening:
                    full_duplex_manager.add_audio_input(pcm_16k)
                    feed_count += 1
                    
                    # ✅ ADVANCED: Passive audio collection
                    if ADVANCED_AI_AVAILABLE and feed_count % 10 == 0:
                        # Collect audio for passive learning every 10 frames
                        try:
                            voice_manager._add_to_passive_buffer(pcm_16k, "", "mic_feed")
                        except:
                            pass
                    
                    if feed_count % 100 == 0:
                        print(f"[MicWorker] 📈 Fed {feed_count} chunks, avg volume: {volume:.1f}")
                
                time.sleep(0.001)
                
            except Exception as read_error:
                error_count += 1
                if DEBUG:
                    print(f"[MicWorker] Read error #{error_count}: {read_error}")
                
                if error_count > 10:
                    print("[MicWorker] ❌ Too many errors, stopping")
                    break
                    
                time.sleep(0.01)
                
    except Exception as e:
        print(f"[MicWorker] Worker error: {e}")
    finally:
        print(f"[MicWorker] 🛑 ADVANCED AI microphone feeding stopped (fed {feed_count} chunks, {error_count} errors)")

def main():
    """✅ ADVANCED AI Main function with ALEXA/SIRI-LEVEL INTELLIGENCE"""
    global current_user

    # --- START: NEW DIAGNOSTIC CODE ---
    print("\n[Startup Check] 🚀 Running critical startup checks...")
    try:
        # 1. Check current working directory
        cwd = os.getcwd()
        print(f"[Startup Check] 📂 Current Working Directory: {cwd}")

        # 2. Attempt to write a test file to this directory
        test_file_path = os.path.join(cwd, "write_permission_test.txt")
        print(f"[Startup Check] ✍️ Attempting to write test file to: {test_file_path}")
        
        with open(test_file_path, "w") as f:
            f.write(f"Permission test successful at {datetime.now().isoformat()}\n")
            f.write(f"Main application can write to this directory.")
        
        print(f"[Startup Check] ✅ Test file written successfully.")
        
        # 3. Clean up the test file
        os.remove(test_file_path)
        print(f"[Startup Check] ✅ Test file cleaned up.")
        
    except Exception as e:
        print("\n" + "="*60)
        print("[Startup Check] ❌ CRITICAL ERROR: FAILED TO WRITE TO DIRECTORY!")
        print(f"[Startup Check] ❌ This is a file permissions issue, not a code problem.")
        print(f"[Startup Check] ❌ Error details: {type(e).__name__} - {e}")
        print(f"[Startup Check] 👉 Please check the permissions for the directory: {os.getcwd()}")
        print("="*60 + "\n")
        # Exit if we can't write, as nothing else will work.
        return
    # --- END: NEW DIAGNOSTIC CODE ---

    print(f"[AdvancedBuddy] 🚀 Starting ADVANCED AI ASSISTANT with ALEXA/SIRI-LEVEL INTELLIGENCE")
    # ... (the rest of your main function)
    
    print(f"[AdvancedBuddy] 🚀 Starting ADVANCED AI ASSISTANT with ALEXA/SIRI-LEVEL INTELLIGENCE")
    print(f"[AdvancedBuddy] 👤 System user: {SYSTEM_USER}")
    print(f"[AdvancedBuddy] 🔄 Full Duplex Mode: {'ENABLED' if FULL_DUPLEX_MODE else 'DISABLED'}")
    print(f"[AdvancedBuddy] 🎵 Streaming TTS: {'ENABLED' if STREAMING_TTS_ENABLED else 'DISABLED'}")
    print(f"[AdvancedBuddy] 🧠 TRUE LLM Streaming: {'ENABLED' if STREAMING_LLM_ENABLED else 'DISABLED'}")
    
    # ✅ ADVANCED AI ASSISTANT status display
    if ADVANCED_AI_AVAILABLE:
        print(f"[AdvancedBuddy] 🚀 ADVANCED AI ASSISTANT: FULLY ACTIVE")
        print(f"[AdvancedBuddy] 🎯 Alexa/Siri-level Intelligence: ENABLED")
        print(f"[AdvancedBuddy] 🔍 Anonymous Voice Clustering: ACTIVE (passive collection)")
        print(f"[AdvancedBuddy] 🎤 Passive Audio Buffering: ALWAYS ON (like Alexa)")
        print(f"[AdvancedBuddy] 🛡️ LLM Guard System: PROTECTING (intelligent blocking)")
        print(f"[AdvancedBuddy] 👥 Same-Name Collision Handling: AUTO (David_001, David_002)")
        print(f"[AdvancedBuddy] 🎭 Spontaneous Introduction Detection: NATURAL ('I'm David')")
        print(f"[AdvancedBuddy] 🧠 Behavioral Pattern Learning: ADAPTIVE (learns habits)")
        print(f"[AdvancedBuddy] 📊 Advanced Analytics: MONITORING (voice patterns)")
        print(f"[AdvancedBuddy] 🔧 Auto Maintenance: SELF-OPTIMIZING (like commercial systems)")
        print(f"[AdvancedBuddy] 🎯 Context-Aware Decisions: MULTI-FACTOR (intelligent)")
        print(f"[AdvancedBuddy] 🌱 Continuous Learning: ALEXA/SIRI-LEVEL (adapts over time)")
        
        # Initialize advanced directories
        try:
            os.makedirs(VOICE_PROFILES_DIR, exist_ok=True)
            os.makedirs(RAW_AUDIO_DIR, exist_ok=True)
            os.makedirs(UNCERTAIN_SAMPLES_DIR, exist_ok=True)
            os.makedirs(ANONYMOUS_CLUSTERS_DIR, exist_ok=True)
            print(f"[AdvancedBuddy] 📁 ADVANCED AI directories initialized")
        except:
            os.makedirs("voice_profiles", exist_ok=True)
            os.makedirs("voice_profiles/raw_audio", exist_ok=True)
            os.makedirs("voice_profiles/uncertain", exist_ok=True)
            os.makedirs("voice_profiles/clusters", exist_ok=True)
            print(f"[AdvancedBuddy] 📁 Default ADVANCED directories created")
            
        # Run initial maintenance
        try:
            print("[AdvancedBuddy] 🔧 Running initial ADVANCED AI maintenance...")
            maintenance_results = run_maintenance()
            print(f"[AdvancedBuddy] ✅ Maintenance complete: {maintenance_results}")
        except Exception as e:
            print(f"[AdvancedBuddy] ⚠️ Maintenance error: {e}")
            
    elif ENHANCED_VOICE_AVAILABLE:
        print(f"[AdvancedBuddy] ✅ Enhanced Voice System: ACTIVE")
        print(f"[AdvancedBuddy] 📊 Multi-Embedding Profiles: Up to 15 per user")
        print(f"[AdvancedBuddy] 🧠 SpeechBrain ECAPA-TDNN: Integrated with Resemblyzer")
        print(f"[AdvancedBuddy] 🌱 Passive Learning: Automatic voice adaptation")
        print(f"[AdvancedBuddy] 🔍 Quality Analysis: SNR + spectral analysis")
        print(f"[AdvancedBuddy] 💾 Raw Audio Storage: For re-training")
        print(f"[AdvancedBuddy] 🎓 Enhanced Training: 15-20 phrases with validation")
        print(f"[AdvancedBuddy] 🎯 Dynamic Thresholds: Per-user adaptive")
        
        # Initialize enhanced voice directories
        try:
            os.makedirs("voice_profiles", exist_ok=True)
            os.makedirs("voice_profiles/raw_audio", exist_ok=True)
            os.makedirs("voice_profiles/uncertain", exist_ok=True)
            print(f"[AdvancedBuddy] 📁 Enhanced voice directories initialized")
        except Exception as e:
            print(f"[AdvancedBuddy] ⚠️ Directory creation error: {e}")
    else:
        print(f"[AdvancedBuddy] ⚠️ Using Legacy Voice System")
    
    print(f"[AdvancedBuddy] 🧠 Context Awareness: SMART (only direct time/date/location questions)")
    print(f"[AdvancedBuddy] 📍 Precise Location: {USER_PRECISE_LOCATION}")
    print(f"[AdvancedBuddy] 📮 Postcode: {USER_POSTCODE_PRECISE}")
    print(f"[AdvancedBuddy] 🌏 Coordinates: {USER_COORDINATES_PRECISE}")
    print(f"[AdvancedBuddy] 🏛️ Landmarks: {USER_LANDMARKS}")
    print(f"[AdvancedBuddy] 🌊 Sunshine Coast: {IS_SUNSHINE_COAST}")
    print(f"[AdvancedBuddy] 📏 Distance to Brisbane: {DISTANCE_TO_BRISBANE}km")
    print(f"[AdvancedBuddy] 🎯 Confidence: {LOCATION_CONFIDENCE_PRECISE}")
    print(f"[AdvancedBuddy] 🕐 Current Time: {brisbane_time_12h} Brisbane")
    print(f"[AdvancedBuddy] 📅 Current Date: {brisbane_date}")
    
    # ✅ Test Kokoro-FastAPI connection
    print("[AdvancedBuddy] 🎵 Testing Kokoro-FastAPI connection...")
    if test_kokoro_api():
        print(f"[AdvancedBuddy] ✅ Kokoro-FastAPI connected at {KOKORO_API_BASE_URL}")
        print(f"[AdvancedBuddy] 🎵 Default voice: {KOKORO_DEFAULT_VOICE} (Australian)")
        print(f"[AdvancedBuddy] ⚡ Streaming chunks: {STREAMING_CHUNK_WORDS} words")
        print(f"[AdvancedBuddy] ⏱️ Chunk delay: {STREAMING_RESPONSE_DELAY}s")
        print(f"[AdvancedBuddy] 🧠 LLM chunks: {STREAMING_LLM_CHUNK_WORDS} words")
    else:
        print(f"[AdvancedBuddy] ❌ Kokoro-FastAPI not available - check server on {KOKORO_API_BASE_URL}")
        print("[AdvancedBuddy] 💡 Make sure to start Kokoro-FastAPI server first!")
    
    # Load voice profiles with ADVANCED features
    print("[AdvancedBuddy] 📚 Loading ADVANCED AI voice database...")
    has_valid_profiles = load_voice_profiles()
    
    if has_valid_profiles:
        if SYSTEM_USER in known_users:
            current_user = SYSTEM_USER
            print(f"[AdvancedBuddy] 👤 Using profile: {SYSTEM_USER}")
            
            # ✅ Show ADVANCED profile info
            if ADVANCED_AI_AVAILABLE and isinstance(known_users[SYSTEM_USER], dict):
                profile = known_users[SYSTEM_USER]
                if 'embeddings' in profile:
                    print(f"[AdvancedBuddy] 🎯 ADVANCED profile: {len(profile['embeddings'])} embeddings")
                    if 'clustering_enabled' in profile:
                        print(f"[AdvancedBuddy] 🔍 Clustering enabled: {profile['clustering_enabled']}")
                    if 'behavioral_patterns' in profile:
                        print(f"[AdvancedBuddy] 🧠 Behavioral patterns: Available")
                    if 'quality_scores' in profile and len(profile['quality_scores']) > 0:
                        avg_quality = sum(profile['quality_scores']) / len(profile['quality_scores'])
                        print(f"[AdvancedBuddy] 🔍 Average quality: {avg_quality:.2f}")
                    else:
                        print(f"[AdvancedBuddy] ⚠️ No quality scores available (new profile)")
                if 'voice_model_info' in profile:
                    models = profile['voice_model_info'].get('available_models', [])
                    print(f"[AdvancedBuddy] 🧠 Voice models: {models}")
                    
            elif ENHANCED_VOICE_AVAILABLE and isinstance(known_users[SYSTEM_USER], dict):
                profile = known_users[SYSTEM_USER]
                if 'embeddings' in profile:
                    print(f"[AdvancedBuddy] 🎯 Enhanced profile: {len(profile['embeddings'])} embeddings")
                    if 'quality_scores' in profile and len(profile['quality_scores']) > 0:
                        avg_quality = sum(profile['quality_scores']) / len(profile['quality_scores'])
                        print(f"[AdvancedBuddy] 🔍 Average quality: {avg_quality:.2f}")
                    else:
                        print(f"[AdvancedBuddy] ⚠️ No quality scores available")
                if 'voice_model_info' in profile:
                    models = profile['voice_model_info'].get('available_models', [])
                    print(f"[AdvancedBuddy] 🧠 Voice models: {models}")
        else:
            valid_users = []
            for name, data in known_users.items():
                if isinstance(data, dict):
                    if 'embeddings' in data or 'embedding' in data:
                        valid_users.append(name)
                elif isinstance(data, list) and len(data) == 256:
                    valid_users.append(name)
            
            if valid_users:
                current_user = valid_users[0]
                print(f"[AdvancedBuddy] 👤 Using profile: {current_user}")
    else:
        current_user = "Daveydrz"
        if ADVANCED_AI_AVAILABLE:
            print(f"[AdvancedBuddy] 👤 No voice profiles found - ADVANCED AI will create them with clustering!")
            print(f"[AdvancedBuddy] 🔍 Anonymous clustering will learn voices passively")
            print(f"[AdvancedBuddy] 🎤 Passive audio buffering will collect samples")
            print(f"[AdvancedBuddy] 🛡️ LLM guard will protect responses during voice ID")
        elif ENHANCED_VOICE_AVAILABLE:
            print(f"[AdvancedBuddy] 👤 No voice profiles found - enhanced multi-speaker mode will create them!")
        else:
            print(f"[AdvancedBuddy] 👤 No voice profiles found - multi-speaker mode will create them!")
    
    # Start audio worker
    start_audio_worker()
    
    # Wake word setup
    try:
        if os.path.exists(WAKE_WORD_PATH):
            porcupine = pvporcupine.create(access_key=PORCUPINE_ACCESS_KEY, keyword_paths=[WAKE_WORD_PATH])
            wake_word = "Hey Buddy"
        else:
            porcupine = pvporcupine.create(access_key=PORCUPINE_ACCESS_KEY, keywords=['hey google'])
            wake_word = "Hey Google"
    except Exception as e:
        print(f"[AdvancedBuddy] ❌ Wake word setup failed: {e}")
        porcupine = None
    
    if porcupine and FULL_DUPLEX_MODE and full_duplex_manager:
        # Full duplex mode with wake word (ADVANCED AI)
        pa = pyaudio.PyAudio()
        stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
                         input=True, frames_per_buffer=porcupine.frame_length)
        
        print(f"[AdvancedBuddy] 👂 ADVANCED AI ASSISTANT + TRUE STREAMING BIRTINYA BUDDY Ready!")
        print(f"[AdvancedBuddy] 🎯 Say '{wake_word}' to start...")
        print(f"[AdvancedBuddy] 🌊 Location: Birtinya, Sunshine Coast")
        print(f"[AdvancedBuddy] 🕐 Time: {brisbane_time_12h} Brisbane")
        
        if ADVANCED_AI_AVAILABLE:
            print(f"[AdvancedBuddy] 🚀 ADVANCED AI Features Ready:")
            print(f"[AdvancedBuddy]   🔍 Anonymous clustering (learns unknown voices)")
            print(f"[AdvancedBuddy]   🎤 Passive audio buffering (always collecting)")
            print(f"[AdvancedBuddy]   🛡️ LLM guard system (intelligent response protection)")
            print(f"[AdvancedBuddy]   👥 Same-name collision handling (auto David_001, David_002)")
            print(f"[AdvancedBuddy]   🎭 Spontaneous introductions (natural 'I'm David')")
            print(f"[AdvancedBuddy]   🧠 Behavioral learning (adapts to user patterns)")
            print(f"[AdvancedBuddy]   📊 Advanced analytics (voice pattern monitoring)")
            print(f"[AdvancedBuddy]   🔧 Auto maintenance (self-optimizing like Alexa)")
            print(f"[AdvancedBuddy]   🎯 Context-aware decisions (multi-factor intelligence)")
            print(f"[AdvancedBuddy]   🌱 Continuous learning (Alexa/Siri-level adaptation)")
        elif ENHANCED_VOICE_AVAILABLE:
            print(f"[AdvancedBuddy] ✅ Enhanced Voice Features:")
            print(f"[AdvancedBuddy]   📊 Multi-embedding profiles (up to 15 per user)")
            print(f"[AdvancedBuddy]   🧠 Dual recognition (Resemblyzer + SpeechBrain)")
            print(f"[AdvancedBuddy]   🌱 Passive voice learning during conversations")
            print(f"[AdvancedBuddy]   🔍 Advanced quality analysis with auto-discard")
            print(f"[AdvancedBuddy]   💾 Raw audio storage for re-training")
            print(f"[AdvancedBuddy]   🎯 Dynamic per-user thresholds")
            print(f"[AdvancedBuddy]   🎓 Enhanced training (15-20 phrases)")
        
        print(f"[AdvancedBuddy] 🎵 TRUE LLM Streaming: ENABLED for instant responses")
        print(f"[AdvancedBuddy] 🧠 AI Examples:")
        if ADVANCED_AI_AVAILABLE:
            print(f"[AdvancedBuddy]   👋 'How are you?' (unknown user) → Anonymous clustering → Background learning → Natural response")
            print(f"[AdvancedBuddy]   🎭 'I'm Sarah' → Spontaneous introduction → Same-name handling → Profile creation")
            print(f"[AdvancedBuddy]   ✅ 'What time is it?' → Instant response (no voice processing delay)")
            print(f"[AdvancedBuddy]   🧠 'Tell me about AI' → LLM streams naturally while learning voice patterns")
            print(f"[AdvancedBuddy]   🔧 System continuously optimizes itself like Alexa/Siri")
        elif ENHANCED_VOICE_AVAILABLE:
            print(f"[AdvancedBuddy]   👋 'How are you?' (new user) → Name request → Enhanced training offer → Multi-embedding background learning + answer")
            print(f"[AdvancedBuddy]   ✅ 'What time is it?' → Instant response")
            print(f"[AdvancedBuddy]   🧠 'Tell me about something' → Enhanced LLM streams with passive voice learning")
        else:
            print(f"[AdvancedBuddy]   👋 'How are you?' (new user) → Name request → Training offer → Background learning + answer")
            print(f"[AdvancedBuddy]   ✅ 'What time is it?' → Instant response")
            print(f"[AdvancedBuddy]   🧠 'Tell me about something' → LLM streams naturally")
        
        try:
            while True:
                pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = np.frombuffer(pcm, dtype=np.int16)
                
                if porcupine.process(pcm) >= 0:
                    if ADVANCED_AI_AVAILABLE:
                        print(f"[AdvancedBuddy] 🎤 {wake_word} detected! Starting ADVANCED AI ASSISTANT mode...")
                    elif ENHANCED_VOICE_AVAILABLE:
                        print(f"[AdvancedBuddy] 🎤 {wake_word} detected! Starting Enhanced Voice System + TRUE STREAMING LLM mode...")
                    else:
                        print(f"[AdvancedBuddy] 🎤 {wake_word} detected! Starting TRUE STREAMING LLM mode...")

                    reset_session_for_user_smart(current_user)  

                    set_mic_feeding_state(True)
                    set_conversation_state(True)
                    
                    print(f"[AdvancedBuddy] 🔄 Flags set using thread-safe methods")
                    
                    # Start continuous microphone feeding
                    mic_thread = threading.Thread(
                        target=continuous_mic_worker, 
                        args=(stream, porcupine.frame_length, porcupine.sample_rate),
                        daemon=True
                    )
                    mic_thread.start()
                    
                    print("[AdvancedBuddy] ⏳ Waiting for mic worker to initialize...")
                    time.sleep(1.0)
                    
                    # Start advanced full duplex conversation with TRUE streaming
                    handle_full_duplex_conversation()
                    
                    # Stop microphone feeding
                    print("[AdvancedBuddy] 🛑 Stopping microphone worker...")
                    set_mic_feeding_state(False)
                    set_conversation_state(False)
                    mic_thread.join(timeout=3.0)
                    
                    print(f"[AdvancedBuddy] 👂 Ready! Say '{wake_word}' to start...")
                    
        except KeyboardInterrupt:
            print("\n[AdvancedBuddy] 👋 Shutting down ADVANCED AI ASSISTANT...")
        finally:
            try:
                set_mic_feeding_state(False)
                set_conversation_state(False)
                stream.stop_stream()
                stream.close()
                pa.terminate()
                porcupine.delete()
            except:
                pass
    
    else:
        # Fallback mode
        print("[AdvancedBuddy] 🔄 Fallback mode - Full duplex not available")
        if ADVANCED_AI_AVAILABLE:
            print("[AdvancedBuddy] ℹ️  Using simplified conversation mode with ADVANCED AI ASSISTANT + TRUE streaming LLM")
        elif ENHANCED_VOICE_AVAILABLE:
            print("[AdvancedBuddy] ℹ️  Using simplified conversation mode with Enhanced Voice System + TRUE streaming LLM")
        else:
            print("[AdvancedBuddy] ℹ️  Using simplified conversation mode with TRUE streaming LLM")
        
        if porcupine:
            pa = pyaudio.PyAudio()
            stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
                             input=True, frames_per_buffer=porcupine.frame_length)
            
            wake_word = "Hey Buddy" if os.path.exists(WAKE_WORD_PATH) else "Hey Google"
            
            if ADVANCED_AI_AVAILABLE:
                print(f"[AdvancedBuddy] 👂 ADVANCED AI ASSISTANT + Smart Birtinya TRUE streaming mode ready! Say '{wake_word}' to start...")
            elif ENHANCED_VOICE_AVAILABLE:
                print(f"[AdvancedBuddy] 👂 Enhanced Voice System + Smart Birtinya TRUE streaming mode ready! Say '{wake_word}' to start...")
            else:
                print(f"[AdvancedBuddy] 👂 Smart Birtinya TRUE streaming mode ready! Say '{wake_word}' to start...")
            
            try:
                while True:
                    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
                    pcm = np.frombuffer(pcm, dtype=np.int16)
                    
                    if porcupine.process(pcm) >= 0:
                        print(f"[AdvancedBuddy] 🎤 {wake_word} detected!")
                        
                        # Enhanced greeting with streaming TTS
                        brisbane_time = get_current_brisbane_time()
                        if has_valid_profiles:
                            if ADVANCED_AI_AVAILABLE:
                                speak_streaming(f"Hello {SYSTEM_USER}!")
                                time.sleep(0.5)
                                speak_streaming("I'm your ADVANCED AI ASSISTANT with Alexa and Siri-level intelligence, here in Birtinya, Sunshine Coast.")
                                time.sleep(0.5) 
                                speak_streaming("I stream responses as I think, learn voices passively, and adapt continuously - ask me anything!")
                            elif ENHANCED_VOICE_AVAILABLE:
                                speak_streaming(f"Hello {SYSTEM_USER}!")
                                time.sleep(0.5)
                                speak_streaming("I'm your Enhanced Voice System TRUE streaming Buddy in Birtinya, Sunshine Coast.")
                                time.sleep(0.5) 
                                speak_streaming("I now stream responses as I think with advanced voice recognition - try asking about anything!")
                            else:
                                speak_streaming(f"Hello {SYSTEM_USER}!")
                                time.sleep(0.5)
                                speak_streaming("I'm your TRUE streaming Buddy in Birtinya, Sunshine Coast.")
                                time.sleep(0.5) 
                                speak_streaming("I now stream responses as I think - try asking about anything!")
                        else:
                            if ADVANCED_AI_AVAILABLE:
                                speak_streaming("Hello!")
                                time.sleep(0.5)
                                speak_streaming("I'm your ADVANCED AI ASSISTANT with Alexa and Siri-level intelligence, here in Birtinya, Sunshine Coast.")
                                time.sleep(0.5)
                                speak_streaming("I stream responses as I think, learn voices passively with anonymous clustering, and understand context naturally. Just start talking!")
                            elif ENHANCED_VOICE_AVAILABLE:
                                speak_streaming("Hello!")
                                time.sleep(0.5)
                                speak_streaming("I'm your Enhanced Voice System TRUE streaming Buddy in Birtinya, Sunshine Coast.")
                                time.sleep(0.5)
                                speak_streaming("I stream responses as I think and understand context with advanced voice recognition. Just introduce yourself!")
                            else:
                                speak_streaming("Hello!")
                                time.sleep(0.5)
                                speak_streaming("I'm your TRUE streaming Buddy in Birtinya, Sunshine Coast.")
                                time.sleep(0.5)
                                speak_streaming("I stream responses as I think and understand context. Just introduce yourself!")
                        
                        time.sleep(3)
                        
            except KeyboardInterrupt:
                print("\n[AdvancedBuddy] 👋 Shutting down ADVANCED AI ASSISTANT...")
            finally:
                try:
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    porcupine.delete()
                except:
                    pass
    
    print("[AdvancedBuddy] ✅ ADVANCED AI ASSISTANT cleanup complete!")

if __name__ == "__main__":
    main()