"""
Query Router for Intent Classification

Routes user queries to appropriate agents based on intent classification.
This is Layer 1 (Query Intelligence) in the orchestration architecture.

Part of Phase 1: Foundation
"""

import re
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Intent(str, Enum):
    """Query intent types"""
    PICOT = "picot"  # PICOT question development
    SEARCH = "search"  # Literature search
    TIMELINE = "timeline"  # Project timeline/milestones
    DATA_ANALYSIS = "data_analysis"  # Data analysis planning
    WRITING = "writing"  # Research writing
    UNKNOWN = "unknown"  # Cannot classify


class QueryRouter:
    """
    Routes queries to appropriate agents using keyword-based classification.
    
    Phase 1 uses keyword/regex patterns (no LLM).
    LLM-based classification will be added in Phase 2.
    """
    
    def __init__(self):
        """Initialize router with intent patterns"""
        # Define keyword patterns for each intent
        self.intent_patterns = {
            Intent.PICOT: [
                r'\b(picot|pico)\b',
                r'\bresearch question\b',
                r'\bpopulation.*intervention.*comparison.*outcome\b',
                r'\bformulate.*question\b',
                r'\bdefine.*research\b',
                r'\bdevelop.*question\b',
                r'\bhelp.*picot\b',
            ],
            Intent.SEARCH: [
                r'\b(search|find|locate|retrieve)\b.*\b(articles|papers|studies|literature)\b',
                r'\bpubmed\b',
                r'\bmedline\b',
                r'\bliterature\b',
                r'\bevidence\b',
                r'\bresearch\b.*\b(cauti|clabsi|pressure.*ulcer|fall)\b',
                r'\b(need|want)\b.*\b(literature|articles|studies)\b',
            ],
            Intent.TIMELINE: [
                r'\b(timeline|schedule|milestone|milestones|deadline|deadlines)\b',
                r'\bwhen\b.*\b(due|next)\b',
                r'\bwhat\b.*\b(due|next)\b',
                r'\bproject\b.*\b(plan|timeline)\b',
                r'\bcalendar\b',
                r'\bnext step\b',
                r'\bshow\b.*\b(timeline|milestone)\b',
                r'\bdue\b.*\b(this|next)\b.*\b(week|month)\b',
                r'\b(this|next)\b.*\b(week|month)\b.*\b(due|deadline)\b',
                r'\bwhat.*month\b',
                r'\bmonthly\b',
                r'\bupcoming\b',
            ],
            Intent.DATA_ANALYSIS: [
                r'\b(data|statistics|statistical)\b.*\b(analysis|analyze|plan)\b',
                r'\banalyze\b',
                r'\bmeasure\b',
                r'\bmetric\b',
                r'\boutcome measure\b',
                r'\bspss|excel|chi.*square|t.*test\b',
                r'\bsample\s*size\b',
                r'\bpower\s*analysis\b',
                r'\bcalculate\b.*\b(sample|size|power)\b',
                r'\b(rct|trial)\b',
                r'\bsignificance\b',
                r'\bp.?value\b',
                r'\bconfidence\s*interval\b',
            ],
            Intent.WRITING: [
                r'\b(write|draft|compose|edit|synthesize)\b',
                r'\bpaper\b',
                r'\bmanuscript\b',
                r'\babstract\b',
                r'\bintroduction|methods|results|discussion\b',
                r'\bcitation|reference\b',
                r'\bapa\b.*\bformat\b',
                r'\bliterature\s*review\b',
                r'\bsynthesis\b',
                r'\bsummarize\b',
                r'\bsummary\b',
                r'\bparagraph\b',
                r'\bessay\b',
            ],
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {
            intent: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for intent, patterns in self.intent_patterns.items()
        }
    
    def classify_intent(self, query: str) -> Intent:
        """
        Classify query intent using keyword matching.
        
        Args:
            query: User query string
        
        Returns:
            Intent enum value (PICOT, SEARCH, etc.)
        """
        if not query or not isinstance(query, str):
            return Intent.UNKNOWN
        
        # Count matches for each intent
        intent_scores = {}
        
        for intent, patterns in self.compiled_patterns.items():
            matches = sum(1 for pattern in patterns if pattern.search(query))
            if matches > 0:
                intent_scores[intent] = matches
        
        # Return intent with highest score
        if not intent_scores:
            return Intent.UNKNOWN
        
        return max(intent_scores, key=intent_scores.get)
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract key entities from query (simple keyword extraction).
        
        Args:
            query: User query string
        
        Returns:
            Dict of entity types to extracted values
        """
        entities = {
            "conditions": [],
            "interventions": [],
            "databases": [],
        }
        
        # Common health conditions
        condition_patterns = [
            r'\bcauti\b', r'\bclabsi\b', r'\bpressure.*ulcer\b',
            r'\bfall\b', r'\bsepsis\b', r'\buti\b',
        ]
        
        # Common interventions
        intervention_patterns = [
            r'\bbundle\b', r'\bprotocol\b', r'\bchecklist\b',
            r'\beducation\b', r'\btraining\b',
        ]
        
        # Databases
        database_patterns = [
            r'\bpubmed\b', r'\bmedline\b', r'\bcinahl\b',
            r'\bembase\b', r'\bcochrane\b',
        ]
        
        query_lower = query.lower()
        
        for pattern in condition_patterns:
            if re.search(pattern, query_lower):
                entities["conditions"].append(pattern.strip(r'\b'))
        
        for pattern in intervention_patterns:
            if re.search(pattern, query_lower):
                entities["interventions"].append(pattern.strip(r'\b'))
        
        for pattern in database_patterns:
            if re.search(pattern, query_lower):
                entities["databases"].append(pattern.strip(r'\b'))
        
        return entities
    
    def estimate_confidence(self, query: str, intent: Intent) -> float:
        """
        Estimate confidence in the intent classification.
        
        Args:
            query: User query string
            intent: Classified intent
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if intent == Intent.UNKNOWN:
            return 0.0
        
        # Count pattern matches
        patterns = self.compiled_patterns.get(intent, [])
        matches = sum(1 for pattern in patterns if pattern.search(query))
        
        if matches == 0:
            return 0.0
        
        # Simple heuristic: more matches = higher confidence
        # 1 match = 0.65, 2 matches = 0.85, 3+ matches = 0.95
        if matches == 1:
            return 0.65
        elif matches == 2:
            return 0.85
        else:
            return 0.95
    
    def route_query(self, query: str) -> Tuple[Intent, float, Dict[str, List[str]]]:
        """
        Complete routing: classify intent, extract entities, estimate confidence.
        
        Args:
            query: User query string
        
        Returns:
            Tuple of (intent, confidence, entities)
        """
        intent = self.classify_intent(query)
        confidence = self.estimate_confidence(query, intent)
        entities = self.extract_entities(query)
        
        return intent, confidence, entities
