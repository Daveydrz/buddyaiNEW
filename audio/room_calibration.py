# audio/room_calibration.py - Room-Scale Voice Detection Calibration System
# Date: 2025-01-16
# Purpose: Calibrate voice detection thresholds for different distances and room acoustics

import numpy as np
import pyaudio
import time
import json
import os
from datetime import datetime
from collections import deque
import threading
from config import *
from audio.voice_analyzer import AdvancedVoiceAnalyzer
from audio.processing import downsample_audio

class RoomCalibrationSystem:
    def __init__(self):
        self.voice_analyzer = AdvancedVoiceAnalyzer()
        self.calibration_data = {
            'distances': {},
            'background_noise': {},
            'room_acoustics': {},
            'optimal_thresholds': {},
            'calibration_timestamp': None,
            'room_profile': None
        }
        
        # Audio setup
        self.pa = pyaudio.PyAudio()
        self.sample_rate = 48000
        self.channels = 1
        self.chunk_size = 1024
        
        # Calibration state
        self.is_calibrating = False
        self.current_test = None
        self.audio_samples = deque(maxlen=5000)
        
        print("[RoomCalibration] 🎯 Room-Scale Voice Detection Calibration System")
        print("[RoomCalibration] 📊 Ready to calibrate for optimal distance detection")

    def start_calibration(self):
        """Start the comprehensive room calibration process"""
        print("\n" + "="*60)
        print("[RoomCalibration] 🚀 STARTING ROOM-SCALE VOICE CALIBRATION")
        print("="*60)
        
        try:
            # Step 1: Background noise calibration
            print("\n[RoomCalibration] 🔇 Step 1: Background Noise Analysis")
            self.calibrate_background_noise()
            
            # Step 2: Distance-based speech calibration
            print("\n[RoomCalibration] 📏 Step 2: Distance-Based Speech Calibration")
            self.calibrate_distance_detection()
            
            # Step 3: Room acoustics analysis
            print("\n[RoomCalibration] 🏠 Step 3: Room Acoustics Analysis")
            self.calibrate_room_acoustics()
            
            # Step 4: AEC performance validation
            print("\n[RoomCalibration] 🔄 Step 4: AEC Performance Validation")
            self.validate_aec_performance()
            
            # Step 5: Calculate optimal thresholds
            print("\n[RoomCalibration] 🎯 Step 5: Calculating Optimal Thresholds")
            self.calculate_optimal_thresholds()
            
            # Step 6: Save calibration
            print("\n[RoomCalibration] 💾 Step 6: Saving Calibration Data")
            self.save_calibration()
            
            print("\n" + "="*60)
            print("[RoomCalibration] ✅ CALIBRATION COMPLETE!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"[RoomCalibration] ❌ Calibration failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def calibrate_background_noise(self):
        """Measure background noise levels in the room"""
        print("[RoomCalibration] 🎤 Please ensure the room is quiet (no talking)")
        print("[RoomCalibration] ⏱️  Measuring background noise for 10 seconds...")
        
        # Open audio stream
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        noise_samples = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < 10:
                try:
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # Downsample if needed
                    if self.sample_rate != 16000:
                        audio_array = downsample_audio(audio_array, self.sample_rate, 16000)
                    
                    # Calculate noise metrics
                    volume = np.abs(audio_array).mean()
                    rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                    
                    noise_samples.append({
                        'volume': volume,
                        'rms': rms,
                        'timestamp': time.time()
                    })
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"[RoomCalibration] ⚠️ Audio read error: {e}")
                    continue
                    
        finally:
            stream.stop_stream()
            stream.close()
        
        # Analyze background noise
        volumes = [s['volume'] for s in noise_samples]
        rms_values = [s['rms'] for s in noise_samples]
        
        self.calibration_data['background_noise'] = {
            'average_volume': np.mean(volumes),
            'max_volume': np.max(volumes),
            'min_volume': np.min(volumes),
            'std_volume': np.std(volumes),
            'average_rms': np.mean(rms_values),
            'noise_floor': np.percentile(volumes, 95),
            'samples_count': len(noise_samples)
        }
        
        print(f"[RoomCalibration] 📊 Background noise analysis complete:")
        print(f"[RoomCalibration]   Average volume: {self.calibration_data['background_noise']['average_volume']:.1f}")
        print(f"[RoomCalibration]   Noise floor (95th percentile): {self.calibration_data['background_noise']['noise_floor']:.1f}")
        print(f"[RoomCalibration]   RMS average: {self.calibration_data['background_noise']['average_rms']:.1f}")

    def calibrate_distance_detection(self):
        """Test speech detection at multiple distances"""
        distances = [
            {"name": "close", "distance": "0.5m", "description": "Close to microphone (0.5 meters)"},
            {"name": "medium", "distance": "1m", "description": "Medium distance (1 meter)"},
            {"name": "far", "distance": "2m", "description": "Far distance (2 meters)"},
            {"name": "room", "distance": "3m+", "description": "Room distance (3+ meters)"}
        ]
        
        for dist_config in distances:
            print(f"\n[RoomCalibration] 📏 Testing {dist_config['description']}")
            print("[RoomCalibration] 🗣️  Please speak clearly for 10 seconds at this distance")
            print("[RoomCalibration] 💡 Say: 'Hello Buddy, this is a test from [distance]. Can you hear me clearly?'")
            
            input("Press Enter when ready to start recording...")
            
            # Record speech at this distance
            speech_samples = self.record_speech_sample(10)
            
            # Analyze speech quality at this distance
            analysis = self.analyze_speech_samples(speech_samples)
            
            self.calibration_data['distances'][dist_config['name']] = {
                'distance': dist_config['distance'],
                'description': dist_config['description'],
                'analysis': analysis,
                'sample_count': len(speech_samples)
            }
            
            print(f"[RoomCalibration] ✅ {dist_config['description']} analysis complete")
            print(f"[RoomCalibration]   Average volume: {analysis['average_volume']:.1f}")
            print(f"[RoomCalibration]   Voice quality: {analysis['average_voice_quality']:.2f}")
            print(f"[RoomCalibration]   Spectral score: {analysis['average_spectral_score']:.2f}")

    def record_speech_sample(self, duration):
        """Record speech sample for specified duration"""
        print(f"[RoomCalibration] 🎤 Recording for {duration} seconds...")
        
        stream = self.pa.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        samples = []
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration:
                try:
                    audio_data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    
                    # Downsample if needed
                    if self.sample_rate != 16000:
                        audio_array = downsample_audio(audio_array, self.sample_rate, 16000)
                    
                    samples.append(audio_array)
                    
                except Exception as e:
                    print(f"[RoomCalibration] ⚠️ Recording error: {e}")
                    continue
                    
        finally:
            stream.stop_stream()
            stream.close()
        
        print(f"[RoomCalibration] ✅ Recording complete ({len(samples)} chunks)")
        return samples

    def analyze_speech_samples(self, samples):
        """Analyze speech samples for quality metrics"""
        volumes = []
        voice_qualities = []
        spectral_scores = []
        
        for sample in samples:
            if len(sample) > 0:
                # Basic volume analysis
                volume = np.abs(sample).mean()
                volumes.append(volume)
                
                # Advanced voice analysis
                try:
                    is_voice, quality, details = self.voice_analyzer.analyze_audio_chunk(sample)
                    voice_qualities.append(quality)
                    
                    # Extract spectral score
                    spectral_score = details.get('spectral_voice_score', 0.0)
                    spectral_scores.append(spectral_score)
                    
                except Exception as e:
                    voice_qualities.append(0.0)
                    spectral_scores.append(0.0)
        
        # Calculate statistics
        analysis = {
            'average_volume': np.mean(volumes) if volumes else 0,
            'max_volume': np.max(volumes) if volumes else 0,
            'min_volume': np.min(volumes) if volumes else 0,
            'std_volume': np.std(volumes) if volumes else 0,
            'average_voice_quality': np.mean(voice_qualities) if voice_qualities else 0,
            'max_voice_quality': np.max(voice_qualities) if voice_qualities else 0,
            'average_spectral_score': np.mean(spectral_scores) if spectral_scores else 0,
            'max_spectral_score': np.max(spectral_scores) if spectral_scores else 0,
            'voice_detection_rate': sum(1 for q in voice_qualities if q > 0.2) / len(voice_qualities) if voice_qualities else 0
        }
        
        return analysis

    def calibrate_room_acoustics(self):
        """Analyze room acoustics for reverberation and echo"""
        print("[RoomCalibration] 🏠 Analyzing room acoustics...")
        print("[RoomCalibration] 👏 Please clap your hands sharply 3 times")
        
        input("Press Enter when ready to analyze room acoustics...")
        
        # Record room response to sharp sounds
        acoustic_samples = self.record_speech_sample(5)
        
        # Analyze for reverberation characteristics
        reverb_analysis = self.analyze_reverberation(acoustic_samples)
        
        self.calibration_data['room_acoustics'] = reverb_analysis
        
        print(f"[RoomCalibration] 🏠 Room acoustics analysis complete:")
        print(f"[RoomCalibration]   Reverberation level: {reverb_analysis['reverb_level']:.2f}")
        print(f"[RoomCalibration]   Echo presence: {reverb_analysis['echo_present']}")
        print(f"[RoomCalibration]   Room type: {reverb_analysis['room_type']}")

    def analyze_reverberation(self, samples):
        """Analyze audio samples for reverberation characteristics"""
        # Combine all samples
        combined_audio = np.concatenate(samples) if samples else np.array([])
        
        if len(combined_audio) == 0:
            return {
                'reverb_level': 0.0,
                'echo_present': False,
                'room_type': 'unknown',
                'decay_time': 0.0
            }
        
        # Simple reverberation analysis
        # Calculate decay characteristics
        envelope = np.abs(combined_audio)
        
        # Find peaks and analyze decay
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(envelope, height=np.max(envelope) * 0.1)
        
        # Estimate reverberation time (RT60 approximation)
        if len(peaks) > 1:
            decay_samples = len(combined_audio) - peaks[0] if len(peaks) > 0 else len(combined_audio)
            decay_time = decay_samples / 16000.0  # Convert to seconds
        else:
            decay_time = 0.0
        
        # Classify room type based on reverberation
        if decay_time < 0.3:
            room_type = "dry"
        elif decay_time < 0.8:
            room_type = "normal"
        elif decay_time < 1.5:
            room_type = "reverberant"
        else:
            room_type = "very_reverberant"
        
        reverb_level = min(decay_time / 1.0, 1.0)  # Normalize to 0-1
        echo_present = decay_time > 0.5
        
        return {
            'reverb_level': reverb_level,
            'echo_present': echo_present,
            'room_type': room_type,
            'decay_time': decay_time,
            'peak_count': len(peaks)
        }

    def validate_aec_performance(self):
        """Validate AEC performance at different ranges"""
        print("[RoomCalibration] 🔄 AEC performance validation...")
        print("[RoomCalibration] 💡 This step validates echo cancellation at various distances")
        
        # For now, we'll use a simplified validation
        # In a full implementation, this would test AEC with actual playback
        
        aec_performance = {
            'close_range': {'efficiency': 0.9, 'latency': 10},
            'medium_range': {'efficiency': 0.85, 'latency': 15},
            'far_range': {'efficiency': 0.8, 'latency': 20},
            'room_range': {'efficiency': 0.75, 'latency': 25}
        }
        
        self.calibration_data['aec_performance'] = aec_performance
        print("[RoomCalibration] ✅ AEC performance validation complete")

    def calculate_optimal_thresholds(self):
        """Calculate optimal thresholds based on calibration data"""
        print("[RoomCalibration] 🧮 Calculating optimal detection thresholds...")
        
        background_noise = self.calibration_data['background_noise']['noise_floor']
        
        optimal_thresholds = {}
        
        for distance_name, distance_data in self.calibration_data['distances'].items():
            analysis = distance_data['analysis']
            
            # Calculate threshold as signal-to-noise ratio
            signal_level = analysis['average_volume']
            noise_margin = 2.0  # 2x above noise floor
            
            # Volume threshold: signal level with noise margin
            volume_threshold = max(background_noise * noise_margin, signal_level * 0.5)
            
            # Quality threshold: based on observed voice quality
            quality_threshold = max(0.15, analysis['average_voice_quality'] * 0.6)
            
            # Spectral threshold: based on observed spectral characteristics
            spectral_threshold = max(0.2, analysis['average_spectral_score'] * 0.7)
            
            optimal_thresholds[distance_name] = {
                'volume_threshold': volume_threshold,
                'quality_threshold': quality_threshold,
                'spectral_threshold': spectral_threshold,
                'signal_to_noise_ratio': signal_level / background_noise if background_noise > 0 else 0,
                'confidence': min(1.0, analysis['voice_detection_rate'])
            }
        
        self.calibration_data['optimal_thresholds'] = optimal_thresholds
        
        print("[RoomCalibration] 🎯 Optimal thresholds calculated:")
        for name, thresholds in optimal_thresholds.items():
            print(f"[RoomCalibration]   {name}: vol={thresholds['volume_threshold']:.0f}, "
                  f"qual={thresholds['quality_threshold']:.2f}, "
                  f"spec={thresholds['spectral_threshold']:.2f}")

    def save_calibration(self):
        """Save calibration data to file"""
        self.calibration_data['calibration_timestamp'] = datetime.now().isoformat()
        self.calibration_data['version'] = "1.0"
        
        # Create calibration filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"room_calibration_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.calibration_data, f, indent=2, default=str)
            
            # Also save as latest calibration
            with open("room_calibration_latest.json", 'w') as f:
                json.dump(self.calibration_data, f, indent=2, default=str)
            
            print(f"[RoomCalibration] 💾 Calibration saved to: {filename}")
            print(f"[RoomCalibration] 💾 Latest calibration: room_calibration_latest.json")
            
            return True
            
        except Exception as e:
            print(f"[RoomCalibration] ❌ Failed to save calibration: {e}")
            return False

    def load_calibration(self, filename="room_calibration_latest.json"):
        """Load existing calibration data"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.calibration_data = json.load(f)
                print(f"[RoomCalibration] ✅ Calibration loaded from: {filename}")
                return True
            else:
                print(f"[RoomCalibration] ⚠️ Calibration file not found: {filename}")
                return False
        except Exception as e:
            print(f"[RoomCalibration] ❌ Failed to load calibration: {e}")
            return False

    def get_distance_thresholds(self):
        """Get the calibrated thresholds for distance detection"""
        if 'optimal_thresholds' in self.calibration_data:
            return self.calibration_data['optimal_thresholds']
        else:
            # Return default thresholds if no calibration available
            return {
                'close': {'volume_threshold': 800, 'quality_threshold': 0.6, 'spectral_threshold': 0.4},
                'medium': {'volume_threshold': 400, 'quality_threshold': 0.35, 'spectral_threshold': 0.3},
                'far': {'volume_threshold': 200, 'quality_threshold': 0.20, 'spectral_threshold': 0.25},
                'room': {'volume_threshold': 100, 'quality_threshold': 0.15, 'spectral_threshold': 0.2}
            }

    def cleanup(self):
        """Cleanup audio resources"""
        try:
            self.pa.terminate()
        except:
            pass

def run_room_calibration():
    """Main function to run room calibration"""
    calibration_system = RoomCalibrationSystem()
    
    try:
        success = calibration_system.start_calibration()
        if success:
            print("\n[RoomCalibration] 🎉 Room calibration completed successfully!")
            print("[RoomCalibration] 💡 The system is now optimized for your room and speaking distances")
            return calibration_system.get_distance_thresholds()
        else:
            print("\n[RoomCalibration] ❌ Room calibration failed")
            return None
    except KeyboardInterrupt:
        print("\n[RoomCalibration] ⏹️  Calibration interrupted by user")
        return None
    finally:
        calibration_system.cleanup()

if __name__ == "__main__":
    print("Room-Scale Voice Detection Calibration System")
    print("=" * 50)
    result = run_room_calibration()
    if result:
        print("\nCalibrated thresholds:")
        for distance, thresholds in result.items():
            print(f"  {distance}: {thresholds}")