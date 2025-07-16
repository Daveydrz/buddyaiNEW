# ai/chat_enhanced_smart_with_fusion.py - Enhanced chat with intelligent memory fusion
from ai.human_memory_smart import SmartHumanLikeMemory
from ai.chat import generate_response_streaming
from ai.memory_fusion_intelligent import get_intelligent_unified_username
import random

# Global memory instances
smart_memories = {}

def get_smart_memory(username: str) -> SmartHumanLikeMemory:
    """Get or create smart memory for user"""
    if username not in smart_memories:
        smart_memories[username] = SmartHumanLikeMemory(username)
    return smart_memories[username]

def generate_response_streaming_with_intelligent_fusion(question: str, username: str, lang="en"):
    """🧠 Generate response with intelligent memory fusion and smart memory + PERSONALITY"""
    
    # 🔧 FIX: Check for unified username from memory fusion
    print(f"[ChatFusion] 🔍 Checking memory fusion for user: {username}")
    try:
        unified_username = get_intelligent_unified_username(username)
        
        if unified_username != username:
            print(f"[ChatFusion] 🎯 MEMORY FUSION: {username} → {unified_username}")
            print(f"[ChatFusion] 🧠 Using unified memory for response generation")
        else:
            print(f"[ChatFusion] ✅ No fusion needed for {username}")
        
        # 🔧 CRITICAL: Use unified username for ALL subsequent operations
        username = unified_username
        
    except ImportError:
        print(f"[ChatFusion] ⚠️ Memory fusion not available, using original username: {username}")
    except Exception as e:
        print(f"[ChatFusion] ❌ Memory fusion error: {e}, using original username: {username}")
    
    # Step 2: Use unified username for all memory operations
    smart_memory = get_smart_memory(username)
    
    # Step 3: Extract and store memories from current message
    smart_memory.extract_and_store_human_memories(question)
    
    # Step 4: Check for natural context responses (reminders, follow-ups)
    context_response = smart_memory.check_for_natural_context_response()
    
    if context_response:
        print(f"[ChatFusion] 🎯 Context response triggered: {context_response}")
        
        # Yield context response first - with personality!
        casual_transitions = [
            "Oh hey, before I forget - ", 
            "Actually, ", 
            "By the way, ",
            "Quick thing - ",
            ""
        ]
        transition = random.choice(casual_transitions)
        if transition:
            yield transition
        
        # Make context response more casual
        casual_context = context_response.replace("I wanted to", "I was gonna")
        casual_context = casual_context.replace("remind you", "remind ya")
        casual_context = casual_context.replace("follow up", "check in")
        
        for word in casual_context.split():
            yield word + " "
        
        # Add transition to main response
        casual_connectors = [
            "Anyway, ", "So, ", "But yeah, ", "And ", ""
        ]
        connector = random.choice(casual_connectors)
        if connector:
            yield connector
    
    # Step 5: Generate main response with unified memory context + PERSONALITY
    print(f"[ChatFusion] 💭 Generating PERSONALITY response with unified memory for {username}")
    
    for chunk in generate_response_streaming(question, username, lang):
        yield chunk

# Export for main.py
__all__ = ['generate_response_streaming_with_intelligent_fusion']