"""
AMBIGUITY DETECTION PIPELINE - COMPREHENSIVE GUIDE

This document describes the complete pipeline for detecting syntactic and semantic
ambiguity in natural language sentences.

================================================================================
PIPELINE ARCHITECTURE
================================================================================

The pipeline consists of 4 main stages:

┌─────────────────────────────────────────────────────────────────────────────┐
│                        INPUT: Raw Text                                      │
└────────────────────┬────────────────────────────────────────────────────────┘
                     │
        ┌────────────▼────────────────┐
        │  STAGE 1: PREPROCESSING    │
        ├────────────────────────────┤
        │ • Text cleaning            │
        │ • Tokenization             │
        │ • Stopword removal (opt)   │
        │ • POS tagging              │
        └────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      │                             │
  ┌───▼────────┐          ┌────────▼──────┐
  │  CFG Parser│          │ Dep. Parser    │
  │  (NLTK)    │          │  (spaCy)       │
  └───┬────────┘          └────────┬───────┘
      │                             │
  ┌───▼─────────────────────────────▼─────┐
  │  STAGE 2: PARSING                      │
  ├────────────────────────────────────────┤
  │ • Multiple parse trees (syntactic)     │
  │ • Dependency structures                │
  │ • Named entities                       │
  │ • Noun phrases                         │
  └────────────────────────────────────────┘
                     │
        ┌────────────▼────────────────┐
        │  STAGE 3: AMBIGUITY        │
        │  DETECTION & ANALYSIS      │
        ├────────────────────────────┤
        │ • Syntactic ambiguity      │
        │ • Semantic/lexical ambig.  │
        │ • PP-attachment detection  │
        │ • Coordination ambiguity   │
        │ • Confidence scoring       │
        └────────────────────────────┘
                     │
        ┌────────────▼────────────────┐
        │  STAGE 4: OUTPUT           │
        ├────────────────────────────┤
        │ • Classification result    │
        │ • Detailed explanations    │
        │ • Suggestions              │
        │ • Multiple formats (JSON)  │
        └────────────────────────────┘
                     │
        ┌────────────▼──────────────────┐
        │  OUTPUT: Structured Result    │
        └───────────────────────────────┘

================================================================================
DETAILED COMPONENT DESCRIPTION
================================================================================

1. TEXT PREPROCESSING (text_preprocessing.py)
────────────────────────────────────────────

Module: TextPreprocessor

Features:
  - Text Cleaning
    * Remove URLs, emails, HTML tags
    * Normalize whitespace
    * Lowercase conversion (optional)
  
  - Tokenization
    * NLTK word_tokenize for proper punctuation handling
    * Sentence-level tokenization available
  
  - Stopword Removal (Optional)
    * English stopwords from NLTK corpus
    * Optional based on use case
  
  - POS Tagging
    * Averaged Perceptron Tagger (NLTK)
    * Universal POS tags and fine-grained tags

Example:
    from text_preprocessing import TextPreprocessor
    
    preprocessor = TextPreprocessor(remove_stopwords=False)
    tokens, pos_tags = preprocessor.preprocess(
        "I saw the man with the telescope",
        apply_pos_tagging=True,
        return_tagged=True
    )


2. PARSING METHODS (parsing_ambiguity.py + dependency_parser.py)
─────────────────────────────────────────────────────────────────

a) Context-Free Grammar (CFG) Parser
   Module: parsing_ambiguity.py
   Parser: NLTK ChartParser
   
   - Uses predefined CFG rules
   - Produces multiple parse trees for ambiguous sentences
   - Shows syntactic structure with constituent trees
   
   Example rules in grammar:
     S -> NP VP
     VP -> V NP | VP PP
     NP -> Det N | NP PP
     PP -> P NP
   
   Output: List of parse tree objects

b) Dependency Parser
   Module: dependency_parser.py
   Parser: spaCy (en_core_web_sm)
   
   - Produces dependency relations (head-dependent pairs)
   - Extracts noun phrases and named entities
   - Generates tree structures
   - More flexible than CFG for parsing diverse text
   
   Output: Dependency tuples, tree structure, entities


3. AMBIGUITY DETECTION (ambiguity_output.py)
──────────────────────────────────────────────

Module: AmbiguityClassifier

Ambiguity Types Detected:

  a) SYNTACTIC AMBIGUITY
     - Multiple parse trees from CFG parser
     - Detected when: parse_count > 1
     - Confidence: High (80%+)
     - Example: "I saw the man with the telescope"
       * Parse 1: [I [saw [the man] [with the telescope]]]
       * Parse 2: [I [saw [the man with telescope]]]

  b) PP-ATTACHMENT AMBIGUITY
     - Prepositional phrase can attach to multiple constituents
     - Pattern: verb + NP + PP
     - Example: "saw the man with the telescope"
       * Attach to 'saw'? (saw WITH the telescope)
       * Attach to 'man'? (man WITH the telescope)

  c) COORDINATION AMBIGUITY
     - Coordinated structures with unclear scope
     - Pattern: NP + conj + NP (multiple times)
     - Example: "old men and women" 
       * (old (men and women)) vs ((old men) and (women))

  d) LEXICAL AMBIGUITY
     - Polysemous words (multiple meanings)
     - Example words: "bank", "saw", "bear", "plant", etc.
     - Detected using lexical database

  e) SCOPE AMBIGUITY (Semantic)
     - Negation, quantifiers with unclear scope
     - Example: "Every student didn't finish" 
       * (every student (didn't finish)) vs (NOT(every student finished))

Confidence Scoring:
  - LOW (0.0-0.4): Potential ambiguity but low confidence
  - MEDIUM (0.4-0.7): Moderate likelihood of ambiguity
  - HIGH (0.7-1.0): Clear indicators of ambiguity

Ambiguity Levels:
  - NONE: No ambiguity detected
  - LOW: Minor ambiguity indicators
  - MEDIUM: Some ambiguity present
  - HIGH: Strong ambiguity signals


4. OUTPUT & EXPLANATIONS (ambiguity_output.py)
──────────────────────────────────────────────

Module: OutputFormatter & AmbiguityResult

Output Contains:
  ✓ Classification (Ambiguous / Not Ambiguous)
  ✓ Ambiguity Level (None, Low, Medium, High)
  ✓ Confidence Score (0.0 to 1.0)
  ✓ Parse Tree Count (how many parses found)
  ✓ Ambiguity Types (syntactic, semantic, lexical, etc.)
  ✓ Detailed Explanations (why ambiguity detected)
  ✓ Ambiguous Phrases/Words (which parts are ambiguous)
  ✓ Suggestions (how to clarify)
  ✓ Multiple Output Formats (text, JSON, CSV)

Example Text Output:
    ================================================================================
    SENTENCE: I saw the man with the telescope
    ================================================================================
    Classification: AMBIGUOUS
    Ambiguity Level: HIGH
    Confidence: 85.00%
    Number of Parse Trees: 2
    
    Ambiguity Types:
      • syntactic
      • pp_attachment
    
    Explanations:
      1. Multiple valid parse trees detected (2 parses)
      2. PP-attachment ambiguity: 'with' could attach to 'saw' or to its object
    
    Ambiguous Phrases/Words:
      • with
      • the telescope
    
    Suggestions:
      1. Consider adding context or clarifying the attachment of prepositional phrases
    ================================================================================


================================================================================
COMPLETE PIPELINE INTEGRATION (ambiguity_pipeline.py)
================================================================================

Module: AmbiguityDetectionPipeline

High-level API for full pipeline processing:

    from ambiguity_pipeline import AmbiguityDetectionPipeline
    
    # Initialize
    pipeline = AmbiguityDetectionPipeline(
        remove_stopwords=False,
        use_dependency_parser=True,
        use_cfg_parser=True
    )
    
    # Process single text
    result, formatted_output = pipeline.process(
        "I saw the man with the telescope",
        output_format='text'  # or 'json'
    )
    
    print(formatted_output)
    
    # Process batch
    texts = ["...", "...", "..."]
    results = pipeline.process_batch(texts, output_format='json')


================================================================================
USAGE EXAMPLES
================================================================================

1. Command-line Interface
─────────────────────────

a) Process single text:
   $ python ambiguity_pipeline.py --text "I saw the man with the telescope"

b) Process file:
   $ python ambiguity_pipeline.py --file input.txt --format json --output results.json

c) Run demo:
   $ python ambiguity_pipeline.py --demo

d) With stopword removal:
   $ python ambiguity_pipeline.py --text "..." --remove-stopwords

e) Disable specific parsers:
   $ python ambiguity_pipeline.py --text "..." --no-dependency
   $ python ambiguity_pipeline.py --text "..." --no-cfg


2. Python API
─────────────

from ambiguity_pipeline import AmbiguityDetectionPipeline

pipeline = AmbiguityDetectionPipeline()

# Single sentence
result, output = pipeline.process("I saw the man with the telescope")
print(f"Ambiguous: {result.is_ambiguous}")
print(f"Level: {result.ambiguity_level}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Explanations: {result.explanations}")

# Batch processing
texts = [
    "I saw the man with the telescope",
    "She ate the pizza with mushrooms",
    "The bank can accept new customers",
]

results = pipeline.process_batch(texts)
for result, output in results:
    print(f"Sentence: {result.sentence}")
    print(f"Ambiguous: {result.is_ambiguous}")
    print()


3. Individual Components
────────────────────────

from text_preprocessing import TextPreprocessor
from dependency_parser import DependencyParser, AmbiguityAnalyzer
from parsing_ambiguity import parser, detect_ambiguity

# Preprocessing
preprocessor = TextPreprocessor(remove_stopwords=False)
tokens, pos_tags = preprocessor.preprocess(
    "I saw the man with the telescope",
    apply_pos_tagging=True,
    return_tagged=True
)
print(f"Tokens: {tokens}")
print(f"POS: {pos_tags}")

# CFG Parsing
trees = list(parser.parse(tokens))
print(f"Parse count: {len(trees)}")

# Dependency Parsing
dep_parser = DependencyParser()
deps = dep_parser.get_dependencies("I saw the man with the telescope")
print(f"Dependencies: {deps}")

analyzer = AmbiguityAnalyzer()
ambiguity_info = analyzer.analyze_dependency_ambiguity("...")
print(f"Ambiguity indicators: {ambiguity_info['ambiguity_indicators']}")


================================================================================
CONFIGURATION & CUSTOMIZATION
================================================================================

1. Stopword Removal
   - Default: disabled (keeps all words)
   - Use case: enabling useful when analyzing semantic similarity
   - Languages: English only (current)

2. POS Tagging
   - Default: enabled (Averaged Perceptron Tagger)
   - Alternative: Could use other NLTK taggers
   - Used for: lexical ambiguity detection, semantic analysis

3. Dependency Parser Model
   - Default: en_core_web_sm (small model, ~40MB)
   - Alternative: en_core_web_md (medium, ~100MB), en_core_web_lg (large, ~600MB)
   - Trade-off: accuracy vs speed/memory

4. CFG Grammar
   - File: parsing_ambiguity.py (GRAMMAR variable)
   - Can be extended with domain-specific rules
   - Can load from file (--pcfg option in parsing_ambiguity.py)

5. Ambiguity Thresholds
   - Edit: ambiguity_output.py (AmbiguityClassifier._check_lexical_ambiguity)
   - Customize polysemous word lists
   - Adjust confidence thresholds


================================================================================
OUTPUT FORMATS
================================================================================

1. TEXT FORMAT (Default)
   - Human-readable
   - Shows all analysis details
   - Good for manual review

2. JSON FORMAT
   - Machine-readable
   - Complete metadata
   - Suitable for further processing
   
   Example:
   {
     "sentence": "I saw the man with the telescope",
     "is_ambiguous": true,
     "ambiguity_level": "HIGH",
     "ambiguity_types": ["syntactic", "pp_attachment"],
     "parse_count": 2,
     "confidence": 0.85,
     "explanations": [...],
     "ambiguous_phrases": [...],
     "suggestions": [...]
   }

3. CSV FORMAT
   - Batch processing results
   - Excel/spreadsheet compatible
   - Suitable for statistical analysis

   Columns: sentence, is_ambiguous, ambiguity_level, ambiguity_types,
            parse_count, confidence, explanations, ambiguous_phrases, suggestions


================================================================================
TESTING & VALIDATION
================================================================================

Example sentences with known ambiguities:

1. PP-Attachment:
   "I saw the man with the telescope"
   - Expected: Multiple parse trees, HIGH confidence

2. Coordination:
   "old men and women"
   - Expected: Ambiguous, MEDIUM confidence

3. Lexical:
   "I saw the bank by the river"
   - Expected: Low-medium confidence (word ambiguity)

4. Clear (non-ambiguous):
   "The dog ate the bone"
   - Expected: NOT AMBIGUOUS

5. Complex:
   "I heard that she left with the manager"
   - Expected: Potentially ambiguous (attachment)


================================================================================
PERFORMANCE NOTES
================================================================================

- Preprocessing: ~1-10ms per sentence
- CFG Parsing: ~5-50ms (depends on sentence length)
- Dependency Parsing: ~10-100ms (first run downloads model)
- Classification: ~1-5ms
- Total: ~20-150ms per sentence

Memory usage:
- NLTK data: ~50MB
- spaCy model: ~40MB (small model)
- Total: ~100MB+ for full pipeline

Scalability:
- Batch processing: process 1000 sentences in ~30-150 seconds
- For larger batches: use multiprocessing (custom implementation)


================================================================================
TROUBLESHOOTING
================================================================================

1. "No module named 'spacy'"
   Solution: pip install spacy

2. "en_core_web_sm not found"
   Solution: python -m spacy download en_core_web_sm

3. "No tokenizers/punkt found"
   Solution: nltk.download('punkt')

4. "Grammar doesn't cover some tokens"
   - Sentence contains words not in CFG grammar
   - Solution: Extend grammar or disable CFG parser (--no-cfg)

5. Memory issues with large batches
   Solution: Process in smaller batches, or use only dependency parser

6. Incorrect POS tags
   Reason: Averaged Perceptron Tagger has ~97% accuracy
   Solution: Acceptable for most use cases
"""

print(__doc__)
