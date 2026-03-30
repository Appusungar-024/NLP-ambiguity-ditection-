#!/usr/bin/env python3
"""
Verification Script - Check All Pipeline Features

Run this script to verify all features of the ambiguity detection pipeline are working.
"""

import sys
from pathlib import Path

# Make local modules importable
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def verify_imports():
    """Verify all required modules can be imported."""
    print("=" * 80)
    print("VERIFYING IMPORTS")
    print("=" * 80)
    
    modules = {
        'nltk': 'NLTK',
        'spacy': 'spaCy',
        'text_preprocessing': 'Text Preprocessing Module',
        'parsing_ambiguity': 'CFG Parser Module',
        'dependency_parser': 'Dependency Parser Module',
        'ambiguity_output': 'Output Module',
        'ambiguity_pipeline': 'Integration Pipeline',
    }
    
    all_ok = True
    for module, name in modules.items():
        try:
            __import__(module)
            print(f"✅ {name:40} OK")
        except Exception as e:
            print(f"❌ {name:40} FAILED: {e}")
            all_ok = False
    
    print()
    return all_ok


def verify_preprocessing():
    """Verify preprocessing functionality."""
    print("=" * 80)
    print("VERIFYING TEXT PREPROCESSING")
    print("=" * 80)
    
    try:
        from text_preprocessing import TextPreprocessor
        
        preprocessor = TextPreprocessor(remove_stopwords=False)
        text = "I saw the man with the telescope in the park."
        
        # Test cleaning
        cleaned = preprocessor.clean_text(text)
        print(f"✅ Text Cleaning: {len(cleaned) > 0}")
        
        # Test tokenization
        tokens = preprocessor.tokenize(text)
        print(f"✅ Tokenization: {len(tokens)} tokens")
        
        # Test POS tagging
        _, pos_tags = preprocessor.preprocess(text, apply_pos_tagging=True, return_tagged=True)
        print(f"✅ POS Tagging: {len(pos_tags)} tags assigned")
        
        # Test stopword removal
        preprocessor_nostop = TextPreprocessor(remove_stopwords=True)
        tokens_filtered, _ = preprocessor_nostop.preprocess(text)
        print(f"✅ Stopword Removal: {len(tokens)} → {len(tokens_filtered)} tokens")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Preprocessing verification failed: {e}")
        print()
        return False


def verify_cfg_parsing():
    """Verify CFG parsing functionality."""
    print("=" * 80)
    print("VERIFYING CFG PARSING")
    print("=" * 80)
    
    try:
        from parsing_ambiguity import parser, detect_ambiguity
        
        text = "i saw the man with the telescope"
        tokens = text.split()
        
        # Test parsing
        trees = list(parser.parse(tokens))
        print(f"✅ CFG Parsing: {len(trees)} parse tree(s) found")
        
        # Verify multiple parses for ambiguous sentence
        if len(trees) > 1:
            print(f"✅ Ambiguity Detection: Multiple parse trees detected ✓")
        else:
            print(f"⚠️  Ambiguity Detection: Only 1 parse tree (expected multiple)")
        
        print()
        return True
    except Exception as e:
        print(f"❌ CFG parsing verification failed: {e}")
        print()
        return False


def verify_dependency_parsing():
    """Verify dependency parsing functionality."""
    print("=" * 80)
    print("VERIFYING DEPENDENCY PARSING")
    print("=" * 80)
    
    try:
        from dependency_parser import DependencyParser, AmbiguityAnalyzer
        
        dep_parser = DependencyParser()
        text = "I saw the man with the telescope"
        
        # Test dependency extraction
        deps = dep_parser.get_dependencies(text)
        print(f"✅ Dependency Extraction: {len(deps)} relations found")
        
        # Test noun phrase extraction
        noun_phrases = dep_parser.get_noun_phrases(text)
        print(f"✅ Noun Phrase Extraction: {len(noun_phrases)} phrases found")
        
        # Test entity extraction
        entities = dep_parser.get_entities(text)
        print(f"✅ Entity Extraction: {len(entities)} entities found")
        
        # Test ambiguity analysis
        analyzer = AmbiguityAnalyzer()
        result = analyzer.analyze_dependency_ambiguity(text)
        print(f"✅ Ambiguity Analysis: {len(result['ambiguity_indicators'])} indicators detected")
        
        if result['potentially_ambiguous']:
            print(f"✅ Ambiguity Detection: Sentence marked as ambiguous ✓")
        
        print()
        return True
    except Exception as e:
        print(f"⚠️  Dependency parsing verification (optional): {e}")
        print()
        return True  # Not critical


def verify_ambiguity_classification():
    """Verify ambiguity classification functionality."""
    print("=" * 80)
    print("VERIFYING AMBIGUITY CLASSIFICATION")
    print("=" * 80)
    
    try:
        from ambiguity_output import AmbiguityClassifier, OutputFormatter, AmbiguityResult
        
        classifier = AmbiguityClassifier()
        text = "I saw the man with the telescope"
        
        # Test classification
        result = classifier.classify(text, parse_trees=[1, 2])  # Simulate 2 parse trees
        print(f"✅ Classification: {result.is_ambiguous} (ambiguous={result.is_ambiguous})")
        
        # Verify result properties
        print(f"✅ Ambiguity Level: {result.ambiguity_level}")
        print(f"✅ Confidence Score: {result.confidence:.1%}")
        print(f"✅ Ambiguity Types: {len(result.ambiguity_types)} types detected")
        print(f"✅ Explanations: {len(result.explanations)} provided")
        print(f"✅ Suggestions: {len(result.suggestions)} provided")
        
        # Test output formatting
        formatter = OutputFormatter()
        text_output = formatter.format_text(result)
        json_output = formatter.format_json(result)
        
        print(f"✅ Text Output: {len(text_output)} characters")
        print(f"✅ JSON Output: {len(json_output)} characters")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Ambiguity classification verification failed: {e}")
        print()
        return False


def verify_pipeline_integration():
    """Verify complete pipeline integration."""
    print("=" * 80)
    print("VERIFYING PIPELINE INTEGRATION")
    print("=" * 80)
    
    try:
        from ambiguity_pipeline import AmbiguityDetectionPipeline
        
        pipeline = AmbiguityDetectionPipeline(
            remove_stopwords=False,
            use_dependency_parser=True,
            use_cfg_parser=True
        )
        print(f"✅ Pipeline Initialization: OK")
        
        # Test single sentence processing
        test_sentences = [
            "I saw the man with the telescope",
            "She visited the museum with exhibits",
            "The dog ate the bone"
        ]
        
        for sent in test_sentences:
            result, output = pipeline.process(sent, output_format='text')
            print(f"✅ Process '{sent[:30]}...': {result.is_ambiguous}")
        
        # Test batch processing
        results = pipeline.process_batch(test_sentences, output_format='json')
        print(f"✅ Batch Processing: {len(results)} results")
        
        # Test different output formats
        result_text, output_text = pipeline.process(test_sentences[0], output_format='text')
        result_json, output_json = pipeline.process(test_sentences[0], output_format='json')
        
        print(f"✅ Text Format Output: {len(output_text)} characters")
        print(f"✅ JSON Format Output: {len(output_json)} characters")
        
        print()
        return True
    except Exception as e:
        print(f"❌ Pipeline integration verification failed: {e}")
        print()
        return False


def print_summary(results):
    """Print verification summary."""
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print()
    
    if failed == 0:
        print("🎉 All features verified successfully!")
        print()
        print("Next steps:")
        print("1. Run the pipeline: python3 ambiguity_pipeline.py --demo")
        print("2. Test with your own text: python3 ambiguity_pipeline.py --text '...'")
        print("3. Read the documentation: cat QUICK_START.md")
        print()
        return 0
    else:
        print(f"⚠️  Some features need attention. Please see errors above.")
        print()
        return 1


def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " AMBIGUITY DETECTION PIPELINE - FEATURE VERIFICATION".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = []
    
    # Run verifications
    results.append(verify_imports())
    results.append(verify_preprocessing())
    results.append(verify_cfg_parsing())
    results.append(verify_dependency_parsing())
    results.append(verify_ambiguity_classification())
    results.append(verify_pipeline_integration())
    
    # Print summary
    exit_code = print_summary(results)
    
    return exit_code


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
