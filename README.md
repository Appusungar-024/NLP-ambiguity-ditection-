Parsing Ambiguity Detection — Complete NLP Pipeline

## What This Project Includes ✨

### Complete Ambiguity Detection Pipeline

A comprehensive NLP pipeline that detects syntactic, semantic, and lexical ambiguity:

1. **Text Preprocessing** — cleaning, tokenization, stopword removal, POS tagging
2. **Parsing** — Context-Free Grammar (CFG) parser + spaCy dependency parser
3. **Ambiguity Detection** — syntactic, semantic, lexical, PP-attachment, coordination ambiguities
4. **Output Module** — structured classification with detailed explanations

### Key Features

✅ **Multiple Parsing Methods**
  - CFG Parser (NLTK ChartParser) for syntactic trees
  - Dependency Parser (spaCy) for linguistic relations
  - Probabilistic parsing support (PCFG)

✅ **Comprehensive Ambiguity Detection**
  - Syntactic ambiguity (multiple parse trees)
  - PP-attachment ambiguity
  - Coordination ambiguity  
  - Lexical/semantic ambiguity (polysemous words)
  - Confidence scoring

✅ **Detailed Output**
  - Classification (Ambiguous/Not Ambiguous)
  - Ambiguity type and level
  - Detailed explanations
  - Ambiguous phrases identification
  - Suggestions for clarification
  - Multiple formats (text, JSON, CSV)

✅ **Easy-to-Use API**
  - Command-line interface
  - Python API
  - Batch processing support

## Quick Start

### Installation

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
python3 -m pip install --upgrade pip
pip install -r nlp_project/requirements.txt

# 3. Download spaCy model (first run only)
python -m spacy download en_core_web_sm
```

### Basic Usage

```bash
# Run the complete pipeline demo
python3 nlp_project/ambiguity_pipeline.py --demo

# Process single text
python3 nlp_project/ambiguity_pipeline.py --text "I saw the man with the telescope"

# Process file
python3 nlp_project/ambiguity_pipeline.py --file input.txt --output results.json --format json

# With options
python3 nlp_project/ambiguity_pipeline.py --text "..." --remove-stopwords --format json
```

### Python API

```python
from ambiguity_pipeline import AmbiguityDetectionPipeline

# Initialize pipeline
pipeline = AmbiguityDetectionPipeline(remove_stopwords=False)

# Process text
result, formatted_output = pipeline.process(
    "I saw the man with the telescope",
    output_format='text'
)

print(f"Ambiguous: {result.is_ambiguous}")
print(f"Level: {result.ambiguity_level}")
print(f"Confidence: {result.confidence:.1%}")
print(formatted_output)
```

## Pipeline Stages

### Stage 1: Text Preprocessing

**Module:** `text_preprocessing.py`

- Text cleaning (remove URLs, emails, HTML)
- Tokenization (word and sentence level)
- Optional stopword removal
- POS tagging (part-of-speech tags)

```python
from text_preprocessing import TextPreprocessor

preprocessor = TextPreprocessor(remove_stopwords=False)
tokens, pos_tags = preprocessor.preprocess(
    "I saw the man with the telescope",
    apply_pos_tagging=True,
    return_tagged=True
)
```

### Stage 2: Parsing

**Modules:** `parsing_ambiguity.py`, `dependency_parser.py`

#### CFG Parser (NLTK)
- Produces constituent parse trees
- Shows syntactic structure
- Detects multiple valid parses

#### Dependency Parser (spaCy)
- Extracts grammatical relations
- Identifies noun phrases
- Extracts named entities
- Provides alternative parsing perspective

```python
from dependency_parser import DependencyParser, AmbiguityAnalyzer

analyzer = AmbiguityAnalyzer()
result = analyzer.analyze_dependency_ambiguity(
    "I saw the man with the telescope"
)
print(result['ambiguity_indicators'])  # Shows detected ambiguities
```

### Stage 3: Ambiguity Detection

**Module:** `ambiguity_output.py`

Detects multiple types of ambiguity:

- **Syntactic**: Multiple valid parse trees
- **PP-Attachment**: "I saw the man with the telescope"
- **Coordination**: Unclear scope of conjunctions
- **Lexical**: Polysemous words (bank, saw, bear, etc.)
- **Scope**: Negation/quantifier scope issues

Outputs confidence score and detailed explanations.

### Stage 4: Structured Output

**Module:** `ambiguity_output.py`

Provides:
- ✓ Classification (Ambiguous/Not Ambiguous)
- ✓ Ambiguity Level (None, Low, Medium, High)
- ✓ Confidence Score (0.0 to 1.0)
- ✓ Type of ambiguity
- ✓ Explanations with reasons
- ✓ Ambiguous phrases/words identified
- ✓ Suggestions for clarification

## Example Output

```
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
```

## Original Mini Demo

The classic minimal demo is still available:

```bash
python3 nlp_project/parsing_ambiguity.py
```


Notes
- Example grammar focuses on PP-attachment ambiguity (e.g., "I saw the man with the telescope").
- To experiment, modify `EXAMPLES` sentences or extend `GRAMMAR` in `parsing_ambiguity.py`.
- For detailed documentation of the entire pipeline, see `PIPELINE_GUIDE.py`

## Project Structure

```
nlp_project/
├── ambiguity_pipeline.py          # Main integration pipeline
├── ambiguity_output.py            # Output formatting & classification
├── text_preprocessing.py          # Preprocessing (tokenization, POS tagging)
├── dependency_parser.py           # Dependency parsing (spaCy)
├── parsing_ambiguity.py           # CFG parsing (NLTK)
├── ldc_loader.py                  # Dataset loading utilities
├── analyze_conversations.py       # GUM dataset analysis
├── PIPELINE_GUIDE.py              # Complete documentation
├── README.md                      # This file
├── requirements.txt               # Dependencies
└── tests/                         # Unit tests
```

## Supported Ambiguity Types

| Type | Definition | Example | Detection |
|------|-----------|---------|-----------|
| **Syntactic** | Multiple valid parse trees | "I saw the man with the telescope" | Multiple CFG parses |
| **PP-Attachment** | Prepositional phrase attachment | "saw man with telescope" | Dependency patterns |
| **Coordination** | Unclear scope of conjunctions | "old men and women" | Pattern matching |
| **Lexical** | Polysemous words | "I heard about the bank" | Word sense list |
| **Scope** | Quantifier/negation scope | "Every student didn't finish" | Semantic analysis |

## LDC Dataset Support (Optional)

Using LDC datasets (LDC99T42) for large-scale testing:

```bash
# 1. Download from LDC (requires registration)
# https://catalog.ldc.upenn.edu/LDC99T42

# 2. Extract and place under data/ directory
# nlp_project/data/LDC99T42/

# 3. Run ambiguity detection on dataset
python3 nlp_project/parsing_ambiguity.py --ldc-dir nlp_project/data/LDC99T42 \
    --max 100 --only-ambiguous --show-trees

# 4. Or use the full pipeline
python3 nlp_project/ambiguity_pipeline.py --file input.txt --output results.json
```

Notes
- LDC datasets are licensed and must be downloaded manually from the LDC catalog: https://catalog.ldc.upenn.edu/LDC99T42
- After you download and extract the files, place them under `nlp_project/data/LDC99T42/`.

Example: load sentences from the dataset
- A helper loader is provided at `nlp_project/ldc_loader.py` which can iterate `.mrg` (bracketed tree) and `.txt` files.

Quick commands (after placing files):
```bash
python3 -m pip install -r nlp_project/requirements.txt
python3 nlp_project/ldc_loader.py nlp_project/data/LDC99T42 --max 30
# Run ambiguity detection over LDC data (only shows ambiguous sentences and trees):
python3 nlp_project/parsing_ambiguity.py --ldc-dir nlp_project/data/LDC99T42 --max 100 --only-ambiguous --show-trees
```

---

## How to run this project locally ✅

Short steps (recommended):

1. Create and activate a virtual environment (POSIX):

```bash
python -m venv .venv
. .venv/bin/activate
```

2. Install runtime dependencies:

```bash
python -m pip install --upgrade pip
pip install -r nlp_project/requirements.txt
```

3. (Optional) Install dev/test dependencies and run tests:

```bash
pip install -r requirements-dev.txt
python -m pytest -q nlp_project/tests
```

Quick helper script (automates the steps above):

```bash
# Make it executable once
chmod +x scripts/setup_dev.sh
# Run (creates/uses .venv, installs deps, runs tests)
./scripts/setup_dev.sh

# Options:
#  --no-dev         Skip installing dev dependencies
#  --upgrade        Force upgrade pip
#  --force-install  Force reinstall packages even if requirements did not change
#  --skip-tests     Skip running tests after setup

Note: the script stores a combined hash of `nlp_project/requirements.txt` (and `requirements-dev.txt` when present) at `.venv/.requirements.hash` and will skip re-installing packages when the requirements have not changed. Use `--force-install` to override and reinstall regardless.
```

Notes & tips:
- The repo contains heavier submodules that may require additional packages (e.g., `torch` and `allennlp`) — running `python -m pytest` at the repo root may try to collect those tests. Use `python -m pytest -q nlp_project/tests` to run lightweight package tests only.
- LDC datasets are licensed and must be downloaded manually from the LDC catalog. After extraction, point the loader or demo scripts to the extracted path (e.g., `nlp_project/data/LDC99T42`).

If you'd like, I can also add a short `CONTRIBUTING.md` or a README badge showing CI status. See the top-level `CONTRIBUTING.md` for contribution guidelines and a PR checklist.

Note: the simple demo grammar is intentionally small and will not parse many sentences from a real corpus. For large-scale or noisy datasets, consider converting to a PCFG, using a pretrained constituency parser (e.g., benepar) or a dependency parser (spaCy) and comparing results (see Suggested next experiments in the repo).
Notes about licensing and automation
- I cannot download or redistribute LDC data for you due to licensing restrictions. The loader assumes you have lawful access and have placed the files locally.
- If you tell me the exact filenames in your extracted dataset I can adapt the loader to the layout and add parsing/ambiguous-detection glue code.
