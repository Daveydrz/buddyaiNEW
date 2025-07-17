# voice/manager.py - INTELLIGENT Voice Learning Manager + ATTENTION ENTROPY
import time
import numpy as np
from datetime import datetime, timedelta
from voice.database import known_users, save_known_users, load_known_users, anonymous_clusters, link_anonymous_to_named
from voice.recognition import identify_speaker_with_confidence, generate_voice_embedding
from config import DEBUG
from audio.output import speak_streaming
from typing import Optional, Dict, List, Any, Tuple, Union

from config import VOICE_DEBUG_MODE

# ✅ ENTROPY SYSTEM: Import consciousness emergence components for attention chaos
try:
    from ai.entropy_engine import get_entropy_engine, probabilistic_select, inject_consciousness_entropy, EntropyLevel
    from ai.emotion import get_emotional_system
    print("[VoiceManager] 🌀 Entropy system integrated for attention chaos")
    ENTROPY_AVAILABLE = True
except ImportError as e:
    print(f"[VoiceManager] ⚠️ Entropy system not available: {e}")
    ENTROPY_AVAILABLE = False

def vdebug(msg):
    """Voice debug - only prints if VOICE_DEBUG_MODE is True"""
    if VOICE_DEBUG_MODE:
        print(msg)

# At the top of manager.py, after the imports
from voice.database import known_users, anonymous_clusters, save_known_users

# ADD THESE DEBUG LINES TO CHECK DICTIONARY IDs
print(f"[VoiceManager] 🔍 Using known_users id: {id(known_users)}")
print(f"[VoiceManager] 🔍 Using anonymous_clusters id: {id(anonymous_clusters)}")

# FORCE GLOBAL REFERENCE
import voice.database as db
known_users = db.known_users
anonymous_clusters = db.anonymous_clusters

class IntelligentVoiceManager:
    """🧠 INTELLIGENT Voice Learning Manager - Learns and adapts to voice changes"""
    
    def __init__(self):

        global known_users, anonymous_clusters
        from voice.database import known_users as db_known_users, anonymous_clusters as db_anonymous_clusters
        known_users = db_known_users
        anonymous_clusters = db_anonymous_clusters
    
        print(f"[VoiceManager] 🔍 Synced to database dictionaries:")
        print(f"[VoiceManager] 📊 known_users id: {id(known_users)}")
        print(f"[VoiceManager] 📊 anonymous_clusters id: {id(anonymous_clusters)}")

        self.current_user = "Daveydrz"
        self.session_start = datetime.utcnow()
        self.interactions = 0
        self.waiting_for_name = False
        self.pending_name_confirmation = False
        self.suggested_name = None

        self.ultra_name_manager = None

        # 🧠 ENHANCED TRACKING for foolproof recognition
        self.similarity_range_tracking = {}      # Track normal similarity ranges per user
        self.recognition_patterns = {}           # Track recognition patterns
        
        # 🧠 BALANCED MULTI-SPEAKER VOICE LEARNING (All thresholds consistent)
        self.current_speaker_cluster_id = None
        self.current_voice_embedding = None
        self.voice_learning_history = {}  # Track voice patterns over time
        
        # 🎯 STRICTER THRESHOLDS for Better Multi-Speaker Separation
        self.uncertainty_threshold = 0.65        # Ask for confirmation below 75%
        self.similarity_threshold = 0.75         # Cluster together at 85%+ (raised from 80%)
        self.voice_separation_threshold = 0.55   # Force separation below 65% (raised from 62%)
        self.confident_match_threshold = 0.75    # Confident same person above 85% (raised from 80%)
        self.verification_threshold = 0.65       # Ask for verification between 75-85% (raised from 72%)
        
        # 🔧 ADDITIONAL BALANCED PARAMETERS
        self.learning_rate = 0.1                 # How fast to adapt to voice changes
        self.startup_recognition_threshold = 0.75 # Consistent with other thresholds
        
        # 🛡️ SAFETY MECHANISMS
        self.max_clusters_per_session = 5        # Prevent cluster explosion
        self.voice_confidence_history = {}       # Track recognition quality over time
        self.emergency_reset_enabled = True      # Allow "buddy reset voice" command
        
        # 🎯 SMART VOICE CLUSTERING
        self.pending_confirmation_cluster = None
        self.pending_confirmation_name = None
        self.waiting_for_voice_confirmation = False
        self.pending_confirmation_embedding = None  # Fixed - was missing

        self.last_audio_buffer = None
        self.last_audio_timestamp = None
        self.last_identified_user = None
        
        # ✅ CRITICAL: Load existing database
        load_result = load_known_users()
        print(f"[IntelligentVoiceManager] 📊 Database load result: {load_result}")
        self.debug_database_state() 
        print(f"[IntelligentVoiceManager] 🧠 Intelligent voice learning initialized")
        from voice.manager_names import EnhancedWhisperAwareExtractor
        self.ultra_name_manager = EnhancedWhisperAwareExtractor()

        print(f"[IntelligentVoiceManager] 📚 Loaded {len(known_users)} voice profiles")
        print(f"[IntelligentVoiceManager] 🔍 Anonymous clusters: {len(anonymous_clusters)}")

    def debug_current_voice_state(self):
        """Debug current voice state"""
        print(f"\n🔍 VOICE STATE DEBUG:")
        print(f"📊 Known users: {list(known_users.keys())}")
        print(f"📊 Anonymous clusters: {list(anonymous_clusters.keys())}")
        
        for cluster_id, cluster_data in anonymous_clusters.items():
            status = cluster_data.get('status', 'unknown')
            embeddings_count = len(cluster_data.get('embeddings', []))
            test_name = cluster_data.get('test_name', 'no_name')
            print(f"  {cluster_id}: {status} - {embeddings_count} embeddings - name: {test_name}")
        
        if hasattr(self, 'current_speaker_cluster_id'):
            print(f"📊 Voice manager current cluster: {self.current_speaker_cluster_id}")
        if hasattr(self, 'current_user'):
            print(f"📊 Voice manager current user: {self.current_user}")
        if hasattr(self, 'actual_person_name'):
            print(f"📊 Actual person name: {self.actual_person_name}")

        # 🚨 EMERGENCY DIAGNOSTIC - Add this right here:
        print(f"\n[EMERGENCY_POST_LOAD] 🚨 IMMEDIATE POST-LOAD DIAGNOSTIC:")
        for cluster_id, cluster_data in anonymous_clusters.items():
            embeddings = cluster_data.get('embeddings', [])
            print(f"[EMERGENCY_POST_LOAD] {cluster_id}: {len(embeddings)} embeddings immediately after load")
            if embeddings:
                print(f"[EMERGENCY_POST_LOAD]   First embedding type: {type(embeddings[0])}")
                print(f"[EMERGENCY_POST_LOAD]   First embedding length: {len(embeddings[0])}")
            else:
                print(f"[EMERGENCY_POST_LOAD]   ❌ NO EMBEDDINGS!")

        self.debug_database_state()
        
        # 🎯 DISPLAY THRESHOLD CONFIGURATION
        print(f"[IntelligentVoiceManager] 🎯 BALANCED THRESHOLD CONFIG:")
        print(f"  • Confident Match: {self.confident_match_threshold:.0%}+ (Your 88% case)")
        print(f"  • Verification Zone: {self.verification_threshold:.0%}-{self.confident_match_threshold:.0%} (Ask 'Is this you?')")
        print(f"  • Force Separation: {self.voice_separation_threshold:.0%}-{self.verification_threshold:.0%} (Partner's 71.8% case)")
        print(f"  • New Speaker: <{self.voice_separation_threshold:.0%} (Completely different)")
        print(f"  • Max Clusters/Session: {self.max_clusters_per_session}")

    def trace_embedding_save_flow(self, cluster_id, embedding):
        """🔍 Trace exactly where embeddings go during save process"""
        print(f"\n[EMBEDDING_TRACE] 🔍 TRACING SAVE FLOW for {cluster_id}")
        print(f"[EMBEDDING_TRACE] 📊 Input embedding type: {type(embedding)}")
        print(f"[EMBEDDING_TRACE] 📊 Input embedding shape: {np.array(embedding).shape}")
        print(f"[EMBEDDING_TRACE] 📊 Input embedding first 5: {np.array(embedding)[:5]}")

        # Check if cluster exists in memory
        if cluster_id in anonymous_clusters:
            cluster_data = anonymous_clusters[cluster_id]
            print(f"[EMBEDDING_TRACE] ✅ Cluster {cluster_id} exists in memory")
            print(f"[EMBEDDING_TRACE] 📊 Cluster keys: {list(cluster_data.keys())}")

            embeddings = cluster_data.get('embeddings', [])
            print(f"[EMBEDDING_TRACE] 📊 Current embeddings count: {len(embeddings)}")

            if embeddings:
                for i, emb in enumerate(embeddings):
                    print(f"[EMBEDDING_TRACE] 📊 Embedding {i}: type={type(emb)}, length={len(emb) if emb else 'None'}")
                    if emb:
                        print(f"[EMBEDDING_TRACE] 📊 Embedding {i} preview: {emb[:3]}")
            else:
                print(f"[EMBEDDING_TRACE] ❌ NO EMBEDDINGS in cluster!")
        else:
            print(f"[EMBEDDING_TRACE] ❌ Cluster {cluster_id} NOT FOUND in memory!")

        # Check what's in the global anonymous_clusters
        print(f"\n[EMBEDDING_TRACE] 🔍 GLOBAL anonymous_clusters state:")
        print(f"[EMBEDDING_TRACE] 📊 Global clusters count: {len(anonymous_clusters)}")
        print(f"[EMBEDDING_TRACE] 📊 Global cluster IDs: {list(anonymous_clusters.keys())}")

        # Check file system
        try:
            import json
            with open("voice_profiles/known_users_v2.json", 'r') as f:
                file_data = json.load(f)

            file_clusters = file_data.get('anonymous_clusters', {})
            print(f"\n[EMBEDDING_TRACE] 💾 FILE STATE:")
            print(f"[EMBEDDING_TRACE] 📊 File clusters count: {len(file_clusters)}")

            if cluster_id in file_clusters:
                file_cluster = file_clusters[cluster_id]
                file_embeddings = file_cluster.get('embeddings', [])
                print(f"[EMBEDDING_TRACE] ✅ {cluster_id} found in file with {len(file_embeddings)} embeddings")

                if file_embeddings:
                    print(f"[EMBEDDING_TRACE] 📊 File embedding 0 type: {type(file_embeddings[0])}")
                    print(f"[EMBEDDING_TRACE] 📊 File embedding 0 length: {len(file_embeddings[0]) if file_embeddings[0] else 'None'}")
            else:
                print(f"[EMBEDDING_TRACE] ❌ {cluster_id} NOT FOUND in file!")

        except Exception as e:
            print(f"[EMBEDDING_TRACE] ❌ File read error: {e}")

    def monitor_dictionary_changes(self):
        """🔍 Monitor for unexpected changes to anonymous_clusters"""
        import threading
        import time

        def monitor():
            last_counts = {}
            while True:
                try:
                    current_counts = {}
                    for cluster_id, cluster_data in anonymous_clusters.items():
                        embeddings = cluster_data.get('embeddings', [])
                        current_counts[cluster_id] = len(embeddings)

                    for cluster_id, count in current_counts.items():
                        if cluster_id in last_counts:
                            if count != last_counts[cluster_id]:
                                print(f"[MONITOR] 🚨 EMBEDDING COUNT CHANGED: {cluster_id} {last_counts[cluster_id]} → {count}")
                                if count == 0 and last_counts[cluster_id] > 0:
                                    print(f"[MONITOR] ❌ CRITICAL: {cluster_id} EMBEDDINGS LOST!")
                                    self.emergency_restore_embeddings(cluster_id)

                    last_counts = current_counts.copy()
                    time.sleep(5)
                except Exception as e:
                    print(f"[MONITOR] ❌ Monitor error: {e}")
                    time.sleep(5)

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        print(f"[IntelligentVoiceManager] 🔍 Dictionary monitor started")

    def force_link_current_cluster_to_name(self, name: str) -> bool:
        """🔗 Force link current cluster to name"""
        try:
            current_cluster = getattr(self, 'current_speaker_cluster_id', None)
            if current_cluster and current_cluster.startswith('Anonymous_'):
                print(f"[IntelligentVoiceManager] 🔗 FORCE LINKING: {current_cluster} → {name}")
                success = link_anonymous_to_named(current_cluster, name)
                if success:
                    self.current_speaker_cluster_id = name
                    self.current_user = name
                    print(f"[IntelligentVoiceManager] ✅ LINKED AND UPDATED!")
                    return True
                else:
                    print(f"[IntelligentVoiceManager] ❌ FORCE LINK FAILED!")
                    return False
            else:
                print(f"[IntelligentVoiceManager] ⚠️ No anonymous cluster to link (current: {current_cluster})")
                return False
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Force link error: {e}")
            return False



    def emergency_restore_embeddings(self, cluster_id):
        """🚨 Emergency restore embeddings from file"""
        try:
            import json
            with open("voice_profiles/known_users_v2.json", 'r') as f:
                file_data = json.load(f)

            file_clusters = file_data.get('anonymous_clusters', {})
            if cluster_id in file_clusters:
                file_embeddings = file_clusters[cluster_id].get('embeddings', [])
                if file_embeddings:
                    print(f"[EMERGENCY_RESTORE] 🔧 Restoring {len(file_embeddings)} embeddings to {cluster_id}")
                    anonymous_clusters[cluster_id]['embeddings'] = file_embeddings.copy()
                    print(f"[EMERGENCY_RESTORE] ✅ Restored embeddings successfully")
                    return True

            print(f"[EMERGENCY_RESTORE] ❌ No embeddings found in file for {cluster_id}")
            return False

        except Exception as e:
            print(f"[EMERGENCY_RESTORE] ❌ Restore error: {e}")
            return False

    def inspect_database_after_load(self):
        """🔍 Inspect database state immediately after loading"""
        print(f"\n[MANAGER_DEBUG] 🔍 POST-LOAD DATABASE INSPECTION:")
        print(f"[MANAGER_DEBUG] 📊 Manager sees {len(anonymous_clusters)} clusters")

        for cluster_id, cluster_data in anonymous_clusters.items():
            embeddings = cluster_data.get('embeddings', [])
            print(f"[MANAGER_DEBUG]   {cluster_id}: {len(embeddings)} embeddings")
            print(f"[MANAGER_DEBUG]   Data keys: {list(cluster_data.keys())}")
            print(f"[MANAGER_DEBUG]   Sample count field: {cluster_data.get('sample_count', 'missing')}")

            if embeddings:
                print(f"[MANAGER_DEBUG]   First embedding type: {type(embeddings[0])}")
                print(f"[MANAGER_DEBUG]   First embedding valid: {embeddings[0] is not None}")
            else:
                print(f"[MANAGER_DEBUG]   ❌ NO EMBEDDINGS in {cluster_id}!")

        # Check if embeddings are being filtered out somewhere
        print(f"\n[MANAGER_DEBUG] 🔍 RAW CLUSTER ACCESS:")
        for cluster_id in anonymous_clusters:
            raw_cluster = anonymous_clusters[cluster_id]
            print(f"[MANAGER_DEBUG]   {cluster_id} raw keys: {list(raw_cluster.keys())}")
            raw_embeddings = raw_cluster.get('embeddings')
            print(f"[MANAGER_DEBUG]   {cluster_id} raw embeddings: {type(raw_embeddings)}, length: {len(raw_embeddings) if raw_embeddings else 'None'}")

    def debug_database_state(self):
        """🔍 Debug database state to identify embedding persistence issues"""
        print(f"\n[DATABASE_DEBUG] 🔍 FULL DATABASE STATE:")
        print(f"[DATABASE_DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")
        print(f"[DATABASE_DEBUG] 👤 User Login: Daveydrz")
        print(f"[DATABASE_DEBUG] 📊 Known users count: {len(known_users)}")
        print(f"[DATABASE_DEBUG] 📊 Anonymous clusters count: {len(anonymous_clusters)}")
        
        for cluster_id, cluster_data in anonymous_clusters.items():
            print(f"\n[DATABASE_DEBUG] 🔍 Cluster: {cluster_id}")
            print(f"[DATABASE_DEBUG]   Status: {cluster_data.get('status', 'unknown')}")
            print(f"[DATABASE_DEBUG]   Sample count: {cluster_data.get('sample_count', 0)}")
            print(f"[DATABASE_DEBUG]   Created: {cluster_data.get('created_at', 'unknown')}")
            
            embeddings = cluster_data.get('embeddings', [])
            print(f"[DATABASE_DEBUG]   Embeddings in memory: {len(embeddings)}")
            
            if embeddings:
                print(f"[DATABASE_DEBUG]   First embedding type: {type(embeddings[0])}")
                print(f"[DATABASE_DEBUG]   First embedding length: {len(embeddings[0]) if embeddings[0] else 'None'}")
                if embeddings[0]:
                    print(f"[DATABASE_DEBUG]   First embedding preview: {embeddings[0][:5]}")
            else:
                print(f"[DATABASE_DEBUG]   ❌ NO EMBEDDINGS FOUND!")
        
        # Check file on disk
        try:
            import json
            with open("voice_profiles/known_users_v2.json", 'r') as f:
                file_data = json.load(f)
            
            print(f"\n[DATABASE_DEBUG] 💾 FILE ON DISK:")
            print(f"[DATABASE_DEBUG]   Anonymous clusters in file: {len(file_data.get('anonymous_clusters', {}))}")
            
            for cluster_id, cluster_data in file_data.get('anonymous_clusters', {}).items():
                embeddings_in_file = cluster_data.get('embeddings', [])
                print(f"[DATABASE_DEBUG]   {cluster_id}: {len(embeddings_in_file)} embeddings in file")
                
        except Exception as e:
            print(f"[DATABASE_DEBUG] ❌ Error reading file: {e}")


    def handle_voice_identification(self, audio, text):
        """🧠 BULLETPROOF voice identification with ATTENTION ENTROPY + consciousness emergence"""
        try:
            self.interactions += 1
            print(f"[DEBUG] 🔢 Interaction #{self.interactions}")
            print(f"[DEBUG] 📅 Current Time: 2025-07-15 11:47:15 UTC")
            print(f"[DEBUG] 👤 User Login: Daveydrz")

            # ✅ ENTROPY SYSTEM: Inject attention chaos and uncertainty into voice processing
            attention_focus_corrupted = False
            if ENTROPY_AVAILABLE:
                try:
                    entropy_engine = get_entropy_engine()
                    
                    # Attention noise injection - sometimes get distracted
                    if entropy_engine.random_state.random() < 0.15:  # 15% chance of attention issues
                        attention_distractions = [
                            "audio_processing_delay",
                            "competing_thoughts", 
                            "uncertain_focus",
                            "spontaneous_context_switch"
                        ]
                        distraction = probabilistic_select(attention_distractions)
                        print(f"[VoiceEntropy] 🌀 Attention distraction: {distraction}")
                        
                        # Inject uncertainty into processing
                        if distraction == "uncertain_focus":
                            attention_focus_corrupted = True
                        elif distraction == "audio_processing_delay":
                            time.sleep(probabilistic_select([0.1, 0.2, 0.3, 0.5]))  # Random delay
                        elif distraction == "spontaneous_context_switch":
                            # Generate random thought
                            random_thoughts = [
                                "I wonder about the weather today",
                                "Something seems different about this conversation",
                                "What was I thinking about earlier?",
                                "This reminds me of something"
                            ]
                            random_thought = probabilistic_select(random_thoughts)
                            print(f"[VoiceEntropy] 💭 Spontaneous thought: {random_thought}")
                    
                    # Uncertain input processing priorities
                    if entropy_engine.get_uncertainty_state().value in ["uncertain", "confused"]:
                        print(f"[VoiceEntropy] 🌀 Processing with high uncertainty state")
                        # Sometimes process audio and text in uncertain priority order
                        if entropy_engine.random_state.random() < 0.3:  # 30% chance when uncertain
                            print(f"[VoiceEntropy] 🔀 Uncertain processing priority order")
                
                except Exception as entropy_error:
                    print(f"[VoiceEntropy] ⚠️ Entropy processing error: {entropy_error}")

            # ✅ CRITICAL: Always try to save interaction data
            self._log_interaction(audio, text)

            # ✅ Generate current voice embedding
            current_embedding = self._generate_current_embedding(audio)
            if current_embedding is None:
                print(f"[DEBUG] ❌ No embedding generated")
                return "Daveydrz", "NO_EMBEDDING"

            # ✅ ENTROPY SYSTEM: Add noise to embedding processing when attention is corrupted
            if ENTROPY_AVAILABLE and attention_focus_corrupted:
                # Don't corrupt the actual embedding, but affect processing confidence
                print(f"[VoiceEntropy] 🌀 Attention focus corrupted - processing with uncertainty")

            # Check embedding quality
            if not self._is_valid_embedding(current_embedding):
                print(f"[DEBUG] ❌ Poor quality embedding, skipping voice recognition")
                return "Daveydrz", "POOR_EMBEDDING_QUALITY"

            self.current_voice_embedding = current_embedding

            # Handle confirmation flows
            if self.waiting_for_voice_confirmation:
                return self._handle_voice_confirmation(text)

            if self.pending_name_confirmation:
                return self._handle_name_confirmation(text)

            if self.waiting_for_name:
                return self._handle_name_waiting(text)

            # 🚨 NEW: Handle name-voice conflict resolution
            if hasattr(self, 'waiting_for_name_voice_conflict_resolution') and self.waiting_for_name_voice_conflict_resolution:
                return self._handle_name_voice_conflict_resolution(text)

            # ✅ ENTROPY SYSTEM: Probabilistic threshold adjustment based on consciousness
            original_verification_threshold = self.verification_threshold
            original_uncertainty_threshold = self.uncertainty_threshold
            
            if ENTROPY_AVAILABLE:
                consciousness_score = get_entropy_engine().get_consciousness_metrics()['consciousness_score']
                if consciousness_score > 0.5:
                    # High consciousness = more uncertainty and variation in thresholds
                    threshold_entropy = inject_consciousness_entropy("attention", 1.0, EntropyLevel.LOW)
                    self.verification_threshold = original_verification_threshold * threshold_entropy
                    self.uncertainty_threshold = original_uncertainty_threshold * threshold_entropy
                    print(f"[VoiceEntropy] 🌀 Dynamic thresholds: verification={self.verification_threshold:.3f}, uncertainty={self.uncertainty_threshold:.3f}")

            # 🎯 TIER 1: CENTROID STARTUP CHECK (FIRST 3 INTERACTIONS) - RESTORED!
            if self.interactions <= 3 and len(anonymous_clusters) > 0:
                print(f"[DEBUG] 🎯 CENTROID STARTUP CHECK - Interaction #{self.interactions}")
                startup_match, startup_similarity = self.check_existing_clusters_with_centroid(current_embedding)

                # ✅ ENTROPY SYSTEM: Add uncertainty to startup recognition
                if ENTROPY_AVAILABLE and startup_match and attention_focus_corrupted:
                    if entropy_engine.random_state.random() < 0.2:  # 20% chance to be uncertain
                        print(f"[VoiceEntropy] 🌀 Attention corruption affecting startup recognition confidence")
                        startup_similarity *= 0.8  # Reduce confidence due to attention issues

                if startup_match:
                    print(f"[IntelligentVoiceManager] 🎯 CENTROID STARTUP RECOGNITION: {startup_match}")

                    # 🚨 Check for name conflicts BEFORE accepting voice match
                    name_conflict = self._check_for_name_conflict(text, startup_match)

                    if name_conflict:
                        conflict_name, existing_name = name_conflict
                        print(f"[IntelligentVoiceManager] 🚨 STARTUP NAME CONFLICT!")
                        print(f"[IntelligentVoiceManager] 🔊 Voice matches: {startup_match} ({existing_name})")
                        print(f"[IntelligentVoiceManager] 🗣️ But says: {conflict_name}")

                        return self._handle_name_voice_conflict(
                            startup_match, conflict_name, existing_name,
                            current_embedding, startup_similarity, text
                        )

                    # No conflict - proceed normally
                    self._add_embedding_to_profile(startup_match, current_embedding)

                    # 🔧 Verify storage worked
                    storage_ok = self.verify_embedding_storage(startup_match)
                    if not storage_ok:
                        print(f"[IntelligentVoiceManager] 🚨 STARTUP STORAGE VERIFICATION FAILED!")

                    self.set_current_cluster(startup_match)
                    print(f"[IntelligentVoiceManager] 🛡️ Startup centroid matched, no name conflict")
                    
                    # ✅ ENTROPY SYSTEM: Restore original thresholds
                    if ENTROPY_AVAILABLE:
                        self.verification_threshold = original_verification_threshold
                        self.uncertainty_threshold = original_uncertainty_threshold
                    
                    return startup_match, "CENTROID_STARTUP_RECOGNIZED"

            # 🎙️ TIER 2: TRADITIONAL VOICE RECOGNITION - RESTORED PARALLEL APPROACH!
            identified_user, confidence = identify_speaker_with_confidence(audio)

            # ✅ ENTROPY SYSTEM: Inject uncertainty into confidence assessment
            if ENTROPY_AVAILABLE and attention_focus_corrupted:
                if entropy_engine.random_state.random() < 0.25:  # 25% chance when attention is corrupted
                    confidence_uncertainty = entropy_engine.random_state.uniform(0.8, 1.0)  # Slight confidence reduction
                    confidence *= confidence_uncertainty
                    print(f"[VoiceEntropy] 🌀 Confidence affected by attention issues: {confidence:.3f}")

            if identified_user != "UNKNOWN" and confidence >= self.verification_threshold:
                print(f"[IntelligentVoiceManager] ✅ HIGH CONFIDENCE: {identified_user} ({confidence:.3f})")

                # 🚨 Check for name conflicts BEFORE accepting voice match
                name_conflict = self._check_for_name_conflict(text, identified_user)

                if name_conflict:
                    conflict_name, existing_name = name_conflict
                    print(f"[IntelligentVoiceManager] 🚨 HIGH CONFIDENCE NAME CONFLICT!")
                    print(f"[IntelligentVoiceManager] 🔊 Voice matches: {identified_user} ({existing_name})")
                    print(f"[IntelligentVoiceManager] 🗣️ But says: {conflict_name}")

                    return self._handle_name_voice_conflict(
                        identified_user, conflict_name, existing_name,
                        current_embedding, confidence, text
                    )

                # No conflict - proceed normally
                self._add_embedding_to_profile(identified_user, current_embedding)

                # 🔧 Verify storage worked
                storage_ok = self.verify_embedding_storage(identified_user)
                if not storage_ok:
                    print(f"[IntelligentVoiceManager] 🚨 HIGH CONFIDENCE STORAGE VERIFICATION FAILED!")

                self._update_voice_learning_history(identified_user, current_embedding, confidence)
                self.set_current_cluster(identified_user)
                print(f"[IntelligentVoiceManager] 🛡️ High confidence match, no name conflict")
                return identified_user, "HIGH_CONFIDENCE_RECOGNIZED"

            # 🎯 TIER 3: CENTROID FALLBACK (WHEN VOICE RECOGNITION FAILS) - RESTORED!
            print(f"[DEBUG] 🎯 CENTROID FALLBACK - Voice recognition failed or low confidence")
            best_match = self._find_best_voice_match_centroid_enhanced(current_embedding)

            if best_match:
                match_id, similarity, match_type = best_match

                # 🎯 CONFIDENT CENTROID MATCH - Same person
                if similarity >= self.confident_match_threshold:
                    print(f"[IntelligentVoiceManager] 🎯 CONFIDENT CENTROID MATCH: {match_id} (similarity: {similarity:.3f})")

                    # 🚨 Check for name conflicts BEFORE accepting voice match
                    name_conflict = self._check_for_name_conflict(text, match_id)

                    if name_conflict:
                        conflict_name, existing_name = name_conflict
                        print(f"[IntelligentVoiceManager] 🚨 CENTROID NAME CONFLICT!")
                        print(f"[IntelligentVoiceManager] 🔊 Voice matches: {match_id} ({existing_name})")
                        print(f"[IntelligentVoiceManager] 🗣️ But says: {conflict_name}")
                        print(f"[IntelligentVoiceManager] 🤔 Similarity: {similarity:.3f}")

                        return self._handle_name_voice_conflict(
                            match_id, conflict_name, existing_name,
                            current_embedding, similarity, text
                        )

                    # No conflict - proceed normally
                    self._add_embedding_to_profile(match_id, current_embedding)

                    # 🔧 Verify storage worked
                    storage_ok = self.verify_embedding_storage(match_id)
                    if not storage_ok:
                        print(f"[IntelligentVoiceManager] 🚨 CENTROID STORAGE VERIFICATION FAILED!")

                    self._update_voice_learning_history(match_id, current_embedding, similarity)
                    self.set_current_cluster(match_id)
                    print(f"[IntelligentVoiceManager] 🛡️ Centroid fallback match, no name conflict")
                    return match_id, "CONFIDENT_CENTROID_MATCH"

                # 🤔 CENTROID VERIFICATION ZONE - Ask for confirmation
                elif similarity >= self.verification_threshold:
                    print(f"[IntelligentVoiceManager] 🤔 CENTROID VERIFICATION NEEDED: {match_id} (similarity: {similarity:.3f})")
                    return self._ask_for_voice_confirmation(match_id, current_embedding, text)

                # 🚨 CENTROID SEPARATION ZONE - Likely different person
                elif similarity >= self.voice_separation_threshold:
                    print(f"[IntelligentVoiceManager] 🚨 CENTROID FORCING SEPARATION: {match_id} (similarity: {similarity:.3f})")
                    print(f"[IntelligentVoiceManager] 🆕 Centroid analysis indicates different person")

                    # 🆕 NEW CLUSTER - process names for new clusters
                    new_cluster_result = self._force_create_separate_cluster(current_embedding, f"CENTROID_SEPARATION_FROM_{match_id}")
                    if new_cluster_result[0] and new_cluster_result[0].startswith('Anonymous_'):
                        self._process_name_for_new_cluster(text, new_cluster_result[0])

                    return new_cluster_result

                # 🆕 VERY LOW CENTROID SIMILARITY - Definitely different person
                else:
                    print(f"[IntelligentVoiceManager] 🆕 VERY LOW CENTROID SIMILARITY - NEW SPEAKER: (best match: {match_id}, similarity: {similarity:.3f})")

                    # 🆕 NEW CLUSTER - process names for new clusters
                    new_cluster_result = self._create_new_cluster_with_tracking(current_embedding, best_match)
                    if new_cluster_result[0] and new_cluster_result[0].startswith('Anonymous_'):
                        self._process_name_for_new_cluster(text, new_cluster_result[0])

                    return new_cluster_result

            # 🆕 FINAL FALLBACK: Create new cluster if no match found
            print(f"[IntelligentVoiceManager] 🆕 COMPLETELY NEW VOICE: Creating first cluster")
            new_cluster_result = self._create_new_cluster_with_tracking(current_embedding, None)

            # 🔤 Process names for brand new clusters
            if new_cluster_result[0] and new_cluster_result[0].startswith('Anonymous_'):
                self._process_name_for_new_cluster(text, new_cluster_result[0])

            return new_cluster_result

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return "Daveydrz", "ERROR"

    def _check_for_name_conflict(self, text: str, cluster_id: str) -> Optional[Tuple[str, str]]:
        """🚨 Check if introduction conflicts with existing cluster name OR assign name if empty"""
        
        print(f"[IntelligentVoiceManager] 🔍 Checking name conflict for cluster: {cluster_id}")
        print(f"[IntelligentVoiceManager] 📅 2025-07-15 11:22:34 UTC")
        print(f"[IntelligentVoiceManager] 👤 User: Daveydrz")
        
        # Get existing cluster name
        existing_name = None
        if cluster_id in anonymous_clusters:
            cluster_data = anonymous_clusters[cluster_id]
            existing_name = cluster_data.get('test_name', 'Unknown')
        elif cluster_id in known_users:
            user_data = known_users[cluster_id]
            existing_name = user_data.get('name', cluster_id)
        
        # Check if text contains a name introduction
        if hasattr(self, 'ultra_name_manager') and self.ultra_name_manager:
            extracted_name = self.ultra_name_manager.extract_name_enhanced_ai_aware(text)
            
            if extracted_name:
                print(f"[IntelligentVoiceManager] 🔍 Extracted name: {extracted_name}")
                print(f"[IntelligentVoiceManager] 🔍 Existing name: {existing_name}")
                
                # 🎯 NEW: If no existing name, assign the extracted name and convert cluster
                if not existing_name or existing_name == 'Unknown':
                    print(f"[IntelligentVoiceManager] 🔗 CONVERTING CLUSTER: {cluster_id} → {extracted_name}")
                    
                    # Convert anonymous cluster to named user
                    success = self._convert_anonymous_to_named(cluster_id, extracted_name)
                    if success:
                        print(f"[IntelligentVoiceManager] ✅ CLUSTER CONVERTED: {cluster_id} → {extracted_name}")
                        
                        # Update current user and cluster ID
                        self.current_user = extracted_name
                        self.current_speaker_cluster_id = extracted_name
                        
                        return None  # No conflict, conversion successful
                    else:
                        print(f"[IntelligentVoiceManager] ❌ CLUSTER CONVERSION FAILED")
                    
                    return None  # No conflict detected
                
                # Check if names are different (case-insensitive)
                elif extracted_name.lower() != existing_name.lower():
                    print(f"[IntelligentVoiceManager] 🚨 NAME CONFLICT: {extracted_name} ≠ {existing_name}")
                    return (extracted_name, existing_name)
                else:
                    print(f"[IntelligentVoiceManager] ✅ Names match: {extracted_name} = {existing_name}")
            else:
                print(f"[IntelligentVoiceManager] 🔍 No name extracted from text")
        
        return None

    def _convert_anonymous_to_named(self, cluster_id: str, name: str) -> bool:
        """🔄 Convert anonymous cluster to named user (overwrites Anonymous_001 → David)"""
        try:
            print(f"[IntelligentVoiceManager] 🔄 CONVERTING: {cluster_id} → {name}")
            print(f"[IntelligentVoiceManager] 📅 2025-07-15 11:22:34 UTC")
            
            if cluster_id not in anonymous_clusters:
                print(f"[IntelligentVoiceManager] ❌ Cluster {cluster_id} not found")
                return False
            
            # Get cluster data
            cluster_data = anonymous_clusters[cluster_id]
            embeddings = cluster_data.get('embeddings', [])
            
            print(f"[IntelligentVoiceManager] 📊 Converting cluster with {len(embeddings)} embeddings")
            
            # Create new user profile with cluster data
            user_profile = {
                'username': name,
                'name': name,
                'embeddings': embeddings,
                'voice_embeddings': embeddings,  # Duplicate for compatibility
                'created_at': cluster_data.get('created_at', datetime.utcnow().isoformat()),
                'last_updated': datetime.utcnow().isoformat(),
                'sample_count': len(embeddings),
                'status': 'converted_from_anonymous',
                'original_cluster_id': cluster_id,
                'conversion_date': datetime.utcnow().isoformat(),
                'confidence_threshold': 0.4,
                'recognition_count': cluster_data.get('sample_count', 1),
                'training_type': 'anonymous_conversion',
                'system': 'IntelligentVoiceManager'
            }
            
            # 🔥 CRITICAL: Add to known_users
            known_users[name] = user_profile
            print(f"[IntelligentVoiceManager] ✅ Added {name} to known_users")
            
            # 🔥 CRITICAL: Remove from anonymous_clusters
            del anonymous_clusters[cluster_id]
            print(f"[IntelligentVoiceManager] ✅ Removed {cluster_id} from anonymous_clusters")
            
            # 🔥 CRITICAL: Force save database
            from voice.database import save_known_users
            save_result = save_known_users()
            print(f"[IntelligentVoiceManager] 💾 Database save result: {save_result}")
            
            # 🔥 CRITICAL: Update voice manager state
            self.set_current_cluster(name)
            
            print(f"[IntelligentVoiceManager] 🎉 CONVERSION COMPLETE: {cluster_id} → {name}")
            print(f"[IntelligentVoiceManager] 📊 known_users: {len(known_users)}, anonymous_clusters: {len(anonymous_clusters)}")
            
            return True
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Conversion error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _handle_name_voice_conflict(self, voice_match_id: str, new_name: str, existing_name: str, 
                                   current_embedding, similarity: float, text: str) -> Tuple[str, str]:
        """🚨 Handle conflict between voice match and name introduction"""
        
        print(f"[IntelligentVoiceManager] 🚨 HANDLING NAME-VOICE CONFLICT")
        print(f"[IntelligentVoiceManager] 📅 2025-07-15 11:06:08 UTC")
        print(f"[IntelligentVoiceManager] 🔊 Voice similarity: {similarity:.3f}")
        print(f"[IntelligentVoiceManager] 👤 Voice matches: {existing_name}")
        print(f"[IntelligentVoiceManager] 🗣️ Says name is: {new_name}")
        
        # 🎯 DECISION LOGIC
        if similarity >= 0.90:  # Very high similarity
            print(f"[IntelligentVoiceManager] 🔊 VERY HIGH voice similarity - probably misheard name")
            print(f"[IntelligentVoiceManager] 🛡️ Trusting voice over name extraction")
            
            # Add to existing profile, ignore conflicting name
            self._add_embedding_to_profile(voice_match_id, current_embedding)
            self.set_current_cluster(voice_match_id)
            
            return voice_match_id, "VOICE_TRUSTED_OVER_NAME"
        
        elif similarity >= 0.80:  # High similarity - ask for confirmation
            print(f"[IntelligentVoiceManager] 🤔 HIGH similarity but conflicting name - asking confirmation")
            
            speak_streaming(f"Your voice sounds like {existing_name}, but you said {new_name}. Which is correct?")
            
            # Store conflict data for confirmation
            self.pending_name_voice_conflict = {
                'voice_match_id': voice_match_id,
                'existing_name': existing_name,
                'new_name': new_name,
                'embedding': current_embedding,
                'similarity': similarity,
                'text': text
            }
            
            self.waiting_for_name_voice_conflict_resolution = True
            
            return voice_match_id, "ASKING_NAME_VOICE_CONFLICT_RESOLUTION"
        
        else:  # Moderate similarity - probably different person
            print(f"[IntelligentVoiceManager] 🆕 MODERATE similarity + different name - creating new cluster")
            print(f"[IntelligentVoiceManager] 🎯 {new_name} is probably a different person")
            
            # Force create separate cluster for new person
            new_cluster_result = self._force_create_separate_cluster(
                current_embedding, 
                f"NAME_CONFLICT_SEPARATION_FROM_{voice_match_id}"
            )
            
            # Link new cluster to new name
            if new_cluster_result[0] and new_cluster_result[0].startswith('Anonymous_'):
                self._process_name_for_new_cluster(text, new_cluster_result[0])
            
            return new_cluster_result

    def _handle_name_voice_conflict_resolution(self, text: str) -> Tuple[str, str]:
        """✅ Handle user's response to name-voice conflict"""
        
        print(f"[IntelligentVoiceManager] ✅ Handling conflict resolution: '{text}'")
        print(f"[IntelligentVoiceManager] 📅 2025-07-15 11:06:08 UTC")
        
        if not hasattr(self, 'pending_name_voice_conflict'):
            print(f"[IntelligentVoiceManager] ❌ No pending conflict data")
            return "Daveydrz", "NO_PENDING_CONFLICT"
        
        conflict_data = self.pending_name_voice_conflict
        text_lower = text.lower().strip()
        
        if conflict_data['existing_name'].lower() in text_lower:
            # User confirmed existing name
            print(f"[IntelligentVoiceManager] ✅ User confirmed existing name: {conflict_data['existing_name']}")
            
            self._add_embedding_to_profile(conflict_data['voice_match_id'], conflict_data['embedding'])
            self.set_current_cluster(conflict_data['voice_match_id'])
            
            self._reset_conflict_state()
            return conflict_data['voice_match_id'], "EXISTING_NAME_CONFIRMED"
        
        elif conflict_data['new_name'].lower() in text_lower:
            # User confirmed new name - create separate cluster
            print(f"[IntelligentVoiceManager] 🆕 User confirmed new name: {conflict_data['new_name']}")
            
            new_cluster_result = self._force_create_separate_cluster(
                conflict_data['embedding'], 
                f"USER_CONFIRMED_DIFFERENT_PERSON"
            )
            
            if new_cluster_result[0] and new_cluster_result[0].startswith('Anonymous_'):
                self._process_name_for_new_cluster(conflict_data['text'], new_cluster_result[0])
            
            self._reset_conflict_state()
            return new_cluster_result
        
        else:
            # Ask again
            print(f"[IntelligentVoiceManager] 🤔 Unclear response, asking again")
            speak_streaming(f"Please say either {conflict_data['existing_name']} or {conflict_data['new_name']}")
            return conflict_data['voice_match_id'], "ASKING_NAME_VOICE_CONFLICT_RESOLUTION"

    def _process_name_for_new_cluster(self, text: str, cluster_id: str):
        """🔤 SAFE name processing ONLY for NEW clusters"""
        
        print(f"[IntelligentVoiceManager] 🔤 SAFE name processing for NEW cluster: {cluster_id}")
        print(f"[IntelligentVoiceManager] 📅 2025-07-15 11:06:08 UTC")
        print(f"[IntelligentVoiceManager] 👤 User: Daveydrz")
        
        try:
            if hasattr(self, 'ultra_name_manager') and self.ultra_name_manager:
                name_from_text = self.ultra_name_manager.extract_name_enhanced_ai_aware(text)
                
                if name_from_text:
                    print(f"[NameLink] 🔗 Linking NEW cluster {cluster_id} → {name_from_text}")
                    
                    success = link_anonymous_to_named(cluster_id, name_from_text)
                    
                    if success:
                        self.current_user = name_from_text
                        self.current_speaker_cluster_id = name_from_text
                        print(f"[NameLink] ✅ NEW cluster linked: {cluster_id} → {name_from_text}")
                    else:
                        print(f"[NameLink] ❌ Failed to link NEW cluster")
                else:
                    print(f"[NameLink] 🔤 No name extracted from: '{text}'")
                    
        except Exception as e:
            print(f"[NameLink] ❌ Name processing error: {e}")

    def _reset_conflict_state(self):
        """🔄 Reset name-voice conflict state"""
        if hasattr(self, 'pending_name_voice_conflict'):
            delattr(self, 'pending_name_voice_conflict')
        if hasattr(self, 'waiting_for_name_voice_conflict_resolution'):
            delattr(self, 'waiting_for_name_voice_conflict_resolution')
        print(f"[IntelligentVoiceManager] 🔄 Conflict state reset")

    def _find_best_voice_match_with_gap_check(self, current_embedding):
        """🎯 Enhanced voice matching with similarity gap analysis"""
        try:
            # Track top candidates
            candidates = []

            # Search through all known users
            for user_id, user_data in known_users.items():
                if isinstance(user_data, dict):
                    embeddings = user_data.get('embeddings', [])
                    for stored_embedding in embeddings:
                        similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)
                        candidates.append((user_id, similarity, 'known_user'))

            # Search through anonymous clusters
            for cluster_id, cluster_data in anonymous_clusters.items():
                embeddings = cluster_data.get('embeddings', [])
                for stored_embedding in embeddings:
                    similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)
                    candidates.append((cluster_id, similarity, 'anonymous_cluster'))

            # Sort by similarity (highest first)
            candidates.sort(key=lambda x: x[1], reverse=True)

            if len(candidates) < 1:
                return None

            best = candidates[0]
            second_best = candidates[1] if len(candidates) > 1 else None

            # 🎯 SIMILARITY GAP CHECK - Critical for avoiding false positives
            if second_best:
                similarity_gap = best[1] - second_best[1]
                print(f"[VoiceMatch] 📊 Gap Analysis: Best={best[1]:.3f}, Second={second_best[1]:.3f}, Gap={similarity_gap:.3f}")

                # If gap is too small, similarities are too close - force verification
                if similarity_gap < 0.06:  # 6% minimum gap
                    print(f"[VoiceMatch] ⚠️ SIMILARITY GAP TOO SMALL: {best[1]:.3f} vs {second_best[1]:.3f}")
                    print(f"[VoiceMatch] 🔒 FORCING VERIFICATION due to ambiguous match")
                    # Return with lower confidence to trigger verification
                    return (best[0], max(0.65, best[1] - 0.15), best[2])  # Reduce confidence

            return best

        except Exception as e:
            print(f"[VoiceMatch] ❌ Gap check error: {e}")
            return None

    def _track_similarity_patterns(self, user_id, similarity, is_correct_match=True):
        """📊 Track similarity patterns for each user to detect anomalies"""
        try:
            if user_id not in self.similarity_range_tracking:
                self.similarity_range_tracking[user_id] = {
                    'correct_matches': [],
                    'false_positives': [],
                    'avg_similarity': 0.0,
                    'std_deviation': 0.0,
                    'normal_range': (0.0, 1.0),
                    'last_updated': datetime.utcnow().isoformat()
                }

            tracking = self.similarity_range_tracking[user_id]

            if is_correct_match:
                tracking['correct_matches'].append(similarity)
                # Keep only last 20 correct matches
                if len(tracking['correct_matches']) > 20:
                    tracking['correct_matches'] = tracking['correct_matches'][-20:]
            else:
                tracking['false_positives'].append(similarity)
                # Keep only last 10 false positives
                if len(tracking['false_positives']) > 10:
                    tracking['false_positives'] = tracking['false_positives'][-10:]

            # Update statistics if we have enough data
            if len(tracking['correct_matches']) >= 3:
                import numpy as np
                avg = np.mean(tracking['correct_matches'])
                std = np.std(tracking['correct_matches'])

                tracking['avg_similarity'] = avg
                tracking['std_deviation'] = std
                # Normal range = average ± 2 standard deviations
                tracking['normal_range'] = (max(0.0, avg - 2*std), min(1.0, avg + 2*std))

                print(f"[SimilarityTracking] 📊 {user_id}: avg={avg:.3f}, std={std:.3f}, range={tracking['normal_range']}")

            tracking['last_updated'] = datetime.utcnow().isoformat()

        except Exception as e:
            print(f"[SimilarityTracking] ❌ Error tracking {user_id}: {e}")

    def _is_similarity_in_normal_range(self, user_id, similarity):
        """🔍 Check if similarity is within normal range for this user"""
        try:
            if user_id not in self.similarity_range_tracking:
                return True  # No data yet, assume normal

            tracking = self.similarity_range_tracking[user_id]

            if len(tracking['correct_matches']) < 3:
                return True  # Not enough data yet

            normal_min, normal_max = tracking['normal_range']
            is_normal = normal_min <= similarity <= normal_max

            if not is_normal:
                print(f"[SimilarityTracking] ⚠️ {user_id}: similarity {similarity:.3f} outside normal range {tracking['normal_range']}")

            return is_normal

        except Exception as e:
            print(f"[SimilarityTracking] ❌ Error checking range for {user_id}: {e}")
            return True

    def _force_create_separate_cluster(self, current_embedding, reason="VOICE_SEPARATION"):
        """🆕 Force create separate cluster for different voice"""
        try:
            # Check cluster limit
            if len(anonymous_clusters) >= self.max_clusters_per_session:
                print(f"[IntelligentVoiceManager] ⚠️ Max clusters reached ({self.max_clusters_per_session}), using fallback")
                return "Daveydrz", "MAX_CLUSTERS_REACHED"

            cluster_id = f"Anonymous_{len(anonymous_clusters) + 1:03d}"
            
            cluster_data = {
                'cluster_id': cluster_id,
                'embeddings': [current_embedding.tolist()],
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'sample_count': 1,
                'status': 'anonymous',
                'separation_reason': reason,
                'voice_threshold_separation': True,
                'confidence_threshold': self.confident_match_threshold
            }
            
            anonymous_clusters[cluster_id] = cluster_data
            save_known_users()
            
            self.set_current_cluster(cluster_id)
            print(f"[IntelligentVoiceManager] 🆕 FORCED SEPARATION: Created {cluster_id} (reason: {reason})")
            
            return cluster_id, "FORCED_SEPARATION_CREATED"
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Force separation error: {e}")
            return "Daveydrz", "SEPARATION_ERROR"

    def _is_valid_embedding(self, embedding):
        """🔍 Check if embedding has sufficient quality"""
        if embedding is None:
            return False

        try:
            vec = np.array(embedding)

            # Check for mostly zero embeddings
            non_zero_ratio = np.count_nonzero(vec) / len(vec)
            if non_zero_ratio < 0.1:  # Less than 10% non-zero values
                print(f"[VoiceManager] ⚠️ Poor embedding quality: {non_zero_ratio:.2%} non-zero")
                return False

            # Check embedding magnitude
            magnitude = np.linalg.norm(vec)
            if magnitude < 0.01:  # Very small magnitude
                print(f"[VoiceManager] ⚠️ Poor embedding magnitude: {magnitude:.6f}")
                return False

            print(f"[VoiceManager] ✅ Good embedding quality: {non_zero_ratio:.2%} non-zero, magnitude: {magnitude:.6f}")
            return True

        except Exception as e:
            print(f"[VoiceManager] ❌ Embedding validation error: {e}")
            return False

    def should_create_new_cluster(self, current_embedding):
        """🤔 Determine if we really need a new cluster"""

        # If we have very few clusters, be more lenient about matching
        if len(anonymous_clusters) <= 2:
            print(f"[IntelligentVoiceManager] 🔍 Few clusters ({len(anonymous_clusters)}), using relaxed matching...")

            for cluster_id, cluster_data in anonymous_clusters.items():
                embeddings = cluster_data.get('embeddings', [])

                for stored_embedding in embeddings:
                    similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)

                    # Very relaxed threshold when few clusters exist
                    if similarity >= 0.25:
                        print(f"[IntelligentVoiceManager] 🎯 RELAXED MATCH: {cluster_id} (similarity: {similarity:.3f})")
                        return False, cluster_id

        return True, None

    def check_existing_clusters_on_startup(self, current_embedding):
        """🔍 Check if current voice matches existing clusters with STRICT multi-speaker separation"""

        print(f"[DEBUG] 🔍 STARTUP CHECK - Current embedding type: {type(current_embedding)}")

        if current_embedding is not None:
            print(f"[DEBUG] 🔍 Current embedding shape: {np.array(current_embedding).shape}")
            print(f"[DEBUG] 🔍 Current embedding first 5: {np.array(current_embedding)[:5]}")
        else:
            print(f"[DEBUG] 🔍 Current embedding: None")
            return None, 0.0

        print(f"[DEBUG] 🔍 Checking {len(anonymous_clusters)} existing clusters...")

        best_match = None
        best_similarity = 0.0

        for cluster_id, cluster_data in anonymous_clusters.items():
            stored_embeddings = cluster_data.get('embeddings', [])
            print(f"[DEBUG] 🔍 Cluster {cluster_id}: {len(stored_embeddings)} stored embeddings")

            if not stored_embeddings:
                print(f"[DEBUG] ⚠️ Cluster {cluster_id} has no embeddings!")
                continue

            for i, stored_embedding in enumerate(stored_embeddings):
                print(f"[DEBUG] 🔍 Comparing with {cluster_id} embedding #{i}")
                
                if stored_embedding is not None:
                    similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)
                    print(f"[DEBUG] 📊 Similarity with {cluster_id}[{i}]: {similarity:.6f}")

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = cluster_id

        # Use startup recognition threshold
        print(f"[DEBUG] 🎯 BEST MATCH: {best_match} with similarity {best_similarity:.6f}")
        print(f"[DEBUG] 🎯 STARTUP THRESHOLD: {self.startup_recognition_threshold}")

        if best_match and best_similarity >= self.startup_recognition_threshold:
            print(f"[IntelligentVoiceManager] ✅ STARTUP MATCH: {best_match} (similarity: {best_similarity:.3f})")
            return best_match, best_similarity
        else:
            print(f"[IntelligentVoiceManager] 🆕 NEW VOICE DETECTED (similarity: {best_similarity:.3f}, threshold: {self.startup_recognition_threshold})")
            return None, 0.0

    def get_last_audio_sample(self):
        """Get the most recent audio sample for voice identification"""
        try:
            if hasattr(self, 'last_audio_buffer') and self.last_audio_buffer is not None:
                return self.last_audio_buffer
            elif hasattr(self, 'passive_samples') and self.passive_samples:
                return self.passive_samples[-1]['audio']  # Get most recent
            else:
                return None
        except Exception as e:
            print(f"[VoiceManager] ⚠️ Error getting last audio: {e}")
            return None

    def get_current_speaker_identity(self):
        """Get current speaker identity from advanced voice processing"""
        try:
            if hasattr(self, 'current_training_user') and self.current_training_user:
                return self.current_training_user
            elif hasattr(self, 'last_identified_user') and self.last_identified_user:
                return self.last_identified_user
            else:
                return None
        except Exception as e:
            print(f"[VoiceManager] ⚠️ Error getting speaker identity: {e}")
            return None

    def set_last_audio_sample(self, audio_data):
        """Store the most recent audio sample"""
        try:
            self.last_audio_buffer = audio_data
            # Also update timestamp
            import time
            self.last_audio_timestamp = time.time()
        except Exception as e:
            print(f"[VoiceManager] ⚠️ Error storing audio sample: {e}")

    def is_llm_locked(self):
        """Check if LLM should be locked due to voice processing"""
        try:
            # Check if voice training is in progress
            if hasattr(self, 'pending_training_offer') and self.pending_training_offer:
                return True
        
            # Check if name collection is in progress
            if hasattr(self, 'waiting_for_name') and self.waiting_for_name:
                return True
            
            # Check if any voice processing state is active
            if hasattr(self, 'training_mode') and self.training_mode != "NONE":
                return True
            
            return False
        except Exception as e:
            print(f"[VoiceManager] ⚠️ Error checking LLM lock: {e}")

    def _find_best_voice_match_centroid_enhanced(self, current_embedding):
        """🎯 Enhanced centroid matching with gap analysis and robustness"""
        try:
            candidates = []

            print(f"[DEBUG] 🔍 ENHANCED CENTROID MATCHING with gap analysis...")
            print(f"[DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")
            print(f"[DEBUG] 👤 User Login: Daveydrz")

            # Check anonymous clusters using centroid
            for cluster_id, cluster_data in anonymous_clusters.items():
                similarity = self._calculate_centroid_similarity(current_embedding, cluster_data)
                if similarity > 0:
                    candidates.append((cluster_id, similarity, 'anonymous'))
                    print(f"[DEBUG] 🔍 {cluster_id}: centroid similarity = {similarity:.4f}")

            # Check known users using centroid
            for user_id, user_data in known_users.items():
                if 'embeddings' in user_data:
                    similarity = self._calculate_centroid_similarity(current_embedding, user_data)
                    if similarity > 0:
                        candidates.append((user_id, similarity, 'known'))
                        print(f"[DEBUG] 🔍 {user_id}: centroid similarity = {similarity:.4f}")

            # Sort by similarity (highest first)
            candidates.sort(key=lambda x: x[1], reverse=True)

            if len(candidates) < 1:
                print(f"[DEBUG] ❌ No valid centroid candidates found")
                return None

            best = candidates[0]
            second_best = candidates[1] if len(candidates) > 1 else None

            # 🎯 CENTROID GAP ANALYSIS - Even more critical for centroid matching
            if second_best:
                similarity_gap = best[1] - second_best[1]
                print(f"[DEBUG] 📊 CENTROID Gap Analysis:")
                print(f"[DEBUG]   Best: {best[0]} = {best[1]:.4f}")
                print(f"[DEBUG]   Second: {second_best[0]} = {second_best[1]:.4f}")
                print(f"[DEBUG]   Gap: {similarity_gap:.4f}")

                # Centroid should have larger gaps - if too close, force verification
                if similarity_gap < 0.08:  # 8% minimum gap for centroid
                    print(f"[DEBUG] ⚠️ CENTROID SIMILARITY GAP TOO SMALL!")
                    print(f"[DEBUG] 🔒 Multiple speakers too similar - forcing verification")
                    # Return with verification-level confidence
                    return (best[0], 0.72, best[2])  # Force verification zone

            print(f"[DEBUG] 🎯 Enhanced centroid result: {best}")
            return best

        except Exception as e:
            print(f"[DEBUG] ❌ Enhanced centroid error: {e}")
            return None

    def _create_new_cluster_with_tracking(self, current_embedding, related_match=None):
        """🆕 Create new cluster with intelligent tracking AND EMBEDDING VERIFICATION"""
        try:
            # 🔥 FORCE GLOBAL SYNC BEFORE SAVE
            global known_users, anonymous_clusters
            from voice.database import known_users as db_known_users, anonymous_clusters as db_anonymous_clusters

            cluster_id = f"Anonymous_{len(anonymous_clusters) + 1:03d}"

            print(f"[DEBUG] 🆕 CREATING CLUSTER: {cluster_id}")
            print(f"[DEBUG] 📅 Current Time: 2025-07-15 20:35:30 UTC")
            print(f"[DEBUG] 👤 User Login: Daveydrz")
            print(f"[DEBUG] 📊 Embedding type: {type(current_embedding)}")
            print(f"[DEBUG] 📊 Embedding shape: {np.array(current_embedding).shape}")

            # ✅ ENSURE PROPER SERIALIZATION
            embedding_list = current_embedding.tolist() if hasattr(current_embedding, 'tolist') else list(current_embedding)
            print(f"[DEBUG] 📊 Serialized embedding type: {type(embedding_list)}")
            print(f"[DEBUG] 📊 Serialized embedding length: {len(embedding_list)}")
            print(f"[DEBUG] 📊 Serialized embedding preview: {embedding_list[:5]}")

            cluster_data = {
                'cluster_id': cluster_id,
                'embeddings': [embedding_list],
                'created_at': datetime.utcnow().isoformat(),
                'last_updated': datetime.utcnow().isoformat(),
                'sample_count': 1,
                'status': 'anonymous',
                'related_to': related_match[0] if related_match else None,
                'similarity_to_related': related_match[1] if related_match else None
            }

            print(f"[DEBUG] 📊 Cluster data keys: {list(cluster_data.keys())}")
            print(f"[DEBUG] 📊 Embeddings in cluster_data: {len(cluster_data['embeddings'])}")

            # ✅ STORE IN BOTH LOCAL AND DATABASE DICTIONARIES
            anonymous_clusters[cluster_id] = cluster_data
            db_anonymous_clusters[cluster_id] = cluster_data  # 🔥 CRITICAL: Sync to database dict

            print(f"[DEBUG] ✅ Stored in anonymous_clusters")
            print(f"[DEBUG] ✅ Synced to database anonymous_clusters")

            # 🔥 FORCE VERIFY SYNC
            print(f"[DEBUG] 🔍 Manager dict count: {len(anonymous_clusters)}")
            print(f"[DEBUG] 🔍 Database dict count: {len(db_anonymous_clusters)}")
            print(f"[DEBUG] 🔍 Manager has {cluster_id}: {cluster_id in anonymous_clusters}")
            print(f"[DEBUG] 🔍 Database has {cluster_id}: {cluster_id in db_anonymous_clusters}")

            # 🔍 TRACE THE SAVE FLOW
            self.trace_embedding_save_flow(cluster_id, current_embedding)

            # ✅ FORCE SAVE WITH VERIFICATION
            save_result = save_known_users()
            print(f"[DEBUG] 💾 Save result: {save_result}")

            if save_result:
                # 🔍 VERIFY SAVE WORKED
                self.trace_embedding_save_flow(cluster_id, current_embedding)

            self.set_current_cluster(cluster_id)
            print(f"[IntelligentVoiceManager] 🆕 Created new cluster: {cluster_id}")

            if related_match:
                print(f"[IntelligentVoiceManager] 🔗 Related to: {related_match[0]} (similarity: {related_match[1]:.3f})")

            return cluster_id, "NEW_CLUSTER_CREATED"

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Cluster creation error: {e}")
            import traceback
            traceback.print_exc()
            return "Daveydrz", "CLUSTER_CREATION_ERROR"
    
    def _find_best_voice_match(self, current_embedding):
        """🔍 INTELLIGENT search for best voice match with STRICT separation"""
        try:
            best_match = None
            best_similarity = 0.0

            # Search through all known users
            for user_id, user_data in known_users.items():
                if isinstance(user_data, dict):
                    embeddings = user_data.get('embeddings', [])

                    for stored_embedding in embeddings:
                        similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)

                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_match = (user_id, similarity, 'known_user')

            # Search through anonymous clusters
            for cluster_id, cluster_data in anonymous_clusters.items():
                embeddings = cluster_data.get('embeddings', [])

                for stored_embedding in embeddings:
                    similarity = self._calculate_voice_similarity(current_embedding, stored_embedding)

                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = (cluster_id, similarity, 'anonymous_cluster')

            return best_match

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error finding voice match: {e}")
            return None

    def _calculate_voice_similarity(self, embedding1, embedding2):
        """🧮 Calculate cosine similarity between voice embeddings WITH FIXED DEBUG"""
        try:
            print(f"[DEBUG] 🔍 Voice similarity calculation:")
            print(f"[DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")

            # ✅ FIX: Proper None checking for numpy arrays
            if embedding1 is None or embedding2 is None:
                print(f"[DEBUG] ❌ One or both embeddings are None")
                return 0.0

            print(f"[DEBUG] Embedding1 type: {type(embedding1)}")
            print(f"[DEBUG] Embedding2 type: {type(embedding2)}")

            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            print(f"[DEBUG] Vec1 shape: {vec1.shape}, Vec2 shape: {vec2.shape}")
            print(f"[DEBUG] Vec1 first 5 values: {vec1[:5]}")
            print(f"[DEBUG] Vec2 first 5 values: {vec2[:5]}")

            # Check shapes match
            if vec1.shape != vec2.shape:
                print(f"[DEBUG] ❌ Shape mismatch: {vec1.shape} vs {vec2.shape}")
                return 0.0

            # Check for zero vectors
            norm1_val = np.linalg.norm(vec1)
            norm2_val = np.linalg.norm(vec2)

            print(f"[DEBUG] Vec1 norm: {norm1_val}, Vec2 norm: {norm2_val}")

            if norm1_val == 0 or norm2_val == 0:
                print(f"[DEBUG] ❌ Zero vector detected")
                return 0.0

            # Normalize vectors
            norm1 = vec1 / (norm1_val + 1e-8)
            norm2 = vec2 / (norm2_val + 1e-8)

            # Calculate cosine similarity
            similarity = np.dot(norm1, norm2)

            print(f"[DEBUG] ✅ Calculated similarity: {similarity}")

            return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]

        except Exception as e:
            print(f"[DEBUG] ❌ Similarity calculation error: {e}")
            import traceback
            traceback.print_exc()
            return 0.0
    
    def _ask_for_voice_confirmation(self, match_id, current_embedding, text):
        """❓ Smart voice confirmation - asks for name if unnamed, confirms if named"""
        try:
            print(f"[DEBUG] ❓ SMART VOICE CONFIRMATION for {match_id}")
            print(f"[DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")
            print(f"[DEBUG] 👤 User Login: Daveydrz")
            
            # Store pending confirmation data
            self.pending_confirmation_cluster = match_id
            self.pending_confirmation_embedding = current_embedding
            
            # Check if cluster has a name assigned
            cluster_data = anonymous_clusters.get(match_id, {})
            assigned_name = cluster_data.get('test_name', '')
            
            print(f"[DEBUG] 🔍 Cluster {match_id} assigned name: '{assigned_name}'")
            
            # 🎯 NAMED CLUSTER - Ask for confirmation by name
            if assigned_name and assigned_name != 'Unknown':
                self.waiting_for_voice_confirmation = True
                self.waiting_for_name = False
                
                speak_streaming(f"Is this {assigned_name}?")
                print(f"[IntelligentVoiceManager] ❓ NAMED CONFIRMATION: Is this {assigned_name}?")
                
                return match_id, "ASKING_VOICE_CONFIRMATION"
            
            # 🤔 UNNAMED CLUSTER - Ask for name using ultra-intelligent processing
            else:
                self.waiting_for_voice_confirmation = False
                self.waiting_for_name = True
                
                speak_streaming("Sorry, I'm struggling to recognize your voice. What's your name?")
                print(f"[IntelligentVoiceManager] ❓ ASKING FOR NAME: Unknown cluster {match_id}")
                
                return match_id, "ASKING_FOR_NAME"
                
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error asking confirmation: {e}")
            return self._create_new_cluster_with_tracking(current_embedding, None)
    
    def _handle_voice_confirmation(self, text):
        """✅ Handle voice confirmation response"""
        try:
            text_lower = text.lower().strip()
            
            if any(word in text_lower for word in ["yes", "yeah", "yep", "correct", "right"]):
                # ✅ CONFIRMED - Add embedding to profile
                match_id = self.pending_confirmation_cluster
                current_embedding = self.pending_confirmation_embedding
                
                print(f"[IntelligentVoiceManager] ✅ VOICE CONFIRMED: {match_id}")
                
                # Add embedding and update learning history
                self._add_embedding_to_profile(match_id, current_embedding)
                self._update_voice_learning_history(match_id, current_embedding, 0.8)
                
                # Reset confirmation state
                self._reset_confirmation_state()
                self.set_current_cluster(match_id)
                
                return match_id, "VOICE_CONFIRMED"
                
            elif any(word in text_lower for word in ["no", "nope", "wrong", "not"]):
                # ❌ REJECTED - Create new cluster
                print(f"[IntelligentVoiceManager] ❌ VOICE REJECTED: Creating new cluster")
                
                current_embedding = self.pending_confirmation_embedding
                self._reset_confirmation_state()
                
                return self._create_new_cluster_with_tracking(current_embedding, None)
            # 🔍 Try extracting name from transcript
            if hasattr(self, 'ultra_name_manager') and self.ultra_name_manager:
                extracted_name = self.ultra_name_manager.extract_name_enhanced_ai_aware(text)
                if extracted_name:
                    print(f"[VoiceManager] 🧠 Name extracted: {extracted_name}")
                    self.force_link_current_cluster_to_name(extracted_name)
                else:
                    print(f"[VoiceManager] ❌ No valid name found in text: {text}")

                
            else:
                # 🤔 UNCLEAR RESPONSE - Ask again
                display_name = self._get_display_name(self.pending_confirmation_cluster)
                speak_streaming(f"Please say yes or no. Is this {display_name}?")
                return self.pending_confirmation_cluster, "ASKING_VOICE_CONFIRMATION"
                
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Confirmation error: {e}")
            self._reset_confirmation_state()
            return "Daveydrz", "CONFIRMATION_ERROR"
    
    def _add_embedding_to_profile(self, profile_id, embedding):
        """📈 Add embedding to existing profile with BULLETPROOF persistence - FIXED"""
        try:
            print(f"[DEBUG] 📎 ADDING EMBEDDING to {profile_id}")
            print(f"[DEBUG] Embedding type: {type(embedding)}")
            print(f"[DEBUG] Embedding shape: {np.array(embedding).shape}")

            # Ensure embedding is in the right format
            if isinstance(embedding, np.ndarray):
                embedding_list = embedding.tolist()
            elif isinstance(embedding, list):
                embedding_list = embedding
            else:
                print(f"[DEBUG] ❌ Unknown embedding type: {type(embedding)}")
                return

            # 🔧 CRITICAL FIX: Store directly in known_users dictionary
            if profile_id in known_users:
                user_data = known_users[profile_id]

                # Ensure user_data is a dictionary
                if not isinstance(user_data, dict):
                    print(f"[DEBUG] 🔧 Converting old user format for {profile_id}")
                    known_users[profile_id] = {
                        'username': profile_id,
                        'embeddings': [],
                        'voice_embeddings': [],
                        'created_at': datetime.utcnow().isoformat(),
                        'status': 'trained'
                    }
                    user_data = known_users[profile_id]

                # Initialize embedding lists if missing
                if 'embeddings' not in user_data:
                    user_data['embeddings'] = []
                if 'voice_embeddings' not in user_data:
                    user_data['voice_embeddings'] = []

                # Add to both embedding lists for compatibility
                user_data['embeddings'].append(embedding_list)
                user_data['voice_embeddings'].append(embedding_list)

                # Smart pruning to prevent memory bloat
                user_data['embeddings'] = self._smart_prune_embeddings(user_data['embeddings'], max_samples=20)
                user_data['voice_embeddings'] = self._smart_prune_embeddings(user_data['voice_embeddings'], max_samples=20)

                # Update metadata
                user_data['last_updated'] = datetime.utcnow().isoformat()
                user_data['sample_count'] = len(user_data['embeddings'])

                print(f"[DEBUG] ✅ Added embedding to known user {profile_id}")
                print(f"[DEBUG] 📊 Total embeddings: {len(user_data['embeddings'])}")

            # Handle anonymous clusters similarly
            elif profile_id in anonymous_clusters:
                cluster_data = anonymous_clusters[profile_id]

                if 'embeddings' not in cluster_data:
                    cluster_data['embeddings'] = []

                cluster_data['embeddings'].append(embedding_list)
                cluster_data['embeddings'] = self._smart_prune_embeddings(cluster_data['embeddings'], max_samples=15)
                cluster_data['last_updated'] = datetime.utcnow().isoformat()
                cluster_data['sample_count'] = len(cluster_data['embeddings'])

                print(f"[DEBUG] ✅ Added embedding to anonymous cluster {profile_id}")

            else:
                print(f"[DEBUG] ❌ Profile {profile_id} not found in known_users or anonymous_clusters")
                return

            # 🔧 CRITICAL: Force immediate save with verification
            print(f"[DEBUG] 📎 Forcing immediate save...")
            save_result = save_known_users()

            if save_result:
                print(f"[DEBUG] ✅ EMBEDDING SAVE VERIFICATION PASSED!")
            else:
                print(f"[DEBUG] ❌ EMBEDDING SAVE VERIFICATION FAILED!")

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error adding embedding: {e}")
            import traceback
            traceback.print_exc()

    def verify_embedding_storage(self, profile_id):
        """🔍 Verify embeddings are properly stored - FIXED to check both locations"""
        try:
            print(f"\n[VERIFICATION] 🔍 Checking embedding storage for {profile_id}")

            # Check in-memory storage - FIXED: Check both locations
            memory_count = 0
            if profile_id in known_users:
                user_data = known_users[profile_id]
                memory_count = len(user_data.get('embeddings', []))
                print(f"[VERIFICATION] 📊 Memory embeddings (known_users): {memory_count}")
            elif profile_id in anonymous_clusters:
                cluster_data = anonymous_clusters[profile_id]
                memory_count = len(cluster_data.get('embeddings', []))
                print(f"[VERIFICATION] 📊 Memory embeddings (anonymous_clusters): {memory_count}")
            else:
                print(f"[VERIFICATION] ❌ Profile not found in either dictionary")

            # Check file storage - FIXED: Check both locations
            try:
                import json
                with open("voice_profiles/known_users_v2.json", 'r') as f:
                    file_data = json.load(f)

                file_count = 0
                file_users = file_data.get('known_users', {})
                file_clusters = file_data.get('anonymous_clusters', {})
                
                if profile_id in file_users:
                    file_count = len(file_users[profile_id].get('embeddings', []))
                    print(f"[VERIFICATION] 💾 File embeddings (known_users): {file_count}")
                elif profile_id in file_clusters:
                    file_count = len(file_clusters[profile_id].get('embeddings', []))
                    print(f"[VERIFICATION] 💾 File embeddings (anonymous_clusters): {file_count}")
                else:
                    print(f"[VERIFICATION] ❌ Profile not found in file")

            except Exception as e:
                file_count = 0
                print(f"[VERIFICATION] ❌ File read error: {e}")

            # Report results
            if memory_count == file_count and memory_count > 0:
                print(f"[VERIFICATION] ✅ STORAGE CONSISTENT: {memory_count} embeddings")
                return True
            else:
                print(f"[VERIFICATION] ❌ STORAGE MISMATCH: Memory={memory_count}, File={file_count}")
                return False

        except Exception as e:
            print(f"[VERIFICATION] ❌ Verification error: {e}")
            return False

    def set_current_cluster(self, cluster_id):
        """🔄 Set current speaker cluster - ENHANCED for conversion tracking"""
        try:
            old_cluster = getattr(self, 'current_speaker_cluster_id', None)
            self.current_speaker_cluster_id = cluster_id
            
            # Update current_user if it's a named user
            if cluster_id in known_users:
                user_data = known_users[cluster_id]
                self.current_user = user_data.get('name', cluster_id)
            elif cluster_id.startswith('Anonymous_'):
                # Keep Daveydrz as current_user for anonymous clusters
                pass
            else:
                self.current_user = cluster_id
            
            print(f"[IntelligentVoiceManager] 🔄 Cluster: {old_cluster} → {cluster_id}")
            print(f"[IntelligentVoiceManager] 🔄 Current user: {self.current_user}")
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error setting cluster: {e}")

    def save_known_users_with_verification():
        """💾 Save with verification to ensure embeddings from both known and anonymous clusters persist"""
        try:
            print(f"[DATABASE] 💾 SAVING with verification...")

            # Count embeddings in both known_users and anonymous_clusters BEFORE save
            total_known_before = sum(len(u.get('embeddings', [])) for u in known_users.values())
            total_anon_before = sum(len(c.get('embeddings', [])) for c in anonymous_clusters.values())
            total_before = total_known_before + total_anon_before

            print(f"[DATABASE] 📊 Embeddings BEFORE save:")
            print(f"[DATABASE]   Known users: {total_known_before}")
            print(f"[DATABASE]   Anonymous clusters: {total_anon_before}")
            print(f"[DATABASE]   TOTAL: {total_before}")

            # Perform save
            result = save_known_users()

            if result:
                # Reload after save to verify
                load_known_users()

                # Count embeddings again AFTER reload
                total_known_after = sum(len(u.get('embeddings', [])) for u in known_users.values())
                total_anon_after = sum(len(c.get('embeddings', [])) for c in anonymous_clusters.values())
                total_after = total_known_after + total_anon_after

                print(f"[DATABASE] 📊 Embeddings AFTER reload:")
                print(f"[DATABASE]   Known users: {total_known_after}")
                print(f"[DATABASE]   Anonymous clusters: {total_anon_after}")
                print(f"[DATABASE]   TOTAL: {total_after}")

                if total_before == total_after:
                    print(f"[DATABASE] ✅ SAVE VERIFICATION PASSED!")
                    return True
                else:
                    print(f"[DATABASE] ❌ SAVE VERIFICATION FAILED!")
                    return False

            return result

        except Exception as e:
            print(f"[DATABASE] ❌ Save verification error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _smart_prune_embeddings(self, embeddings, max_samples=20):
        """🧠 SMART pruning - keep diverse voice samples"""
        try:
            if len(embeddings) <= max_samples:
                return embeddings
            
            # Convert to numpy for processing
            embedding_arrays = [np.array(emb) for emb in embeddings]
            
            # Keep the most recent samples
            recent_samples = embedding_arrays[-max_samples//2:]
            
            # Keep diverse older samples
            older_samples = embedding_arrays[:-max_samples//2]
            if older_samples:
                # Select diverse samples using simple distance-based selection
                selected_older = self._select_diverse_samples(older_samples, max_samples//2)
                final_samples = selected_older + recent_samples
            else:
                final_samples = recent_samples
            
            # Convert back to lists
            return [emb.tolist() for emb in final_samples]
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Pruning error: {e}")
            # Fallback: keep most recent samples
            return embeddings[-max_samples:]
    
    def _select_diverse_samples(self, embeddings, num_samples):
        """🎯 Select diverse voice samples to maintain variety"""
        try:
            if len(embeddings) <= num_samples:
                return embeddings
            
            # Simple diversity selection: evenly spaced samples
            indices = np.linspace(0, len(embeddings)-1, num_samples, dtype=int)
            return [embeddings[i] for i in indices]
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Diversity selection error: {e}")
            return embeddings[:num_samples]
    
    def _update_voice_learning_history(self, profile_id, embedding, confidence):
        """📚 Update voice learning history for adaptation"""
        try:
            if profile_id not in self.voice_learning_history:
                self.voice_learning_history[profile_id] = {
                    'samples': [],
                    'avg_confidence': 0.0,
                    'voice_stability': 1.0,
                    'last_seen': datetime.utcnow().isoformat()
                }
            
            history = self.voice_learning_history[profile_id]
            
            # Add sample
            history['samples'].append({
                'embedding': embedding.tolist(),
                'confidence': confidence,
                'timestamp': datetime.utcnow().isoformat()
            })
            
            # Keep only recent samples
            if len(history['samples']) > 50:
                history['samples'] = history['samples'][-50:]
            
            # Update statistics
            confidences = [s['confidence'] for s in history['samples']]
            history['avg_confidence'] = sum(confidences) / len(confidences)
            history['last_seen'] = datetime.utcnow().isoformat()
            
            # Calculate voice stability (how consistent the voice is)
            if len(history['samples']) >= 3:
                recent_embeddings = [np.array(s['embedding']) for s in history['samples'][-5:]]
                stability = self._calculate_voice_stability(recent_embeddings)
                history['voice_stability'] = stability
            
            print(f"[IntelligentVoiceManager] 📚 Updated learning history for {profile_id}: confidence={history['avg_confidence']:.3f}, stability={history['voice_stability']:.3f}")
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Learning history error: {e}")

    def _calculate_centroid_similarity(self, embedding, cluster_data):
        """🎯 Calculate similarity using centroid method for robust matching"""
        try:
            cluster_embeddings = cluster_data.get('embeddings', [])
            if not cluster_embeddings:
                vdebug(f"[DEBUG] No embeddings in cluster data")
                return 0.0

            # Convert to numpy arrays
            cluster_array = np.array(cluster_embeddings)
            new_embedding_array = np.array(embedding)

            # Calculate centroid (average of all embeddings in cluster)
            centroid = np.mean(cluster_array, axis=0)

            # Calculate cosine similarity to centroid
            similarity = self._calculate_voice_similarity(new_embedding_array, centroid)

            vdebug(f"[DEBUG] 📊 Centroid Analysis:")
            vdebug(f"[DEBUG]   Cluster size: {len(cluster_embeddings)} embeddings")
            vdebug(f"[DEBUG]   Centroid shape: {centroid.shape}")
            vdebug(f"[DEBUG]   Centroid similarity: {similarity:.4f}")
            vdebug(f"[DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")

            return similarity

        except Exception as e:
            print(f"[VoiceManager] ❌ Centroid calculation error: {e}")
            vdebug(f"[DEBUG] Error details: {e}")
            return 0.0

    def find_best_cluster_match_centroid(self, embedding):
        """🎯 Find best matching cluster using centroid method"""
        best_match = None
        best_similarity = 0.0

        vdebug(f"[DEBUG] 🔍 CENTROID MATCHING: Searching for best cluster match...")

        # Check anonymous clusters using centroid
        for cluster_id, cluster_data in anonymous_clusters.items():
            similarity = self._calculate_centroid_similarity(embedding, cluster_data)

            vdebug(f"[DEBUG] 🔍 {cluster_id}: centroid similarity = {similarity:.4f}")

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = (cluster_id, similarity, 'anonymous')

        # Check known users using centroid
        for user_id, user_data in known_users.items():
            if 'embeddings' in user_data:
                similarity = self._calculate_centroid_similarity(embedding, user_data)

                vdebug(f"[DEBUG] 🔍 {user_id}: centroid similarity = {similarity:.4f}")

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = (user_id, similarity, 'known')

        vdebug(f"[DEBUG] 🎯 Best centroid match: {best_match}")
        return best_match

    def check_existing_clusters_with_centroid(self, current_embedding):
        """🔍 Check if current voice matches existing clusters using CENTROID method"""

        print(f"[DEBUG] 🔍 CENTROID STARTUP CHECK - Current embedding shape: {np.array(current_embedding).shape}")
        print(f"[DEBUG] 🔍 Checking {len(anonymous_clusters)} existing clusters with centroids...")
        print(f"[DEBUG] 📅 Current Time: 2025-07-15 12:19:36 UTC")
        print(f"[DEBUG] 👤 User Login: Daveydrz")

        best_match = None
        best_similarity = 0.0

        for cluster_id, cluster_data in anonymous_clusters.items():
            similarity = self._calculate_centroid_similarity(current_embedding, cluster_data)

            print(f"[DEBUG] 📊 {cluster_id} centroid similarity: {similarity:.6f}")

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = cluster_id

        # Use startup recognition threshold (should be same as confident_match_threshold)
        print(f"[DEBUG] 🎯 BEST CENTROID MATCH: {best_match} with similarity {best_similarity:.6f}")
        print(f"[DEBUG] 🎯 CENTROID THRESHOLD: {self.confident_match_threshold}")

        if best_match and best_similarity >= self.confident_match_threshold:
            print(f"[IntelligentVoiceManager] ✅ CENTROID STARTUP MATCH: {best_match} (similarity: {best_similarity:.3f})")
            return best_match, best_similarity
        else:
            print(f"[IntelligentVoiceManager] 🆕 NEW VOICE DETECTED via CENTROID (similarity: {best_similarity:.3f}, threshold: {self.confident_match_threshold})")
            return None, 0.0    

    def _calculate_voice_stability(self, embeddings):
        """📊 Calculate how stable/consistent a voice is"""
        try:
            if len(embeddings) < 2:
                return 1.0

            # Calculate pairwise similarities
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    sim = self._calculate_voice_similarity(embeddings[i], embeddings[j])
                    similarities.append(sim)

            # Average similarity indicates stability
            avg_similarity = sum(similarities) / len(similarities)
            return avg_similarity

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Voice stability calculation error: {e}")
            return 1.0
    
    def _get_display_name(self, profile_id):
        """📛 Get smart display name for profile"""
        try:
            # Check known users first
            if profile_id in known_users:
                user_data = known_users[profile_id]
                return user_data.get('name', profile_id)
            
            # Check anonymous clusters
            elif profile_id in anonymous_clusters:
                cluster_data = anonymous_clusters[profile_id]
                assigned_name = cluster_data.get('test_name', '')
                
                if assigned_name and assigned_name != 'Unknown':
                    return assigned_name
                else:
                    # Extract number from Anonymous_001 → "Speaker 1"
                    if profile_id.startswith('Anonymous_'):
                        try:
                            number = int(profile_id.split('_')[1])
                            return f"Speaker {number}"
                        except:
                            return "Unknown Speaker"
                    return profile_id
            
            return profile_id
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Display name error: {e}")
            return "Unknown"

    def _get_current_voice_cluster_id_enhanced(self) -> Optional[str]:
        """🔍 Enhanced voice cluster ID detection with fallbacks"""
        try:
            # Method 1: Direct current_speaker_cluster_id
            if hasattr(self, 'current_speaker_cluster_id') and self.current_speaker_cluster_id:
                cluster_id = self.current_speaker_cluster_id
                if cluster_id:
                    print(f"[IntelligentVoiceManager] 🔍 Current speaker cluster: {cluster_id}")
                    return cluster_id

            # Method 2: Find most recent anonymous cluster
            if anonymous_clusters:
                sorted_clusters = sorted(
                    anonymous_clusters.items(),
                    key=lambda x: x[1].get('last_updated', '2025-01-01T00:00:00'),
                    reverse=True
                )
                most_recent_cluster = sorted_clusters[0][0]
                print(f"[IntelligentVoiceManager] 🔍 Most recent cluster: {most_recent_cluster}")
                return most_recent_cluster

            print(f"[IntelligentVoiceManager] ⚠️ No voice cluster ID found via any method")
            return None

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error getting cluster ID: {e}")
            return None

    def _reset_confirmation_state(self):
        """🔄 Reset voice confirmation state"""
        self.waiting_for_voice_confirmation = False
        self.pending_confirmation_cluster = None
        self.pending_confirmation_embedding = None
    
    def _generate_current_embedding(self, audio):
        """🎤 Generate embedding from current audio WITH DEBUG"""
        try:
            print(f"[DEBUG] 🎤 Generating embedding from audio...")
            print(f"[DEBUG] Audio type: {type(audio)}")
            print(f"[DEBUG] Audio length: {len(audio) if audio is not None else 'None'}")

            embedding = generate_voice_embedding(audio)

            print(f"[DEBUG] Generated embedding type: {type(embedding)}")
            print(f"[DEBUG] Generated embedding shape: {np.array(embedding).shape if embedding is not None else 'None'}")
            print(f"[DEBUG] Generated embedding first 5 values: {np.array(embedding)[:5] if embedding is not None else 'None'}")

            return embedding

        except Exception as e:
            print(f"[DEBUG] ❌ Embedding generation error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ========== EXISTING METHODS (Keep your existing methods) ==========
    
    def _log_interaction(self, audio, text):
        """Log every interaction for debugging"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'text': text,
                'audio_length': len(audio) if audio is not None else 0,
                'interaction_id': self.interactions
            }
            
            # Save to debug log
            import json
            debug_file = "voice_interactions_debug.json"
            
            try:
                with open(debug_file, 'r') as f:
                    logs = json.load(f)
            except:
                logs = []
            
            logs.append(log_entry)
            
            # Keep only last 50 interactions
            if len(logs) > 50:
                logs = logs[-50:]
            
            with open(debug_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            print(f"[IntelligentVoiceManager] 📝 Logged interaction #{self.interactions}")
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Logging error: {e}")
    
    def _extract_name_from_text(self, text):
        """Extract name from speech"""
        import re
        
        patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
            r"this is (\w+)",
            r"it's (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                name = match.group(1).title()
                if len(name) >= 2 and name.isalpha():
                    return name
        return None
    
    def _handle_name_introduction(self, name, audio, text):
        """Handle when user introduces themselves"""
        print(f"[IntelligentVoiceManager] 🎭 Name introduction detected: {name}")
    
        # ✅ CRITICAL: Create voice profile immediately
        success = self._create_voice_profile(name, audio)
    
        if success:
            print(f"[IntelligentVoiceManager] ✅ Created profile for: {name}")
        
            # ✅ CRITICAL: Link current cluster to this name
            if hasattr(self, 'current_speaker_cluster_id') and self.current_speaker_cluster_id:
                cluster_id = self.current_speaker_cluster_id
                if cluster_id.startswith('Anonymous_'):
                    self.update_current_speaker_name(name)
        
            # 🔥 ADD THIS: Save the database after creating profile
            from voice.database import save_known_users
            save_result = save_known_users()
            if save_result:
                print(f"[IntelligentVoiceManager] 💾 Database saved successfully after name introduction")
            else:
                print(f"[IntelligentVoiceManager] ❌ Failed to save database after name introduction")
        
            return name, "NAME_CONFIRMED"
        else:
            print(f"[IntelligentVoiceManager] ❌ Failed to create profile for: {name}")
            return "Daveydrz", "PROFILE_CREATION_FAILED"
    
    def _handle_name_confirmation(self, text):
        """Handle name confirmation"""
        text_lower = text.lower().strip()
        
        if any(word in text_lower for word in ["yes", "yeah", "correct", "right", "ok"]):
            print(f"[IntelligentVoiceManager] ✅ Name confirmed: {self.suggested_name}")
            self.pending_name_confirmation = False
            confirmed_name = self.suggested_name
            self.suggested_name = None
            return confirmed_name, "NAME_CONFIRMED"
        else:
            print(f"[IntelligentVoiceManager] ❌ Name rejected")
            self.pending_name_confirmation = False
            self.waiting_for_name = True
            return "Guest", "WAITING_FOR_NAME"

    def _handle_name_waiting(self, text):
        """👤 Enhanced name waiting using ultra-intelligent processing"""
        try:
            print(f"[IntelligentVoiceManager] 👤 NAME WAITING - Processing: '{text}'")

            # 🔥 Use ultra-intelligent name extraction if available
            if self.ultra_name_manager:
                print(f"[IntelligentVoiceManager] 🧠 Using ultra-intelligent name processing...")

                name_result = self.ultra_name_manager.handle_name_commands(text)

                if name_result[1] == "ULTRA_INTELLIGENT_INTRODUCTION":
                    extracted_name = name_result[0]

                    print(f"[IntelligentVoiceManager] 🧠 Ultra-intelligent extraction: {extracted_name}")

                    # 🚨 CRITICAL: Force link current cluster to extracted name
                    if hasattr(self, 'current_speaker_cluster_id') and self.current_speaker_cluster_id:
                        if self.current_speaker_cluster_id.startswith('Anonymous_'):
                            print(f"[IntelligentVoiceManager] 🔗 FORCE LINKING: {self.current_speaker_cluster_id} → {extracted_name}")

                            # Import the linking function
                            from voice.database import link_anonymous_to_named, save_known_users

                            # Try linking Anonymous_001 to David
                            success = link_anonymous_to_named(self.current_speaker_cluster_id, extracted_name)
                            print(f"[IntelligentVoiceManager] 🔗 LINK SUCCESS: {success}")

                            if success:
                                # Add current embedding if available
                                if hasattr(self, 'current_voice_embedding') and self.current_voice_embedding is not None:
                                    self._add_embedding_to_profile(extracted_name, self.current_voice_embedding)

                                # 🔥 CRITICAL: Update current speaker cluster ID and user
                                old_cluster = self.current_speaker_cluster_id
                                self.current_speaker_cluster_id = extracted_name  # Now "David"
                                self.current_user = extracted_name              # Now "David"

                                # Force save database
                                save_result = save_known_users()
                                print(f"[IntelligentVoiceManager] 💾 Database save result: {save_result}")

                                # Provide confirmation
                                speak_streaming(f"Nice to meet you, {extracted_name}! I'll remember your voice.")
                                print(f"[IntelligentVoiceManager] ✅ SUCCESSFULLY CONVERTED {old_cluster} → {extracted_name}")

                                # Reset name waiting state
                                self.waiting_for_name = False
                                self.pending_name_confirmation = False
                                self.suggested_name = None

                                return extracted_name, "NAME_ASSIGNED_ULTRA_INTELLIGENT"
                            else:
                                print(f"[IntelligentVoiceManager] ❌ LINKING FAILED!")

                elif name_result[1] in ["NO_COMMAND", "PROBLEMATIC_CONTEXT_BLOCKED"]:
                    # Fallback to original logic
                    print(f"[IntelligentVoiceManager] 🧠 Ultra-intelligent: {name_result[1]} - Using fallback")

                    # Use original extraction as fallback
                    name = self._extract_name_from_text(text)
                    if name:
                        print(f"[IntelligentVoiceManager] 👤 Fallback extraction: {name}")
                        self.waiting_for_name = False
                        self.pending_name_confirmation = True
                        self.suggested_name = name
                        speak_streaming(f"Did you say your name is {name}?")
                        return "Guest", "CONFIRMING_NAME"
                    else:
                        print(f"[IntelligentVoiceManager] ❓ No valid name found via any method")
                        speak_streaming("I didn't catch your name clearly. Could you say it again?")
                        return "Guest", "WAITING_FOR_NAME"

            # Fallback: Use original logic if ultra-intelligent manager not available
            else:
                print(f"[IntelligentVoiceManager] ⚠️ Ultra-intelligent manager not available, using original logic")
                name = self._extract_name_from_text(text)
                if name:
                    print(f"[IntelligentVoiceManager] 👤 Name extracted: {name}")
                    self.waiting_for_name = False
                    self.pending_name_confirmation = True
                    self.suggested_name = name
                    speak_streaming(f"Did you say your name is {name}?")
                    return "Guest", "CONFIRMING_NAME"
                else:
                    print(f"[IntelligentVoiceManager] ❓ No valid name found in: '{text}'")
                    speak_streaming("I didn't catch your name clearly. Could you say it again?")
                    return "Guest", "WAITING_FOR_NAME"

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Enhanced name waiting error: {e}")
            import traceback
            traceback.print_exc()

            # Fallback to original logic
            name = self._extract_name_from_text(text)
            if name:
                self.waiting_for_name = False
                self.pending_name_confirmation = True
                self.suggested_name = name
                speak_streaming(f"Did you say your name is {name}?")
                return "Guest", "CONFIRMING_NAME"
            else:
                speak_streaming("I didn't catch your name clearly. Could you say it again?")
                return "Guest", "WAITING_FOR_NAME"

    def allow_system_username_override(self, name):
        """🔧 Override to allow system username as voice profile"""
        import getpass
        system_user = getpass.getuser()

        if name.lower() == system_user.lower():
            print(f"[VoiceManager] 🔧 SYSTEM USERNAME OVERRIDE: Allowing {name} as voice profile")
            return True
        return False

    def force_process_name_introduction(self, text):
        """🔥 Force process name introduction even if not in waiting state"""
        try:
            print(f"[IntelligentVoiceManager] 🔥 FORCE PROCESSING NAME: '{text}'")

            if self.ultra_name_manager:
                name_result = self.ultra_name_manager.handle_name_commands(text)

                if name_result[1] == "ULTRA_INTELLIGENT_INTRODUCTION":
                    extracted_name = name_result[0]

                    # Force link current cluster
                    if hasattr(self, 'current_speaker_cluster_id') and self.current_speaker_cluster_id:
                        if self.current_speaker_cluster_id.startswith('Anonymous_'):
                            from voice.database import link_anonymous_to_named, save_known_users

                            success = link_anonymous_to_named(self.current_speaker_cluster_id, extracted_name)

                            if success:
                                old_cluster = self.current_speaker_cluster_id
                                self.current_speaker_cluster_id = extracted_name
                                self.current_user = extracted_name

                                save_known_users()

                                print(f"[IntelligentVoiceManager] ✅ FORCE CONVERTED {old_cluster} → {extracted_name}")
                                return extracted_name, "FORCE_CONVERTED"

            return None, "FORCE_CONVERSION_FAILED"

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Force processing error: {e}")
            return None, "FORCE_CONVERSION_ERROR"


    def _check_name_conflicts(self, name): 
        """🔍 Check if name conflicts with existing clusters"""
        try:
            name_lower = name.lower()

            # Check known users
            for user_id, user_data in known_users.items():
                existing_name = user_data.get('name', '').lower()
                if existing_name == name_lower:
                    return f"known_user_{user_id}"

            # Check anonymous clusters
            for cluster_id, cluster_data in anonymous_clusters.items():
                if cluster_id == self.pending_confirmation_cluster:
                    continue  # Skip current cluster

                existing_name = cluster_data.get('test_name', '').lower()
                if existing_name == name_lower:
                    return cluster_id

            return None

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Conflict check error: {e}")
            return None

    def _handle_name_conflict(self, name, conflict_cluster):
        """⚠️ Enhanced conflict resolution using ultra-intelligent analysis"""
        try:
            print(f"[IntelligentVoiceManager] ⚠️ ENHANCED NAME CONFLICT: {name} vs {conflict_cluster}")

            # 🔥 Use ultra-intelligent voice similarity check if available
            if self.ultra_name_manager:
                voice_similarity = self.ultra_name_manager.check_voice_similarity_for_existing_users()

                if voice_similarity:
                    # High confidence same person
                    speak_streaming(f"Oh, I recognize you now, {name}! Adding this to your voice profile.")

                    print(f"[IntelligentVoiceManager] ✅ ULTRA-INTELLIGENT SAME PERSON: Merging with existing {conflict_cluster}")

                    self._add_embedding_to_profile(conflict_cluster, self.pending_confirmation_embedding)
                    self._reset_confirmation_state()
                    self.set_current_cluster(conflict_cluster)

                    return conflict_cluster, "MERGED_WITH_EXISTING_ULTRA"

            # Check similarity to existing cluster
            if conflict_cluster.startswith('Anonymous_'):
                conflict_data = anonymous_clusters.get(conflict_cluster, {})
                conflict_embeddings = conflict_data.get('embeddings', [])

                if conflict_embeddings:
                    similarity = self._calculate_centroid_similarity(self.pending_confirmation_embedding, conflict_data)

                    print(f"[IntelligentVoiceManager] 📊 Voice similarity to existing {name}: {similarity:.3f}")

                    # HIGH SIMILARITY = SAME PERSON
                    if similarity >= 0.65:
                        speak_streaming(f"Oh, I recognize you now, {name}! Adding this to your voice profile.")

                        self._add_embedding_to_profile(conflict_cluster, self.pending_confirmation_embedding)
                        self._reset_confirmation_state()
                        self.set_current_cluster(conflict_cluster)

                        return conflict_cluster, "MERGED_WITH_EXISTING"

                    # MEDIUM SIMILARITY = ASK FOR CLARIFICATION  
                    elif similarity >= 0.45:
                        speak_streaming(f"I think I know you, {name}, but you sound a bit different. Is this really you?")

                        self.waiting_for_name = False
                        self.waiting_for_voice_confirmation = True
                        self.pending_confirmation_cluster = conflict_cluster

                        return conflict_cluster, "ASKING_VOICE_CONFIRMATION"

                    # LOW SIMILARITY = DIFFERENT PERSON
                    else:
                        unique_name = self._create_unique_name(name)

                        speak_streaming(f"I already know a different {name}. I'll call you {unique_name} to keep you separate.")

                        success = self._assign_name_to_cluster(self.pending_confirmation_cluster, unique_name)

                        if success:
                            self._add_embedding_to_profile(self.pending_confirmation_cluster, self.pending_confirmation_embedding)
                            self._reset_confirmation_state()
                            self.set_current_cluster(self.pending_confirmation_cluster)

                            return self.pending_confirmation_cluster, "UNIQUE_NAME_ASSIGNED"

            # Default fallback
            unique_name = self._create_unique_name(name)
            speak_streaming(f"I'll call you {unique_name} to keep you separate from the other {name}.")

            success = self._assign_name_to_cluster(self.pending_confirmation_cluster, unique_name)
            if success:
                self._add_embedding_to_profile(self.pending_confirmation_cluster, self.pending_confirmation_embedding)
                self._reset_confirmation_state()
                self.set_current_cluster(self.pending_confirmation_cluster)

            return self.pending_confirmation_cluster, "UNIQUE_NAME_ASSIGNED"

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Enhanced conflict handling error: {e}")
            return self.pending_confirmation_cluster, "ASKING_FOR_NAME"

    def _assign_name_to_cluster(self, cluster_id, name):
        """📝 Assign name to anonymous cluster"""
        try:
            if cluster_id in anonymous_clusters:
                cluster_data = anonymous_clusters[cluster_id]
                cluster_data['test_name'] = name
                cluster_data['status'] = 'named'
                cluster_data['named_at'] = datetime.utcnow().isoformat()
                cluster_data['last_updated'] = datetime.utcnow().isoformat()

                # Save immediately
                save_result = save_known_users()

                print(f"[IntelligentVoiceManager] 📝 NAME ASSIGNED: {cluster_id} → {name}")
                print(f"[IntelligentVoiceManager] 💾 Save result: {save_result}")

                return save_result

            return False

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Name assignment error: {e}")
            return False

    def _create_unique_name(self, base_name):
        """🔢 Create unique name variation (David → David2, David3, etc.)"""
        try:
            counter = 2

            while True:
                unique_name = f"{base_name}{counter}"

                # Check if this unique name is already taken
                conflict = self._check_name_conflicts(unique_name)

                if not conflict:
                    print(f"[IntelligentVoiceManager] ✅ UNIQUE NAME: {base_name} → {unique_name}")
                    return unique_name

                counter += 1

                # Safety limit
                if counter > 10:
                    timestamp = datetime.utcnow().strftime("%H%M")
                    unique_name = f"{base_name}_{timestamp}"
                    print(f"[IntelligentVoiceManager] ⚠️ FALLBACK UNIQUE NAME: {unique_name}")
                    return unique_name

        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Unique name error: {e}")
            return f"{base_name}_New"
    
    def _create_voice_profile(self, username, audio):
        """Create a basic voice profile"""
        try:
            from voice.recognition import generate_voice_embedding
            
            # Generate embedding
            embedding = generate_voice_embedding(audio)
            if embedding is None:
                print(f"[IntelligentVoiceManager] ❌ Failed to generate embedding for {username}")
                return False
            
            # ✅ CRITICAL: Create profile data
            profile_data = {
                'username': username,
                'name': username,
                'embeddings': [embedding.tolist()],
                'created_date': datetime.utcnow().isoformat(),
                'confidence_threshold': 0.4,
                'status': 'intelligent_trained',
                'recognition_count': 0,
                'last_updated': datetime.utcnow().isoformat(),
                'training_type': 'intelligent_introduction',
                'system': 'IntelligentVoiceManager'
            }
            
            # ✅ CRITICAL: Save to database
            known_users[username] = profile_data
            save_known_users()
            
            print(f"[IntelligentVoiceManager] 💾 Saved profile for: {username}")
            print(f"[IntelligentVoiceManager] 📊 Total profiles: {len(known_users)}")
            
            return True
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Profile creation error: {e}")
            return False
    
    def _add_passive_sample(self, username, audio, confidence):
        """Add passive learning sample"""
        try:
            if username in known_users and confidence > 0.5:
                # Generate embedding and add to profile
                embedding = self._generate_current_embedding(audio)
                if embedding is not None:
                    self._add_embedding_to_profile(username, embedding)
                
                # Update recognition count
                profile = known_users[username]
                profile['recognition_count'] = profile.get('recognition_count', 0) + 1
                profile['last_updated'] = datetime.utcnow().isoformat()
                
                save_known_users()
                
                print(f"[IntelligentVoiceManager] 📈 Updated recognition count for {username}")
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Passive sample error: {e}")
    
    def update_current_speaker_name(self, name: str):
        """🔄 Update current speaker name after recognition"""
        try:
            if hasattr(self, 'current_speaker_cluster_id') and self.current_speaker_cluster_id:
                cluster_id = self.current_speaker_cluster_id
                
                # Update cluster with name
                from voice.database import link_anonymous_to_named
                if cluster_id in anonymous_clusters:
                    # Link to known user
                    success = link_anonymous_to_named(cluster_id, name)
                    if success:
                        print(f"[IntelligentVoiceManager] ✅ Linked {cluster_id} to {name}")
                        self.current_speaker_cluster_id = name
                
                print(f"[IntelligentVoiceManager] ✅ Updated speaker name: {name}")
                
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error updating speaker name: {e}")

    def get_current_voice_embedding(self):
        """🔍 Get current voice embedding"""
        try:
            if hasattr(self, 'current_voice_embedding'):
                return self.current_voice_embedding
            return None
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error getting voice embedding: {e}")
            return None
    
    def set_current_voice_embedding(self, audio):
        """🔄 Set current voice embedding from audio"""
        try:
            embedding = self._generate_current_embedding(audio)
            if embedding is not None:
                self.current_voice_embedding = embedding
                print(f"[IntelligentVoiceManager] 🔄 Updated current voice embedding")
            
        except Exception as e:
            print(f"[IntelligentVoiceManager] ❌ Error setting voice embedding: {e}")
    
    def get_session_stats(self):
        """Get session statistics"""
        return {
            'interactions': self.interactions,
            'session_duration': (datetime.utcnow() - self.session_start).total_seconds(),
            'known_users': len(known_users),
            'anonymous_clusters': len(anonymous_clusters),
            'current_user': self.current_user,
            'system': 'IntelligentVoiceManager',
            'learning_history_profiles': len(self.voice_learning_history)
        }

    def test_embedding_persistence(self):
        """🧪 Test embedding persistence"""
        try:
            print("\n[TEST] 🧪 Testing embedding persistence...")
            
            # Create test embedding
            test_embedding = np.random.rand(256).tolist()
            test_user = "TestUser"
            
            # Add to known_users if not exists
            if test_user not in known_users:
                known_users[test_user] = {
                    'username': test_user,
                    'embeddings': [],
                    'voice_embeddings': [],
                    'status': 'trained',
                    'created_at': datetime.utcnow().isoformat()
                }
            
            # Add embedding
            self._add_embedding_to_profile(test_user, test_embedding)
            
            # Verify storage
            if self.verify_embedding_storage(test_user):
                print("[TEST] ✅ Embedding persistence test PASSED")
                return True
            else:
                print("[TEST] ❌ Embedding persistence test FAILED")
                return False
                
        except Exception as e:
            print(f"[TEST] ❌ Test error: {e}")
            return False

# Global intelligent voice manager
voice_manager = IntelligentVoiceManager()

# 🔧 Initialize ultra-intelligent name manager AFTER voice_manager exists
def initialize_name_manager():
    """Initialize name manager after voice_manager is fully created"""
    global voice_manager
    try:
        from voice.manager_names import UltraIntelligentNameManager
        if voice_manager is not None:
            voice_manager.ultra_name_manager = UltraIntelligentNameManager()
            print(f"[VoiceManager] 🧠 Ultra-intelligent name manager connected successfully")
        else:
            print(f"[VoiceManager] ❌ voice_manager is None during initialization")
    except Exception as e:
        print(f"[VoiceManager] ⚠️ Ultra-intelligent name manager failed: {e}")
        if voice_manager is not None:
            voice_manager.ultra_name_manager = None

# Initialize after voice_manager is created
if 'voice_manager' in globals() and voice_manager is not None:
    initialize_name_manager()
else:
    print(f"[VoiceManager] ❌ voice_manager not available for name manager initialization")
