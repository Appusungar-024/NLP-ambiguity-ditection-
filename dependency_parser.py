"""
Dependency Parser Module

Provides dependency parsing capabilities using spaCy and NLTK alternatives.
This enables detection of syntactic ambiguity through multiple parsing paths.
"""

from typing import List, Tuple, Optional, Dict
from pathlib import Path
import sys

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from nltk import Tree
from nltk.chunk import ne_chunk


class DependencyParser:
    """Dependency parser using spaCy."""
    
    def __init__(self, model: str = "en_core_web_sm"):
        """
        Initialize the dependency parser.
        
        Args:
            model: spaCy model name
        """
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy is not installed. Install with: pip install spacy")
        
        self.model = model
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Downloading spaCy model: {model}")
            import subprocess
            subprocess.run([sys.executable, "-m", "spacy", "download", model], 
                          check=True, capture_output=True)
            self.nlp = spacy.load(model)
    
    def parse(self, text: str) -> 'spacy.tokens.Doc':
        """
        Parse text using spaCy dependency parser.
        
        Args:
            text: Input text
            
        Returns:
            spaCy Doc object
        """
        doc = self.nlp(text)
        return doc
    
    def get_dependencies(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Extract dependency relations from text.
        
        Args:
            text: Input text
            
        Returns:
            List of (head_word, dep_relation, child_word) tuples
        """
        doc = self.parse(text)
        deps = []
        
        for token in doc:
            if token.head != token:  # Skip root's self-loop
                deps.append((token.head.text, token.dep_, token.text))
        
        return deps
    
    def get_syntax_tree_structure(self, text: str) -> Dict:
        """
        Get tree structure representation of dependencies.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with tree structure
        """
        doc = self.parse(text)
        
        # Find root
        root = None
        for token in doc:
            if token.head == token:
                root = token
                break
        
        def build_tree(token):
            children = [child for child in token.children]
            return {
                'text': token.text,
                'tag': token.pos_,
                'dep': token.dep_,
                'children': [build_tree(child) for child in children]
            }
        
        if root:
            return build_tree(root)
        return {}
    
    def get_entities(self, text: str) -> List[Tuple[str, str]]:
        """
        Extract named entities.
        
        Args:
            text: Input text
            
        Returns:
            List of (entity_text, entity_label) tuples
        """
        doc = self.parse(text)
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        return entities
    
    def get_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases.
        
        Args:
            text: Input text
            
        Returns:
            List of noun phrases
        """
        doc = self.parse(text)
        noun_phrases = [chunk.text for chunk in doc.noun_chunks]
        return noun_phrases


class ParseTree:
    """Represents a parse tree for ambiguity analysis."""
    
    def __init__(self, dependencies: List[Tuple[str, str, str]], 
                 tokens: List[str], 
                 tree_id: int = 0):
        """
        Initialize a parse tree.
        
        Args:
            dependencies: List of dependency tuples
            tokens: List of tokens
            tree_id: Unique identifier for this tree
        """
        self.dependencies = dependencies
        self.tokens = tokens
        self.tree_id = tree_id
    
    def __eq__(self, other):
        """Check if two parse trees are identical."""
        if not isinstance(other, ParseTree):
            return False
        return set(self.dependencies) == set(other.dependencies)
    
    def __hash__(self):
        """Make parse tree hashable for set operations."""
        return hash(frozenset(self.dependencies))
    
    def __repr__(self):
        """String representation."""
        return f"ParseTree({self.tree_id}): {self.dependencies}"


class AmbiguityAnalyzer:
    """Analyzes parsing ambiguity through multiple parsing methods."""
    
    def __init__(self):
        """Initialize the ambiguity analyzer."""
        try:
            self.dep_parser = DependencyParser()
        except Exception as e:
            print(f"Warning: Could not initialize dependency parser: {e}")
            self.dep_parser = None
    
    def analyze_dependency_ambiguity(self, text: str) -> Dict:
        """
        Analyze syntactic ambiguity using dependency parsing.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with ambiguity analysis
        """
        if not self.dep_parser:
            return {'error': 'Dependency parser not available'}
        
        doc = self.dep_parser.parse(text)
        deps = self.dep_parser.get_dependencies(text)
        noun_phrases = self.dep_parser.get_noun_phrases(text)
        
        # Potential ambiguity indicators
        indicators = []
        
        # Check for prepositional phrase attachment ambiguity
        pp_count = sum(1 for _, dep, _ in deps if dep in ['prep', 'pmod'])
        if pp_count > 1:
            indicators.append("Multiple prepositional phrases (PP-attachment ambiguity)")
        
        # Check for coordinate structures
        conj_count = sum(1 for _, dep, _ in deps if dep in ['conj', 'cc'])
        if conj_count > 1:
            indicators.append("Multiple coordinated structures (coordination ambiguity)")
        
        # Check for noun sequences
        if len(noun_phrases) > 1:
            indicators.append(f"Multiple noun phrases (possible attachment ambiguity)")
        
        return {
            'tokens': [token.text for token in doc],
            'dependencies': deps,
            'noun_phrases': noun_phrases,
            'entities': self.dep_parser.get_entities(text),
            'ambiguity_indicators': indicators,
            'potentially_ambiguous': len(indicators) > 0
        }
    
    def compare_parse_structures(self, text: str) -> Dict:
        """
        Compare multiple parsing perspectives.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary comparing different parse structures
        """
        if not self.dep_parser:
            return {'error': 'Dependency parser not available'}
        
        doc = self.dep_parser.parse(text)
        tree = self.dep_parser.get_syntax_tree_structure(text)
        
        return {
            'dependency_tree': tree,
            'tokens_count': len(doc),
            'pos_tags': [(token.text, token.pos_, token.tag_) for token in doc],
        }


# Example usage and testing
if __name__ == '__main__':
    if not SPACY_AVAILABLE:
        print("spaCy not installed. Install with: pip install spacy")
        sys.exit(1)
    
    print("=" * 80)
    print("DEPENDENCY PARSER AND AMBIGUITY ANALYZER DEMO")
    print("=" * 80)
    
    analyzer = AmbiguityAnalyzer()
    
    test_sentences = [
        "I saw the man with the telescope in the park",
        "She visited the museum with interesting exhibits",
        "He gave the book to his friend during class"
    ]
    
    for sent in test_sentences:
        print(f"\n\nSentence: {sent}")
        print("-" * 80)
        
        result = analyzer.analyze_dependency_ambiguity(sent)
        
        print(f"Tokens: {result['tokens']}")
        print(f"Dependencies: {result['dependencies']}")
        print(f"Noun Phrases: {result['noun_phrases']}")
        print(f"Entities: {result['entities']}")
        print(f"Ambiguity Indicators: {result['ambiguity_indicators']}")
        print(f"Potentially Ambiguous: {result['potentially_ambiguous']}")
        
        compare = analyzer.compare_parse_structures(sent)
        print(f"\nPOS Tags: {compare['pos_tags']}")
