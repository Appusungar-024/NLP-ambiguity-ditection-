# Quick Start Guide - Ambiguity Detection Pipeline

## Installation (60 seconds)

```bash
# 1. Navigate to project
cd nlp_project

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install nltk spacy

# 4. Download language models
python3 -m spacy download en_core_web_sm
python3 -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('stopwords')"

# Done! ✅
```

## Run Pipeline

### 1. Demo (See All Features)

```bash
python3 ambiguity_pipeline.py --demo
```

Output shows:
- Text preprocessing (tokens + POS tags)
- CFG parsing results
- Dependency parsing results
- Ambiguity classification
- Detailed explanations
- Suggestions for clarification

### 2. Analyze Single Text

```bash
python3 ambiguity_pipeline.py --text "I saw the man with the telescope"
```

Output:
```
================================================================================
SENTENCE: I saw the man with the telescope
================================================================================
Classification: AMBIGUOUS
Ambiguity Level: HIGH
Confidence: 80.00%
Number of Parse Trees: 2

Ambiguity Types:
  • syntactic
  • lexical
  • pp_attachment

Explanations:
  1. Multiple valid parse trees detected (2 parses)
  2. Polysemous word(s) detected: saw (multiple meanings)
  3. Multiple noun phrases (possible attachment ambiguity)

Suggestions:
  1. Consider adding context or clarifying the attachment of prepositional phrases
================================================================================
```

### 3. Process File

```bash
# Create input file
echo "I saw the man with the telescope
She ate the pizza with mushrooms
The bank can accept new customers" > input.txt

# Process file
python3 ambiguity_pipeline.py --file input.txt --output results.txt

# View results
cat results.txt
```

### 4. JSON Output

```bash
python3 ambiguity_pipeline.py --text "I saw the man with the telescope" --format json
```

```json
{
  "sentence": "I saw the man with the telescope",
  "is_ambiguous": true,
  "ambiguity_level": "HIGH",
  "ambiguity_types": ["syntactic", "lexical", "pp_attachment"],
  "parse_count": 2,
  "confidence": 0.8,
  "explanations": [...],
  "ambiguous_phrases": [...],
  "suggestions": [...]
}
```

## Python API

```python
from ambiguity_pipeline import AmbiguityDetectionPipeline

# Initialize
pipeline = AmbiguityDetectionPipeline()

# Process text
result, output = pipeline.process(
    "I saw the man with the telescope",
    output_format='text'
)

# Access results
print(f"Ambiguous: {result.is_ambiguous}")
print(f"Level: {result.ambiguity_level}")
print(f"Confidence: {result.confidence:.1%}")
print(f"Types: {result.ambiguity_types}")
print(f"Explanations: {result.explanations}")
print(f"Suggestions: {result.suggestions}")

# Batch processing
texts = [
    "I saw the man with the telescope",
    "She visited the museum with exhibits",
    "The dog ate the bone"
]

results = pipeline.process_batch(texts)
for result, output in results:
    print(f"{result.sentence}: {result.is_ambiguous}")
```

## What Gets Detected

### Syntactic Ambiguity
Multiple valid parse trees for same sentence
```
"I saw the man with the telescope"
→ Detected ✓ (2 parse trees)
```

### PP-Attachment Ambiguity
Prepositional phrase can attach to multiple parts
```
"saw the man with the telescope"
→ Detected ✓ (attach to 'saw' or 'man'?)
```

### Lexical Ambiguity
Polysemous words (multiple meanings)
```
"I heard about the bank"
→ Detected ✓ (financial bank vs river bank)
```

### Coordination Ambiguity
Unclear scope of conjunctions
```
"old men and women"
→ Detected ✓ ((old men) and women vs old (men and women))
```

### Scope Ambiguity
Negation/quantifier scope issues
```
"Every student didn't finish"
→ Detected ✓ (Every(NOT finished) vs NOT(Every finished))
```

## Common Commands

```bash
# Single text, text format (default)
python3 ambiguity_pipeline.py --text "..."

# Single text, JSON format
python3 ambiguity_pipeline.py --text "..." --format json

# File input, file output
python3 ambiguity_pipeline.py --file input.txt --output output.txt

# Remove stopwords
python3 ambiguity_pipeline.py --text "..." --remove-stopwords

# Disable dependency parser (faster, less features)
python3 ambiguity_pipeline.py --text "..." --no-dependency

# Disable CFG parser (faster, less ambiguity detection)
python3 ambiguity_pipeline.py --text "..." --no-cfg

# Run demo
python3 ambiguity_pipeline.py --demo

# Get help
python3 ambiguity_pipeline.py --help
```

## Output Interpretation

### Ambiguity Levels
- **NONE**: Not ambiguous (clear)
- **LOW**: Minor ambiguity (confidence 0-0.4)
- **MEDIUM**: Moderate ambiguity (confidence 0.4-0.7)
- **HIGH**: Strong ambiguity (confidence 0.7-1.0)

### Confidence Score
- 0.0-1.0 scale (0-100%)
- Higher = more confident it's ambiguous
- Based on:
  - Number of parse trees
  - Dependency patterns
  - Lexical ambiguity
  - Pattern matches

### Explanations
Clear reasons why ambiguity was detected:
- "Multiple valid parse trees detected (X parses)"
- "PP-attachment ambiguity: 'word' could attach to..."
- "Polysemous word(s) detected: word (multiple meanings)"
- "Multiple noun phrases (possible attachment ambiguity)"

### Suggestions
Actionable recommendations:
- "Consider adding context or clarifying..."
- "Clarify the scope of coordinate structures..."
- "Consider rephrasing for clarity"

## Test It Out

### Test 1: Classic PP-Attachment Ambiguity
```bash
python3 ambiguity_pipeline.py --text "I saw the man with the telescope"
```
✓ Expected: AMBIGUOUS, HIGH level, 2 parse trees

### Test 2: Multiple Ambiguities
```bash
python3 ambiguity_pipeline.py --text "I heard the news from my friend with the phone"
```
✓ Expected: AMBIGUOUS, HIGH level, multiple explanations

### Test 3: Lexical Ambiguity
```bash
python3 ambiguity_pipeline.py --text "The bank can accept new customers"
```
✓ Expected: AMBIGUOUS, lexical ambiguity (bank, can)

### Test 4: Clear Sentence
```bash
python3 ambiguity_pipeline.py --text "The dog ate the bone"
```
✓ Expected: NOT AMBIGUOUS (or LOW ambiguity)

## Features Overview

| Feature | Status | Module |
|---------|--------|--------|
| Text Cleaning | ✅ | text_preprocessing.py |
| Tokenization | ✅ | text_preprocessing.py |
| Stopword Removal | ✅ | text_preprocessing.py |
| POS Tagging | ✅ | text_preprocessing.py |
| CFG Parsing | ✅ | parsing_ambiguity.py |
| Dependency Parsing | ✅ | dependency_parser.py |
| Syntactic Ambiguity Detection | ✅ | ambiguity_output.py |
| PP-Attachment Detection | ✅ | ambiguity_output.py |
| Lexical Ambiguity Detection | ✅ | ambiguity_output.py |
| Coordination Ambiguity Detection | ✅ | ambiguity_output.py |
| Confidence Scoring | ✅ | ambiguity_output.py |
| Detailed Explanations | ✅ | ambiguity_output.py |
| Suggestions | ✅ | ambiguity_output.py |
| Text Output | ✅ | ambiguity_output.py |
| JSON Output | ✅ | ambiguity_output.py |
| CSV Output | ✅ | ambiguity_output.py |
| Batch Processing | ✅ | ambiguity_pipeline.py |
| CLI Interface | ✅ | ambiguity_pipeline.py |

## Documentation

- `README.md` - Project overview
- `PIPELINE_GUIDE.py` - Detailed pipeline documentation
- `IMPLEMENTATION_SUMMARY.py` - Complete implementation details
- `QUICK_START.md` - This file

## Support

For detailed information:
```bash
# View pipeline guide
python3 PIPELINE_GUIDE.py

# View implementation summary
python3 IMPLEMENTATION_SUMMARY.py

# View this guide
cat QUICK_START.md
```

---

**Happy analyzing! 🚀**
