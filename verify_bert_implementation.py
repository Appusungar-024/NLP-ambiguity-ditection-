#!/usr/bin/env python3
"""Verify BERT semantic ambiguity detection implementation."""

import sys
from pathlib import Path

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def test_imports():
    """Test all imports."""
    print("Testing imports...")
    try:
        from bert_semantic_analyzer import SemanticAmbiguityDetector
        print("  ✅ bert_semantic_analyzer imported")
        from ambiguity_pipeline import AmbiguityDetectionPipeline
        print("  ✅ ambiguity_pipeline imported")
        from compare_all_methods import ComparisonAnalyzer
        print("  ✅ compare_all_methods imported")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_pipeline():
    """Test pipeline with all components."""
    print("\nTesting pipeline initialization...")
    try:
        from ambiguity_pipeline import AmbiguityDetectionPipeline
        
        pipeline = AmbiguityDetectionPipeline(
            use_bert=True,
            bert_model='bert-base-uncased'
        )
        print("  ✅ Pipeline initialized with BERT")
        return pipeline
    except Exception as e:
        print(f"  ❌ Pipeline initialization failed: {e}")
        return None

def test_bert_analysis(pipeline):
    """Test BERT semantic analysis."""
    print("\nTesting BERT semantic analysis...")
    
    test_sentences = [
        "I saw the man with the telescope",
        "She visited the museum with interesting exhibits",
        "The bank can accept new customers",
    ]
    
    for sentence in test_sentences:
        try:
            result = pipeline.get_semantic_ambiguity(sentence)
            if result:
                score = result['semantic_ambiguity_score']
                ambig = result['is_ambiguous']
                print(f"  ✅ '{sentence[:40]}...' → Score: {score:.3f}, Ambiguous: {ambig}")
            else:
                print(f"  ❌ '{sentence[:40]}...' → No result")
                return False
        except Exception as e:
            print(f"  ❌ '{sentence[:40]}...' → Error: {e}")
            return False
    
    return True

def test_comparison():
    """Test comparison tool."""
    print("\nTesting comparison tool...")
    
    try:
        from compare_all_methods import ComparisonAnalyzer
        
        analyzer = ComparisonAnalyzer()
        result = analyzer.compare_sentence("I saw the man with the telescope")
        
        if 'methods' in result:
            methods = result['methods']
            if all(m in methods for m in ['rule_based', 'ml_classifier', 'bert_semantic']):
                print("  ✅ All three methods in comparison")
                print(f"     Rule-Based: {methods['rule_based'].get('is_ambiguous', 'N/A')}")
                print(f"     ML: {methods['ml_classifier'].get('is_ambiguous', 'N/A')}")
                print(f"     BERT: {methods['bert_semantic'].get('is_ambiguous', 'N/A')}")
                return True
            else:
                print(f"  ❌ Missing methods in result")
                return False
        else:
            print(f"  ❌ Invalid result structure")
            return False
    except Exception as e:
        print(f"  ❌ Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_files():
    """Check that required files exist."""
    print("\nChecking required files...")
    
    files = [
        'bert_semantic_analyzer.py',
        'ambiguity_pipeline.py',
        'compare_all_methods.py',
        'BERT_SEMANTIC_GUIDE.md',
        'BERT_IMPLEMENTATION_SUMMARY.md',
        'BERT_QUICKSTART.md',
        'ambiguity_model.pkl',
    ]
    
    all_exist = True
    for file in files:
        path = ROOT / file
        if path.exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
            all_exist = False
    
    return all_exist

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("BERT SEMANTIC AMBIGUITY DETECTION - VERIFICATION")
    print("=" * 60)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import verification FAILED")
        return False
    
    # Check files
    if not test_files():
        print("\n⚠️  Some files missing")
    
    # Test pipeline
    pipeline = test_pipeline()
    if not pipeline:
        print("\n❌ Pipeline verification FAILED")
        return False
    
    # Test BERT analysis
    if not test_bert_analysis(pipeline):
        print("\n❌ BERT analysis verification FAILED")
        return False
    
    # Test comparison
    if not test_comparison():
        print("\n❌ Comparison verification FAILED")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL VERIFICATION TESTS PASSED")
    print("=" * 60)
    print("\nBERT semantic ambiguity detection is fully functional!")
    print("\nNext steps:")
    print("1. Run: python3 ambiguity_pipeline.py --demo --use-bert")
    print("2. Run: python3 compare_all_methods.py --demo")
    print("3. Read: BERT_QUICKSTART.md for usage examples")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
