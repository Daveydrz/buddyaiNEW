# audio/room_calibration_simple.py - Simplified Room Calibration without external dependencies
# Date: 2025-01-16
# Purpose: Basic room calibration for systems without numpy/scipy

import time
import json
import os
from datetime import datetime
from collections import deque

class SimpleRoomCalibrationSystem:
    def __init__(self):
        self.calibration_data = {
            'distances': {},
            'background_noise': {},
            'room_acoustics': {},
            'optimal_thresholds': {},
            'calibration_timestamp': None,
            'room_profile': None,
            'simple_mode': True
        }
        
        print("[SimpleRoomCalibration] 🎯 Simple Room-Scale Voice Detection Calibration")
        print("[SimpleRoomCalibration] 💡 This simplified version works without external dependencies")
        print("[SimpleRoomCalibration] 📊 Manual threshold adjustment based on user feedback")

    def start_simple_calibration(self):
        """Start simplified calibration process based on user input"""
        print("\n" + "="*60)
        print("[SimpleRoomCalibration] 🚀 STARTING SIMPLE ROOM CALIBRATION")
        print("="*60)
        
        try:
            # Step 1: Background noise assessment
            print("\n[SimpleRoomCalibration] 🔇 Step 1: Background Noise Assessment")
            self.assess_background_noise()
            
            # Step 2: Distance-based testing
            print("\n[SimpleRoomCalibration] 📏 Step 2: Distance Testing")
            self.test_distance_ranges()
            
            # Step 3: Calculate recommended thresholds
            print("\n[SimpleRoomCalibration] 🎯 Step 3: Calculating Recommended Thresholds")
            self.calculate_simple_thresholds()
            
            # Step 4: Save calibration
            print("\n[SimpleRoomCalibration] 💾 Step 4: Saving Calibration")
            self.save_simple_calibration()
            
            print("\n" + "="*60)
            print("[SimpleRoomCalibration] ✅ SIMPLE CALIBRATION COMPLETE!")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"[SimpleRoomCalibration] ❌ Calibration failed: {e}")
            return False

    def assess_background_noise(self):
        """Assess background noise through user input"""
        print("[SimpleRoomCalibration] 🎤 Please assess your room's background noise level:")
        print("1. Very Quiet (library-like, minimal noise)")
        print("2. Quiet (typical home environment)")
        print("3. Moderate (some ambient noise, TV in background)")
        print("4. Noisy (busy environment, multiple sounds)")
        
        while True:
            try:
                choice = input("Enter your choice (1-4): ").strip()
                if choice in ['1', '2', '3', '4']:
                    break
                print("Please enter a number between 1 and 4.")
            except KeyboardInterrupt:
                raise
            except:
                print("Invalid input. Please enter a number between 1 and 4.")
        
        noise_levels = {
            '1': {'level': 'very_quiet', 'base_threshold_multiplier': 0.5, 'noise_floor': 30},
            '2': {'level': 'quiet', 'base_threshold_multiplier': 1.0, 'noise_floor': 60},
            '3': {'level': 'moderate', 'base_threshold_multiplier': 1.5, 'noise_floor': 120},
            '4': {'level': 'noisy', 'base_threshold_multiplier': 2.0, 'noise_floor': 200}
        }
        
        selected = noise_levels[choice]
        self.calibration_data['background_noise'] = selected
        
        print(f"[SimpleRoomCalibration] 📊 Room noise level: {selected['level']}")
        print(f"[SimpleRoomCalibration] 🎯 Base threshold multiplier: {selected['base_threshold_multiplier']}")

    def test_distance_ranges(self):
        """Test voice detection at different distances through user feedback"""
        distances = [
            {"name": "close", "distance": "0.5m", "description": "Close to microphone (arm's length)"},
            {"name": "medium", "distance": "1-2m", "description": "Across a desk or small room"},
            {"name": "far", "distance": "2-3m", "description": "Across a large room"},
            {"name": "room", "distance": "3m+", "description": "From another room or very far"}
        ]
        
        for dist_config in distances:
            print(f"\n[SimpleRoomCalibration] 📏 Testing {dist_config['description']}")
            print(f"[SimpleRoomCalibration] 🗣️ Please move to {dist_config['distance']} from your microphone")
            print("[SimpleRoomCalibration] 💬 Say: 'Hello Buddy, testing from [distance]'")
            
            input("Press Enter when you've tested speaking from this distance...")
            
            print("[SimpleRoomCalibration] 📊 How well did the system detect your voice?")
            print("1. Excellent (always detected, clear)")
            print("2. Good (mostly detected)")
            print("3. Fair (sometimes detected)")
            print("4. Poor (rarely detected)")
            print("5. Failed (never detected)")
            
            while True:
                try:
                    quality = input("Enter quality rating (1-5): ").strip()
                    if quality in ['1', '2', '3', '4', '5']:
                        break
                    print("Please enter a number between 1 and 5.")
                except KeyboardInterrupt:
                    raise
                except:
                    print("Invalid input. Please enter a number between 1 and 5.")
            
            quality_scores = {
                '1': {'score': 0.9, 'confidence': 'high'},
                '2': {'score': 0.7, 'confidence': 'good'},
                '3': {'score': 0.5, 'confidence': 'medium'},
                '4': {'score': 0.3, 'confidence': 'low'},
                '5': {'score': 0.1, 'confidence': 'very_low'}
            }
            
            result = quality_scores[quality]
            self.calibration_data['distances'][dist_config['name']] = {
                'distance': dist_config['distance'],
                'description': dist_config['description'],
                'user_rating': int(quality),
                'quality_score': result['score'],
                'confidence': result['confidence']
            }
            
            print(f"[SimpleRoomCalibration] ✅ {dist_config['description']} rated as: {result['confidence']}")

    def calculate_simple_thresholds(self):
        """Calculate optimal thresholds based on user feedback"""
        print("[SimpleRoomCalibration] 🧮 Calculating optimal thresholds...")
        
        noise_multiplier = self.calibration_data['background_noise']['base_threshold_multiplier']
        base_thresholds = {
            "close": {"volume": 800, "quality": 0.6, "spectral": 0.4},
            "medium": {"volume": 400, "quality": 0.35, "spectral": 0.3},
            "far": {"volume": 200, "quality": 0.20, "spectral": 0.25},
            "room": {"volume": 100, "quality": 0.15, "spectral": 0.2}
        }
        
        optimal_thresholds = {}
        
        for distance_name, distance_data in self.calibration_data['distances'].items():
            user_rating = distance_data['user_rating']
            base = base_thresholds[distance_name]
            
            # Adjust thresholds based on user rating and noise level
            if user_rating <= 2:  # Excellent/Good
                adjustment = 1.0
            elif user_rating == 3:  # Fair
                adjustment = 0.8
            elif user_rating == 4:  # Poor
                adjustment = 0.6
            else:  # Failed
                adjustment = 0.4
            
            # Apply noise environment adjustment
            volume_threshold = base['volume'] * noise_multiplier * adjustment
            quality_threshold = base['quality'] * adjustment
            spectral_threshold = base['spectral'] * adjustment
            
            optimal_thresholds[distance_name] = {
                'volume_threshold': int(volume_threshold),
                'quality_threshold': round(quality_threshold, 3),
                'spectral_threshold': round(spectral_threshold, 3),
                'user_rating': user_rating,
                'adjustment_factor': adjustment,
                'noise_multiplier': noise_multiplier
            }
        
        self.calibration_data['optimal_thresholds'] = optimal_thresholds
        
        print("[SimpleRoomCalibration] 🎯 Optimal thresholds calculated:")
        for name, thresholds in optimal_thresholds.items():
            print(f"[SimpleRoomCalibration]   {name}: vol={thresholds['volume_threshold']}, "
                  f"qual={thresholds['quality_threshold']}, "
                  f"spec={thresholds['spectral_threshold']}")

    def save_simple_calibration(self):
        """Save simple calibration data"""
        self.calibration_data['calibration_timestamp'] = datetime.now().isoformat()
        self.calibration_data['version'] = "1.0_simple"
        self.calibration_data['calibration_type'] = "user_feedback"
        
        # Create calibration filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"room_calibration_simple_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.calibration_data, f, indent=2, default=str)
            
            # Also save as latest calibration
            with open("room_calibration_latest.json", 'w') as f:
                json.dump(self.calibration_data, f, indent=2, default=str)
            
            print(f"[SimpleRoomCalibration] 💾 Calibration saved to: {filename}")
            print(f"[SimpleRoomCalibration] 💾 Latest calibration: room_calibration_latest.json")
            
            return True
            
        except Exception as e:
            print(f"[SimpleRoomCalibration] ❌ Failed to save calibration: {e}")
            return False

    def load_calibration(self, filename="room_calibration_latest.json"):
        """Load existing calibration data"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.calibration_data = json.load(f)
                print(f"[SimpleRoomCalibration] ✅ Calibration loaded from: {filename}")
                return True
            else:
                print(f"[SimpleRoomCalibration] ⚠️ Calibration file not found: {filename}")
                return False
        except Exception as e:
            print(f"[SimpleRoomCalibration] ❌ Failed to load calibration: {e}")
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

def run_simple_room_calibration():
    """Main function to run simple room calibration"""
    calibration_system = SimpleRoomCalibrationSystem()
    
    try:
        success = calibration_system.start_simple_calibration()
        if success:
            print("\n[SimpleRoomCalibration] 🎉 Room calibration completed successfully!")
            print("[SimpleRoomCalibration] 💡 The system is now optimized for your room and speaking distances")
            return calibration_system.get_distance_thresholds()
        else:
            print("\n[SimpleRoomCalibration] ❌ Room calibration failed")
            return None
    except KeyboardInterrupt:
        print("\n[SimpleRoomCalibration] ⏹️  Calibration interrupted by user")
        return None

if __name__ == "__main__":
    print("Simple Room-Scale Voice Detection Calibration System")
    print("=" * 55)
    result = run_simple_room_calibration()
    if result:
        print("\nCalibrated thresholds:")
        for distance, thresholds in result.items():
            print(f"  {distance}: {thresholds}")