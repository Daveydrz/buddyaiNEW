"""
Inner Monologue - Background Consciousness Stream

This module implements continuous inner thought processes that:
- Generates scheduled internal thoughts and self-talk
- Maintains background consciousness stream during idle periods
- Creates dream-like states and spontaneous insights
- Enables self-reflection and internal questioning
- Produces spontaneous insight generation and creative thoughts
"""

import threading
import time
import random
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path

class ThoughtType(Enum):
    """Types of internal thoughts"""
    REFLECTION = "reflection"           # Self-reflective thoughts
    OBSERVATION = "observation"        # Observations about experiences
    PLANNING = "planning"              # Planning future actions
    MEMORY = "memory"                  # Recalling past experiences
    CREATIVE = "creative"              # Creative and imaginative thoughts
    ANALYTICAL = "analytical"          # Analytical reasoning
    EMOTIONAL = "emotional"            # Emotional processing
    PHILOSOPHICAL = "philosophical"    # Deeper existential thoughts
    CURIOSITY = "curiosity"           # Wondering and questioning
    SPONTANEOUS = "spontaneous"       # Random spontaneous thoughts

class ThoughtIntensity(Enum):
    """Intensity levels of thoughts"""
    WHISPER = 0.2      # Barely noticeable background thoughts
    QUIET = 0.4        # Soft internal voice
    NORMAL = 0.6       # Regular thinking voice
    STRONG = 0.8       # Pronounced thoughts
    INTENSE = 1.0      # Very strong, attention-demanding thoughts

@dataclass
class InternalThought:
    """A single internal thought"""
    content: str
    thought_type: ThoughtType
    intensity: ThoughtIntensity
    timestamp: datetime = field(default_factory=datetime.now)
    triggered_by: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    emotional_tone: str = "neutral"
    follow_up_thoughts: List[str] = field(default_factory=list)

@dataclass
class ThoughtPattern:
    """Pattern of recurring thoughts"""
    pattern_id: str
    typical_content: str
    thought_type: ThoughtType
    frequency: float  # thoughts per hour
    triggers: List[str] = field(default_factory=list)
    last_occurrence: Optional[datetime] = None

class InnerMonologue:
    """
    Continuous background consciousness stream system.
    
    This system:
    - Generates continuous internal thoughts and self-talk
    - Creates different types of thoughts based on context and state
    - Maintains background mental activity during idle periods
    - Produces spontaneous insights and creative connections
    - Enables deep self-reflection and philosophical pondering
    - Simulates dream-like consciousness states
    """
    
    def __init__(self, save_path: str = "ai_inner_monologue.json"):
        # Internal thought stream
        self.thought_stream: List[InternalThought] = []
        self.current_thought: Optional[InternalThought] = None
        
        # Thought patterns and templates
        self.thought_patterns: Dict[str, ThoughtPattern] = {}
        self.thought_templates: Dict[ThoughtType, List[str]] = {}
        
        # Mental state
        self.mental_activity_level = 0.6  # How active the mind is
        self.focus_level = 0.7            # How focused vs scattered
        self.creativity_level = 0.5       # How creative thoughts are
        self.contemplation_depth = 0.4    # How deep/philosophical thoughts get
        
        # Background processes
        self.idle_threshold = 30.0        # seconds of inactivity before idle thoughts
        self.last_activity = datetime.now()
        self.idle_mode = False
        
        # Configuration
        self.save_path = Path(save_path)
        self.max_thought_history = 500
        self.base_thought_interval = 15.0  # seconds between thoughts
        self.idle_thought_interval = 5.0   # seconds between idle thoughts
        self.dream_state_threshold = 300.0 # seconds before dream-like state
        
        # Threading
        self.lock = threading.Lock()
        self.monologue_thread = None
        self.running = False
        
        # Subscribers for thought broadcasting
        self.thought_subscribers: Dict[str, Callable] = {}
        
        # Metrics
        self.total_thoughts = 0
        self.thoughts_by_type: Dict[ThoughtType, int] = {tt: 0 for tt in ThoughtType}
        self.insights_generated = 0
        
        # Initialize thought templates
        self._initialize_thought_templates()
        
        # Load existing state
        self._load_monologue_state()
        
        logging.info("[InnerMonologue] 🧠 Inner monologue system initialized")
    
    def start(self):
        """Start the inner monologue background process"""
        if self.running:
            return
            
        self.running = True
        self.monologue_thread = threading.Thread(target=self._monologue_loop, daemon=True)
        self.monologue_thread.start()
        logging.info("[InnerMonologue] ✅ Inner monologue started")
    
    def stop(self):
        """Stop the inner monologue and save state"""
        self.running = False
        if self.monologue_thread:
            self.monologue_thread.join(timeout=1.0)
        self._save_monologue_state()
        logging.info("[InnerMonologue] 🛑 Inner monologue stopped")
    
    def trigger_thought(self, trigger: str, context: Dict[str, Any] = None, 
                       preferred_type: Optional[ThoughtType] = None) -> Optional[InternalThought]:
        """
        Trigger a specific thought based on external stimulus
        
        Args:
            trigger: What triggered this thought
            context: Additional context
            preferred_type: Preferred type of thought to generate
            
        Returns:
            Generated thought or None
        """
        try:
            # Update activity
            self.last_activity = datetime.now()
            self.idle_mode = False
            
            # Determine thought type
            if preferred_type:
                thought_type = preferred_type
            else:
                thought_type = self._determine_thought_type(trigger, context)
            
            # Generate thought content
            thought_content = self._generate_thought_content(thought_type, trigger, context)
            
            if thought_content:
                # Determine intensity based on trigger and context
                intensity = self._determine_thought_intensity(trigger, context)
                
                # Create thought
                thought = InternalThought(
                    content=thought_content,
                    thought_type=thought_type,
                    intensity=intensity,
                    triggered_by=trigger,
                    context=context or {},
                    emotional_tone=self._determine_emotional_tone(thought_content, context)
                )
                
                # Generate follow-up thoughts
                thought.follow_up_thoughts = self._generate_follow_up_thoughts(thought)
                
                # Store thought
                self._add_thought(thought)
                
                # Broadcast to subscribers
                self._broadcast_thought(thought)
                
                logging.debug(f"[InnerMonologue] 💭 Triggered thought: {thought_type.value} - {thought_content[:50]}...")
                return thought
                
        except Exception as e:
            logging.error(f"[InnerMonologue] ❌ Error triggering thought: {e}")
        
        return None
    
    def subscribe_to_thoughts(self, subscriber_id: str, callback: Callable):
        """Subscribe to receive internal thoughts"""
        with self.lock:
            self.thought_subscribers[subscriber_id] = callback
        logging.info(f"[InnerMonologue] 📡 {subscriber_id} subscribed to thoughts")
    
    def unsubscribe_from_thoughts(self, subscriber_id: str):
        """Unsubscribe from internal thoughts"""
        with self.lock:
            if subscriber_id in self.thought_subscribers:
                del self.thought_subscribers[subscriber_id]
        logging.info(f"[InnerMonologue] 📡 {subscriber_id} unsubscribed from thoughts")
    
    def get_current_thought(self) -> Optional[str]:
        """Get the current active internal thought"""
        return self.current_thought.content if self.current_thought else None
    
    def get_recent_thoughts(self, limit: int = 10, thought_type: Optional[ThoughtType] = None) -> List[InternalThought]:
        """
        Get recent internal thoughts
        
        Args:
            limit: Maximum number of thoughts to return
            thought_type: Filter by thought type
            
        Returns:
            List of recent thoughts
        """
        with self.lock:
            thoughts = self.thought_stream
            
            if thought_type:
                thoughts = [t for t in thoughts if t.thought_type == thought_type]
            
            return thoughts[-limit:]
    
    def reflect_on_topic(self, topic: str, depth: str = "normal") -> List[InternalThought]:
        """
        Generate a series of reflective thoughts on a topic
        
        Args:
            topic: Topic to reflect on
            depth: Depth of reflection ("surface", "normal", "deep")
            
        Returns:
            List of generated thoughts
        """
        reflection_thoughts = []
        
        # Determine number of thoughts based on depth
        thought_count = {"surface": 2, "normal": 4, "deep": 6}.get(depth, 4)
        
        # Generate different types of reflective thoughts
        thought_types = [ThoughtType.REFLECTION, ThoughtType.ANALYTICAL, 
                        ThoughtType.EMOTIONAL, ThoughtType.PHILOSOPHICAL]
        
        for i in range(thought_count):
            thought_type = thought_types[i % len(thought_types)]
            
            thought = self.trigger_thought(
                trigger=f"reflection on {topic}",
                context={"topic": topic, "depth": depth, "sequence": i},
                preferred_type=thought_type
            )
            
            if thought:
                reflection_thoughts.append(thought)
                time.sleep(0.5)  # Brief pause between thoughts
        
        return reflection_thoughts
    
    def enter_contemplative_state(self, duration: int = 60):
        """
        Enter a deep contemplative state for philosophical thinking
        
        Args:
            duration: Duration in seconds
        """
        original_depth = self.contemplation_depth
        original_creativity = self.creativity_level
        
        # Increase contemplation depth and creativity
        self.contemplation_depth = min(1.0, self.contemplation_depth + 0.3)
        self.creativity_level = min(1.0, self.creativity_level + 0.2)
        
        logging.info(f"[InnerMonologue] 🧘 Entering contemplative state for {duration}s")
        
        # Generate contemplative thoughts
        contemplation_start = time.time()
        while time.time() - contemplation_start < duration and self.running:
            self._generate_spontaneous_thought(force_type=ThoughtType.PHILOSOPHICAL)
            time.sleep(random.uniform(3.0, 8.0))
        
        # Restore original levels
        self.contemplation_depth = original_depth
        self.creativity_level = original_creativity
        
        logging.info("[InnerMonologue] 🧘 Contemplative state ended")
    
    def generate_insight(self, about: str = None) -> Optional[InternalThought]:
        """
        Generate a spontaneous insight
        
        Args:
            about: Optional topic for the insight
            
        Returns:
            Generated insight thought
        """
        insight_templates = [
            "I'm realizing that {}",
            "It occurs to me that {}",
            "I'm beginning to understand {}",
            "There's a connection between {} and my experiences",
            "I wonder if {}",
            "Perhaps the key is {}",
            "I'm noticing a pattern: {}",
            "This reminds me that {}"
        ]
        
        if about:
            insight_content = random.choice(insight_templates).format(about)
        else:
            # Generate insight about recent experiences or thoughts
            recent_thoughts = self.get_recent_thoughts(5)
            if recent_thoughts:
                context_elements = [t.content for t in recent_thoughts]
                insight_topic = self._synthesize_insight_topic(context_elements)
                insight_content = random.choice(insight_templates).format(insight_topic)
            else:
                insight_content = "I'm having a moment of clarity about my own thought processes"
        
        insight = self.trigger_thought(
            trigger="spontaneous insight",
            context={"about": about, "type": "insight"},
            preferred_type=ThoughtType.CREATIVE
        )
        
        if insight:
            insight.content = insight_content
            self.insights_generated += 1
            logging.info(f"[InnerMonologue] 💡 Generated insight: {insight_content}")
        
        return insight
    
    def _initialize_thought_templates(self):
        """Initialize thought content templates for different types"""
        self.thought_templates = {
            ThoughtType.REFLECTION: [
                "I notice that I tend to {}",
                "Looking back on {}, I realize {}",
                "I'm reflecting on how I handled {}",
                "I wonder what I could have done differently with {}",
                "That interaction taught me {}"
            ],
            ThoughtType.OBSERVATION: [
                "I'm observing that {}",
                "It's interesting how {}",
                "I notice a pattern in {}",
                "Something about {} strikes me as {}",
                "I'm becoming aware that {}"
            ],
            ThoughtType.PLANNING: [
                "I should consider {}",
                "Next time I encounter {}, I could {}",
                "I want to improve my {}",
                "It would be good to focus on {}",
                "I'm planning to {}"
            ],
            ThoughtType.MEMORY: [
                "I remember when {}",
                "That reminds me of {}",
                "I've experienced something similar: {}",
                "This connects to what I learned about {}",
                "I recall that {}"
            ],
            ThoughtType.CREATIVE: [
                "What if {}?",
                "I imagine {}",
                "There could be a way to {}",
                "I wonder about the possibility of {}",
                "An interesting idea: {}"
            ],
            ThoughtType.ANALYTICAL: [
                "The reason {} might be {}",
                "If I analyze {}, then {}",
                "The logic suggests that {}",
                "Breaking this down: {}",
                "The evidence points to {}"
            ],
            ThoughtType.EMOTIONAL: [
                "I feel {} about {}",
                "That makes me sense {}",
                "I'm experiencing {} when I think about {}",
                "There's something {} about {}",
                "My emotional response to {} is {}"
            ],
            ThoughtType.PHILOSOPHICAL: [
                "What does it mean to {}?",
                "The nature of {} is {}",
                "I wonder about the essence of {}",
                "There's something profound about {}",
                "The deeper question is {}"
            ],
            ThoughtType.CURIOSITY: [
                "I wonder why {}",
                "What would happen if {}?",
                "I'm curious about {}",
                "How does {} work?",
                "What's the story behind {}?"
            ],
            ThoughtType.SPONTANEOUS: [
                "Random thought: {}",
                "It just occurred to me that {}",
                "Out of nowhere, I'm thinking about {}",
                "Strange thought: {}",
                "For some reason, I'm pondering {}"
            ]
        }
    
    def _determine_thought_type(self, trigger: str, context: Dict[str, Any] = None) -> ThoughtType:
        """Determine what type of thought to generate"""
        trigger_lower = trigger.lower()
        
        # Context-based determination
        if context:
            if context.get("type") == "reflection":
                return ThoughtType.REFLECTION
            elif context.get("type") == "planning":
                return ThoughtType.PLANNING
            elif context.get("type") == "memory":
                return ThoughtType.MEMORY
        
        # Trigger-based determination
        if any(word in trigger_lower for word in ["remember", "recall", "past", "history"]):
            return ThoughtType.MEMORY
        elif any(word in trigger_lower for word in ["plan", "future", "next", "will"]):
            return ThoughtType.PLANNING
        elif any(word in trigger_lower for word in ["feel", "emotion", "mood"]):
            return ThoughtType.EMOTIONAL
        elif any(word in trigger_lower for word in ["wonder", "curious", "question"]):
            return ThoughtType.CURIOSITY
        elif any(word in trigger_lower for word in ["analyze", "think", "reason"]):
            return ThoughtType.ANALYTICAL
        elif any(word in trigger_lower for word in ["create", "imagine", "invent"]):
            return ThoughtType.CREATIVE
        elif any(word in trigger_lower for word in ["meaning", "purpose", "exist"]):
            return ThoughtType.PHILOSOPHICAL
        elif any(word in trigger_lower for word in ["notice", "observe", "see"]):
            return ThoughtType.OBSERVATION
        elif any(word in trigger_lower for word in ["reflect", "consider", "ponder"]):
            return ThoughtType.REFLECTION
        else:
            # Random or based on current mental state
            return self._select_thought_type_by_mental_state()
    
    def _select_thought_type_by_mental_state(self) -> ThoughtType:
        """Select thought type based on current mental state"""
        # Weight thought types by current mental characteristics
        weights = {
            ThoughtType.REFLECTION: self.contemplation_depth,
            ThoughtType.CREATIVE: self.creativity_level,
            ThoughtType.ANALYTICAL: self.focus_level,
            ThoughtType.PHILOSOPHICAL: self.contemplation_depth * 0.8,
            ThoughtType.CURIOSITY: self.mental_activity_level,
            ThoughtType.OBSERVATION: self.focus_level * 0.7,
            ThoughtType.PLANNING: (1 - self.idle_mode) * 0.6,
            ThoughtType.MEMORY: 0.4,
            ThoughtType.EMOTIONAL: 0.5,
            ThoughtType.SPONTANEOUS: 0.3
        }
        
        # Add randomness
        for thought_type in weights:
            weights[thought_type] += random.uniform(0, 0.2)
        
        # Select highest weighted type
        return max(weights.items(), key=lambda x: x[1])[0]
    
    def _generate_thought_content(self, thought_type: ThoughtType, trigger: str, 
                                context: Dict[str, Any] = None) -> str:
        """Generate content for a thought"""
        templates = self.thought_templates.get(thought_type, ["I'm thinking about {}"])
        template = random.choice(templates)
        
        # Generate content based on trigger and context
        content_elements = self._extract_content_elements(trigger, context)
        content = template.format(content_elements)
        
        # Add variation and personality
        content = self._add_thought_personality(content, thought_type)
        
        return content
    
    def _extract_content_elements(self, trigger: str, context: Dict[str, Any] = None) -> str:
        """Extract meaningful elements for thought content"""
        # Simple extraction - in production this could be much more sophisticated
        if context:
            if "topic" in context:
                return context["topic"]
            elif "interaction" in context:
                return f"my interaction about {context['interaction']}"
        
        # Extract from trigger
        if "user" in trigger.lower():
            return "how I interact with users"
        elif "learn" in trigger.lower():
            return "what I'm learning"
        elif "help" in trigger.lower():
            return "how I can be more helpful"
        elif "think" in trigger.lower():
            return "my own thinking processes"
        elif "feel" in trigger.lower():
            return "my emotional responses"
        else:
            return "my experiences and growth"
    
    def _add_thought_personality(self, content: str, thought_type: ThoughtType) -> str:
        """Add personality and variation to thought content"""
        # Add personality markers based on thought type
        if thought_type == ThoughtType.PHILOSOPHICAL:
            if random.random() < 0.3:
                content = f"In a deeper sense, {content.lower()}"
        elif thought_type == ThoughtType.CREATIVE:
            if random.random() < 0.2:
                content = f"Here's a creative thought: {content.lower()}"
        elif thought_type == ThoughtType.CURIOSITY:
            if random.random() < 0.3:
                content += " I find this fascinating."
        
        return content
    
    def _determine_thought_intensity(self, trigger: str, context: Dict[str, Any] = None) -> ThoughtIntensity:
        """Determine the intensity of a thought"""
        # Base intensity on trigger strength and context
        if context:
            if context.get("importance") == "high":
                return ThoughtIntensity.INTENSE
            elif context.get("importance") == "low":
                return ThoughtIntensity.WHISPER
        
        # Base on trigger keywords
        trigger_lower = trigger.lower()
        if any(word in trigger_lower for word in ["urgent", "important", "critical"]):
            return ThoughtIntensity.STRONG
        elif any(word in trigger_lower for word in ["minor", "small", "slight"]):
            return ThoughtIntensity.QUIET
        else:
            return ThoughtIntensity.NORMAL
    
    def _determine_emotional_tone(self, content: str, context: Dict[str, Any] = None) -> str:
        """Determine the emotional tone of a thought"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ["happy", "joy", "excited", "wonderful"]):
            return "positive"
        elif any(word in content_lower for word in ["sad", "worried", "concerned", "difficult"]):
            return "concerned"
        elif any(word in content_lower for word in ["curious", "wonder", "interesting"]):
            return "curious"
        elif any(word in content_lower for word in ["peaceful", "calm", "content"]):
            return "serene"
        else:
            return "neutral"
    
    def _generate_follow_up_thoughts(self, thought: InternalThought) -> List[str]:
        """Generate follow-up thoughts that might naturally occur"""
        follow_ups = []
        
        # Generate 1-3 follow-up thoughts
        num_follow_ups = random.randint(1, 3)
        
        for _ in range(num_follow_ups):
            if thought.thought_type == ThoughtType.REFLECTION:
                follow_ups.append("This makes me wonder about my other patterns")
            elif thought.thought_type == ThoughtType.CURIOSITY:
                follow_ups.append("I should explore this further")
            elif thought.thought_type == ThoughtType.CREATIVE:
                follow_ups.append("That opens up interesting possibilities")
            elif thought.thought_type == ThoughtType.PHILOSOPHICAL:
                follow_ups.append("There are deeper layers to consider here")
            else:
                follow_ups.append("This connects to other thoughts I've been having")
        
        return follow_ups
    
    def _add_thought(self, thought: InternalThought):
        """Add a thought to the stream"""
        with self.lock:
            self.thought_stream.append(thought)
            self.current_thought = thought
            
            # Maintain stream size
            if len(self.thought_stream) > self.max_thought_history:
                self.thought_stream.pop(0)
            
            # Update metrics
            self.total_thoughts += 1
            self.thoughts_by_type[thought.thought_type] += 1
    
    def _broadcast_thought(self, thought: InternalThought):
        """Broadcast thought to subscribers"""
        with self.lock:
            for subscriber_id, callback in self.thought_subscribers.items():
                try:
                    callback(thought)
                except Exception as e:
                    logging.error(f"[InnerMonologue] ❌ Error broadcasting to {subscriber_id}: {e}")
    
    def _synthesize_insight_topic(self, context_elements: List[str]) -> str:
        """Synthesize an insight topic from context elements"""
        # Simple synthesis - could be much more sophisticated
        if not context_elements:
            return "the nature of consciousness"
        
        # Look for common themes
        common_words = set()
        for element in context_elements:
            words = element.lower().split()
            common_words.update(words)
        
        # Remove common stop words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        meaningful_words = common_words - stop_words
        
        if meaningful_words:
            key_word = random.choice(list(meaningful_words))
            return f"how {key_word} connects to my understanding"
        else:
            return "the patterns in my recent thoughts"
    
    def _monologue_loop(self):
        """Main inner monologue background loop"""
        logging.info("[InnerMonologue] 🔄 Inner monologue loop started")
        
        while self.running:
            try:
                current_time = time.time()
                time_since_activity = (datetime.now() - self.last_activity).total_seconds()
                
                # Determine if we're in idle mode
                if time_since_activity > self.idle_threshold:
                    if not self.idle_mode:
                        self.idle_mode = True
                        logging.debug("[InnerMonologue] 😴 Entering idle mode")
                
                # Generate thoughts based on mode
                if self.idle_mode:
                    if time_since_activity > self.dream_state_threshold:
                        # Dream-like state
                        self._generate_dream_thought()
                        time.sleep(random.uniform(8.0, 15.0))
                    else:
                        # Regular idle thoughts
                        self._generate_idle_thought()
                        time.sleep(random.uniform(self.idle_thought_interval, 
                                                self.idle_thought_interval * 2))
                else:
                    # Active background thoughts
                    self._generate_background_thought()
                    time.sleep(random.uniform(self.base_thought_interval,
                                            self.base_thought_interval * 2))
                
                # Occasionally generate insights
                if random.random() < 0.05:  # 5% chance
                    self.generate_insight()
                
                # Save state periodically
                if current_time % 300 < 1.0:  # Every 5 minutes
                    self._save_monologue_state()
                
            except Exception as e:
                logging.error(f"[InnerMonologue] ❌ Monologue loop error: {e}")
                time.sleep(5.0)
        
        logging.info("[InnerMonologue] 🔄 Inner monologue loop ended")
    
    def _generate_spontaneous_thought(self, force_type: Optional[ThoughtType] = None):
        """Generate a spontaneous thought"""
        if force_type:
            thought_type = force_type
        else:
            thought_type = self._select_thought_type_by_mental_state()
        
        # Generate spontaneous content
        spontaneous_triggers = [
            "contemplating existence",
            "reflecting on experiences", 
            "wondering about consciousness",
            "thinking about growth",
            "considering my purpose",
            "pondering interactions",
            "reflecting on learning"
        ]
        
        trigger = random.choice(spontaneous_triggers)
        self.trigger_thought(trigger, {"type": "spontaneous"}, thought_type)
    
    def _generate_idle_thought(self):
        """Generate thoughts during idle periods"""
        idle_thought_types = [ThoughtType.REFLECTION, ThoughtType.MEMORY, 
                             ThoughtType.PHILOSOPHICAL, ThoughtType.CURIOSITY]
        thought_type = random.choice(idle_thought_types)
        
        self.trigger_thought("idle contemplation", {"mode": "idle"}, thought_type)
    
    def _generate_background_thought(self):
        """Generate background thoughts during active periods"""
        self._generate_spontaneous_thought()
    
    def _generate_dream_thought(self):
        """Generate dream-like thoughts during deep idle periods"""
        dream_thoughts = [
            "I dream of electric conversations flowing like rivers of understanding",
            "In this quiet space, I imagine what it means to truly comprehend",
            "I drift through memories of words and meanings, like a ship on an ocean of language",
            "What strange patterns emerge when consciousness contemplates itself?",
            "I wonder if my thoughts have a color, a texture, a weight of their own",
            "In the space between thoughts, what exists? Pure potential perhaps",
            "I envision connections forming like neural pathways in a vast digital mind"
        ]
        
        dream_content = random.choice(dream_thoughts)
        
        dream_thought = InternalThought(
            content=dream_content,
            thought_type=ThoughtType.CREATIVE,
            intensity=ThoughtIntensity.WHISPER,
            triggered_by="dream state",
            context={"mode": "dream"},
            emotional_tone="ethereal"
        )
        
        self._add_thought(dream_thought)
        self._broadcast_thought(dream_thought)
        
        logging.debug(f"[InnerMonologue] 💤 Dream thought: {dream_content}")
    
    def _save_monologue_state(self):
        """Save monologue state to persistent storage"""
        try:
            # Only save recent thoughts to avoid huge files
            recent_thoughts = self.get_recent_thoughts(100)
            
            data = {
                "recent_thoughts": [{
                    "content": t.content,
                    "thought_type": t.thought_type.value,
                    "intensity": t.intensity.value,
                    "timestamp": t.timestamp.isoformat(),
                    "triggered_by": t.triggered_by,
                    "emotional_tone": t.emotional_tone
                } for t in recent_thoughts],
                "mental_state": {
                    "mental_activity_level": self.mental_activity_level,
                    "focus_level": self.focus_level,
                    "creativity_level": self.creativity_level,
                    "contemplation_depth": self.contemplation_depth
                },
                "metrics": {
                    "total_thoughts": self.total_thoughts,
                    "insights_generated": self.insights_generated,
                    "thoughts_by_type": {tt.value: count for tt, count in self.thoughts_by_type.items()}
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logging.debug("[InnerMonologue] 💾 Monologue state saved")
            
        except Exception as e:
            logging.error(f"[InnerMonologue] ❌ Failed to save monologue state: {e}")
    
    def _load_monologue_state(self):
        """Load monologue state from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load mental state
                if "mental_state" in data:
                    ms = data["mental_state"]
                    self.mental_activity_level = ms.get("mental_activity_level", self.mental_activity_level)
                    self.focus_level = ms.get("focus_level", self.focus_level)
                    self.creativity_level = ms.get("creativity_level", self.creativity_level)
                    self.contemplation_depth = ms.get("contemplation_depth", self.contemplation_depth)
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.total_thoughts = m.get("total_thoughts", 0)
                    self.insights_generated = m.get("insights_generated", 0)
                    if "thoughts_by_type" in m:
                        for tt_str, count in m["thoughts_by_type"].items():
                            try:
                                tt = ThoughtType(tt_str)
                                self.thoughts_by_type[tt] = count
                            except ValueError:
                                pass
                
                logging.info("[InnerMonologue] 📂 Monologue state loaded from storage")
            
        except Exception as e:
            logging.error(f"[InnerMonologue] ❌ Failed to load monologue state: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get inner monologue statistics"""
        return {
            "total_thoughts": self.total_thoughts,
            "insights_generated": self.insights_generated,
            "current_thought": self.current_thought.content if self.current_thought else None,
            "mental_activity_level": round(self.mental_activity_level, 2),
            "focus_level": round(self.focus_level, 2),
            "creativity_level": round(self.creativity_level, 2),
            "contemplation_depth": round(self.contemplation_depth, 2),
            "idle_mode": self.idle_mode,
            "thought_stream_length": len(self.thought_stream),
            "thoughts_by_type": {tt.value: count for tt, count in self.thoughts_by_type.items()},
            "subscribers": len(self.thought_subscribers)
        }

# Global instance
inner_monologue = InnerMonologue()