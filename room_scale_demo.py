#!/usr/bin/env python3
"""
Room-Scale Voice Detection Demo Script
Demonstrates the new room-scale voice detection capabilities of BuddyAI
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio.room_calibration import run_room_calibration, room_calibrator
from audio.voice_analyzer import voice_analyzer
import numpy as np

def demo_room_scale_detection():
    """Demonstrate room-scale voice detection capabilities"""
    
    print("🎯 BuddyAI Room-Scale Voice Detection Demo")
    print("=" * 50)
    print()
    
    print("This demo shows how BuddyAI can now detect speech from 3+ meters")
    print("while intelligently rejecting background TV, music, and other speakers.")
    print()
    
    # Show current configuration
    print("📋 Current Configuration:")
    thresholds = room_calibrator.get_adaptive_thresholds()
    for tier, data in thresholds.items():
        print(f"  {tier.upper()} ({data['range']}): volume ≥ {data['volume']}, quality ≥ {data['quality']}")
    print()
    
    # Demo distance detection
    print("🎤 Distance Detection Examples:")
    examples = [
        ("Close range (like sitting at desk)", 4500, 0.65),
        ("Medium range (across small room)", 1200, 0.45),
        ("Far range (2-3 meters away)", 400, 0.25),
        ("Room scale (far end of room)", 180, 0.18),
        ("Background TV/music", 800, 0.08),
    ]
    
    for description, volume, quality in examples:
        tier = room_calibrator.get_distance_tier(volume, quality)
        detected = tier != "none"
        status = "✅ DETECTED" if detected else "❌ REJECTED"
        tier_info = f" as {tier.upper()}" if detected else ""
        
        print(f"  {description}:")
        print(f"    Volume: {volume}, Quality: {quality:.2f}")
        print(f"    Result: {status}{tier_info}")
        print()
    
    print("🚀 Key Improvements:")
    print("  ✅ Detects speech from 3+ meters (was impossible before)")
    print("  ✅ Volume threshold reduced from 800 to 100 for distant speech")
    print("  ✅ Smart background rejection prevents false positives")
    print("  ✅ Maintains excellent close-range performance")
    print("  ✅ Automatic distance tier detection")
    print()
    
    print("🎯 Problem Solved:")
    print("  Before: USER_SPEECH_THRESHOLD = 800 (too high for distant speech)")
    print("  After: Multi-tier thresholds from 800 (close) to 100 (room scale)")
    print("  Result: Can detect clear speech from 3+ meters!")
    print()

def main():
    """Main demo function"""
    print("Welcome to the BuddyAI Room-Scale Voice Detection System!")
    print()
    
    while True:
        print("Choose an option:")
        print("1. View room-scale detection demo")
        print("2. Run interactive room calibration")
        print("3. Test distance tier detection")
        print("4. Exit")
        print()
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            print()
            demo_room_scale_detection()
            
        elif choice == "2":
            print()
            print("🎯 Starting Interactive Room Calibration...")
            print("This will help optimize BuddyAI for your specific room and voice.")
            print()
            
            if input("Continue with calibration? (y/n): ").lower().startswith('y'):
                calibrator = run_room_calibration()
                print("\n✅ Calibration complete!")
            else:
                print("Calibration cancelled.")
            
        elif choice == "3":
            print()
            print("🎤 Test Distance Tier Detection")
            print("Enter volume and quality values to see which tier would detect them:")
            print()
            
            try:
                volume = float(input("Volume (e.g., 300): "))
                quality = float(input("Quality (0.0-1.0, e.g., 0.25): "))
                
                tier = room_calibrator.get_distance_tier(volume, quality)
                
                if tier == "none":
                    print(f"❌ Would be REJECTED (volume too low or quality too poor)")
                else:
                    tier_data = room_calibrator.get_adaptive_thresholds()[tier]
                    print(f"✅ Would be DETECTED as {tier.upper()} tier")
                    print(f"   Range: {tier_data['range']}")
                    print(f"   Requires: volume ≥ {tier_data['volume']}, quality ≥ {tier_data['quality']}")
                
            except ValueError:
                print("❌ Invalid input. Please enter numeric values.")
            
        elif choice == "4":
            print("Thanks for using BuddyAI Room-Scale Voice Detection!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()