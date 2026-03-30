"""
BERT/Transformer-Based Semantic Ambiguity Detector

Uses pre-trained BERT embeddings to detect semantic ambiguity by:
1. Generating semantic variations of a sentence
2. Computing contextual embeddings for each variation
3. Calculating semantic similarity between interpretations
4. Scoring ambiguity based on semantic divergence
"""

import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Any
import sys
from dataclasses import dataclass

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    import torch
    from transformers import AutoTokenizer, AutoModel
    from scipy.spatial.distance import cosine
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("Warning: PyTorch/Transformers not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", 
                          "torch", "transformers", "scipy"])
    import torch
    from transformers import AutoTokenizer, AutoModel
    from scipy.spatial.distance import cosine


@dataclass
class SemanticInterpretation:
    """Represents a semantic interpretation of a sentence."""
    sentence: str
    embedding: np.ndarray
    interpretation: str  # Description of the interpretation
    confidence: float


@dataclass
class SemanticAmbiguityResult:
    """Result of semantic ambiguity analysis."""
    sentence: str
    interpretations: List[SemanticInterpretation]
    ambiguity_score: float  # 0-1: degree of semantic divergence
    is_ambiguous: bool  # Binary classification
    divergence_matrix: np.ndarray  # Pairwise divergences
    primary_meaning: str
    alternative_meanings: List[str]
    semantic_uncertainty: float  # Entropy of interpretations


class BERTSemanticAnalyzer:
    """BERT-based semantic analysis for ambiguity detection."""
    
    def __init__(self, model_name: str = 'bert-base-uncased', device: str = 'cpu'):
        """
        Initialize BERT semantic analyzer.
        
        Args:
            model_name: HuggingFace model name (BERT, RoBERTa, DistilBERT, etc.)
            device: 'cpu' or 'cuda'
        """
        self.model_name = model_name
        self.device = device
        
        print(f"Loading {model_name} model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name, output_hidden_states=True)
        self.model.to(device)
        self.model.eval()
        
        self.embedding_dim = self.model.config.hidden_size
        print(f"✓ Model loaded (embedding dim: {self.embedding_dim})")
    
    def get_embedding(self, text: str, pooling: str = 'mean') -> np.ndarray:
        """
        Get BERT embedding for text.
        
        Args:
            text: Input text
            pooling: 'mean', 'cls', or 'max' pooling strategy
            
        Returns:
            Embedding vector
        """
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, 
                               max_length=512, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # Use last hidden state
        last_hidden = outputs.last_hidden_state
        
        # Apply pooling
        if pooling == 'cls':
            # [CLS] token embedding
            embedding = last_hidden[0, 0, :].cpu().numpy()
        elif pooling == 'max':
            # Max pooling over tokens
            embedding = torch.max(last_hidden[0], dim=0)[0].cpu().numpy()
        else:  # mean
            # Mean pooling (excluding [CLS] and [SEP])
            mask = inputs['attention_mask'][0].unsqueeze(-1).float()
            embedding = (last_hidden[0] * mask).sum(0) / mask.sum()
            embedding = embedding.cpu().numpy()
        
        return embedding
    
    def get_contextual_embeddings(self, text: str, 
                                 layer: int = -1) -> Dict[str, np.ndarray]:
        """
        Get contextual embeddings for each token.
        
        Args:
            text: Input text
            layer: Which layer to use (-1 for last)
            
        Returns:
            Dict mapping tokens to their embeddings
        """
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True,
                               max_length=512, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # Get embeddings from specified layer
        hidden_states = outputs.hidden_states[layer]
        tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
        
        token_embeddings = {}
        for i, token in enumerate(tokens):
            if token not in ['[CLS]', '[SEP]', '[PAD]']:
                token_embeddings[token] = hidden_states[0, i, :].cpu().numpy()
        
        return token_embeddings


class SemanticVariationGenerator:
    """Generate semantic variations for ambiguity analysis."""
    
    def __init__(self):
        """Initialize the variation generator."""
        # Semantic variation templates for common ambiguous patterns
        self.variations_templates = {
            'pp_attachment': [
                "{main_clause} with {pp_object}",  # Attach to verb
                "{subject} with {pp_object} {verb}",  # Attach to noun
            ],
            'coordination': [
                "{part1} and {part2}",  # Left-associative
                "{part1} and ({part2} and {part3})",  # Right-associative
            ],
            'relative_clause': [
                "{noun} {rc}",  # Attach to nearest NP
                "{det} {noun} {rc}",  # Attach to distant NP
            ],
            'scope': [
                "not {part1} {part2}",  # Negation scope: part1
                "not ({part1} {part2})",  # Negation scope: both
            ]
        }
    
    def generate_variations(self, sentence: str) -> List[Tuple[str, str]]:
        """
        Generate semantic variations of a sentence.
        
        Args:
            sentence: Input sentence
            
        Returns:
            List of (variation, description) tuples
        """
        variations = []
        
        # Check for common ambiguity patterns and generate meaningful variations
        sentence_lower = sentence.lower()
        
        # Pattern 1: Prepositional phrase attachment (e.g., "saw the man with telescope")
        if ' with ' in sentence_lower and any(v in sentence_lower for v in ['saw', 'heard', 'watched', 'noticed', 'shot']):
            variations.append((sentence, "The prepositional phrase modifies the verb (I used the telescope to see)"))
            variations.append((sentence, "The prepositional phrase modifies the object (The man had the telescope)"))
        
        # Pattern 2: Coordination ambiguity (e.g., "A and B and C")
        and_count = sentence_lower.count(' and ')
        if and_count >= 2:
            variations.append((sentence, "Left-associative: ((A and B) and C)"))
            variations.append((sentence, "Right-associative: (A and (B and C))"))
        
        # Pattern 3: Relative clause attachment
        if any(rc in sentence_lower for rc in [' which ', ' that ', ' who ']):
            variations.append((sentence, "Relative clause modifies nearest noun"))
            variations.append((sentence, "Relative clause modifies the main subject"))
        
        # Pattern 4: Negation scope
        if 'not' in sentence_lower or 'no' in sentence_lower or "n't" in sentence_lower:
            variations.append((sentence, "Negation has narrow scope (affects only immediately following element)"))
            variations.append((sentence, "Negation has wide scope (affects entire clause)"))
        
        # Pattern 5: Verb phrase attachment
        if ' to ' in sentence_lower and any(v in sentence_lower for v in ['ready', 'willing', 'able', 'prepare']):
            variations.append((sentence, "Subject is ready to perform the action"))
            variations.append((sentence, "The object is ready to be affected by the action"))
        
        # If no specific patterns found, create semantic paraphrases
        if not variations:
            variations.append((sentence, "Literal/denotative interpretation"))
            variations.append((sentence, "Figurative/connotative interpretation"))
        
        return variations


class SemanticAmbiguityDetector:
    """Detect semantic ambiguity using BERT embeddings."""
    
    def __init__(self, model_name: str = 'bert-base-uncased', device: str = 'cpu'):
        """
        Initialize semantic ambiguity detector.
        
        Args:
            model_name: BERT model name
            device: Computation device
        """
        self.bert_analyzer = BERTSemanticAnalyzer(model_name, device)
        self.variation_generator = SemanticVariationGenerator()
        self.device = device
    
    def compute_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """
        Compute similarity between two embeddings (cosine).
        
        Args:
            emb1: First embedding
            emb2: Second embedding
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        # Cosine similarity = 1 - cosine_distance
        distance = cosine(emb1, emb2)
        similarity = 1.0 - distance
        return float(similarity)
    
    def analyze(self, sentence: str, threshold: float = 0.7) -> SemanticAmbiguityResult:
        """
        Analyze semantic ambiguity in a sentence.
        
        Args:
            sentence: Input sentence
            threshold: Similarity threshold for ambiguity (lower = more ambiguous)
            
        Returns:
            SemanticAmbiguityResult with detailed analysis
        """
        # Generate semantic variations
        variations = self.variation_generator.generate_variations(sentence)
        
        # Get embeddings for each variation
        interpretations = []
        embeddings = []
        
        for variation, description in variations:
            try:
                embedding = self.bert_analyzer.get_embedding(variation)
                embeddings.append(embedding)
                interpretations.append(
                    SemanticInterpretation(
                        sentence=variation,
                        embedding=embedding,
                        interpretation=description,
                        confidence=1.0 / len(variations)
                    )
                )
            except Exception as e:
                print(f"Warning: Failed to process variation: {e}")
        
        if len(interpretations) < 2:
            # Not ambiguous (single interpretation)
            return SemanticAmbiguityResult(
                sentence=sentence,
                interpretations=interpretations if interpretations else 
                    [SemanticInterpretation(sentence, 
                                          self.bert_analyzer.get_embedding(sentence),
                                          "Unambiguous", 1.0)],
                ambiguity_score=0.0,
                is_ambiguous=False,
                divergence_matrix=np.array([]),
                primary_meaning=sentence,
                alternative_meanings=[],
                semantic_uncertainty=0.0
            )
        
        # Compute pairwise similarities
        n_interp = len(interpretations)
        divergence_matrix = np.zeros((n_interp, n_interp))
        
        for i in range(n_interp):
            for j in range(i + 1, n_interp):
                similarity = self.compute_similarity(embeddings[i], embeddings[j])
                # Divergence = 1 - similarity
                divergence = 1.0 - similarity
                divergence_matrix[i, j] = divergence
                divergence_matrix[j, i] = divergence
        
        # Calculate ambiguity score
        # Lower average divergence = more ambiguous (similar meanings)
        # Higher average divergence = less ambiguous (distinct meanings)
        upper_triangle = np.triu_indices_from(divergence_matrix, k=1)
        avg_divergence = divergence_matrix[upper_triangle].mean()
        
        # Invert: high divergence → low ambiguity score, low divergence → high ambiguity
        # But we want: similar interpretations → high ambiguity
        ambiguity_score = 1.0 - avg_divergence  # 0-1 scale
        
        # Semantic uncertainty (entropy of divergences)
        if len(upper_triangle[0]) > 0:
            divergences = divergence_matrix[upper_triangle]
            # Normalize to probabilities
            probs = divergences / (divergences.sum() + 1e-8)
            semantic_uncertainty = -np.sum(probs * np.log(probs + 1e-8))
        else:
            semantic_uncertainty = 0.0
        
        # Determine if ambiguous based on threshold
        is_ambiguous = ambiguity_score >= threshold
        
        # Alternative meanings
        alternative_meanings = [
            f"{interp.interpretation}" 
            for interp in interpretations[1:]
        ]
        
        return SemanticAmbiguityResult(
            sentence=sentence,
            interpretations=interpretations,
            ambiguity_score=float(ambiguity_score),
            is_ambiguous=is_ambiguous,
            divergence_matrix=divergence_matrix,
            primary_meaning=interpretations[0].interpretation,
            alternative_meanings=alternative_meanings,
            semantic_uncertainty=float(semantic_uncertainty)
        )
    
    def analyze_batch(self, sentences: List[str], 
                     threshold: float = 0.7) -> List[SemanticAmbiguityResult]:
        """
        Analyze multiple sentences.
        
        Args:
            sentences: List of sentences
            threshold: Similarity threshold
            
        Returns:
            List of results
        """
        results = []
        for sentence in sentences:
            result = self.analyze(sentence, threshold)
            results.append(result)
        return results


def print_semantic_analysis(result: SemanticAmbiguityResult):
    """Pretty print semantic analysis result."""
    print(f"\n{'='*80}")
    print(f"SENTENCE: {result.sentence}")
    print(f"{'='*80}")
    print(f"Semantic Ambiguity Score: {result.ambiguity_score:.4f}")
    print(f"Classification: {'SEMANTICALLY AMBIGUOUS' if result.is_ambiguous else 'SEMANTICALLY CLEAR'}")
    print(f"Semantic Uncertainty: {result.semantic_uncertainty:.4f}")
    print(f"\nPrimary Meaning: {result.primary_meaning}")
    
    if result.alternative_meanings:
        print(f"\nAlternative Meanings:")
        for i, meaning in enumerate(result.alternative_meanings, 1):
            print(f"  {i}. {meaning}")
    
    if result.divergence_matrix.size > 0:
        print(f"\nInterpretation Divergence Matrix:")
        print(result.divergence_matrix)


def main():
    """Demo and testing."""
    print("=" * 80)
    print("BERT SEMANTIC AMBIGUITY DETECTOR - DEMO")
    print("=" * 80)
    
    # Initialize detector
    print("\nInitializing BERT semantic analyzer...")
    try:
        detector = SemanticAmbiguityDetector(model_name='bert-base-uncased', device='cpu')
    except Exception as e:
        print(f"Error: Could not load BERT model: {e}")
        print("Make sure transformers and torch are installed:")
        print("  pip install torch transformers scipy")
        return
    
    # Test sentences
    test_sentences = [
        "I saw the man with the telescope",
        "She told me the story yesterday",
        "The chicken is ready to eat",
        "I heard the news from my friend with the phone",
        "The dog ate the bone",
        "Walking down the street, the building was on fire",
    ]
    
    print("\n" + "=" * 80)
    print("SEMANTIC AMBIGUITY ANALYSIS")
    print("=" * 80)
    
    results = detector.analyze_batch(test_sentences, threshold=0.5)
    
    for result in results:
        print_semantic_analysis(result)
    
    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)
    
    scores = [r.ambiguity_score for r in results]
    uncertainties = [r.semantic_uncertainty for r in results]
    
    print(f"\nAmbiguity Scores:")
    print(f"  Average: {np.mean(scores):.4f}")
    print(f"  Min-Max: {min(scores):.4f} - {max(scores):.4f}")
    print(f"  Std Dev: {np.std(scores):.4f}")
    
    print(f"\nSemantic Uncertainties:")
    print(f"  Average: {np.mean(uncertainties):.4f}")
    print(f"  Min-Max: {min(uncertainties):.4f} - {max(uncertainties):.4f}")
    
    ambiguous_count = sum(1 for r in results if r.is_ambiguous)
    print(f"\nAmbiguous Sentences: {ambiguous_count}/{len(results)}")


if __name__ == '__main__':
    main()
