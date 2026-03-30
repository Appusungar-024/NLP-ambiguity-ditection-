# System Architecture & Design - Visual Guide

## How the System Identifies Ambiguity

### 1. Parse Tree Variations Analysis

```
┌─────────────────────────────────────────────────────────────────┐
│ Input: "I saw the man with the telescope"                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ TOKENIZATION: ["i", "saw", "the", "man", "with", "the", ...]    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ CFG PARSER + GRAMMAR RULES                                      │
│                                                                  │
│ Rules:                          Parse Results:                  │
│ • S → NP VP                                                      │
│ • VP → V NP | VP PP      ──→   Parse 1: [saw [man] [with tele]] │
│ • NP → Det N | NP PP            └─ "saw with the telescope"      │
│ • PP → P NP                                                      │
│                               Parse 2: [saw [man with tele]]    │
│                               └─ "saw the man with telescope"    │
│                                                                  │
│ Result: 2 VALID PARSE TREES ─► SYNTACTIC AMBIGUITY DETECTED    │
│         Confidence: 0.60 (MEDIUM)                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Semantic Inconsistencies Detection

```
┌─────────────────────────────────────────────────────────────────┐
│ DEPENDENCY PARSER (spaCy)                                       │
│                                                                  │
│ Extracted Dependencies:                                         │
│ • (saw, nsubj, I)       ← "I" is subject of "saw"               │
│ • (man, det, the)       ← "the" modifies "man"                  │
│ • (saw, dobj, man)      ← "man" is object of "saw"              │
│ • (man, prep, with)     ← "with" modifies "man" (or saw?)       │
│ • (with, pobj, telescope) ← "telescope" is object of "with"     │
│                                                                  │
│ SEMANTIC INCONSISTENCY:                                         │
│ ┌─ Multiple attachment points for "with":                       │
│ │  ├─ Could modify "saw" (instrument):                          │
│ │  │  "I saw (using the telescope) the man"                     │
│ │  │                                                             │
│ │  └─ Could modify "man" (possession):                          │
│ │     "I saw (the man who has the telescope)"                   │
│ │                                                               │
│ └─ Result: PP-ATTACHMENT AMBIGUITY                              │
│    Confidence: +0.30                                            │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Linguistic Rules & Patterns

```
┌──────────────────────────────────────────────────────────────────┐
│ PATTERN MATCHING                                                 │
│                                                                   │
│ Pattern 1: Multiple Prepositional Phrases                        │
│ ──────────────────────────────────────────                       │
│ Sentence: "I saw the man with the telescope in the park"         │
│ Pattern:  V    NP    PP            PP                            │
│           ↓    ↓     ↓             ↓                             │
│           saw  man   with tele     in park                       │
│                 └─────┬─────────────┘                            │
│                 Multiple PP's can attach at different levels    │
│                 Result: 5+ parse trees (HIGH ambiguity)         │
│                                                                   │
│ Pattern 2: Coordination Ambiguity                                │
│ ──────────────────────────────────                               │
│ Sentence: "old men and women"                                    │
│ Parses:                                                          │
│   • ((old men) and women)     ← men and women groups separately  │
│   • (old (men and women))     ← both men and women are old       │
│   Result: 2 valid interpretations                                │
│                                                                   │
│ Pattern 3: Relative Clause Scope                                 │
│ ──────────────────────────────────                               │
│ Sentence: "The student in the corner who solved the problem"     │
│ Parses:                                                          │
│   • [(student in corner) who solved]  ← modifier of student      │
│   • [student (in (corner who solved))] ← modifier of corner      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 4. Lexical Databases - Polysemous Words

```
┌────────────────────────────────────────────────────────────┐
│ LEXICAL ANALYSIS                                           │
│                                                            │
│ Sentence: "The bank can accept new customers"             │
│                                                            │
│ Step 1: Tokenize & Check Dictionary                       │
│ ─────────────────────────────────────                     │
│ Words: [the, bank, can, accept, new, customers]           │
│                │     │                                    │
│                ▼     ▼                                    │
│         ┌─────────────────┐                              │
│         │ Polysemous?     │                              │
│         └─────────────────┘                              │
│                │                                          │
│         ┌──────┴────────┐                                │
│         ▼               ▼                                │
│       "bank"          "can"                              │
│       Senses:         Senses:                            │
│       1. Financial    1. Container                       │
│          Institution  2. Ability/Permission             │
│       2. River edge                                      │
│       3. Turn sharply                                    │
│                                                          │
│ Result: 2 polysemous words detected                       │
│ ─────────────────────────────────────                    │
│ • Meaning 1: "The bank [financial] can [ability]..."     │
│ • Meaning 2: "The bank [riverbank] can [container]..."   │
│ • Meaning 3: "The bank [turn] can [ability]..."          │
│                                                          │
│ Lexical Ambiguity Detected ✓                             │
│ Confidence: +0.50                                        │
│                                                          │
└────────────────────────────────────────────────────────────┘
```

## Integrated Analysis Pipeline

```
INPUT TEXT: "I saw the man with the telescope"
│
├─► STAGE 1: PREPROCESSING
│   ├─ Clean text
│   ├─ Tokenize: ["i", "saw", "the", "man", "with", "the", "telescope"]
│   ├─ POS Tag: [PRP, VBD, DET, NN, IN, DET, NN]
│   └─ Output: Cleaned tokens with POS tags
│
├─► STAGE 2a: CFG PARSING (Parse Tree Variations)
│   ├─ Apply grammar rules
│   ├─ Generate all valid parse trees
│   ├─ Result: 2 parse trees
│   └─ Signal: SYNTACTIC AMBIGUITY ✓
│       Confidence: 0.60
│
├─► STAGE 2b: DEPENDENCY PARSING (Semantic Analysis)
│   ├─ Extract head-dependent relations
│   ├─ Identify noun phrases
│   ├─ Detect attachment ambiguities
│   └─ Signal: PP-ATTACHMENT AMBIGUITY ✓
│       Confidence: +0.30
│
├─► STAGE 3: LEXICAL ANALYSIS
│   ├─ Check polysemous words
│   ├─ Find: "saw" (polysemous)
│   └─ Signal: LEXICAL AMBIGUITY ✓
│       Confidence: +0.10
│
└─► STAGE 4: AGGREGATION & SCORING
    ├─ Combine signals: 0.60 + 0.30 + 0.10 = 1.0 (capped)
    ├─ Final Confidence: 0.80 (80%)
    ├─ Ambiguity Level: HIGH
    ├─ Types: [syntactic, pp_attachment, lexical]
    ├─ Explanations:
    │  1. Multiple valid parse trees detected (2 parses)
    │  2. PP-attachment ambiguity: 'with' could attach to 'saw' or 'man'
    │  3. Polysemous word(s) detected: saw (multiple meanings)
    ├─ Phrases:
    │  • the man
    │  • saw
    │  • the telescope
    └─ Suggestions:
       • Consider adding context or clarifying attachment
```

## Confidence Scoring Mechanism

```
Base Confidence: 0.0

Signal 1: Parse Tree Count
├─ 1 tree: 0.0 (no ambiguity)
├─ 2 trees: 0.40
├─ 3 trees: 0.60
└─ 5+ trees: 1.0
   └─ Add: 0.40 ← (in this example)

Signal 2: PP-Attachment Pattern
├─ Multiple prepositions: +0.30
│   └─ Running total: 0.70

Signal 3: Lexical Ambiguity
├─ 1 polysemous word: +0.10
│   └─ Running total: 0.80

Signal 4: Other Indicators
├─ Noun phrase count > 1: +0.05
│   └─ Running total: 0.85 → capped at 1.0

═══════════════════════════════════════════════════════════════
FINAL CONFIDENCE: 0.80 (80%)
AMBIGUITY LEVEL: HIGH (0.70-1.0)
═══════════════════════════════════════════════════════════════
```

## Linguistic Rules in Action

### Rule 1: VP → VP PP (Ambiguity Generator)

```
Grammar Rule: VP → VP PP

This rule allows prepositional phrases to attach at different levels:

Sentence: "saw the man with the telescope"

Parse 1: VP
         ├─ VP
         │  ├─ V: saw
         │  └─ NP: the man
         └─ PP: with the telescope
         
         Interpretation: "saw (using the telescope) [the man]"
         
Parse 2: VP
         ├─ V: saw
         └─ NP
            ├─ Det: the
            ├─ N: man
            └─ PP: with the telescope
            
         Interpretation: "saw [the man with the telescope]"

Why ambiguous: The grammar allows PP to attach to either:
  • The VP (modifying the verb "saw") ← Parse 1
  • The NP (modifying the noun "man") ← Parse 2
```

### Rule 2: NP → NP CC NP (Coordination)

```
Grammar Rule: NP → NP CC NP

Creates ambiguity in grouping:

Sentence: "old men and women"

Parse 1: NP
         ├─ AP: old
         ├─ NP: men
         ├─ CC: and
         └─ NP: women
         
         Meaning: (old men) and (women)

Parse 2: NP
         ├─ AP: old
         └─ NP
            ├─ N: men
            ├─ CC: and
            └─ N: women
            
         Meaning: old (men and women)
```

## Key Implementation Details

### Where Each Component Lives

| Component | Module | Purpose |
|-----------|--------|---------|
| Text Cleaning | `text_preprocessing.py` | Remove noise |
| Tokenization | `text_preprocessing.py` | Split into words |
| POS Tagging | `text_preprocessing.py` | Tag word types |
| Grammar Rules | `parsing_ambiguity.py` | Define valid structures |
| CFG Parser | `parsing_ambiguity.py` (NLTK) | Generate parse trees |
| Dependencies | `dependency_parser.py` (spaCy) | Extract relations |
| NP/Entity Detection | `dependency_parser.py` (spaCy) | Identify phrases |
| Polysemous Dictionary | `ambiguity_output.py` | Word senses |
| Classification | `ambiguity_output.py` | Determine ambiguity |
| Scoring | `ambiguity_output.py` | Calculate confidence |
| Formatting | `ambiguity_output.py` | Output results |

### Data Structures

```python
# Result object
class AmbiguityResult:
    sentence: str                      # Original input
    is_ambiguous: bool                 # True/False
    ambiguity_level: str               # NONE, LOW, MEDIUM, HIGH
    confidence: float                  # 0.0-1.0
    ambiguity_types: List[str]         # [syntactic, lexical, pp_attachment, ...]
    parse_count: int                   # Number of valid parses
    explanations: List[str]            # Why ambiguous
    ambiguous_phrases: List[str]       # Which parts are ambiguous
    suggestions: List[str]             # How to clarify

# Parse tree (NLTK)
parse_tree: Tree                       # Hierarchical structure
  ├─ .productions()                   # Grammar rules used
  └─ .leaves()                         # Terminal words

# Dependency (spaCy)
dependency: Tuple[head, relation, dependent]
  ├─ head: str                         # Governor word
  ├─ relation: str                     # Relationship type
  └─ dependent: str                    # Dependent word
```

---

This system combines parse tree variation analysis, semantic analysis, linguistic rules, and lexical databases to comprehensively identify ambiguity in natural language sentences.
