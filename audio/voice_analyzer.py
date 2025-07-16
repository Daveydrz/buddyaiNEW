# audio/voice_analyzer.py - Advanced Voice Quality Analysis with Room-Scale Detection
# Date: 2025-01-16 (Enhanced for room-scale detection)
# ADVANCED: Multi-layer voice detection to reject background noise + distance-adaptive detection

# ✅ GRACEFUL IMPORTS: Handle missing dependencies
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[VoiceAnalyzer] ⚠️ NumPy not available - using fallback math functions")

try:
    import scipy.signal as signal
    from scipy.fft import fft, fftfreq
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("[VoiceAnalyzer] ⚠️ SciPy not available - using simplified analysis")

from collections import deque
import time
import math
from config import *

# ✅ FALLBACK MATH FUNCTIONS when NumPy is not available
def fallback_mean(data):
    """Calculate mean without numpy"""
    if not data:
        return 0.0
    return sum(data) / len(data)

def fallback_max(data):
    """Calculate max without numpy"""
    if not data:
        return 0.0
    return max(data)

def fallback_min(data):
    """Calculate min without numpy"""
    if not data:
        return 0.0
    return min(data)

def fallback_abs_mean(data):
    """Calculate mean of absolute values without numpy"""
    if not data:
        return 0.0
    return sum(abs(x) for x in data) / len(data)

def fallback_clip(value, min_val, max_val):
    """Clip value to range without numpy"""
    return max(min_val, min(max_val, value))

def fallback_variance(data):
    """Calculate variance without numpy"""
    if len(data) < 2:
        return 0.0
    mean_val = fallback_mean(data)
    return sum((x - mean_val) ** 2 for x in data) / len(data)

def fallback_std(data):
    """Calculate standard deviation without numpy"""
    return math.sqrt(fallback_variance(data))

class AdvancedVoiceAnalyzer:
    def __init__(self):
        self.noise_baseline = 100
        self.noise_samples = deque(maxlen=500)
        self.voice_samples = deque(maxlen=100)
        self.environment_calibrated = False
        self.calibration_start_time = time.time()
        
        # Voice detection history
        self.recent_voice_scores = deque(maxlen=20)
        self.recent_spectral_scores = deque(maxlen=20)
        self.recent_temporal_scores = deque(maxlen=20)
        
        # ✅ NEW: Room-scale detection features
        self.distance_adaptive_mode = getattr(globals().get('config', {}), 'ROOM_SCALE_MODE', True)
        self.background_rejection_enabled = getattr(globals().get('config', {}), 'BACKGROUND_REJECTION_ENABLED', True)
        self.voice_fingerprint_matching = getattr(globals().get('config', {}), 'VOICE_FINGERPRINT_MATCHING', True)
        self.multi_speaker_rejection = getattr(globals().get('config', {}), 'MULTI_SPEAKER_REJECTION', True)
        self.media_audio_filtering = getattr(globals().get('config', {}), 'MEDIA_AUDIO_FILTERING', True)
        
        # ✅ NEW: Distance detection tiers
        try:
            self.detection_tiers = DETECTION_TIERS
        except:
            self.detection_tiers = {
                "close": {"volume": 800, "quality": 0.6, "range": "0-50cm", "spectral": 0.4},
                "medium": {"volume": 400, "quality": 0.35, "range": "50cm-1.5m", "spectral": 0.3},
                "far": {"volume": 200, "quality": 0.20, "range": "1.5m-3m", "spectral": 0.25},
                "room": {"volume": 100, "quality": 0.15, "range": "3m+", "spectral": 0.2}
            }
        
        # ✅ NEW: Background audio pattern recognition
        self.background_patterns = deque(maxlen=100)
        self.media_audio_patterns = deque(maxlen=50)
        self.environmental_noise_profile = {}
        
        # ✅ NEW: Voice fingerprinting for primary user
        self.primary_user_voice_profile = None
        self.known_voice_profiles = {}
        
        # ✅ NEW: Auto-gain control for distant speech
        self.auto_gain_enabled = getattr(globals().get('config', {}), 'AUTO_GAIN_CONTROL', True)
        self.gain_history = deque(maxlen=10)
        
        print("[VoiceAnalyzer] 🧠 Advanced Voice Analyzer initialized with Room-Scale Detection")
        print(f"[VoiceAnalyzer] 🎯 Distance Adaptive Mode: {self.distance_adaptive_mode}")
        print(f"[VoiceAnalyzer] 🛡️ Background Rejection: {self.background_rejection_enabled}")
        print(f"[VoiceAnalyzer] 🔍 Voice Fingerprinting: {self.voice_fingerprint_matching}")
        print(f"[VoiceAnalyzer] 👥 Multi-Speaker Rejection: {self.multi_speaker_rejection}")
        print(f"[VoiceAnalyzer] 📺 Media Audio Filtering: {self.media_audio_filtering}")
        print(f"[VoiceAnalyzer] 🔊 Auto-Gain Control: {self.auto_gain_enabled}")
        print(f"[VoiceAnalyzer] 📏 Detection Tiers: {len(self.detection_tiers)} ranges")

    def analyze_audio_chunk(self, audio_chunk, is_buddy_speaking=False):
        """
        Advanced multi-layer analysis to determine if audio contains human voice
        Returns: (is_voice, quality_score, detailed_scores)
        """
        try:
            # ✅ COMPREHENSIVE input validation
            if audio_chunk is None:
                return False, 0.0, {'error': 'audio_chunk is None'}
            
            # ✅ FALLBACK: Handle missing numpy gracefully
            if NUMPY_AVAILABLE:
                # Convert to numpy array and ensure proper data type
                try:
                    if not isinstance(audio_chunk, type(np.array([]))):
                        audio_chunk = np.array(audio_chunk, dtype=np.int16)
                    else:
                        audio_chunk = audio_chunk.astype(np.int16)
                except (ValueError, TypeError) as e:
                    if DEBUG:
                        print(f"[VoiceAnalyzer] ❌ Invalid audio data type: {e}")
                    return False, 0.0, {'error': 'invalid_data_type'}
                
                # Check for empty or too small chunks
                if len(audio_chunk) == 0:
                    return False, 0.0, {'error': 'empty_chunk'}
                
                if len(audio_chunk) < 40:  # Minimum viable chunk size
                    return False, 0.0, {'error': 'chunk_too_small', 'length': len(audio_chunk)}
                
                # Clean and validate audio data
                audio_chunk = np.nan_to_num(audio_chunk, nan=0, posinf=0, neginf=0)
                audio_chunk = np.clip(audio_chunk, -32768, 32767)
                
                # Calculate basic metrics with numpy
                volume = float(np.abs(audio_chunk).mean())
                peak = float(np.max(np.abs(audio_chunk)))
                
            else:
                # ✅ FALLBACK: Use native Python without numpy
                # Ensure we have a list of numbers
                if hasattr(audio_chunk, '__iter__'):
                    audio_chunk = list(audio_chunk)
                else:
                    return False, 0.0, {'error': 'invalid_data_format'}
                
                # Check for empty or too small chunks
                if len(audio_chunk) == 0:
                    return False, 0.0, {'error': 'empty_chunk'}
                
                if len(audio_chunk) < 40:
                    return False, 0.0, {'error': 'chunk_too_small', 'length': len(audio_chunk)}
                
                # Clean data - remove any non-numeric values
                try:
                    audio_chunk = [float(x) for x in audio_chunk if isinstance(x, (int, float))]
                    # Clip to valid range
                    audio_chunk = [fallback_clip(x, -32768, 32767) for x in audio_chunk]
                except (ValueError, TypeError):
                    return False, 0.0, {'error': 'data_conversion_failed'}
                
                # Calculate basic metrics with fallback functions
                volume = fallback_abs_mean(audio_chunk)
                peak = fallback_max([abs(x) for x in audio_chunk])
            
            # Validate basic metrics
            if math.isnan(volume) or math.isinf(volume):
                volume = 0.0
            if math.isnan(peak) or math.isinf(peak):
                peak = 0.0
            
            # ✅ EARLY EXIT for very quiet audio
            if volume < 5.0:  # Very quiet, likely silence
                return False, 0.0, {
                    'volume': volume,
                    'peak': peak,
                    'combined': 0.0,
                    'reason': 'too_quiet',
                    'fallback_mode': not NUMPY_AVAILABLE
                }
            
            # ✅ ROOM-SCALE: Quick distance estimation for adaptive processing
            if self.distance_adaptive_mode:
                estimated_distance = self._quick_distance_estimate(volume)
                distance_tier = self.detection_tiers.get(estimated_distance, self.detection_tiers['room'])
            else:
                estimated_distance = "unknown"
                distance_tier = None
            
            # ✅ RUN ANALYSIS layers with fallback support
            spectral_score = 0.0
            temporal_score = 0.0
            quality_score = 0.0
            harmonic_score = 0.0
            noise_score = 0.5  # Default neutral score
            
            # Spectral analysis
            try:
                if NUMPY_AVAILABLE and SCIPY_AVAILABLE:
                    spectral_score = self._spectral_voice_analysis_numpy(audio_chunk)
                else:
                    spectral_score = self._spectral_voice_analysis_fallback(audio_chunk)
                spectral_score = fallback_clip(spectral_score, 0.0, 1.0)
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Spectral analysis error: {e}")
                spectral_score = 0.0
            
            # Temporal analysis
            try:
                if NUMPY_AVAILABLE:
                    temporal_score = self._temporal_pattern_analysis_numpy(audio_chunk)
                else:
                    temporal_score = self._temporal_pattern_analysis_fallback(audio_chunk)
                temporal_score = fallback_clip(temporal_score, 0.0, 1.0)
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Temporal analysis error: {e}")
                temporal_score = 0.0
            
            # Quality analysis
            try:
                if NUMPY_AVAILABLE:
                    quality_score = self._voice_quality_analysis_numpy(audio_chunk)
                else:
                    quality_score = self._voice_quality_analysis_fallback(audio_chunk)
                quality_score = fallback_clip(quality_score, 0.0, 1.0)
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Quality analysis error: {e}")
                quality_score = 0.0
            
            # Simplified harmonic analysis
            try:
                harmonic_score = self._simple_harmonic_analysis(audio_chunk)
                harmonic_score = fallback_clip(harmonic_score, 0.0, 1.0)
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Harmonic analysis error: {e}")
                harmonic_score = 0.0
            
            # Noise analysis
            try:
                noise_score = self._simple_noise_analysis(volume)
                noise_score = fallback_clip(noise_score, 0.0, 1.0)
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Noise analysis error: {e}")
                noise_score = 0.5
            
            # ✅ COMBINE scores with validation
            try:
                combined_score = (
                    spectral_score * 0.3 +
                    temporal_score * 0.25 +
                    quality_score * 0.25 +
                    harmonic_score * 0.1 +
                    noise_score * 0.1
                )
                combined_score = fallback_clip(combined_score, 0.0, 1.0)
            except:
                combined_score = 0.0
            
            # ✅ DISTANCE-ADAPTIVE thresholds
            if self.distance_adaptive_mode and distance_tier:
                volume_threshold = distance_tier['volume']
                quality_threshold = distance_tier['quality']
                spectral_threshold = distance_tier.get('spectral', 0.2)
                
                # Distance-based detection
                is_voice_volume = volume >= volume_threshold
                is_voice_quality = combined_score >= quality_threshold
                is_voice_spectral = spectral_score >= spectral_threshold
                
                is_voice = is_voice_volume and (is_voice_quality or is_voice_spectral)
            else:
                # Standard detection
                is_voice_volume = volume >= USER_SPEECH_THRESHOLD
                is_voice_quality = combined_score >= USER_SPEECH_QUALITY_THRESHOLD
                is_voice_spectral = spectral_score >= USER_SPEECH_SPECTRAL_THRESHOLD
                
                is_voice = is_voice_volume and is_voice_quality and is_voice_spectral
            
            # ✅ UPDATE learning data
            if is_voice:
                self.recent_voice_scores.append(combined_score)
                self.voice_samples.append(volume)
            else:
                self.noise_samples.append(volume)
            
            # ✅ BUILD detailed results
            detailed_scores = {
                'volume': volume,
                'peak': peak,
                'spectral_voice_score': spectral_score,
                'temporal_score': temporal_score,
                'quality_score': quality_score,
                'harmonic_score': harmonic_score,
                'noise_score': noise_score,
                'combined': combined_score,
                'is_voice_volume': is_voice_volume,
                'is_voice_quality': is_voice_quality,
                'is_voice_spectral': is_voice_spectral,
                'fallback_mode': not NUMPY_AVAILABLE,
                'scipy_available': SCIPY_AVAILABLE,
                'estimated_distance': estimated_distance,
                'distance_adaptive': self.distance_adaptive_mode
            }
            
            return is_voice, combined_score, detailed_scores
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] ❌ Analysis error: {e}")
            return False, 0.0, {'error': str(e), 'fallback_mode': not NUMPY_AVAILABLE}

    def _quick_distance_estimate(self, volume):
        """Quick distance estimation from volume"""
        if volume >= 800:
            return "close"
        elif volume >= 400:
            return "medium"
        elif volume >= 200:
            return "far"
        else:
            return "room"
            
            if len(audio_chunk) < 40:  # Minimum viable chunk size
                return False, 0.0, {'error': 'chunk_too_small', 'length': len(audio_chunk)}
            
            # ✅ FIXED: Clean and validate audio data
            # Remove any NaN, inf, or invalid values
            audio_chunk = np.nan_to_num(audio_chunk, nan=0, posinf=0, neginf=0)
            
            # Clip to valid int16 range
            audio_chunk = np.clip(audio_chunk, -32768, 32767)
            
            # Convert to float for analysis with proper scaling
            try:
                audio_float = audio_chunk.astype(np.float32)
                max_val = np.max(np.abs(audio_float))
                if max_val > 1.0:
                    audio_float = audio_float / 32768.0
                
                # Final validation of float array
                if np.any(np.isnan(audio_float)) or np.any(np.isinf(audio_float)):
                    audio_float = np.nan_to_num(audio_float, nan=0, posinf=0, neginf=0)
                    
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] ❌ Float conversion error: {e}")
                return False, 0.0, {'error': 'float_conversion_failed'}
            
            # ✅ FIXED: Calculate basic metrics with error handling
            try:
                volume = float(np.abs(audio_chunk).mean())
                peak = float(np.max(np.abs(audio_chunk)))
                
                # Validate basic metrics
                if np.isnan(volume) or np.isinf(volume):
                    volume = 0.0
                if np.isnan(peak) or np.isinf(peak):
                    peak = 0.0
                    
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] ❌ Basic metrics error: {e}")
                return False, 0.0, {'error': 'basic_metrics_failed'}
            
            # ✅ FIXED: Early exit for very quiet audio to avoid processing errors
            if volume < 5.0:  # Very quiet, likely silence
                return False, 0.0, {
                    'volume': volume,
                    'peak': peak,
                    'combined': 0.0,
                    'reason': 'too_quiet'
                }
            
            # ✅ FIXED: Run analysis layers with individual error handling
            spectral_score = 0.0
            temporal_score = 0.0
            quality_score = 0.0
            harmonic_score = 0.0
            noise_score = 0.5  # Default neutral score
            
            # Spectral analysis with error handling
            try:
                spectral_score = self._spectral_voice_analysis(audio_float)
                if np.isnan(spectral_score) or np.isinf(spectral_score):
                    spectral_score = 0.0
                spectral_score = max(0.0, min(1.0, float(spectral_score)))
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Spectral analysis error: {e}")
                spectral_score = 0.0
            
            # Temporal analysis with error handling
            try:
                temporal_score = self._temporal_pattern_analysis(audio_float)
                if np.isnan(temporal_score) or np.isinf(temporal_score):
                    temporal_score = 0.0
                temporal_score = max(0.0, min(1.0, float(temporal_score)))
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Temporal analysis error: {e}")
                temporal_score = 0.0
            
            # Quality analysis with error handling
            try:
                quality_score = self._voice_quality_analysis(audio_float)
                if np.isnan(quality_score) or np.isinf(quality_score):
                    quality_score = 0.0
                quality_score = max(0.0, min(1.0, float(quality_score)))
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Quality analysis error: {e}")
                quality_score = 0.0
            
            # Harmonic analysis with error handling
            try:
                harmonic_score = self._harmonic_analysis(audio_float)
                if np.isnan(harmonic_score) or np.isinf(harmonic_score):
                    harmonic_score = 0.0
                harmonic_score = max(0.0, min(1.0, float(harmonic_score)))
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Harmonic analysis error: {e}")
                harmonic_score = 0.0
            
            # Noise analysis with error handling
            try:
                noise_score = self._noise_analysis(audio_float, volume)
                if np.isnan(noise_score) or np.isinf(noise_score):
                    noise_score = 0.5
                noise_score = max(0.0, min(1.0, float(noise_score)))
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Noise analysis error: {e}")
                noise_score = 0.5
            
            # ✅ FIXED: Combine scores with validation
            try:
                combined_score = (
                    spectral_score * 0.25 +
                    temporal_score * 0.20 +
                    quality_score * 0.25 +
                    harmonic_score * 0.15 +
                    noise_score * 0.15
                )
                
                # Validate combined score
                if np.isnan(combined_score) or np.isinf(combined_score):
                    combined_score = 0.0
                combined_score = max(0.0, min(1.0, float(combined_score)))
                
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Score combination error: {e}")
                combined_score = 0.0
            
            # ✅ FIXED: Safe threshold determination
            try:
                if is_buddy_speaking:
                    # Much stricter when Buddy is speaking (interrupts)
                    voice_threshold = getattr(self, 'buddy_interrupt_quality_threshold', 
                                            getattr(globals(), 'BUDDY_INTERRUPT_QUALITY_THRESHOLD', 0.8))
                    volume_threshold = getattr(self, 'buddy_interrupt_threshold',
                                             getattr(globals(), 'BUDDY_INTERRUPT_THRESHOLD', 2500))
                else:
                    # Normal thresholds when waiting for user
                    voice_threshold = getattr(self, 'user_speech_quality_threshold',
                                            getattr(globals(), 'USER_SPEECH_QUALITY_THRESHOLD', 0.6))
                    volume_threshold = getattr(self, 'user_speech_threshold',
                                             getattr(globals(), 'USER_SPEECH_THRESHOLD', 800))
                
                spectral_threshold = getattr(self, 'user_speech_spectral_threshold',
                                           getattr(globals(), 'USER_SPEECH_SPECTRAL_THRESHOLD', 0.5))
                
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Threshold determination error: {e}")
                voice_threshold = 0.6
                volume_threshold = 800
                spectral_threshold = 0.5
            
            # ✅ FIXED: Safe voice detection decision
            try:
                passes_noise_gate = self._passes_noise_gate(audio_float, volume)
            except Exception as e:
                if DEBUG and "non-printable character" not in str(e):
                    print(f"[VoiceAnalyzer] Noise gate error: {e}")
                passes_noise_gate = volume > volume_threshold * 0.5  # Fallback
            
            is_voice = (
                volume > volume_threshold and
                combined_score > voice_threshold and
                spectral_score > spectral_threshold and
                passes_noise_gate
            )
            
            # ✅ FIXED: Safe storage for adaptation
            try:
                if is_voice:
                    if hasattr(self, 'voice_samples') and hasattr(self, 'recent_voice_scores'):
                        self.voice_samples.append(combined_score)
                        self.recent_voice_scores.append(combined_score)
                else:
                    if hasattr(self, 'noise_samples'):
                        self.noise_samples.append(volume)
                
                # Update environment calibration
                if hasattr(self, '_update_environment_calibration'):
                    self._update_environment_calibration()
                    
            except Exception as e:
                if DEBUG:
                    print(f"[VoiceAnalyzer] Storage/calibration error: {e}")
            
            # ✅ FIXED: Build detailed scores dictionary safely
            detailed_scores = {
                'volume': float(volume),
                'peak': float(peak),
                'spectral': float(spectral_score),
                'temporal': float(temporal_score),
                'quality': float(quality_score),
                'harmonic': float(harmonic_score),
                'noise': float(noise_score),
                'combined': float(combined_score),
                'threshold': float(voice_threshold),
                'is_voice': bool(is_voice),
                'analysis_success': True
            }
            
            # ✅ FIXED: Safe debug output
            try:
                if (DEBUG and 
                    getattr(globals(), 'SHOW_VOICE_QUALITY_SCORES', True) and
                    (is_voice or combined_score > 0.3)):
                    print(f"[VoiceAnalyzer] {'✅' if is_voice else '❌'} "
                          f"Vol:{volume:.0f} Combined:{combined_score:.2f} "
                          f"Spec:{spectral_score:.2f} Qual:{quality_score:.2f}")
            except Exception as e:
                # Silently ignore debug output errors
                pass
            
            return bool(is_voice), float(combined_score), detailed_scores
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] ❌ Critical analysis error: {e}")
            return False, 0.0, {
                'error': 'critical_failure',
                'error_message': str(e),
                'volume': 0.0,
                'combined': 0.0
            }

    def _spectral_voice_analysis(self, audio_float):
        """Analyze frequency content to detect voice characteristics"""
        try:
            if len(audio_float) < 160:
                return 0.0
            
            # FFT analysis
            window = np.hanning(len(audio_float))
            windowed = audio_float * window
            fft_result = fft(windowed)
            freqs = fftfreq(len(audio_float), 1/SAMPLE_RATE)
            magnitude = np.abs(fft_result)
            
            # Focus on positive frequencies
            positive_freq_mask = freqs > 0
            freqs = freqs[positive_freq_mask]
            magnitude = magnitude[positive_freq_mask]
            
            # Voice frequency ranges
            voice_mask = (freqs >= VOICE_FREQUENCY_MIN) & (freqs <= VOICE_FREQUENCY_MAX)
            formant1_mask = (freqs >= 200) & (freqs <= 1000)   # First formant
            formant2_mask = (freqs >= 1000) & (freqs <= 3000)  # Second formant
            formant3_mask = (freqs >= 2000) & (freqs <= 4000)  # Third formant
            
            if not np.any(voice_mask):
                return 0.0
            
            # Calculate energy in different bands
            total_energy = np.sum(magnitude**2)
            if total_energy == 0:
                return 0.0
                
            voice_energy = np.sum(magnitude[voice_mask]**2)
            formant1_energy = np.sum(magnitude[formant1_mask]**2)
            formant2_energy = np.sum(magnitude[formant2_mask]**2)
            formant3_energy = np.sum(magnitude[formant3_mask]**2)
            
            # Voice characteristics
            voice_ratio = voice_energy / total_energy
            formant_ratio = (formant1_energy + formant2_energy + formant3_energy) / total_energy
            
            # Spectral centroid (brightness)
            spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
            centroid_score = 1.0 if 200 <= spectral_centroid <= 2000 else 0.5
            
            # Combine scores
            spectral_score = (voice_ratio * 0.4 + formant_ratio * 0.4 + centroid_score * 0.2)
            
            return min(1.0, spectral_score)
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Spectral analysis error: {e}")
            return 0.0

    def _temporal_pattern_analysis(self, audio_float):
        """Analyze temporal patterns typical of human speech"""
        try:
            if len(audio_float) < 320:  # Need at least 20ms
                return 0.0
            
            # Zero crossing rate
            zcr = self._calculate_zcr(audio_float)
            zcr_score = 1.0 if MIN_ZERO_CROSSING_RATE <= zcr <= MAX_ZERO_CROSSING_RATE else 0.0
            
            # Energy variance (speech has varying energy)
            frame_size = 160  # 10ms frames
            frames = [audio_float[i:i+frame_size] for i in range(0, len(audio_float)-frame_size, frame_size)]
            if len(frames) < 2:
                return zcr_score * 0.5
            
            frame_energies = [np.sum(frame**2) for frame in frames]
            if np.mean(frame_energies) == 0:
                return 0.0
                
            energy_variance = np.var(frame_energies) / np.mean(frame_energies)
            variance_score = min(1.0, energy_variance / 0.5)  # Normalize
            
            # Temporal regularity (speech has some regularity but not too much)
            regularity_score = 1.0 - min(1.0, abs(energy_variance - 0.3) / 0.3)
            
            temporal_score = (zcr_score * 0.4 + variance_score * 0.3 + regularity_score * 0.3)
            
            return temporal_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Temporal analysis error: {e}")
            return 0.0

    def _voice_quality_analysis(self, audio_float):
        """Analyze overall voice quality indicators"""
        try:
            if len(audio_float) < 160:
                return 0.0
            
            # Signal-to-noise ratio estimation
            signal_power = np.mean(audio_float**2)
            if signal_power == 0:
                return 0.0
                
            # Estimate noise floor (bottom 10% of signal)
            sorted_power = np.sort(audio_float**2)
            noise_floor = np.mean(sorted_power[:len(sorted_power)//10])
            
            if noise_floor == 0:
                snr_score = 1.0
            else:
                snr = signal_power / noise_floor
                snr_score = min(1.0, np.log10(snr) / 2.0)  # Normalize SNR
            
            # Spectral flatness (voice is not flat)
            fft_result = fft(audio_float)
            magnitude = np.abs(fft_result)
            magnitude = magnitude[magnitude > 0]  # Remove zeros
            
            if len(magnitude) == 0:
                flatness_score = 0.0
            else:
                geometric_mean = np.exp(np.mean(np.log(magnitude)))
                arithmetic_mean = np.mean(magnitude)
                spectral_flatness = geometric_mean / arithmetic_mean
                flatness_score = 1.0 - min(1.0, spectral_flatness)  # Voice should not be flat
            
            # Combine quality indicators
            quality_score = (snr_score * 0.6 + flatness_score * 0.4)
            
            return quality_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Quality analysis error: {e}")
            return 0.0

    def _harmonic_analysis(self, audio_float):
        """Detect harmonic content typical of voice"""
        try:
            if len(audio_float) < 512:
                return 0.0
            
            # Autocorrelation for pitch detection
            correlation = np.correlate(audio_float, audio_float, mode='full')
            correlation = correlation[len(correlation)//2:]
            
            # Look for peaks in autocorrelation (pitch periods)
            min_pitch_samples = SAMPLE_RATE // MAX_PITCH_HZ
            max_pitch_samples = SAMPLE_RATE // MIN_PITCH_HZ
            
            if len(correlation) < max_pitch_samples:
                return 0.0
            
            search_range = correlation[min_pitch_samples:min(max_pitch_samples, len(correlation))]
            if len(search_range) == 0:
                return 0.0
            
            max_correlation = np.max(search_range)
            mean_correlation = np.mean(search_range)
            
            if mean_correlation == 0:
                harmonic_score = 0.0
            else:
                harmonic_score = (max_correlation - mean_correlation) / mean_correlation
                harmonic_score = min(1.0, harmonic_score / 2.0)  # Normalize
            
            return harmonic_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Harmonic analysis error: {e}")
            return 0.0

    def _noise_analysis(self, audio_float, volume):
        """Analyze noise characteristics"""
        try:
            # Compare to learned noise baseline
            if len(self.noise_samples) > 10:
                current_noise_baseline = np.percentile(self.noise_samples, 70)
            else:
                current_noise_baseline = self.noise_baseline
            
            # Noise ratio
            if current_noise_baseline == 0:
                noise_ratio = 1.0
            else:
                noise_ratio = min(1.0, volume / (current_noise_baseline * 3))
            
            # Adaptive scoring based on environment
            if self.environment_calibrated:
                # Well-calibrated environment
                noise_score = noise_ratio
            else:
                # Still learning environment - be more permissive
                noise_score = min(1.0, noise_ratio * 1.5)
            
            return noise_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Noise analysis error: {e}")
            return 0.5

    def _passes_noise_gate(self, audio_float, volume):
        """Advanced noise gate with adaptive threshold"""
        try:
            if not NOISE_GATE_ENABLED:
                return True
            
            # Adaptive noise gate threshold
            if len(self.noise_samples) > 10:
                noise_threshold = np.percentile(self.noise_samples, 80) * (1 + NOISE_GATE_THRESHOLD)
            else:
                noise_threshold = self.noise_baseline * (1 + NOISE_GATE_THRESHOLD)
            
            # Apply environment adaptation
            if self.environment_calibrated:
                if len(self.noise_samples) > 50:
                    avg_noise = np.mean(list(self.noise_samples)[-50:])
                    if avg_noise < 50:  # Quiet environment
                        noise_threshold *= QUIET_ENVIRONMENT_BONUS
                    elif avg_noise > 200:  # Noisy environment
                        noise_threshold *= NOISY_ENVIRONMENT_PENALTY
            
            return volume > noise_threshold
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Noise gate error: {e}")
            return True

    def _calculate_zcr(self, audio_float):
        """Calculate zero crossing rate"""
        try:
            signs = np.sign(audio_float)
            sign_changes = np.diff(signs)
            zero_crossings = np.sum(np.abs(sign_changes)) / 2
            zcr = zero_crossings / len(audio_float)
            return zcr
        except:
            return 0.0

    def _update_environment_calibration(self):
        """Update environment calibration"""
        try:
            # Calibrate for initial period
            if not self.environment_calibrated:
                elapsed = time.time() - self.calibration_start_time
                if elapsed > ENVIRONMENT_CALIBRATION_TIME or len(self.noise_samples) > 100:
                    self.environment_calibrated = True
                    if len(self.noise_samples) > 0:
                        self.noise_baseline = np.percentile(self.noise_samples, 70)
                    print(f"[VoiceAnalyzer] ✅ Environment calibrated: noise baseline {self.noise_baseline:.1f}")
            
            # Continuous adaptation
            if ADAPTIVE_NOISE_FLOOR and len(self.noise_samples) > 20:
                recent_noise = np.mean(list(self.noise_samples)[-20:])
                self.noise_baseline = (self.noise_baseline * (1 - NOISE_ADAPTATION_RATE) + 
                                     recent_noise * NOISE_ADAPTATION_RATE)
                
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Calibration error: {e}")

    def get_environment_stats(self):
        """Get environment and analysis statistics"""
        try:
            return {
                'noise_baseline': self.noise_baseline,
                'environment_calibrated': self.environment_calibrated,
                'noise_samples_count': len(self.noise_samples),
                'voice_samples_count': len(self.voice_samples),
                'recent_voice_avg': np.mean(self.recent_voice_scores) if self.recent_voice_scores else 0,
                'recent_noise_avg': np.mean(list(self.noise_samples)[-10:]) if len(self.noise_samples) >= 10 else self.noise_baseline,
                'calibration_time': time.time() - self.calibration_start_time
            }
        except:
            return {}

    # ✅ NEW: Fallback Analysis Methods (without numpy/scipy)
    
    def _spectral_voice_analysis_numpy(self, audio_float):
        """NumPy-based spectral analysis"""
        return self._spectral_voice_analysis(audio_float)
    
    def _spectral_voice_analysis_fallback(self, audio_chunk):
        """Fallback spectral analysis without scipy"""
        try:
            if len(audio_chunk) < 64:
                return 0.0
            
            # Simple spectral analysis using basic frequency detection
            # Count zero crossings as a proxy for frequency content
            zero_crossings = 0
            for i in range(1, len(audio_chunk)):
                if (audio_chunk[i-1] > 0) != (audio_chunk[i] > 0):
                    zero_crossings += 1
            
            # Estimate fundamental frequency from zero crossings
            sample_rate = 16000  # Assume 16kHz
            zcr = zero_crossings / len(audio_chunk)
            estimated_freq = zcr * sample_rate / 2
            
            # Voice frequency range check (80-1000 Hz for fundamental)
            if 80 <= estimated_freq <= 1000:
                freq_score = 1.0
            elif 50 <= estimated_freq <= 1500:
                freq_score = 0.7
            else:
                freq_score = 0.3
            
            # Energy distribution analysis
            chunk_size = len(audio_chunk) // 4
            if chunk_size > 0:
                quarters = []
                for i in range(4):
                    start = i * chunk_size
                    end = start + chunk_size
                    quarter_energy = sum(x*x for x in audio_chunk[start:end])
                    quarters.append(quarter_energy)
                
                # Voice typically has more energy in lower frequencies
                if quarters[0] > 0:
                    energy_ratio = quarters[0] / (sum(quarters) + 1)
                    energy_score = min(1.0, energy_ratio * 2)
                else:
                    energy_score = 0.0
            else:
                energy_score = 0.0
            
            # Combine scores
            spectral_score = (freq_score * 0.6 + energy_score * 0.4)
            return min(1.0, spectral_score)
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Fallback spectral analysis error: {e}")
            return 0.0
    
    def _temporal_pattern_analysis_numpy(self, audio_float):
        """NumPy-based temporal analysis"""
        return self._temporal_pattern_analysis(audio_float)
    
    def _temporal_pattern_analysis_fallback(self, audio_chunk):
        """Fallback temporal analysis without numpy"""
        try:
            if len(audio_chunk) < 160:  # Need at least 10ms at 16kHz
                return 0.0
            
            # Calculate zero crossing rate manually
            zero_crossings = 0
            for i in range(1, len(audio_chunk)):
                if (audio_chunk[i-1] > 0) != (audio_chunk[i] > 0):
                    zero_crossings += 1
            
            zcr = zero_crossings / len(audio_chunk)
            
            # Voice ZCR is typically 0.01-0.30
            if 0.01 <= zcr <= 0.30:
                zcr_score = 1.0
            elif 0.005 <= zcr <= 0.50:
                zcr_score = 0.7
            else:
                zcr_score = 0.3
            
            # Energy variance analysis
            frame_size = 160  # 10ms frames at 16kHz
            frame_energies = []
            for i in range(0, len(audio_chunk) - frame_size, frame_size):
                frame = audio_chunk[i:i+frame_size]
                energy = sum(x*x for x in frame)
                frame_energies.append(energy)
            
            if len(frame_energies) >= 2:
                mean_energy = fallback_mean(frame_energies)
                if mean_energy > 0:
                    variance = fallback_variance(frame_energies)
                    normalized_variance = variance / (mean_energy * mean_energy)
                    variance_score = min(1.0, normalized_variance)
                else:
                    variance_score = 0.0
            else:
                variance_score = 0.5
            
            # Combine temporal scores
            temporal_score = (zcr_score * 0.6 + variance_score * 0.4)
            return temporal_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Fallback temporal analysis error: {e}")
            return 0.0
    
    def _voice_quality_analysis_numpy(self, audio_float):
        """NumPy-based quality analysis"""
        return self._voice_quality_analysis(audio_float)
    
    def _voice_quality_analysis_fallback(self, audio_chunk):
        """Fallback quality analysis without numpy"""
        try:
            if len(audio_chunk) < 160:
                return 0.0
            
            # Simple SNR estimation
            signal_power = sum(x*x for x in audio_chunk) / len(audio_chunk)
            if signal_power == 0:
                return 0.0
            
            # Estimate noise floor from quietest 10% of samples
            sorted_abs = sorted(abs(x) for x in audio_chunk)
            noise_samples = sorted_abs[:len(sorted_abs)//10]
            if noise_samples:
                noise_power = sum(x*x for x in noise_samples) / len(noise_samples)
                
                if noise_power > 0:
                    snr = signal_power / noise_power
                    snr_score = min(1.0, math.log10(snr + 1) / 3.0)  # Normalize
                else:
                    snr_score = 1.0
            else:
                snr_score = 0.5
            
            # Dynamic range analysis
            max_val = max(abs(x) for x in audio_chunk)
            min_val = min(abs(x) for x in audio_chunk)
            if max_val > 0:
                dynamic_range = (max_val - min_val) / max_val
                range_score = min(1.0, dynamic_range)
            else:
                range_score = 0.0
            
            # Combine quality indicators
            quality_score = (snr_score * 0.7 + range_score * 0.3)
            return quality_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Fallback quality analysis error: {e}")
            return 0.0
    
    def _simple_harmonic_analysis(self, audio_chunk):
        """Simple harmonic analysis without complex FFT"""
        try:
            if len(audio_chunk) < 320:  # Need at least 20ms
                return 0.0
            
            # Simple pitch detection using autocorrelation-like approach
            # Look for repetitive patterns
            max_correlation = 0.0
            best_period = 0
            
            # Check for periods between 50-400 Hz (samples at 16kHz)
            min_period = 16000 // 400  # ~40 samples
            max_period = 16000 // 50   # ~320 samples
            
            for period in range(min_period, min(max_period, len(audio_chunk)//2)):
                correlation = 0.0
                count = 0
                
                for i in range(period, len(audio_chunk) - period):
                    correlation += audio_chunk[i] * audio_chunk[i - period]
                    count += 1
                
                if count > 0:
                    correlation /= count
                    if correlation > max_correlation:
                        max_correlation = correlation
                        best_period = period
            
            # Estimate harmonicity
            if max_correlation > 0:
                # Normalize by signal power
                signal_power = sum(x*x for x in audio_chunk) / len(audio_chunk)
                if signal_power > 0:
                    harmonic_score = min(1.0, max_correlation / signal_power)
                else:
                    harmonic_score = 0.0
            else:
                harmonic_score = 0.0
            
            return harmonic_score
            
        except Exception as e:
            if DEBUG:
                print(f"[VoiceAnalyzer] Simple harmonic analysis error: {e}")
            return 0.0
    
    def _simple_noise_analysis(self, volume):
        """Simple noise analysis based on volume patterns"""
        try:
            # Compare current volume to noise baseline
            if volume <= self.noise_baseline:
                return 0.8  # Likely noise
            elif volume <= self.noise_baseline * 2:
                return 0.6  # Possibly noise
            elif volume <= self.noise_baseline * 5:
                return 0.4  # Likely signal
            else:
                return 0.2  # Definitely signal
                
        except Exception as e:
            return 0.5  # Neutral score on error

    # ✅ NEW: Room-Scale Detection Methods
    
    def analyze_with_distance_adaptation(self, audio_chunk, is_buddy_speaking=False):
        """
        Enhanced analysis with distance-adaptive thresholds for room-scale detection
        Returns: (is_voice, quality_score, detailed_scores, detected_distance)
        """
        try:
            # First run standard analysis
            is_voice, quality_score, detailed_scores = self.analyze_audio_chunk(audio_chunk, is_buddy_speaking)
            
            if not self.distance_adaptive_mode:
                return is_voice, quality_score, detailed_scores, "unknown"
            
            # Extract volume for distance estimation
            volume = detailed_scores.get('volume', 0)
            
            # Determine likely distance tier based on volume and quality
            detected_distance = self._estimate_speaker_distance(volume, quality_score, detailed_scores)
            
            # Apply distance-appropriate thresholds
            distance_tier = self.detection_tiers.get(detected_distance, self.detection_tiers['room'])
            
            # Check if audio meets distance-appropriate criteria
            volume_threshold = distance_tier['volume']
            quality_threshold = distance_tier['quality']
            spectral_threshold = distance_tier.get('spectral', 0.2)
            
            spectral_score = detailed_scores.get('spectral_voice_score', 0)
            
            # Apply auto-gain control for distant speech
            if self.auto_gain_enabled and detected_distance in ['far', 'room']:
                volume, quality_score, spectral_score = self._apply_auto_gain_control(
                    volume, quality_score, spectral_score, detected_distance
                )
            
            # Smart background rejection
            if self.background_rejection_enabled:
                is_background = self._detect_background_audio(audio_chunk, detailed_scores)
                if is_background:
                    return False, 0.0, {**detailed_scores, 'rejection_reason': 'background_audio'}, detected_distance
            
            # Multi-speaker rejection
            if self.multi_speaker_rejection:
                is_other_speaker = self._detect_other_speaker(audio_chunk, detailed_scores)
                if is_other_speaker:
                    return False, 0.0, {**detailed_scores, 'rejection_reason': 'other_speaker'}, detected_distance
            
            # Media audio filtering
            if self.media_audio_filtering:
                is_media = self._detect_media_audio(audio_chunk, detailed_scores)
                if is_media:
                    return False, 0.0, {**detailed_scores, 'rejection_reason': 'media_audio'}, detected_distance
            
            # Distance-adaptive voice detection
            is_voice_distance = (volume >= volume_threshold and 
                               quality_score >= quality_threshold and 
                               spectral_score >= spectral_threshold)
            
            # Combine with original detection (OR logic for better sensitivity)
            final_is_voice = is_voice or is_voice_distance
            
            # Update detailed scores with distance information
            enhanced_scores = {
                **detailed_scores,
                'detected_distance': detected_distance,
                'distance_tier': distance_tier,
                'volume_threshold_met': volume >= volume_threshold,
                'quality_threshold_met': quality_score >= quality_threshold,
                'spectral_threshold_met': spectral_score >= spectral_threshold,
                'auto_gain_applied': self.auto_gain_enabled and detected_distance in ['far', 'room'],
                'background_rejected': False,
                'media_rejected': False,
                'other_speaker_rejected': False
            }
            
            return final_is_voice, quality_score, enhanced_scores, detected_distance
            
        except Exception as e:
            print(f"[VoiceAnalyzer] ❌ Distance adaptation error: {e}")
            return is_voice, quality_score, detailed_scores, "unknown"

    def _estimate_speaker_distance(self, volume, quality_score, detailed_scores):
        """Estimate speaker distance based on audio characteristics"""
        try:
            # Volume-based distance estimation
            if volume >= 800:
                return "close"
            elif volume >= 400:
                return "medium"
            elif volume >= 200:
                return "far"
            else:
                return "room"
                
        except Exception as e:
            return "room"

    def _apply_auto_gain_control(self, volume, quality_score, spectral_score, distance):
        """Apply auto-gain control for distant speech"""
        try:
            if distance == "far":
                gain_factor = 1.5
            elif distance == "room":
                gain_factor = 2.0
            else:
                gain_factor = 1.0
            
            # Apply gain with saturation protection
            enhanced_volume = min(volume * gain_factor, 5000)
            enhanced_quality = min(quality_score * 1.2, 1.0)
            enhanced_spectral = min(spectral_score * 1.1, 1.0)
            
            # Track gain history
            self.gain_history.append(gain_factor)
            
            return enhanced_volume, enhanced_quality, enhanced_spectral
            
        except Exception as e:
            return volume, quality_score, spectral_score

    def _detect_background_audio(self, audio_chunk, detailed_scores):
        """Detect if audio is background noise/conversation"""
        try:
            # Simple background detection based on patterns
            volume = detailed_scores.get('volume', 0)
            quality = detailed_scores.get('combined', 0)
            
            # Very consistent volume levels suggest background noise
            self.background_patterns.append(volume)
            
            if len(self.background_patterns) >= 10:
                recent_volumes = list(self.background_patterns)[-10:]
                volume_variance = np.var(recent_volumes)
                
                # Low variance + moderate volume = likely background
                if volume_variance < 50 and 100 < np.mean(recent_volumes) < 400:
                    return True
            
            return False
            
        except Exception as e:
            return False

    def _detect_other_speaker(self, audio_chunk, detailed_scores):
        """Detect if speaker is different from primary user"""
        try:
            if not self.voice_fingerprint_matching or not self.primary_user_voice_profile:
                return False
            
            # Simple speaker verification based on spectral characteristics
            spectral_score = detailed_scores.get('spectral_voice_score', 0)
            quality_score = detailed_scores.get('combined', 0)
            
            # If we have a primary user profile, check similarity
            # This is a simplified implementation - in practice would use speaker recognition
            if hasattr(self, 'primary_user_spectral_signature'):
                current_signature = (spectral_score, quality_score)
                similarity = self._calculate_voice_similarity(current_signature, self.primary_user_spectral_signature)
                
                # If similarity is too low, might be different speaker
                if similarity < 0.3:
                    return True
            
            return False
            
        except Exception as e:
            return False

    def _detect_media_audio(self, audio_chunk, detailed_scores):
        """Detect TV/music/media audio patterns"""
        try:
            # Media audio often has different characteristics than live speech
            spectral_score = detailed_scores.get('spectral_voice_score', 0)
            harmonic_score = detailed_scores.get('harmonic_score', 0)
            
            # High harmonic content with moderate spectral score suggests music
            if harmonic_score > 0.7 and spectral_score < 0.4:
                return True
            
            # Very consistent patterns suggest media playback
            self.media_audio_patterns.append((spectral_score, harmonic_score))
            
            if len(self.media_audio_patterns) >= 5:
                recent_patterns = list(self.media_audio_patterns)[-5:]
                spectral_variance = np.var([p[0] for p in recent_patterns])
                harmonic_variance = np.var([p[1] for p in recent_patterns])
                
                # Very low variance in both suggests processed audio (TV/media)
                if spectral_variance < 0.01 and harmonic_variance < 0.01:
                    return True
            
            return False
            
        except Exception as e:
            return False

    def _calculate_voice_similarity(self, signature1, signature2):
        """Calculate similarity between voice signatures"""
        try:
            # Simple cosine similarity for demonstration
            s1 = np.array(signature1)
            s2 = np.array(signature2)
            
            norm1 = np.linalg.norm(s1)
            norm2 = np.linalg.norm(s2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = np.dot(s1, s2) / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            return 0.0

    def set_primary_user_voice_profile(self, audio_samples):
        """Set the primary user's voice profile for fingerprinting"""
        try:
            if not audio_samples:
                return False
            
            # Analyze samples to create voice signature
            signatures = []
            for sample in audio_samples:
                is_voice, quality, details = self.analyze_audio_chunk(sample)
                if is_voice and quality > 0.3:
                    spectral_score = details.get('spectral_voice_score', 0)
                    signatures.append((spectral_score, quality))
            
            if signatures:
                # Create average signature
                avg_spectral = np.mean([s[0] for s in signatures])
                avg_quality = np.mean([s[1] for s in signatures])
                self.primary_user_spectral_signature = (avg_spectral, avg_quality)
                
                print(f"[VoiceAnalyzer] ✅ Primary user voice profile set from {len(signatures)} samples")
                return True
            
            return False
            
        except Exception as e:
            print(f"[VoiceAnalyzer] ❌ Error setting voice profile: {e}")
            return False

    def learn_environmental_noise(self, audio_chunk):
        """Learn environmental noise patterns for better rejection"""
        try:
            volume = np.abs(audio_chunk).mean()
            
            # Update environmental noise profile
            if 'average_noise' not in self.environmental_noise_profile:
                self.environmental_noise_profile['average_noise'] = volume
                self.environmental_noise_profile['noise_samples'] = 1
            else:
                # Running average
                current_avg = self.environmental_noise_profile['average_noise']
                sample_count = self.environmental_noise_profile['noise_samples']
                
                new_avg = (current_avg * sample_count + volume) / (sample_count + 1)
                self.environmental_noise_profile['average_noise'] = new_avg
                self.environmental_noise_profile['noise_samples'] = sample_count + 1
            
            # Update noise baseline
            if volume < self.noise_baseline * 2:  # Only learn from quiet periods
                self.noise_samples.append(volume)
                if len(self.noise_samples) >= 50:
                    self.noise_baseline = np.percentile(list(self.noise_samples), 75)
            
        except Exception as e:
            pass  # Silent failure for noise learning

    def get_room_scale_stats(self):
        """Get statistics for room-scale detection system"""
        try:
            stats = self.get_stats()
            
            # Add room-scale specific stats
            stats.update({
                'distance_adaptive_mode': self.distance_adaptive_mode,
                'background_rejection_enabled': self.background_rejection_enabled,
                'voice_fingerprint_matching': self.voice_fingerprint_matching,
                'detection_tiers': len(self.detection_tiers),
                'background_patterns_learned': len(self.background_patterns),
                'media_patterns_learned': len(self.media_audio_patterns),
                'auto_gain_history': list(self.gain_history) if self.gain_history else [],
                'environmental_noise_profile': self.environmental_noise_profile,
                'primary_user_profile_set': hasattr(self, 'primary_user_spectral_signature')
            })
            
            return stats
            
        except Exception as e:
            return self.get_stats()

# Create global instance
try:
    voice_analyzer = AdvancedVoiceAnalyzer()
    print("[VoiceAnalyzer] ✅ Global voice analyzer created")
except Exception as e:
    print(f"[VoiceAnalyzer] ❌ Error creating voice analyzer: {e}")
    voice_analyzer = None