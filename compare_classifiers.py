"""
ML Classifier vs Rule-Based Comparison Demo

Compares predictions from ML classifier with linguistic rule-based system.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ambiguity_classifier import AmbiguityMLClassifier
from ambiguity_pipeline import AmbiguityDetectionPipeline


def print_comparison(sentence: str, ml_classifier, pipeline):
    """Compare ML and rule-based predictions."""
    print(f"\nSentence: {sentence}")
    print("-" * 80)
    
    # ML Classifier Prediction
    try:
        is_ambiguous_ml, prob_ml = ml_classifier.predict(sentence)
        class_ml = "AMBIGUOUS" if is_ambiguous_ml else "CLEAR"
        print(f"ML Classifier:")
        print(f"  Classification: {class_ml}")
        print(f"  Ambiguity Probability: {prob_ml:.4f}")
    except Exception as e:
        print(f"ML Classifier: Error - {e}")
        prob_ml = None
    
    # Rule-Based System
    try:
        result, _ = pipeline.process(sentence, output_format='text')
        print(f"\nRule-Based System:")
        print(f"  Classification: {'AMBIGUOUS' if result.is_ambiguous else 'CLEAR'}")
        print(f"  Ambiguity Level: {result.ambiguity_level}")
        print(f"  Ambiguity Score: {result.ambiguity_score:.4f}")
        print(f"  Confidence: {result.confidence:.2%}")
        
        if result.ambiguity_types:
            print(f"  Types: {', '.join(result.ambiguity_types)}")
    except Exception as e:
        print(f"Rule-Based System: Error - {e}")
    
    # Comparison
    if prob_ml is not None:
        print(f"\nComparison:")
        print(f"  ML Score vs Rule Score: {prob_ml:.4f} vs {result.ambiguity_score:.4f}")
        agreement = "✓ AGREE" if (is_ambiguous_ml == result.is_ambiguous) else "✗ DISAGREE"
        print(f"  Binary Classification: {agreement}")


def main():
    """Run comparison demo."""
    print("=" * 80)
    print("ML CLASSIFIER vs RULE-BASED SYSTEM - COMPARISON DEMO")
    print("=" * 80)
    
    # Initialize models
    print("\nInitializing models...")
    
    ml_classifier = AmbiguityMLClassifier()
    model_path = str(ROOT / "ambiguity_model.pkl")
    
    try:
        ml_classifier.load(model_path)
        print(f"✓ ML Classifier loaded from {model_path}")
    except Exception as e:
        print(f"✗ Failed to load ML classifier: {e}")
        return
    
    pipeline = AmbiguityDetectionPipeline(use_ml_classifier=False)
    print("✓ Rule-Based Pipeline initialized")
    
    # Test sentences
    test_sentences = [
        # Clear sentences
        "The dog ate the bone.",
        "She walks to school every day.",
        "The sun rises in the east.",
        
        # Low ambiguity
        "The bank can accept new customers.",
        "The program ran successfully.",
        "We can meet tomorrow.",
        
        # Medium ambiguity
        "I saw the man with the binoculars.",
        "She told me the story yesterday.",
        "They visited the museum with guides.",
        
        # High ambiguity
        "I saw the man with the telescope",
        "I saw the man in the park with the telescope",
        "She told the boy the girl left.",
    ]
    
    print("\n" + "=" * 80)
    print("RUNNING PREDICTIONS")
    print("=" * 80)
    
    for sentence in test_sentences:
        print_comparison(sentence, ml_classifier, pipeline)
    
    # Statistics
    print("\n" + "=" * 80)
    print("STATISTICS")
    print("=" * 80)
    
    ml_predictions = []
    rule_predictions = []
    agreements = 0
    
    for sentence in test_sentences:
        try:
            is_ambiguous_ml, prob_ml = ml_classifier.predict(sentence)
            result, _ = pipeline.process(sentence)
            
            ml_predictions.append(prob_ml)
            rule_predictions.append(result.ambiguity_score)
            
            if (is_ambiguous_ml == result.is_ambiguous):
                agreements += 1
        except:
            pass
    
    if ml_predictions and rule_predictions:
        import numpy as np
        
        ml_avg = np.mean(ml_predictions)
        rule_avg = np.mean(rule_predictions)
        ml_std = np.std(ml_predictions)
        rule_std = np.std(rule_predictions)
        agreement_rate = agreements / len(test_sentences)
        
        print(f"\nML Classifier:")
        print(f"  Average Score: {ml_avg:.4f} (+/- {ml_std:.4f})")
        print(f"  Min-Max: {min(ml_predictions):.4f} - {max(ml_predictions):.4f}")
        
        print(f"\nRule-Based System:")
        print(f"  Average Score: {rule_avg:.4f} (+/- {rule_std:.4f})")
        print(f"  Min-Max: {min(rule_predictions):.4f} - {max(rule_predictions):.4f}")
        
        print(f"\nAgreement Rate: {agreement_rate:.2%} ({agreements}/{len(test_sentences)})")
        
        # Correlation
        from scipy import stats
        try:
            corr, pval = stats.pearsonr(ml_predictions, rule_predictions)
            print(f"Correlation: {corr:.4f} (p-value: {pval:.4e})")
        except:
            pass


if __name__ == '__main__':
    main()
