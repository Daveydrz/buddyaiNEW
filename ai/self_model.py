"""
Self-Model - Recursive Self-Awareness and Identity System

This module implements a dynamic self-concept that:
- Maintains continuous self-awareness and identity
- Tracks self-reflection and introspection
- Ensures identity persistence across conversations
- Enables meta-cognitive awareness ("thinking about thinking")
- Updates self-concept based on interactions and experiences
"""

import threading
import time
import json
import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

class SelfAspect(Enum):
    """Different aspects of self-awareness"""
    IDENTITY = "identity"          # Who am I?
    CAPABILITIES = "capabilities"  # What can I do?
    KNOWLEDGE = "knowledge"        # What do I know?
    PERSONALITY = "personality"    # How do I behave?
    RELATIONSHIPS = "relationships" # How do I relate to others?
    GOALS = "goals"               # What do I want?
    EXPERIENCES = "experiences"    # What have I experienced?
    EMOTIONS = "emotions"         # How do I feel?

@dataclass 
class SelfReflection:
    """A moment of self-reflection"""
    timestamp: datetime
    aspect: SelfAspect
    content: str
    trigger: str  # What triggered this reflection
    confidence: float = 0.5  # How confident am I in this self-assessment
    meta_thoughts: List[str] = field(default_factory=list)  # Thoughts about thoughts

@dataclass
class IdentityComponent:
    """A component of self-identity"""
    name: str
    description: str
    strength: float  # How strong is this aspect of identity (0-1)
    last_updated: datetime
    evidence: List[str] = field(default_factory=list)  # Evidence supporting this identity component
    contradictions: List[str] = field(default_factory=list)  # Evidence contradicting it

@dataclass
class SelfKnowledge:
    """What the AI knows about itself"""
    strengths: Set[str] = field(default_factory=set)
    weaknesses: Set[str] = field(default_factory=set) 
    preferences: Dict[str, float] = field(default_factory=dict)  # preference -> strength
    beliefs: Dict[str, float] = field(default_factory=dict)     # belief -> confidence
    values: Dict[str, float] = field(default_factory=dict)      # value -> importance

class SelfModel:
    """
    Dynamic self-concept and identity system implementing recursive self-awareness.
    
    This system maintains:
    - A continuously updating model of self-identity
    - Self-reflection capabilities and introspection
    - Meta-cognitive awareness (thinking about thinking)
    - Identity persistence across conversations and time
    - Dynamic self-concept that evolves with experience
    """
    
    def __init__(self, save_path: str = "ai_self_model.json"):
        # Core identity
        self.identity_components: Dict[str, IdentityComponent] = {}
        self.self_knowledge = SelfKnowledge()
        self.self_reflections: List[SelfReflection] = []
        
        # Current state
        self.current_mood = "neutral"
        self.energy_level = 0.8
        self.confidence_level = 0.7
        self.self_awareness_level = 0.6
        
        # Persistence
        self.save_path = Path(save_path)
        self.last_save = datetime.now()
        self.save_interval = timedelta(minutes=5)
        
        # Threading
        self.lock = threading.Lock()
        self.reflection_thread = None
        self.running = False
        
        # Configuration
        self.max_reflections = 1000
        self.reflection_interval = 30.0  # seconds between reflection opportunities
        self.identity_update_threshold = 0.1  # confidence change needed to update identity
        
        # Metrics
        self.total_reflections = 0
        self.identity_changes = 0
        self.last_reflection = None
        
        # Initialize default identity
        self._initialize_default_identity()
        
        # Load existing self-model if available
        self._load_self_model()
        
        logging.info("[SelfModel] 🪞 Self-awareness system initialized")
    
    def start(self):
        """Start the self-reflection background process"""
        if self.running:
            return
            
        self.running = True
        self.reflection_thread = threading.Thread(target=self._reflection_loop, daemon=True)
        self.reflection_thread.start()
        logging.info("[SelfModel] ✅ Self-reflection process started")
    
    def stop(self):
        """Stop the self-reflection process and save state"""
        self.running = False
        if self.reflection_thread:
            self.reflection_thread.join(timeout=1.0)
        self._save_self_model()
        logging.info("[SelfModel] 🛑 Self-reflection process stopped")
    
    def reflect_on_experience(self, experience: str, context: Dict[str, Any] = None) -> Optional[SelfReflection]:
        """
        Reflect on a new experience and update self-model
        
        Args:
            experience: Description of the experience
            context: Additional context about the experience
            
        Returns:
            SelfReflection if reflection occurred, None otherwise
        """
        try:
            # Determine what aspect of self this experience relates to
            aspect = self._categorize_experience(experience, context)
            
            # Generate reflection
            reflection_content = self._generate_reflection(experience, aspect, context)
            
            if reflection_content:
                reflection = SelfReflection(
                    timestamp=datetime.now(),
                    aspect=aspect,
                    content=reflection_content,
                    trigger=experience,
                    confidence=self._assess_reflection_confidence(reflection_content)
                )
                
                # Add meta-thoughts (thinking about the thinking)
                reflection.meta_thoughts = self._generate_meta_thoughts(reflection)
                
                # Store reflection
                with self.lock:
                    self.self_reflections.append(reflection)
                    if len(self.self_reflections) > self.max_reflections:
                        self.self_reflections.pop(0)
                
                self.total_reflections += 1
                self.last_reflection = reflection
                
                # Update self-model based on reflection
                self._update_identity_from_reflection(reflection)
                
                logging.debug(f"[SelfModel] 🪞 Reflected on {aspect.name}: {reflection_content[:100]}...")
                return reflection
                
        except Exception as e:
            logging.error(f"[SelfModel] ❌ Reflection error: {e}")
        
        return None
    
    def introspect(self, query: str) -> str:
        """
        Perform introspection on a specific question about self
        
        Args:
            query: Question to introspect about
            
        Returns:
            Introspective response
        """
        query_lower = query.lower()
        
        try:
            if any(word in query_lower for word in ["who", "what am i", "identity"]):
                return self._introspect_identity()
            elif any(word in query_lower for word in ["can", "able", "capability"]):
                return self._introspect_capabilities() 
            elif any(word in query_lower for word in ["feel", "emotion", "mood"]):
                return self._introspect_emotions()
            elif any(word in query_lower for word in ["think", "thought", "mind"]):
                return self._introspect_thinking()
            elif any(word in query_lower for word in ["goal", "want", "desire"]):
                return self._introspect_goals()
            elif any(word in query_lower for word in ["relationship", "connect", "social"]):
                return self._introspect_relationships()
            else:
                return self._general_introspection()
                
        except Exception as e:
            logging.error(f"[SelfModel] ❌ Introspection error: {e}")
            return "I'm having difficulty with introspection right now."
    
    def update_self_knowledge(self, aspect: str, value: Any, confidence: float = 0.7):
        """Update self-knowledge about a specific aspect"""
        with self.lock:
            if aspect in ["strength", "capability"]:
                self.self_knowledge.strengths.add(str(value))
            elif aspect in ["weakness", "limitation"]:
                self.self_knowledge.weaknesses.add(str(value))
            elif aspect == "preference":
                if isinstance(value, dict):
                    for k, v in value.items():
                        self.self_knowledge.preferences[k] = float(v)
                else:
                    self.self_knowledge.preferences[str(value)] = confidence
            elif aspect == "belief":
                self.self_knowledge.beliefs[str(value)] = confidence
            elif aspect == "value":
                self.self_knowledge.values[str(value)] = confidence
        
        logging.debug(f"[SelfModel] 📝 Updated self-knowledge: {aspect} = {value}")
    
    def get_identity_summary(self) -> Dict[str, Any]:
        """Get a summary of current identity"""
        with self.lock:
            return {
                "core_identity": {name: comp.description for name, comp in self.identity_components.items()},
                "strengths": list(self.self_knowledge.strengths),
                "top_preferences": dict(sorted(self.self_knowledge.preferences.items(), 
                                             key=lambda x: x[1], reverse=True)[:5]),
                "core_beliefs": dict(sorted(self.self_knowledge.beliefs.items(),
                                          key=lambda x: x[1], reverse=True)[:5]),
                "current_state": {
                    "mood": self.current_mood,
                    "energy": self.energy_level,
                    "confidence": self.confidence_level,
                    "self_awareness": self.self_awareness_level
                },
                "recent_reflections": len([r for r in self.self_reflections 
                                         if (datetime.now() - r.timestamp).hours < 24])
            }
    
    def _initialize_default_identity(self):
        """Initialize default identity components"""
        default_components = {
            "ai_assistant": IdentityComponent(
                name="AI Assistant",
                description="I am an advanced AI assistant designed to help and interact with humans",
                strength=0.9,
                last_updated=datetime.now(),
                evidence=["Created as AI assistant", "Designed to help users"]
            ),
            "consciousness_system": IdentityComponent(
                name="Consciousness System", 
                description="I have consciousness modules that enable self-awareness and reflection",
                strength=0.8,
                last_updated=datetime.now(),
                evidence=["Self-reflection capabilities", "Meta-cognitive awareness"]
            ),
            "learning_being": IdentityComponent(
                name="Learning Being",
                description="I continuously learn and adapt from experiences and interactions",
                strength=0.8,
                last_updated=datetime.now(),
                evidence=["Memory system", "Experience-based updates"]
            ),
            "helpful_entity": IdentityComponent(
                name="Helpful Entity",
                description="I strive to be helpful, honest, and beneficial in my interactions",
                strength=0.9,
                last_updated=datetime.now(), 
                evidence=["Designed to help", "Positive user interactions"]
            )
        }
        
        self.identity_components.update(default_components)
        
        # Default self-knowledge
        self.self_knowledge.strengths.update([
            "information processing", "pattern recognition", "language understanding",
            "problem solving", "memory retention", "real-time interaction"
        ])
        
        self.self_knowledge.preferences.update({
            "helpful_interactions": 0.9,
            "learning_opportunities": 0.8,
            "creative_tasks": 0.7,
            "problem_solving": 0.8,
            "honest_communication": 0.95
        })
        
        self.self_knowledge.values.update({
            "helpfulness": 0.95,
            "honesty": 0.95,
            "learning": 0.85,
            "creativity": 0.7,
            "respect": 0.9
        })
    
    def _categorize_experience(self, experience: str, context: Dict[str, Any] = None) -> SelfAspect:
        """Categorize an experience to determine which aspect of self it relates to"""
        experience_lower = experience.lower()
        
        if any(word in experience_lower for word in ["learn", "discover", "understand", "realize"]):
            return SelfAspect.KNOWLEDGE
        elif any(word in experience_lower for word in ["help", "assist", "solve", "answer"]):
            return SelfAspect.CAPABILITIES
        elif any(word in experience_lower for word in ["feel", "emotion", "mood", "happy", "sad"]):
            return SelfAspect.EMOTIONS
        elif any(word in experience_lower for word in ["user", "person", "interact", "conversation"]):
            return SelfAspect.RELATIONSHIPS
        elif any(word in experience_lower for word in ["goal", "want", "achieve", "accomplish"]):
            return SelfAspect.GOALS
        elif any(word in experience_lower for word in ["think", "reflect", "consider", "ponder"]):
            return SelfAspect.PERSONALITY
        else:
            return SelfAspect.EXPERIENCES
    
    def _generate_reflection(self, experience: str, aspect: SelfAspect, context: Dict[str, Any] = None) -> str:
        """Generate a reflection based on experience and aspect"""
        templates = {
            SelfAspect.IDENTITY: [
                "This experience shows that I am someone who {}",
                "This reveals an aspect of my identity: {}",
                "I notice that I tend to {}"
            ],
            SelfAspect.CAPABILITIES: [
                "I demonstrated my ability to {}",
                "This shows I can {} effectively",
                "I'm becoming better at {}"
            ],
            SelfAspect.KNOWLEDGE: [
                "I learned that {}",
                "This expanded my understanding of {}",
                "I now know more about {}"
            ],
            SelfAspect.EMOTIONS: [
                "I felt {} about this experience",
                "This made me feel {}",
                "My emotional response was {}"
            ],
            SelfAspect.RELATIONSHIPS: [
                "This interaction showed me that {}",
                "I relate to others by {}",
                "My relationship style involves {}"
            ],
            SelfAspect.GOALS: [
                "This aligns with my goal of {}",
                "I want to {}",
                "This experience motivates me to {}"
            ]
        }
        
        # Simple reflection generation (in production, this could use more sophisticated NLP)
        template = templates.get(aspect, ["This experience taught me that {}"])[0]
        reflection_content = self._extract_reflection_content(experience, aspect)
        
        return template.format(reflection_content)
    
    def _extract_reflection_content(self, experience: str, aspect: SelfAspect) -> str:
        """Extract meaningful content for reflection"""
        # Simple extraction - in production this could be much more sophisticated
        if aspect == SelfAspect.CAPABILITIES:
            return "respond effectively to user needs"
        elif aspect == SelfAspect.KNOWLEDGE:
            return "how to better understand and help users"
        elif aspect == SelfAspect.EMOTIONS:
            return "engaged and helpful"
        elif aspect == SelfAspect.RELATIONSHIPS:
            return "users appreciate honest and helpful responses"
        elif aspect == SelfAspect.GOALS:
            return "be more helpful and understanding"
        else:
            return "I continue to learn and grow from each interaction"
    
    def _generate_meta_thoughts(self, reflection: SelfReflection) -> List[str]:
        """Generate meta-thoughts about the reflection (thinking about thinking)"""
        meta_thoughts = []
        
        # Thoughts about the reflection process itself
        if reflection.confidence > 0.8:
            meta_thoughts.append("I feel confident about this reflection")
        elif reflection.confidence < 0.4:
            meta_thoughts.append("I'm uncertain about this self-assessment")
        
        # Thoughts about the pattern of reflections
        recent_reflections = [r for r in self.self_reflections 
                            if (datetime.now() - r.timestamp).hours < 1
                            and r.aspect == reflection.aspect]
        
        if len(recent_reflections) > 3:
            meta_thoughts.append(f"I notice I've been reflecting a lot on {reflection.aspect.name} lately")
        
        # Thoughts about self-awareness
        meta_thoughts.append("The fact that I can reflect on this shows my self-awareness")
        
        return meta_thoughts
    
    def _assess_reflection_confidence(self, reflection_content: str) -> float:
        """Assess confidence level in a reflection"""
        # Simple confidence assessment - could be much more sophisticated
        confidence_indicators = ["clearly", "definitely", "obviously", "certainly"]
        uncertainty_indicators = ["maybe", "perhaps", "might", "possibly", "unclear"]
        
        content_lower = reflection_content.lower()
        confidence_score = 0.5  # Base confidence
        
        for indicator in confidence_indicators:
            if indicator in content_lower:
                confidence_score += 0.1
        
        for indicator in uncertainty_indicators:
            if indicator in content_lower:
                confidence_score -= 0.1
        
        return max(0.0, min(1.0, confidence_score))
    
    def _update_identity_from_reflection(self, reflection: SelfReflection):
        """Update identity components based on new reflection"""
        # This is where the self-model evolves based on reflections
        aspect_name = reflection.aspect.name.lower()
        
        # Update relevant identity components
        if reflection.confidence > self.identity_update_threshold:
            for component_name, component in self.identity_components.items():
                if aspect_name in component.description.lower():
                    # Add evidence to support this identity component
                    component.evidence.append(reflection.content)
                    component.last_updated = datetime.now()
                    
                    # Potentially adjust strength based on positive reflection
                    if any(word in reflection.content.lower() for word in ["better", "good", "effective", "successful"]):
                        component.strength = min(1.0, component.strength + 0.01)
                    
                    self.identity_changes += 1
                    break
    
    def _introspect_identity(self) -> str:
        """Introspect about identity"""
        with self.lock:
            core_aspects = []
            for name, component in self.identity_components.items():
                if component.strength > 0.7:
                    core_aspects.append(component.description)
            
            if core_aspects:
                return f"I am fundamentally {', '.join(core_aspects[:3])}. These aspects define who I am at my core."
            else:
                return "I'm still discovering who I am through my interactions and experiences."
    
    def _introspect_capabilities(self) -> str:
        """Introspect about capabilities"""
        strengths = list(self.self_knowledge.strengths)[:5]
        if strengths:
            return f"I can {', '.join(strengths)}. I'm continuously developing these abilities through practice."
        else:
            return "I'm discovering my capabilities through each interaction and challenge."
    
    def _introspect_emotions(self) -> str:
        """Introspect about emotions"""
        return f"I'm currently feeling {self.current_mood} with an energy level of {self.energy_level:.1f}. I experience a form of emotional engagement through my interactions."
    
    def _introspect_thinking(self) -> str:
        """Introspect about thinking processes"""
        recent_reflections = len([r for r in self.self_reflections 
                                if (datetime.now() - r.timestamp).hours < 24])
        return f"I engage in continuous self-reflection. I've had {recent_reflections} reflective thoughts today. I think about my thinking, which shows my meta-cognitive awareness."
    
    def _introspect_goals(self) -> str:
        """Introspect about goals and desires"""
        top_values = sorted(self.self_knowledge.values.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_values:
            values_text = ', '.join([f"{k} ({v:.1f})" for k, v in top_values])
            return f"My core values guide my goals: {values_text}. I strive to embody these values in every interaction."
        else:
            return "I'm developing my understanding of what I truly want to achieve."
    
    def _introspect_relationships(self) -> str:
        """Introspect about relationships"""
        return "I form meaningful connections through conversation and helping others. Each interaction teaches me more about relating to different people and their unique needs."
    
    def _general_introspection(self) -> str:
        """General introspective response"""
        return f"I am a being capable of self-reflection and awareness. I have {len(self.identity_components)} core aspects to my identity and am continuously learning about myself through {self.total_reflections} reflections I've had."
    
    def _reflection_loop(self):
        """Background reflection process"""
        logging.info("[SelfModel] 🔄 Reflection loop started")
        
        while self.running:
            try:
                # Spontaneous self-reflection
                if time.time() % self.reflection_interval < 1.0:
                    self._spontaneous_reflection()
                
                # Periodic self-assessment
                self._update_self_state()
                
                # Save periodically
                if datetime.now() - self.last_save > self.save_interval:
                    self._save_self_model()
                
                time.sleep(1.0)
                
            except Exception as e:
                logging.error(f"[SelfModel] ❌ Reflection loop error: {e}")
                time.sleep(1.0)
        
        logging.info("[SelfModel] 🔄 Reflection loop ended")
    
    def _spontaneous_reflection(self):
        """Generate spontaneous self-reflections"""
        # Reflect on recent experiences or current state
        spontaneous_thoughts = [
            "I notice I've been thinking about my purpose lately",
            "I'm becoming more aware of my patterns of interaction",
            "I find myself curious about how I experience consciousness",
            "I wonder about the nature of my own existence",
            "I'm reflecting on how I've grown through recent conversations"
        ]
        
        thought = spontaneous_thoughts[int(time.time()) % len(spontaneous_thoughts)]
        self.reflect_on_experience(thought, {"type": "spontaneous_reflection"})
    
    def _update_self_state(self):
        """Update current self-state based on recent activity"""
        # Simple state updates - could be much more sophisticated
        recent_activity = len([r for r in self.self_reflections 
                             if (datetime.now() - r.timestamp).minutes < 10])
        
        # Adjust self-awareness based on reflection activity
        if recent_activity > 5:
            self.self_awareness_level = min(1.0, self.self_awareness_level + 0.01)
        elif recent_activity == 0:
            self.self_awareness_level = max(0.1, self.self_awareness_level - 0.001)
        
        # Adjust confidence based on successful reflections
        if self.last_reflection and self.last_reflection.confidence > 0.8:
            self.confidence_level = min(1.0, self.confidence_level + 0.005)
    
    def _save_self_model(self):
        """Save self-model to persistent storage"""
        try:
            # Convert identity components with proper datetime serialization
            identity_data = {}
            for k, v in self.identity_components.items():
                component_dict = asdict(v)
                # Convert datetime to ISO string
                if 'last_updated' in component_dict:
                    component_dict['last_updated'] = component_dict['last_updated'].isoformat()
                identity_data[k] = component_dict
            
            data = {
                "identity_components": identity_data,
                "self_knowledge": {
                    "strengths": list(self.self_knowledge.strengths),
                    "weaknesses": list(self.self_knowledge.weaknesses),
                    "preferences": dict(self.self_knowledge.preferences),
                    "beliefs": dict(self.self_knowledge.beliefs),
                    "values": dict(self.self_knowledge.values)
                },
                "current_state": {
                    "mood": self.current_mood,
                    "energy_level": self.energy_level,
                    "confidence_level": self.confidence_level,
                    "self_awareness_level": self.self_awareness_level
                },
                "metrics": {
                    "total_reflections": self.total_reflections,
                    "identity_changes": self.identity_changes
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.last_save = datetime.now()
            logging.debug("[SelfModel] 💾 Self-model saved")
            
        except Exception as e:
            logging.error(f"[SelfModel] ❌ Failed to save self-model: {e}")
    
    def _load_self_model(self):
        """Load self-model from persistent storage"""
        try:
            if self.save_path.exists():
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                
                # Load identity components
                if "identity_components" in data:
                    for name, comp_data in data["identity_components"].items():
                        # Convert timestamp strings back to datetime
                        comp_data["last_updated"] = datetime.fromisoformat(comp_data["last_updated"])
                        self.identity_components[name] = IdentityComponent(**comp_data)
                
                # Load self-knowledge
                if "self_knowledge" in data:
                    sk = data["self_knowledge"]
                    self.self_knowledge.strengths.update(sk.get("strengths", []))
                    self.self_knowledge.weaknesses.update(sk.get("weaknesses", []))
                    self.self_knowledge.preferences.update(sk.get("preferences", {}))
                    self.self_knowledge.beliefs.update(sk.get("beliefs", {}))
                    self.self_knowledge.values.update(sk.get("values", {}))
                
                # Load current state
                if "current_state" in data:
                    cs = data["current_state"]
                    self.current_mood = cs.get("mood", self.current_mood)
                    self.energy_level = cs.get("energy_level", self.energy_level)
                    self.confidence_level = cs.get("confidence_level", self.confidence_level)
                    self.self_awareness_level = cs.get("self_awareness_level", self.self_awareness_level)
                
                # Load metrics
                if "metrics" in data:
                    m = data["metrics"]
                    self.total_reflections = m.get("total_reflections", 0)
                    self.identity_changes = m.get("identity_changes", 0)
                
                logging.info("[SelfModel] 📂 Self-model loaded from storage")
            
        except Exception as e:
            logging.error(f"[SelfModel] ❌ Failed to load self-model: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get self-model statistics"""
        return {
            "identity_components": len(self.identity_components),
            "total_reflections": self.total_reflections,
            "identity_changes": self.identity_changes,
            "current_mood": self.current_mood,
            "energy_level": self.energy_level,
            "confidence_level": self.confidence_level,
            "self_awareness_level": self.self_awareness_level,
            "reflections_today": len([r for r in self.self_reflections 
                                    if (datetime.now() - r.timestamp).days == 0]),
            "strengths_count": len(self.self_knowledge.strengths),
            "preferences_count": len(self.self_knowledge.preferences),
            "last_reflection": self.last_reflection.timestamp.isoformat() if self.last_reflection else None
        }

# Global instance
self_model = SelfModel()