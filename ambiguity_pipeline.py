"""
Complete Ambiguity Detection Pipeline

Integrates all components:
1. Text Preprocessing (cleaning, tokenization, stopword removal, POS tagging)
2. Parsing (CFG and dependency parsing)
3. Ambiguity Detection
4. Output with explanations
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Any
import argparse
import json
import numpy as np

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from text_preprocessing import TextPreprocessor
from dependency_parser import DependencyParser, AmbiguityAnalyzer
from ambiguity_output import AmbiguityClassifier, OutputFormatter, AmbiguityResult
from parsing_ambiguity import parser as cfg_parser, detect_ambiguity
from ambiguity_classifier import AmbiguityMLClassifier

# Try to import BERT analyzer (optional)
try:
    from bert_semantic_analyzer import SemanticAmbiguityDetector
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False


class AmbiguityDetectionPipeline:
    """Complete pipeline for ambiguity detection."""
    
    def __init__(self, 
                 remove_stopwords: bool = False,
                 use_dependency_parser: bool = True,
                 use_cfg_parser: bool = True,
                 use_ml_classifier: bool = False,
                 ml_model_path: Optional[str] = None,
                 use_bert: bool = False,
                 bert_model: str = 'bert-base-uncased'):
        """
        Initialize the pipeline.
        
        Args:
            remove_stopwords: Whether to remove stopwords
            use_dependency_parser: Whether to use dependency parser
            use_cfg_parser: Whether to use CFG parser
            use_ml_classifier: Whether to use ML classifier for predictions
            ml_model_path: Path to saved ML model
            use_bert: Whether to use BERT for semantic ambiguity detection
            bert_model: BERT model name
        """
        self.remove_stopwords = remove_stopwords
        self.use_dependency_parser = use_dependency_parser
        self.use_cfg_parser = use_cfg_parser
        self.use_ml_classifier = use_ml_classifier
        self.use_bert = use_bert
        
        # Initialize components
        self.preprocessor = TextPreprocessor(remove_stopwords=remove_stopwords)
        self.classifier = AmbiguityClassifier()
        self.formatter = OutputFormatter()
        
        self.dep_parser = None
        self.ambiguity_analyzer = None
        self.ml_classifier = None
        self.bert_detector = None
        
        if self.use_dependency_parser:
            try:
                self.dep_parser = DependencyParser()
                self.ambiguity_analyzer = AmbiguityAnalyzer()
            except Exception as e:
                print(f"Warning: Dependency parser not available: {e}")
                self.use_dependency_parser = False
        
        # Initialize ML classifier if requested
        if self.use_ml_classifier:
            try:
                self.ml_classifier = AmbiguityMLClassifier()
                if ml_model_path and Path(ml_model_path).exists():
                    self.ml_classifier.load(ml_model_path)
                else:
                    print("Warning: ML model path not provided or does not exist")
                    self.use_ml_classifier = False
            except Exception as e:
                print(f"Warning: ML classifier not available: {e}")
                self.use_ml_classifier = False
        
        # Initialize BERT if requested
        if self.use_bert and BERT_AVAILABLE:
            try:
                print("Initializing BERT semantic analyzer...")
                self.bert_detector = SemanticAmbiguityDetector(
                    model_name=bert_model,
                    device='cpu'
                )
            except Exception as e:
                print(f"Warning: BERT semantic analyzer not available: {e}")
                self.use_bert = False
    
    def preprocess(self, text: str) -> Tuple[List[str], Optional[List[Tuple[str, str]]]]:
        """
        Step 1: Text Preprocessing
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (tokens, pos_tags)
        """
        tokens, pos_tags = self.preprocessor.preprocess(
            text,
            apply_pos_tagging=True,
            return_tagged=True
        )
        return tokens, pos_tags
    
    def parse_cfg(self, tokens: List[str]) -> List[Any]:
        """
        Step 2a: Context-Free Grammar Parsing
        
        Args:
            tokens: List of tokens
            
        Returns:
            List of parse trees
        """
        if not self.use_cfg_parser:
            return []
        
        try:
            trees = list(cfg_parser.parse(tokens))
            return trees
        except Exception:
            return []
    
    def parse_dependency(self, text: str) -> Optional[Dict]:
        """
        Step 2b: Dependency Parsing
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with dependency information
        """
        if not self.use_dependency_parser or not self.ambiguity_analyzer:
            return None
        
        try:
            result = self.ambiguity_analyzer.analyze_dependency_ambiguity(text)
            return result
        except Exception as e:
            print(f"Warning: Dependency parsing failed: {e}")
            return None
    
    def detect_ambiguity(self, 
                         sentence: str,
                         tokens: List[str],
                         parse_trees: List[Any],
                         dependency_info: Optional[Dict] = None,
                         pos_tags: Optional[List[Tuple[str, str]]] = None) -> AmbiguityResult:
        """
        Step 3: Ambiguity Detection & Classification
        
        Args:
            sentence: Original sentence
            tokens: Tokenized sentence
            parse_trees: CFG parse trees
            dependency_info: Dependency parsing results
            pos_tags: POS tags
            
        Returns:
            AmbiguityResult object
        """
        result = self.classifier.classify(
            sentence=sentence,
            parse_trees=parse_trees,
            dependency_info=dependency_info,
            pos_tags=pos_tags
        )
        return result
    
    def get_ml_prediction(self, text: str) -> Tuple[int, float]:
        """
        Get ML classifier prediction for ambiguity.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (is_ambiguous: int, probability: float)
        """
        if not self.use_ml_classifier or not self.ml_classifier:
            return None, None
        
        try:
            is_ambiguous, probability = self.ml_classifier.predict(text)
            return is_ambiguous, probability
        except Exception as e:
            print(f"Warning: ML prediction failed: {e}")
            return None, None
    
    def get_semantic_ambiguity(self, text: str) -> Optional[Dict]:
        """
        Get BERT-based semantic ambiguity analysis.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with semantic ambiguity results or None
        """
        if not self.use_bert or not self.bert_detector:
            return None
        
        try:
            result = self.bert_detector.analyze(text)
            return {
                'semantic_ambiguity_score': result.ambiguity_score,
                'is_ambiguous': result.is_ambiguous,
                'num_interpretations': len(result.interpretations),
                'semantic_uncertainty': result.semantic_uncertainty,
                'primary_meaning': result.primary_meaning,
                'alternative_meanings': result.alternative_meanings,
                'avg_divergence': float(np.mean(result.divergence_matrix) if result.divergence_matrix.size > 0 else 0.0)
            }
        except Exception as e:
            print(f"Warning: BERT semantic analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def process(self, text: str, 
                output_format: str = 'text',
                detailed: bool = True) -> Tuple[AmbiguityResult, str]:
        """
        Run the complete pipeline.
        
        Args:
            text: Input text
            output_format: Format for output ('text', 'json')
            detailed: Whether to include detailed analysis
            
        Returns:
            Tuple of (AmbiguityResult, formatted_output)
        """
        # Step 1: Preprocessing
        tokens, pos_tags = self.preprocess(text)
        
        # Step 2a: CFG Parsing
        parse_trees = self.parse_cfg(tokens)
        
        # Step 2b: Dependency Parsing
        dependency_info = self.parse_dependency(text)
        
        # Step 3: Ambiguity Detection
        result = self.detect_ambiguity(
            sentence=text,
            tokens=tokens,
            parse_trees=parse_trees,
            dependency_info=dependency_info,
            pos_tags=pos_tags
        )
        
        # Step 4: Output Formatting
        if output_format == 'json':
            formatted_output = self.formatter.format_json(result)
        else:
            formatted_output = self.formatter.format_text(result)
        
        return result, formatted_output
    
    def process_batch(self, texts: List[str], 
                      output_format: str = 'text') -> List[Tuple[AmbiguityResult, str]]:
        """
        Process multiple texts.
        
        Args:
            texts: List of input texts
            output_format: Format for output
            
        Returns:
            List of (result, formatted_output) tuples
        """
        results = []
        for text in texts:
            result, formatted_output = self.process(text, output_format=output_format)
            results.append((result, formatted_output))
        return results


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description='Complete Ambiguity Detection Pipeline'
    )
    parser.add_argument('--text', '-t', help='Input text to analyze')
    parser.add_argument('--file', '-f', help='File containing texts (one per line)')
    parser.add_argument('--remove-stopwords', '-s', action='store_true',
                       help='Remove stopwords')
    parser.add_argument('--no-dependency', action='store_true',
                       help='Disable dependency parser')
    parser.add_argument('--no-cfg', action='store_true',
                       help='Disable CFG parser')
    parser.add_argument('--use-ml', action='store_true',
                       help='Use trained ML classifier for predictions')
    parser.add_argument('--ml-model', default='ambiguity_model.pkl',
                       help='Path to trained ML model')
    parser.add_argument('--use-bert', action='store_true',
                       help='Use BERT for semantic ambiguity detection')
    parser.add_argument('--bert-model', default='bert-base-uncased',
                       help='BERT model name')
    parser.add_argument('--format', choices=['text', 'json'], default='text',
                       help='Output format')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo with example sentences')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    model_path = str(ROOT / args.ml_model) if args.use_ml else None
    pipeline = AmbiguityDetectionPipeline(
        remove_stopwords=args.remove_stopwords,
        use_dependency_parser=not args.no_dependency,
        use_cfg_parser=not args.no_cfg,
        use_ml_classifier=args.use_ml,
        ml_model_path=model_path,
        use_bert=args.use_bert,
        bert_model=args.bert_model
    )
    
    # Collect output
    outputs = []
    
    if args.demo:
        # Run on demo sentences
        demo_texts = [
            "I saw the man with the telescope",
            "I saw the man in the park with the telescope",
            "She visited the museum with interesting exhibits",
            "The bank can accept new customers",
            "I heard the news from my friend with the phone",
        ]
        
        print("=" * 80)
        print("AMBIGUITY DETECTION PIPELINE - DEMO")
        print("=" * 80)
        print()
        
        results, formatted_outputs = zip(*pipeline.process_batch(
            demo_texts, 
            output_format=args.format
        ))
        
        # Add BERT analysis if enabled
        if args.use_bert:
            print("\n" + "=" * 80)
            print("BERT SEMANTIC AMBIGUITY ANALYSIS")
            print("=" * 80)
            print()
            for text in demo_texts:
                semantic_result = pipeline.get_semantic_ambiguity(text)
                if semantic_result:
                    print(f"Text: {text}")
                    print(f"  Semantic Ambiguity Score: {semantic_result['semantic_ambiguity_score']:.3f}")
                    print(f"  Number of Interpretations: {semantic_result['num_interpretations']}")
                    print(f"  Semantic Uncertainty: {semantic_result['semantic_uncertainty']:.3f}")
                    print(f"  Average Divergence: {semantic_result['avg_divergence']:.3f}")
                    print(f"  Primary Meaning: {semantic_result['primary_meaning']}")
                    if semantic_result['alternative_meanings']:
                        print(f"  Alternative Meanings: {', '.join(semantic_result['alternative_meanings'])}")
                    print()
        
        for output in formatted_outputs:
            outputs.append(output)
            print(output)
            print("\n")
    
    elif args.text:
        # Process single text
        result, formatted_output = pipeline.process(
            args.text,
            output_format=args.format
        )
        outputs.append(formatted_output)
        print(formatted_output)
        
        # Add BERT analysis if enabled
        if args.use_bert:
            semantic_result = pipeline.get_semantic_ambiguity(args.text)
            if semantic_result:
                print("\n" + "=" * 80)
                print("BERT SEMANTIC AMBIGUITY ANALYSIS")
                print("=" * 80)
                print(f"Semantic Ambiguity Score: {semantic_result['semantic_ambiguity_score']:.3f}")
                print(f"Is Ambiguous (threshold 0.7): {semantic_result['is_ambiguous']}")
                print(f"Number of Interpretations: {semantic_result['num_interpretations']}")
                print(f"Semantic Uncertainty: {semantic_result['semantic_uncertainty']:.3f}")
                print(f"Average Divergence: {semantic_result['avg_divergence']:.3f}")
                print(f"Primary Meaning: {semantic_result['primary_meaning']}")
                if semantic_result['alternative_meanings']:
                    print(f"Alternative Meanings: {', '.join(semantic_result['alternative_meanings'])}")
    
    elif args.file:
        # Process file
        try:
            with open(args.file, 'r') as f:
                texts = [line.strip() for line in f if line.strip()]
            
            print(f"Processing {len(texts)} texts from {args.file}...")
            print()
            
            results, formatted_outputs = zip(*pipeline.process_batch(
                texts,
                output_format=args.format
            ))
            
            for output in formatted_outputs:
                outputs.append(output)
                print(output)
                print("\n")
        
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            return
    
    else:
        # Run demo by default if no input provided
        print("=" * 80)
        print("AMBIGUITY DETECTION PIPELINE - DEMO")
        print("=" * 80)
        print()
        
        demo_texts = [
            "I saw the man with the telescope",
            "She visited the museum with interesting exhibits",
            "The bank can accept new customers",
        ]
        
        results, formatted_outputs = zip(*pipeline.process_batch(
            demo_texts,
            output_format=args.format
        ))
        
        for output in formatted_outputs:
            outputs.append(output)
            print(output)
            print("\n")
    
    # Write to file if specified
    if args.output and outputs:
        with open(args.output, 'w') as f:
            f.write('\n'.join(outputs))
        print(f"\nOutput written to {args.output}")


if __name__ == '__main__':
    main()
