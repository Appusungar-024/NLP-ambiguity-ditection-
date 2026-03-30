"""
Compare BERT semantic ambiguity detection with ML classifier and rule-based methods.
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
import json

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ambiguity_pipeline import AmbiguityDetectionPipeline


class ComparisonAnalyzer:
    """Analyze and compare different ambiguity detection methods."""
    
    def __init__(self):
        """Initialize all detection methods."""
        self.pipeline_rules = AmbiguityDetectionPipeline(
            use_ml_classifier=False,
            use_bert=False
        )
        
        self.pipeline_ml = AmbiguityDetectionPipeline(
            use_ml_classifier=True,
            ml_model_path=str(ROOT / 'ambiguity_model.pkl'),
            use_bert=False
        )
        
        self.pipeline_bert = AmbiguityDetectionPipeline(
            use_ml_classifier=False,
            use_bert=True,
            bert_model='bert-base-uncased'
        )
        
        self.pipeline_all = AmbiguityDetectionPipeline(
            use_ml_classifier=True,
            ml_model_path=str(ROOT / 'ambiguity_model.pkl'),
            use_bert=True,
            bert_model='bert-base-uncased'
        )
    
    def compare_sentence(self, text: str) -> Dict:
        """
        Compare all methods on a single sentence.
        
        Args:
            text: Input sentence
            
        Returns:
            Dictionary with results from all methods
        """
        results = {
            'text': text,
            'methods': {}
        }
        
        # Rule-based detection
        try:
            rule_result, _ = self.pipeline_rules.process(text)
            results['methods']['rule_based'] = {
                'ambiguity_score': rule_result.ambiguity_score,
                'is_ambiguous': rule_result.is_ambiguous,
                'confidence': rule_result.confidence,
                'ambiguity_types': rule_result.ambiguity_types,
                'parse_count': rule_result.parse_count
            }
        except Exception as e:
            results['methods']['rule_based'] = {'error': str(e)}
        
        # ML classifier
        try:
            ml_pred, ml_prob = self.pipeline_ml.get_ml_prediction(text)
            results['methods']['ml_classifier'] = {
                'is_ambiguous': bool(ml_pred),
                'probability': float(ml_prob) if ml_prob else None
            }
        except Exception as e:
            results['methods']['ml_classifier'] = {'error': str(e)}
        
        # BERT semantic analysis
        try:
            bert_result = self.pipeline_bert.get_semantic_ambiguity(text)
            if bert_result:
                results['methods']['bert_semantic'] = {
                    'ambiguity_score': bert_result['semantic_ambiguity_score'],
                    'is_ambiguous': bert_result['is_ambiguous'],
                    'num_interpretations': bert_result['num_interpretations'],
                    'semantic_uncertainty': bert_result['semantic_uncertainty'],
                    'primary_meaning': bert_result['primary_meaning'],
                    'alternative_meanings': bert_result['alternative_meanings']
                }
        except Exception as e:
            results['methods']['bert_semantic'] = {'error': str(e)}
        
        return results
    
    def compare_batch(self, texts: List[str], 
                     output_format: str = 'text') -> List[Dict]:
        """
        Compare all methods on multiple sentences.
        
        Args:
            texts: List of sentences
            output_format: 'text' or 'json'
            
        Returns:
            List of comparison results
        """
        results = []
        for i, text in enumerate(texts, 1):
            print(f"Processing {i}/{len(texts)}: {text[:50]}...")
            result = self.compare_sentence(text)
            results.append(result)
        
        return results
    
    def print_comparison(self, comparison: Dict, verbose: bool = True):
        """Print comparison results in readable format."""
        print("\n" + "=" * 100)
        print(f"SENTENCE: {comparison['text']}")
        print("=" * 100)
        
        methods = comparison['methods']
        
        # Rule-based
        if 'error' not in methods.get('rule_based', {}):
            rb = methods['rule_based']
            print(f"\n📋 RULE-BASED:")
            print(f"   Ambiguity Score: {rb['ambiguity_score']:.3f}")
            print(f"   Is Ambiguous: {rb['is_ambiguous']}")
            print(f"   Confidence: {rb['confidence']:.1f}%")
            print(f"   Types: {', '.join(rb['ambiguity_types'])}")
            print(f"   Parse Count: {rb['parse_count']}")
        else:
            print(f"\n📋 RULE-BASED: Error - {methods['rule_based']['error']}")
        
        # ML Classifier
        if 'error' not in methods.get('ml_classifier', {}):
            ml = methods['ml_classifier']
            prob_str = f"{ml['probability']:.3f}" if ml['probability'] is not None else 'N/A'
            print(f"\n🤖 ML CLASSIFIER:")
            print(f"   Is Ambiguous: {ml['is_ambiguous']}")
            print(f"   Probability: {prob_str}")
        else:
            print(f"\n🤖 ML CLASSIFIER: Error - {methods['ml_classifier']['error']}")
        
        # BERT Semantic
        if 'error' not in methods.get('bert_semantic', {}):
            bert = methods['bert_semantic']
            print(f"\n🧠 BERT SEMANTIC:")
            print(f"   Ambiguity Score: {bert['ambiguity_score']:.3f}")
            print(f"   Is Ambiguous: {bert['is_ambiguous']}")
            print(f"   Interpretations: {bert['num_interpretations']}")
            print(f"   Semantic Uncertainty: {bert['semantic_uncertainty']:.3f}")
            print(f"   Primary: {bert['primary_meaning']}")
            if bert['alternative_meanings']:
                for i, alt in enumerate(bert['alternative_meanings'], 1):
                    print(f"   Alternative {i}: {alt}")
        else:
            print(f"\n🧠 BERT SEMANTIC: Error - {methods['bert_semantic']['error']}")
        
        # Consensus
        print(f"\n✅ CONSENSUS:")
        try:
            rb_ambiguous = methods['rule_based']['is_ambiguous']
            ml_ambiguous = methods['ml_classifier']['is_ambiguous']
            bert_ambiguous = methods['bert_semantic']['is_ambiguous']
            
            agreement = sum([rb_ambiguous, ml_ambiguous, bert_ambiguous])
            print(f"   Agreement: {agreement}/3 methods agree")
            
            if agreement == 3:
                consensus = "HIGHLY CONFIDENT"
                if rb_ambiguous:
                    print(f"   Status: ✅ AMBIGUOUS (all methods agree)")
                else:
                    print(f"   Status: ✅ UNAMBIGUOUS (all methods agree)")
            elif agreement >= 2:
                majority = "AMBIGUOUS" if agreement == 2 and ml_ambiguous else "UNAMBIGUOUS"
                print(f"   Status: ⚠️  CONSENSUS: {majority} (2/3 methods)")
            else:
                print(f"   Status: ❌ NO CONSENSUS (methods disagree)")
        except:
            print(f"   Status: Unable to compute consensus")


def main():
    """Run comparison analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Compare ambiguity detection methods'
    )
    parser.add_argument('--text', '-t', help='Single sentence to analyze')
    parser.add_argument('--file', '-f', help='File with sentences (one per line)')
    parser.add_argument('--demo', action='store_true',
                       help='Run demo comparison')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--output', '-o', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    analyzer = ComparisonAnalyzer()
    
    # Collect texts
    texts = []
    
    if args.demo:
        texts = [
            "I saw the man with the telescope",
            "I saw the man in the park with the telescope",
            "She visited the museum with interesting exhibits",
            "The bank can accept new customers",
            "I heard the news from my friend with the phone",
            "She told me about the book yesterday",
            "The cotton clothing was made in the factory",
            "He gave the dog to the boy",
            "Visiting relatives can be boring",
            "I like the movie that won the award"
        ]
    elif args.text:
        texts = [args.text]
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                texts = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            return
    else:
        parser.print_help()
        return
    
    print(f"\n{'='*100}")
    print(f"AMBIGUITY DETECTION COMPARISON")
    print(f"{'='*100}\n")
    print(f"Comparing 3 methods: Rule-Based, ML Classifier, BERT Semantic")
    print(f"Analyzing {len(texts)} sentence(s)...\n")
    
    all_results = []
    for text in texts:
        result = analyzer.compare_sentence(text)
        all_results.append(result)
        analyzer.print_comparison(result, verbose=args.verbose)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"\n✅ Results saved to {args.output}")
    
    # Summary statistics
    if len(texts) > 1:
        print(f"\n{'='*100}")
        print("SUMMARY")
        print(f"{'='*100}")
        
        # Count method agreements
        agreements = []
        for result in all_results:
            methods = result['methods']
            if all(k in methods and 'error' not in methods[k] for k in ['rule_based', 'ml_classifier', 'bert_semantic']):
                rb = methods['rule_based']['is_ambiguous']
                ml = methods['ml_classifier']['is_ambiguous']
                bert = methods['bert_semantic']['is_ambiguous']
                agreement = sum([rb, ml, bert])
                agreements.append(agreement)
        
        if agreements:
            avg_agreement = sum(agreements) / len(agreements)
            print(f"Average agreement: {avg_agreement:.1f}/3 methods")
            print(f"Perfect agreement (3/3): {sum(1 for a in agreements if a == 3)}/{len(agreements)}")
            print(f"Majority agreement (2/3): {sum(1 for a in agreements if a == 2)}/{len(agreements)}")
            print(f"No agreement (1/3): {sum(1 for a in agreements if a == 1)}/{len(agreements)}")


if __name__ == '__main__':
    main()
