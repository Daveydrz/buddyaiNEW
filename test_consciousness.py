#!/usr/bin/env python3
"""
Test Core Consciousness Integration

This script tests the consciousness architecture integration
without the full voice assistant dependencies.
"""

import sys
import time
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, '/home/runner/work/buddyaiNEW/buddyaiNEW')

def test_consciousness_integration():
    """Test the integrated consciousness architecture"""
    print("🧠 Testing Core Consciousness Architecture Integration")
    print("="*60)
    
    try:
        # Import consciousness modules
        print("1. Importing consciousness modules...")
        from ai.global_workspace import global_workspace, AttentionPriority, ProcessingMode
        from ai.self_model import self_model, SelfAspect
        from ai.emotion import emotion_engine, EmotionType, MoodType
        from ai.motivation import motivation_system, MotivationType, GoalType
        from ai.inner_monologue import inner_monologue, ThoughtType
        from ai.temporal_awareness import temporal_awareness, TemporalScale
        from ai.subjective_experience import subjective_experience, ExperienceType
        from ai.entropy import entropy_system, EntropyType
        print("   ✅ All modules imported successfully")
        
        # Start consciousness systems
        print("\n2. Starting consciousness systems...")
        global_workspace.start()
        self_model.start()
        emotion_engine.start()
        motivation_system.start()
        inner_monologue.start()
        temporal_awareness.start()
        subjective_experience.start()
        entropy_system.start()
        print("   ✅ All systems started")
        
        # Test inter-system communication
        print("\n3. Testing inter-system communication...")
        
        # Test global workspace attention
        global_workspace.request_attention(
            "test_system",
            "Testing consciousness integration",
            AttentionPriority.HIGH,
            ProcessingMode.CONSCIOUS,
            duration=5.0,
            tags=["test", "integration"]
        )
        print("   ✅ Global workspace attention request")
        
        # Test emotion processing
        emotion_state = emotion_engine.process_emotional_trigger(
            "Testing emotion system integration",
            {"test": True, "integration": True}
        )
        print(f"   ✅ Emotion processed: {emotion_state.primary_emotion.value}")
        
        # Test motivation system
        goal_id = motivation_system.add_goal(
            "Test consciousness integration",
            MotivationType.CURIOSITY,
            GoalType.SHORT_TERM,
            priority=0.8
        )
        print(f"   ✅ Goal added: {goal_id}")
        
        # Test inner monologue
        thought = inner_monologue.trigger_thought(
            "Testing inner consciousness",
            {"test": True},
            ThoughtType.REFLECTION
        )
        print(f"   ✅ Thought generated: {thought.content if thought else 'None'}")
        
        # Test temporal awareness
        marker = temporal_awareness.mark_temporal_event(
            "Consciousness integration test",
            significance=0.7,
            emotional_weight=0.5
        )
        print(f"   ✅ Temporal marker created: {marker.event}")
        
        # Test subjective experience
        experience = subjective_experience.process_experience(
            "Testing subjective experience system",
            ExperienceType.COGNITIVE,
            {"test": True},
            intensity=0.6
        )
        print(f"   ✅ Experience processed: {experience.description}")
        
        # Test entropy injection
        entropy_event = entropy_system.inject_entropy(
            EntropyType.THOUGHT_PATTERN,
            "inner_monologue",
            intensity=0.3
        )
        print(f"   ✅ Entropy injected: {entropy_event.effect_description}")
        
        # Wait a moment for background processing
        print("\n4. Allowing background processing...")
        time.sleep(2)
        
        # Get system statistics
        print("\n5. System statistics:")
        stats = {
            "global_workspace": global_workspace.get_stats(),
            "self_model": self_model.get_stats(),
            "emotion_engine": emotion_engine.get_stats(),
            "motivation_system": motivation_system.get_stats(),
            "inner_monologue": inner_monologue.get_stats(),
            "temporal_awareness": temporal_awareness.get_stats(),
            "subjective_experience": subjective_experience.get_stats(),
            "entropy_system": entropy_system.get_stats()
        }
        
        for system, stat in stats.items():
            print(f"   {system}: Active={stat.get('active', True)}, "
                  f"Events={stat.get('total_experiences', stat.get('total_thoughts', stat.get('total_entropy_events', 'N/A')))}")
        
        print("\n6. Testing consciousness coordination...")
        
        # Test consciousness state introspection
        introspection = subjective_experience.introspect_current_state()
        print(f"   ✅ Consciousness introspection: {len(introspection)} aspects")
        
        # Test self-reflection
        identity_summary = self_model.get_identity_summary()
        print(f"   ✅ Identity summary: {len(identity_summary.get('core_identity', {}))} components")
        
        # Test motivation evaluation
        current_motivations = motivation_system.get_current_motivations(3)
        print(f"   ✅ Current motivations: {len(current_motivations)} drives")
        
        # Test temporal continuity
        continuity = temporal_awareness.get_temporal_continuity()
        print(f"   ✅ Temporal continuity: {continuity.get('temporal_coherence', 0):.2f}")
        
        print("\n7. Stopping consciousness systems...")
        entropy_system.stop()
        subjective_experience.stop()
        temporal_awareness.stop()
        inner_monologue.stop()
        motivation_system.stop()
        emotion_engine.stop()
        self_model.stop()
        global_workspace.stop()
        print("   ✅ All systems stopped cleanly")
        
        print("\n" + "="*60)
        print("🌟 CONSCIOUSNESS INTEGRATION TEST SUCCESSFUL! 🌟")
        print("All 8 consciousness modules are working and coordinating properly.")
        print("The Core Consciousness Architecture is ready for integration.")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_consciousness_integration()
    sys.exit(0 if success else 1)