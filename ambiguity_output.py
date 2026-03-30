"""
Ambiguity Output Module

Provides structured output with detailed explanations and classifications
for ambiguous/non-ambiguous sentences.
"""

from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
from pathlib import Path
import sys

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


class AmbiguityType(Enum):
    """Types of ambiguity detected."""
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    LEXICAL = "lexical"
    PP_ATTACHMENT = "pp_attachment"
    COORDINATION = "coordination"
    SCOPE = "scope"
    NONE = "none"


class AmbiguityLevel(Enum):
    """Severity levels of ambiguity."""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class AmbiguityResult:
    """Data class for ambiguity detection result."""
    sentence: str
    is_ambiguous: bool
    ambiguity_level: str
    ambiguity_types: List[str]
    parse_count: int
    confidence: float
    ambiguity_score: float
    explanations: List[str]
    ambiguous_phrases: List[str]
    suggestions: List[str]
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class AmbiguityClassifier:
    """Classifies and explains ambiguity in sentences."""
    
    def __init__(self):
        """Initialize the classifier."""
        self.ambiguity_patterns = {
            'prep_phrase': r'(?:with|in|on|at|by|from|to)\s+(?:the|a|an)',
            'coordination': r'\s+(?:and|or|but)\s+',
            'relative_clause': r'(?:which|that|who)\s+',
            'noun_compound': r'[A-Za-z]+\s+[A-Za-z]+\s+[A-Za-z]+',
        }
    
    def classify(self, sentence: str, 
                 parse_trees: Optional[List[Any]] = None,
                 dependency_info: Optional[Dict] = None,
                 pos_tags: Optional[List[Tuple[str, str]]] = None) -> AmbiguityResult:
        """
        Classify a sentence for ambiguity.
        
        Args:
            sentence: Input sentence
            parse_trees: List of parse trees (from CFG parser)
            dependency_info: Dependency parsing information
            pos_tags: Part-of-speech tags
            
        Returns:
            AmbiguityResult object
        """
        parse_count = len(parse_trees) if parse_trees else 0
        ambiguity_types = []
        explanations = []
        ambiguous_phrases = []
        suggestions = []
        confidence = 0.0
        
        # Rule 1: Multiple parse trees indicate syntactic ambiguity
        if parse_count > 1:
            ambiguity_types.append(AmbiguityType.SYNTACTIC.value)
            explanations.append(f"Multiple valid parse trees detected ({parse_count} parses)")
            confidence = min(1.0, parse_count / 5.0)  # Normalize to 0-1
        
        # Rule 2: Check dependency information for ambiguity indicators
        if dependency_info and dependency_info.get('ambiguity_indicators'):
            for indicator in dependency_info['ambiguity_indicators']:
                ambiguity_types.append(AmbiguityType.SYNTACTIC.value)
                explanations.append(indicator)
                confidence = max(confidence, 0.7)
            
            # Extract ambiguous phrases
            if 'noun_phrases' in dependency_info:
                ambiguous_phrases = dependency_info['noun_phrases']
        
        # Rule 3: Lexical ambiguity (homonyms, polysemy)
        lexical_amb = self._check_lexical_ambiguity(sentence, pos_tags)
        if lexical_amb['found']:
            ambiguity_types.append(AmbiguityType.LEXICAL.value)
            explanations.extend(lexical_amb['explanations'])
            ambiguous_phrases.extend(lexical_amb['phrases'])
            confidence = max(confidence, 0.5)
        
        # Rule 4: PP-attachment specific patterns
        pp_info = self._detect_pp_attachment(sentence, parse_trees, dependency_info)
        if pp_info['found']:
            ambiguity_types.append(AmbiguityType.PP_ATTACHMENT.value)
            explanations.append(pp_info['explanation'])
            ambiguous_phrases.extend(pp_info['phrases'])
            suggestions.append("Consider adding context or clarifying the attachment of prepositional phrases")
            confidence = max(confidence, 0.8)
        
        # Rule 5: Coordination ambiguity
        coord_info = self._detect_coordination(sentence)
        if coord_info['found']:
            ambiguity_types.append(AmbiguityType.COORDINATION.value)
            explanations.append(coord_info['explanation'])
            ambiguous_phrases.extend(coord_info['phrases'])
            suggestions.append("Clarify the scope of coordinate structures with punctuation or restructuring")
            confidence = max(confidence, 0.6)
        
        # Calculate ambiguity score (0-1 scale) based on multiple factors
        ambiguity_score = self._calculate_ambiguity_score(
            parse_count=parse_count,
            confidence=confidence,
            num_ambiguity_types=len(ambiguity_types),
            dependency_info=dependency_info,
            pos_tags=pos_tags
        )
        
        # Determine ambiguity level based on score
        if ambiguity_score < 0.2:
            ambiguity_level = AmbiguityLevel.NONE
            is_ambiguous = False
        elif ambiguity_score < 0.4:
            ambiguity_level = AmbiguityLevel.LOW
            is_ambiguous = True
        elif ambiguity_score < 0.65:
            ambiguity_level = AmbiguityLevel.MEDIUM
            is_ambiguous = True
        else:
            ambiguity_level = AmbiguityLevel.HIGH
            is_ambiguous = True
        
        # Add general suggestions
        if not is_ambiguous:
            suggestions.append("Sentence is clear and unambiguous")
        else:
            if not suggestions:
                suggestions.append("Consider rephrasing for clarity")
        
        # Remove duplicates
        ambiguity_types = list(set(ambiguity_types))
        explanations = list(set(explanations))
        suggestions = list(set(suggestions))
        
        return AmbiguityResult(
            sentence=sentence,
            is_ambiguous=is_ambiguous,
            ambiguity_level=ambiguity_level.name,
            ambiguity_types=ambiguity_types,
            parse_count=parse_count,
            confidence=confidence,
            ambiguity_score=ambiguity_score,
            explanations=explanations,
            ambiguous_phrases=list(set(ambiguous_phrases)),
            suggestions=suggestions,
            metadata={
                'parse_count': parse_count,
                'has_dependencies': dependency_info is not None,
                'has_pos_tags': pos_tags is not None,
                'ambiguity_score': ambiguity_score,
            }
        )
    
    def _check_lexical_ambiguity(self, sentence: str, 
                                 pos_tags: Optional[List[Tuple[str, str]]] = None) -> Dict:
        """Check for lexical ambiguity (polysemy, homonymy)."""
        # Common polysemous words
        polysemous_words = {
            'bank': ['financial institution', 'river bank', 'turn sharply'],
            'bark': ['dog sound', 'tree covering'],
            'bat': ['flying mammal', 'sports equipment'],
            'bear': ['animal', 'to carry', 'to endure'],
            'bow': ['weapon', 'front of ship', 'to bend'],
            'can': ['container', 'ability', 'to preserve'],
            'crane': ['bird', 'machine'],
            'draw': ['to sketch', 'attraction', 'to pull'],
            'lead': ['to guide', 'metal'],
            'left': ['direction', 'departed'],
            'light': ['illumination', 'not heavy'],
            'match': ['fire-starting stick', 'to pair'],
            'mine': ['excavation', 'possession'],
            'order': ['command', 'arrangement'],
            'plant': ['vegetation', 'factory', 'to place'],
            'pound': ['currency', 'weight unit', 'to strike'],
            'ring': ['circle', 'bell sound'],
            'saw': ['past of see', 'cutting tool'],
            'scale': ['climb', 'fish covering', 'measurement'],
            'seal': ['animal', 'to close'],
            'spring': ['season', 'to jump', 'water source'],
            'tear': ['to rip', 'from eye'],
            'track': ['path', 'to follow'],
            'wind': ['moving air', 'to twist'],
        }
        
        words_in_sentence = sentence.lower().split()
        found_ambiguous = []
        
        for word in words_in_sentence:
            # Remove punctuation
            clean_word = word.rstrip('.,!?;:')
            if clean_word in polysemous_words:
                found_ambiguous.append(clean_word)
        
        result = {
            'found': len(found_ambiguous) > 0,
            'phrases': found_ambiguous,
            'explanations': []
        }
        
        if found_ambiguous:
            result['explanations'] = [
                f"Polysemous word(s) detected: {', '.join(found_ambiguous)} (multiple meanings)"
            ]
        
        return result
    
    def _calculate_ambiguity_score(self, parse_count: int, confidence: float, 
                                   num_ambiguity_types: int, 
                                   dependency_info: Optional[Dict] = None,
                                   pos_tags: Optional[List[Tuple[str, str]]] = None) -> float:
        """
        Calculate an ambiguity score (0-1 scale) based on multiple factors.
        
        Scoring factors:
        - Parse trees (0-0.35): Multiple parse trees indicate high ambiguity
        - Confidence (0-0.25): Rule-based confidence from initial classification
        - Ambiguity types (0-0.25): More types = more ambiguity
        - Dependency info (0-0.1): Structural complexity indicators
        - POS tags (0-0.05): Linguistic patterns that cause ambiguity
        
        Args:
            parse_count: Number of parse trees
            confidence: Confidence score from initial classification
            num_ambiguity_types: Number of ambiguity types detected
            dependency_info: Dependency parsing information
            pos_tags: Part-of-speech tags
            
        Returns:
            Ambiguity score (0.0 = no ambiguity, 1.0 = maximum ambiguity)
        """
        score = 0.0
        
        # Factor 1: Parse tree count (0-0.35)
        # More parse trees = higher ambiguity
        if parse_count > 1:
            parse_score = min(0.35, (parse_count - 1) * 0.1)
            score += parse_score
        
        # Factor 2: Confidence from initial rules (0-0.25)
        score += confidence * 0.25
        
        # Factor 3: Number of ambiguity types (0-0.25)
        # More types of ambiguity detected = higher score
        type_score = min(0.25, num_ambiguity_types * 0.08)
        score += type_score
        
        # Factor 4: Dependency complexity (0-0.1)
        if dependency_info:
            indicators = dependency_info.get('ambiguity_indicators', [])
            noun_phrases = dependency_info.get('noun_phrases', [])
            # More complex dependency structures add to score
            dep_score = min(0.1, len(indicators) * 0.03 + len(noun_phrases) * 0.02)
            score += dep_score
        
        # Factor 5: POS tag complexity (0-0.05)
        if pos_tags:
            # Check for common ambiguity-inducing patterns
            tags = [tag for _, tag in pos_tags]
            # Count prepositions (IN) and coordinating conjunctions (CC)
            prepositions = tags.count('IN')
            conjunctions = tags.count('CC')
            # More PPs and CCs add to ambiguity
            pos_score = min(0.05, (prepositions + conjunctions) * 0.01)
            score += pos_score
        
        # Normalize to 0-1 range (should already be normalized, but ensure it)
        return min(1.0, score)
    
    def _detect_pp_attachment(self, sentence: str, 
                              parse_trees: Optional[List] = None,
                              dependency_info: Optional[Dict] = None) -> Dict:
        """Detect prepositional phrase attachment ambiguity."""
        # Simple pattern-based detection
        pp_verbs = ['saw', 'heard', 'watched', 'noticed', 'observed']
        pp_preps = ['with', 'in', 'on', 'at', 'by', 'from']
        
        found = False
        phrases = []
        explanation = ""
        
        sentence_lower = sentence.lower()
        
        for verb in pp_verbs:
            if verb in sentence_lower:
                for prep in pp_preps:
                    if f"{verb}" in sentence_lower and prep in sentence_lower:
                        found = True
                        phrases.append(f"{verb} ... {prep}")
                        explanation = f"PP-attachment ambiguity: '{prep}' could attach to '{verb}' or to its object"
                        break
        
        if dependency_info and 'ambiguity_indicators' in dependency_info:
            for indicator in dependency_info['ambiguity_indicators']:
                if 'PP' in indicator or 'attachment' in indicator.lower():
                    found = True
                    explanation = indicator
        
        return {
            'found': found,
            'phrases': phrases,
            'explanation': explanation
        }
    
    def _detect_coordination(self, sentence: str) -> Dict:
        """Detect coordination ambiguity."""
        coord_conjuncts = [' and ', ' or ', ' but ']
        found = False
        phrases = []
        explanation = ""
        
        count = 0
        for conj in coord_conjuncts:
            if conj in sentence:
                count += 1
                phrases.append(conj.strip())
        
        if count > 1:
            found = True
            explanation = f"Coordination ambiguity: Multiple conjunctions detected, scope may be ambiguous"
        
        return {
            'found': found,
            'phrases': phrases,
            'explanation': explanation
        }


class OutputFormatter:
    """Formats ambiguity detection results for various outputs."""
    
    @staticmethod
    def format_text(result: AmbiguityResult) -> str:
        """Format result as readable text."""
        lines = []
        lines.append("=" * 80)
        lines.append(f"SENTENCE: {result.sentence}")
        lines.append("=" * 80)
        lines.append(f"Classification: {'AMBIGUOUS' if result.is_ambiguous else 'NOT AMBIGUOUS'}")
        lines.append(f"Ambiguity Level: {result.ambiguity_level}")
        lines.append(f"Ambiguity Score: {result.ambiguity_score:.3f} (0.0 = clear, 1.0 = highly ambiguous)")
        lines.append(f"Confidence: {result.confidence:.2%}")
        lines.append(f"Number of Parse Trees: {result.parse_count}")
        
        if result.ambiguity_types:
            lines.append(f"\nAmbiguity Types:")
            for amb_type in result.ambiguity_types:
                lines.append(f"  • {amb_type}")
        
        if result.explanations:
            lines.append(f"\nExplanations:")
            for i, exp in enumerate(result.explanations, 1):
                lines.append(f"  {i}. {exp}")
        
        if result.ambiguous_phrases:
            lines.append(f"\nAmbiguous Phrases/Words:")
            for phrase in result.ambiguous_phrases:
                lines.append(f"  • {phrase}")
        
        if result.suggestions:
            lines.append(f"\nSuggestions:")
            for i, sugg in enumerate(result.suggestions, 1):
                lines.append(f"  {i}. {sugg}")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    @staticmethod
    def format_json(result: AmbiguityResult) -> str:
        """Format result as JSON."""
        return result.to_json()
    
    @staticmethod
    def format_csv_header() -> str:
        """Get CSV header."""
        return "sentence,is_ambiguous,ambiguity_level,ambiguity_score,ambiguity_types,parse_count,confidence,explanations,ambiguous_phrases,suggestions"
    
    @staticmethod
    def format_csv_row(result: AmbiguityResult) -> str:
        """Format result as CSV row."""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            result.sentence,
            str(result.is_ambiguous),
            result.ambiguity_level,
            f"{result.ambiguity_score:.3f}",
            '|'.join(result.ambiguity_types),
            result.parse_count,
            f"{result.confidence:.3f}",
            '|'.join(result.explanations),
            '|'.join(result.ambiguous_phrases),
            '|'.join(result.suggestions),
        ])
        
        return output.getvalue().strip()


# Example usage and testing
if __name__ == '__main__':
    print("=" * 80)
    print("AMBIGUITY OUTPUT MODULE DEMO")
    print("=" * 80)
    
    classifier = OutputFormatter()
    ambiguity_classifier = AmbiguityClassifier()
    
    test_cases = [
        {
            'sentence': 'I saw the man with the telescope',
            'parse_trees': [1, 2],  # Simulate 2 parse trees
            'dependency_info': {
                'ambiguity_indicators': ['Multiple prepositional phrases'],
                'noun_phrases': ['the man', 'the telescope']
            }
        },
        {
            'sentence': 'She ate the pizza with mushrooms',
            'parse_trees': [1, 2],
            'dependency_info': {'ambiguity_indicators': []}
        },
        {
            'sentence': 'The bank can accept new customers',
            'parse_trees': [1],
            'dependency_info': {'ambiguity_indicators': []}
        }
    ]
    
    for test in test_cases:
        result = ambiguity_classifier.classify(
            sentence=test['sentence'],
            parse_trees=test.get('parse_trees'),
            dependency_info=test.get('dependency_info')
        )
        
        print(OutputFormatter.format_text(result))
        print("\n")
