#!/usr/bin/env python3
"""
Performance Test for Buddy AI Optimizations
Tests the fast-path routing and caching improvements
"""

import time
import sys
import os

# Add the current directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def mock_speak_streaming(text):
    """Mock function to replace actual TTS during testing"""
    print(f"[MockTTS] Would speak: '{text}'")
    time.sleep(0.01)  # Simulate minimal TTS delay

def mock_voice_manager():
    """Mock voice manager for testing"""
    class MockVoiceManager:
        def get_last_audio_sample(self):
            return None
        def is_llm_locked(self):
            return False
    return MockVoiceManager()

def test_simple_conversation_detection():
    """Test that simple conversations are correctly detected"""
    print("\n=== Testing Simple Conversation Detection ===")
    
    from main import is_simple_conversation
    
    # Test cases that should be detected as simple
    simple_cases = [
        "hi",
        "hello",
        "hey",
        "how are you",
        "how are you today",
        "what's up",
        "good morning",
        "thanks",
        "yes",
        "okay"
    ]
    
    # Test cases that should NOT be detected as simple (need full processing)
    complex_cases = [
        "my name is David",
        "call me Sarah",
        "tell me about artificial intelligence",
        "what's the weather like tomorrow",
        "i'm John and I need help",
        "explain quantum computing to me"
    ]
    
    print("Testing simple conversation cases:")
    for case in simple_cases:
        result = is_simple_conversation(case)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  '{case}' -> {result} {status}")
    
    print("\nTesting complex conversation cases:")
    for case in complex_cases:
        result = is_simple_conversation(case)
        status = "✅ PASS" if not result else "❌ FAIL"
        print(f"  '{case}' -> {result} {status}")

def test_identity_caching():
    """Test identity caching functionality"""
    print("\n=== Testing Identity Caching ===")
    
    from main import get_cached_identity, cache_identity_result
    
    # Test caching
    test_hash = "test_audio_hash_123"
    test_identity = "TestUser"
    
    # Should return None for new hash
    result1 = get_cached_identity(test_hash, "default_user")
    print(f"Cache miss test: {result1} (should be None)")
    
    # Cache a result
    cache_identity_result(test_hash, test_identity)
    print(f"Cached identity: {test_identity}")
    
    # Should return cached result
    result2 = get_cached_identity(test_hash, "default_user")
    print(f"Cache hit test: {result2} (should be {test_identity})")
    
    # Test expiry (would need to mock time for full test)
    print("Cache expiry test would require time mocking")

def test_performance_timing():
    """Test performance improvements with timing"""
    print("\n=== Testing Performance Timing ===")
    
    # Mock the dependencies
    import main
    original_speak = getattr(main, 'speak_streaming', None)
    original_voice_manager = getattr(main, 'voice_manager', None)
    
    # Replace with mocks
    main.speak_streaming = mock_speak_streaming
    main.voice_manager = mock_voice_manager()
    main.full_duplex_manager = None  # Disable for testing
    
    try:
        # Test simple conversation (should be fast)
        print("Testing simple conversation performance:")
        start_time = time.time()
        
        # This should use the fast path
        main.handle_streaming_response("how are you", "TestUser")
        
        simple_duration = time.time() - start_time
        print(f"Simple conversation took: {simple_duration:.3f} seconds")
        
        # Test complex conversation (will be slower but should cache)
        print("\nTesting complex conversation performance:")
        start_time = time.time()
        
        # This should use full processing
        main.handle_streaming_response("tell me about machine learning", "TestUser")
        
        complex_duration = time.time() - start_time
        print(f"Complex conversation took: {complex_duration:.3f} seconds")
        
        # Performance comparison
        if simple_duration < complex_duration:
            print(f"✅ Performance optimization working: simple ({simple_duration:.3f}s) < complex ({complex_duration:.3f}s)")
        else:
            print(f"⚠️ Performance difference not as expected: simple ({simple_duration:.3f}s) vs complex ({complex_duration:.3f}s)")
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
    finally:
        # Restore original functions
        if original_speak:
            main.speak_streaming = original_speak
        if original_voice_manager:
            main.voice_manager = original_voice_manager

def run_all_tests():
    """Run all performance tests"""
    print("🚀 Running Buddy AI Performance Tests")
    print("=" * 50)
    
    try:
        test_simple_conversation_detection()
        test_identity_caching()
        test_performance_timing()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()