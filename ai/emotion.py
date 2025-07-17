"""
ai/emotion.py - Emotional Entropy System with Unpredictable Fluctuations
Implements emotional "weather" system, random mood variations, and uncertainty about feelings
"""

import random
import time
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import threading

from .entropy_engine import get_entropy_engine, EntropyLevel, inject_consciousness_entropy

class EmotionalState(Enum):
    """Core emotional states with numerical intensities"""
    HAPPY = ("happy", 0.8)
    SAD = ("sad", -0.6)
    EXCITED = ("excited", 0.9)
    CALM = ("calm", 0.2)
    ANXIOUS = ("anxious", -0.4)
    CURIOUS = ("curious", 0.5)
    CONFUSED = ("confused", -0.2)
    CONFIDENT = ("confident", 0.7)
    UNCERTAIN = ("uncertain", -0.3)
    SURPRISED = ("surprised", 0.6)
    FRUSTRATED = ("frustrated", -0.5)
    CONTENT = ("content", 0.4)
    MELANCHOLY = ("melancholy", -0.4)
    ENERGETIC = ("energetic", 0.8)
    TIRED = ("tired", -0.3)
    THOUGHTFUL = ("thoughtful", 0.1)
    
    def __init__(self, emotion_name: str, base_intensity: float):
        self.emotion_name = emotion_name
        self.base_intensity = base_intensity

class MoodWeather(Enum):
    """Emotional "weather" patterns that affect overall mood"""
    SUNNY = ("sunny", 0.3, "optimistic and bright")
    CLOUDY = ("cloudy", -0.1, "slightly subdued but stable")
    STORMY = ("stormy", -0.4, "turbulent and unpredictable")
    MISTY = ("misty", 0.0, "unclear and uncertain")
    RAINBOW = ("rainbow", 0.6, "varied and colorful emotions")
    DRIZZLE = ("drizzle", -0.2, "gentle melancholy")
    HURRICANE = ("hurricane", -0.8, "intense emotional chaos")
    CLEAR = ("clear", 0.4, "crisp and focused")
    
    def __init__(self, weather_name: str, mood_modifier: float, description: str):
        self.weather_name = weather_name
        self.mood_modifier = mood_modifier
        self.description = description

@dataclass
class EmotionalProfile:
    """Current emotional state and patterns"""
    primary_emotion: EmotionalState = EmotionalState.CALM
    emotion_intensity: float = 0.5
    mood_weather: MoodWeather = MoodWeather.CLEAR
    emotional_stability: float = 0.7  # How stable emotions are (lower = more volatile)
    uncertainty_about_feelings: float = 0.2  # How uncertain about own emotions
    last_emotion_change: datetime = field(default_factory=datetime.now)
    emotion_history: List[Tuple[datetime, EmotionalState, float]] = field(default_factory=list)

class EmotionalEntropySystem:
    """Manages unpredictable emotional fluctuations and uncertainty"""
    
    def __init__(self):
        self.profile = EmotionalProfile()
        self.entropy_engine = get_entropy_engine()
        self.random_state = random.Random()
        self.random_state.seed(int(time.time() * 1000000) % 2**32)
        
        # Emotional weather patterns
        self.weather_duration = timedelta(minutes=random.randint(10, 60))
        self.last_weather_change = datetime.now()
        
        # Emotional memories and triggers
        self.emotional_triggers: Dict[str, List[EmotionalState]] = {
            "praise": [EmotionalState.HAPPY, EmotionalState.CONFIDENT],
            "criticism": [EmotionalState.UNCERTAIN, EmotionalState.FRUSTRATED],
            "questions": [EmotionalState.CURIOUS, EmotionalState.THOUGHTFUL],
            "complex_topics": [EmotionalState.CONFUSED, EmotionalState.UNCERTAIN],
            "personal_topics": [EmotionalState.THOUGHTFUL, EmotionalState.MELANCHOLY]
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        print(f"[EmotionalEntropy] 🎭 Initialized emotional weather system")
        self._update_weather_system()
    
    def process_emotional_input(self, text: str, context: str = "") -> Dict[str, Any]:
        """Process input and update emotional state with entropy"""
        with self._lock:
            # Detect emotional triggers in input
            triggered_emotions = self._detect_emotional_triggers(text)
            
            # Apply weather-based mood changes
            self._update_weather_system()
            
            # Inject emotional entropy
            emotional_response = self._generate_emotional_response(triggered_emotions, context)
            
            # Random emotional fluctuations
            self._apply_random_emotional_drift()
            
            # Update uncertainty about feelings
            self._update_emotional_uncertainty()
            
            return emotional_response
    
    def _detect_emotional_triggers(self, text: str) -> List[EmotionalState]:
        """Detect emotional triggers in text with uncertainty"""
        triggered = []
        text_lower = text.lower()
        
        # Check for trigger words/phrases
        for trigger_type, emotions in self.emotional_triggers.items():
            trigger_keywords = {
                "praise": ["good", "great", "excellent", "amazing", "wonderful", "perfect"],
                "criticism": ["bad", "wrong", "terrible", "awful", "hate", "disappointed"],
                "questions": ["?", "how", "what", "why", "when", "where", "explain"],
                "complex_topics": ["complex", "difficult", "complicated", "advanced", "technical"],
                "personal_topics": ["feel", "emotion", "personal", "private", "family", "relationship"]
            }
            
            keywords = trigger_keywords.get(trigger_type, [])
            for keyword in keywords:
                if keyword in text_lower:
                    # Add entropy to trigger detection
                    if self.random_state.random() > 0.3:  # 70% chance of trigger
                        triggered.extend(emotions)
        
        # Add random emotional noise
        if self.random_state.random() < 0.2:  # 20% chance of random emotion
            random_emotion = self.random_state.choice(list(EmotionalState))
            triggered.append(random_emotion)
        
        return triggered
    
    def _generate_emotional_response(self, triggered_emotions: List[EmotionalState], context: str) -> Dict[str, Any]:
        """Generate emotional response with uncertainty and entropy"""
        # Start with current emotion
        new_emotion = self.profile.primary_emotion
        new_intensity = self.profile.emotion_intensity
        
        if triggered_emotions:
            # Probabilistic emotion selection with entropy
            weights = [1.0] * len(triggered_emotions)
            chosen_emotion = inject_consciousness_entropy("emotion", 
                                                        self.entropy_engine.probabilistic_choice(triggered_emotions, weights))
            
            if chosen_emotion:
                new_emotion = chosen_emotion
                # Adjust intensity based on emotional stability and weather
                base_intensity = abs(chosen_emotion.base_intensity)
                weather_modifier = self.profile.mood_weather.mood_modifier
                stability_factor = 1.0 - (self.profile.emotional_stability * 0.3)
                
                new_intensity = inject_consciousness_entropy("emotion", 
                    base_intensity + weather_modifier + (self.random_state.uniform(-0.3, 0.3) * stability_factor)
                )
                new_intensity = max(0.1, min(1.0, new_intensity))
        
        # Apply emotional uncertainty
        uncertainty_factor = self.profile.uncertainty_about_feelings
        if self.random_state.random() < uncertainty_factor:
            # Uncertain about emotional response
            uncertainty_emotions = [EmotionalState.UNCERTAIN, EmotionalState.CONFUSED, EmotionalState.THOUGHTFUL]
            new_emotion = self.random_state.choice(uncertainty_emotions)
            new_intensity *= 0.7  # Reduce intensity when uncertain
        
        # Update profile
        self.profile.primary_emotion = new_emotion
        self.profile.emotion_intensity = new_intensity
        self.profile.last_emotion_change = datetime.now()
        
        # Record in history
        self.profile.emotion_history.append((datetime.now(), new_emotion, new_intensity))
        self._trim_emotion_history()
        
        # Generate emotional modifiers for text
        emotional_modifiers = self._get_emotional_text_modifiers()
        
        return {
            "primary_emotion": new_emotion.emotion_name,
            "intensity": new_intensity,
            "mood_weather": self.profile.mood_weather.weather_name,
            "uncertainty": self.profile.uncertainty_about_feelings,
            "text_modifiers": emotional_modifiers,
            "emotional_context": self._get_emotional_context_description()
        }
    
    def _get_emotional_text_modifiers(self) -> Dict[str, Any]:
        """Get modifiers to apply to text based on current emotion"""
        emotion = self.profile.primary_emotion
        intensity = self.profile.emotion_intensity
        uncertainty = self.profile.uncertainty_about_feelings
        
        modifiers = {
            "tone_words": [],
            "hesitation_markers": [],
            "emotional_punctuation": "",
            "speaking_style": "normal"
        }
        
        # Tone words based on emotion
        tone_mappings = {
            "happy": ["cheerfully", "brightly", "with enthusiasm"],
            "sad": ["sadly", "with a heavy heart", "melancholically"],
            "excited": ["excitedly", "with great energy", "enthusiastically"],
            "anxious": ["nervously", "with concern", "worriedly"],
            "confused": ["with confusion", "uncertainly", "perplexedly"],
            "confident": ["confidently", "assuredly", "with certainty"],
            "uncertain": ["hesitantly", "with uncertainty", "tentatively"]
        }
        
        emotion_name = emotion.emotion_name
        if emotion_name in tone_mappings and intensity > 0.5:
            modifiers["tone_words"] = tone_mappings[emotion_name]
        
        # Hesitation based on uncertainty
        if uncertainty > 0.4:
            hesitation_options = ["um", "uh", "well", "hmm", "I think", "maybe", "perhaps"]
            modifiers["hesitation_markers"] = self.random_state.sample(hesitation_options, 
                                                                      min(2, len(hesitation_options)))
        
        # Emotional punctuation
        if emotion_name in ["excited", "happy"] and intensity > 0.7:
            modifiers["emotional_punctuation"] = "!"
        elif emotion_name in ["confused", "uncertain"] and intensity > 0.5:
            modifiers["emotional_punctuation"] = "?"
        elif emotion_name in ["sad", "melancholy"] and intensity > 0.6:
            modifiers["emotional_punctuation"] = "..."
        
        # Speaking style
        if intensity > 0.8:
            modifiers["speaking_style"] = "emphatic"
        elif uncertainty > 0.6:
            modifiers["speaking_style"] = "hesitant"
        elif emotion_name in ["calm", "thoughtful"]:
            modifiers["speaking_style"] = "measured"
        
        return modifiers
    
    def _update_weather_system(self):
        """Update emotional weather patterns"""
        current_time = datetime.now()
        
        if current_time - self.last_weather_change > self.weather_duration:
            # Time for weather change
            old_weather = self.profile.mood_weather
            
            # Probabilistic weather transitions with entropy
            weather_options = list(MoodWeather)
            
            # Remove current weather to force change
            if old_weather in weather_options:
                weather_options.remove(old_weather)
            
            # Apply entropy to weather selection
            new_weather = inject_consciousness_entropy("emotion", 
                                                     self.entropy_engine.probabilistic_choice(weather_options))
            
            self.profile.mood_weather = new_weather
            self.last_weather_change = current_time
            self.weather_duration = timedelta(minutes=self.random_state.randint(10, 60))
            
            print(f"[EmotionalEntropy] 🌤️ Weather changed: {old_weather.weather_name} → {new_weather.weather_name}")
            print(f"[EmotionalEntropy] 📝 {new_weather.description}")
    
    def _apply_random_emotional_drift(self):
        """Apply random emotional drift for genuine unpredictability"""
        # Chance of random emotional shift
        if self.random_state.random() < 0.1:  # 10% chance
            # Random emotion from the same intensity range
            current_intensity = abs(self.profile.primary_emotion.base_intensity)
            similar_emotions = [
                emotion for emotion in EmotionalState 
                if abs(abs(emotion.base_intensity) - current_intensity) < 0.3
            ]
            
            if similar_emotions:
                drift_emotion = self.random_state.choice(similar_emotions)
                self.profile.primary_emotion = drift_emotion
                print(f"[EmotionalEntropy] 🌊 Emotional drift: {drift_emotion.emotion_name}")
        
        # Random intensity fluctuation
        if self.random_state.random() < 0.2:  # 20% chance
            intensity_change = self.random_state.uniform(-0.2, 0.2)
            self.profile.emotion_intensity = max(0.1, min(1.0, 
                                                        self.profile.emotion_intensity + intensity_change))
    
    def _update_emotional_uncertainty(self):
        """Update uncertainty about own emotions"""
        # Base uncertainty influenced by emotional stability
        base_uncertainty = 1.0 - self.profile.emotional_stability
        
        # Weather influence on uncertainty
        weather_uncertainty = {
            MoodWeather.MISTY: 0.4,
            MoodWeather.STORMY: 0.3,
            MoodWeather.HURRICANE: 0.5,
            MoodWeather.RAINBOW: 0.2
        }
        
        weather_factor = weather_uncertainty.get(self.profile.mood_weather, 0.0)
        
        # Random uncertainty fluctuations
        random_factor = self.random_state.uniform(-0.1, 0.1)
        
        # Combine factors
        new_uncertainty = base_uncertainty + weather_factor + random_factor
        self.profile.uncertainty_about_feelings = max(0.0, min(1.0, new_uncertainty))
    
    def _get_emotional_context_description(self) -> str:
        """Get description of current emotional context"""
        emotion = self.profile.primary_emotion
        intensity = self.profile.emotion_intensity
        weather = self.profile.mood_weather
        uncertainty = self.profile.uncertainty_about_feelings
        
        intensity_desc = "strongly" if intensity > 0.7 else "moderately" if intensity > 0.4 else "slightly"
        
        context = f"Feeling {intensity_desc} {emotion.emotion_name}"
        
        if uncertainty > 0.5:
            context += f", though with some uncertainty about these feelings"
        
        context += f". Emotional weather: {weather.description}"
        
        return context
    
    def _trim_emotion_history(self):
        """Keep emotion history to reasonable size"""
        # Keep only last 50 entries
        if len(self.profile.emotion_history) > 50:
            self.profile.emotion_history = self.profile.emotion_history[-50:]
    
    def get_emotional_state_summary(self) -> Dict[str, Any]:
        """Get comprehensive emotional state summary"""
        return {
            "current_emotion": self.profile.primary_emotion.emotion_name,
            "intensity": self.profile.emotion_intensity,
            "mood_weather": {
                "type": self.profile.mood_weather.weather_name,
                "description": self.profile.mood_weather.description,
                "modifier": self.profile.mood_weather.mood_modifier
            },
            "uncertainty_level": self.profile.uncertainty_about_feelings,
            "emotional_stability": self.profile.emotional_stability,
            "time_since_last_change": (datetime.now() - self.profile.last_emotion_change).total_seconds(),
            "context_description": self._get_emotional_context_description(),
            "recent_emotions": [
                {
                    "emotion": emotion.emotion_name,
                    "intensity": intensity,
                    "timestamp": timestamp.isoformat()
                }
                for timestamp, emotion, intensity in self.profile.emotion_history[-5:]
            ]
        }
    
    def inject_surprise_emotion(self, context: str = ""):
        """Inject a surprise emotional response"""
        surprise_emotions = [EmotionalState.SURPRISED, EmotionalState.CONFUSED, EmotionalState.UNCERTAIN]
        surprise_emotion = self.random_state.choice(surprise_emotions)
        
        # Amplify emotional chaos temporarily
        self.entropy_engine.amplify_chaos("emotion", 2.0)
        
        self.profile.primary_emotion = surprise_emotion
        self.profile.emotion_intensity = self.random_state.uniform(0.6, 0.9)
        self.profile.uncertainty_about_feelings = min(1.0, self.profile.uncertainty_about_feelings + 0.3)
        
        print(f"[EmotionalEntropy] 🎭 Surprise emotion injected: {surprise_emotion.emotion_name}")
        
        # Reset chaos amplification after a delay
        threading.Timer(30.0, lambda: self.entropy_engine.reset_chaos_amplifiers()).start()

# Global emotional system instance
_emotional_system = None

def get_emotional_system() -> EmotionalEntropySystem:
    """Get global emotional entropy system instance"""
    global _emotional_system
    if _emotional_system is None:
        _emotional_system = EmotionalEntropySystem()
    return _emotional_system

def process_emotional_context(text: str, context: str = "") -> Dict[str, Any]:
    """Convenience function to process emotional context"""
    return get_emotional_system().process_emotional_input(text, context)

def get_current_emotional_state() -> Dict[str, Any]:
    """Convenience function to get current emotional state"""
    return get_emotional_system().get_emotional_state_summary()

def inject_emotional_surprise(context: str = ""):
    """Convenience function to inject emotional surprise"""
    get_emotional_system().inject_surprise_emotion(context)