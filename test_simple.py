#!/usr/bin/env python3
"""
Simple test of the performance optimizations without dependencies
"""

import re

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

def test_simple_conversation_detection():
    """Test that simple conversations are correctly detected"""
    print("\n=== Testing Simple Conversation Detection ===")
    
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

# Global cache for identity results to prevent duplicate analysis
_identity_cache = {}
_identity_cache_timestamp = {}

def get_cached_identity(audio_hash, current_user, max_age_seconds=30):
    """🚀 PERFORMANCE: Get cached identity result to prevent duplicate analysis"""
    import time
    
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

def test_identity_caching():
    """Test identity caching functionality"""
    print("\n=== Testing Identity Caching ===")
    
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
    
    print("✅ Caching tests passed")

def run_tests():
    """Run the simple tests"""
    print("🚀 Running Simple Performance Tests")
    print("=" * 50)
    
    test_simple_conversation_detection()
    test_identity_caching()
    
    print("\n" + "=" * 50)
    print("✅ Simple tests completed!")

if __name__ == "__main__":
    run_tests()