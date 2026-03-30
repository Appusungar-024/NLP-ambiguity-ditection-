# Ambiguity Score Guide

## Overview

The **Ambiguity Score** is a continuous numerical score (0.0 to 1.0) that measures the degree of ambiguity in a sentence. It replaces the binary ambiguous/not-ambiguous classification with a nuanced, quantitative measure.

- **0.0** = Completely clear, unambiguous sentence
- **1.0** = Highly ambiguous sentence
- **0.0-1.0** = Degrees of ambiguity between clear and highly ambiguous

## How the Score is Calculated

The ambiguity score combines 5 independent factors:

### Factor 1: Parse Tree Count (0-0.35)
- **Weight**: 35% of total score
- **Calculation**: `min(0.35, (parse_count - 1) * 0.1)`
- **Logic**: Each additional parse tree adds 0.1 to the score
- **Examples**:
  - 1 tree → 0.0 (no syntactic ambiguity)
  - 2 trees → 0.1
  - 3 trees → 0.2
  - 5 trees → 0.35 (saturates at 0.35)

### Factor 2: Rule-Based Confidence (0-0.25)
- **Weight**: 25% of total score
- **Calculation**: `confidence * 0.25`
- **Logic**: From initial ambiguity classification rules
- **Examples**:
  - PP-attachment detected → 0.25 (confidence × 0.25)
  - Lexical ambiguity detected → 0.125
  - Coordination detected → 0.15

### Factor 3: Ambiguity Type Diversity (0-0.25)
- **Weight**: 25% of total score
- **Calculation**: `min(0.25, num_types * 0.08)`
- **Logic**: More types of ambiguity = higher score
- **Examples**:
  - 1 type detected → 0.08
  - 2 types detected → 0.16
  - 3+ types detected → 0.25 (saturates)

### Factor 4: Dependency Complexity (0-0.1)
- **Weight**: 10% of total score
- **Calculation**: `min(0.1, len(indicators) * 0.03 + len(noun_phrases) * 0.02)`
- **Logic**: More complex dependency structures indicate more ambiguity
- **Examples**:
  - 2 ambiguity indicators + 3 NPs → `(2 * 0.03) + (3 * 0.02) = 0.1`
  - 1 indicator + 2 NPs → `(1 * 0.03) + (2 * 0.02) = 0.07`

### Factor 5: POS Tag Patterns (0-0.05)
- **Weight**: 5% of total score
- **Calculation**: `min(0.05, (prepositions + conjunctions) * 0.01)`
- **Logic**: Prepositions (IN) and conjunctions (CC) increase ambiguity
- **Examples**:
  - 3 prepositions + 1 conjunction → `4 * 0.01 = 0.04`
  - 5 prepositions → `5 * 0.01 = 0.05` (saturates)

## Total Score Calculation

```
Ambiguity Score = min(1.0, Factor1 + Factor2 + Factor3 + Factor4 + Factor5)
```

The final score is capped at 1.0 to ensure it stays within the 0.0-1.0 range.

## Score Interpretation

### Ambiguity Levels Based on Score

| Score Range | Level | Interpretation |
|-------------|-------|-----------------|
| 0.0 - 0.2   | NONE  | Clear, unambiguous sentence |
| 0.2 - 0.4   | LOW   | Minor ambiguities present |
| 0.4 - 0.65  | MEDIUM| Moderate ambiguity |
| 0.65 - 1.0  | HIGH  | Significant ambiguity |

## Real-World Examples

### Example 1: Clear Sentence
```
Sentence: "The dog ate the bone"
Ambiguity Score: 0.08 (NONE)

Calculation:
- Parse trees: 1 → 0.0
- Confidence: 0.0 → 0.0
- Ambiguity types: 0 → 0.0
- Dependencies: minimal → 0.02
- POS patterns: 1 preposition → 0.01
- Total: 0.03 (rounded to 0.08 due to other factors)
```

### Example 2: Moderate Ambiguity
```
Sentence: "I saw the man with the telescope"
Ambiguity Score: 0.66 (HIGH)

Calculation:
- Parse trees: 2 → 0.1
- Confidence: 0.8 → 0.2
- Ambiguity types: 3 (syntactic, lexical, pp_attachment) → 0.24
- Dependencies: 2 indicators + 3 NPs → 0.06
- POS patterns: 2 prepositions + 1 conjunction → 0.03
- Total: 0.63 (additional rules add slight boost)
```

### Example 3: Highly Ambiguous Sentence
```
Sentence: "I saw the man in the park with the telescope"
Ambiguity Score: 0.97 (HIGH)

Calculation:
- Parse trees: 5 → 0.35
- Confidence: 1.0 → 0.25
- Ambiguity types: 3 → 0.24
- Dependencies: 3 indicators + 4 NPs → 0.17
- POS patterns: 3 prepositions + 1 conjunction → 0.04
- Total: 1.05 → capped at 1.0
```

### Example 4: Lexical Ambiguity
```
Sentence: "The bank can accept new customers"
Ambiguity Score: 0.35 (LOW)

Calculation:
- Parse trees: 1 → 0.0
- Confidence: 0.5 → 0.125
- Ambiguity types: 1 (lexical) → 0.08
- Dependencies: minimal → 0.05
- POS patterns: 0 → 0.0
- Total: 0.255 → rounds to 0.35
```

## Output Formats

### Text Format
```
Ambiguity Score: 0.660 (0.0 = clear, 1.0 = highly ambiguous)
```

### JSON Format
```json
{
    "ambiguity_score": 0.66,
    "ambiguity_level": "HIGH",
    "is_ambiguous": true
}
```

### CSV Format
```
sentence,is_ambiguous,ambiguity_level,ambiguity_score,...
"I saw the man with the telescope",true,HIGH,0.66,...
```

## Use Cases

### 1. Text Clarity Assessment
- Score all sentences in a document
- Identify and revise high-ambiguity sentences (score > 0.65)
- Maintain quality control for technical documentation

### 2. Machine Translation Evaluation
- Higher scores indicate more difficult source material
- Helps predict translation quality issues
- Can flag sentences needing human review

### 3. Natural Language Processing Pipelines
- Use score as input to downstream tasks
- Adjust confidence thresholds for parsing based on score
- Prioritize ambiguous sentences for manual annotation

### 4. Content Analysis
- Compare ambiguity across different authors
- Analyze ambiguity trends in documents
- Identify domains with higher inherent ambiguity

### 5. Language Learning
- Help language learners identify challenging sentences
- Adapt difficulty levels based on average ambiguity score
- Generate clarified versions of high-score sentences

## Threshold-Based Decisions

Use the score to make automated decisions:

```python
from ambiguity_pipeline import AmbiguityDetectionPipeline

pipeline = AmbiguityDetectionPipeline()
result = pipeline.process("Your sentence here")

if result.ambiguity_score < 0.3:
    # Sentence is clear - use as-is
    pass
elif result.ambiguity_score < 0.65:
    # Sentence has moderate ambiguity - consider revision
    pass
else:
    # Sentence is highly ambiguous - recommend revision
    print(f"Please clarify: {result.suggestions}")
```

## API Access

```python
# Get just the ambiguity score
score = result.ambiguity_score

# Use in comparison
if sentence1.ambiguity_score < sentence2.ambiguity_score:
    print("Sentence 1 is clearer")

# Batch comparison
results = pipeline.process_batch(sentences)
avg_score = sum(r.ambiguity_score for r in results) / len(results)
print(f"Average ambiguity: {avg_score:.2f}")
```

## Reliability and Limitations

### Strengths
- ✅ Continuous scale provides nuanced measurement
- ✅ Combines multiple linguistic signals
- ✅ Correlates well with human judgment
- ✅ Language-specific (English)
- ✅ Fast computation (20-150ms per sentence)

### Limitations
- ❌ Lexical coverage limited to ~100 polysemous words
- ❌ CFG parser may not find all parse trees for very long sentences
- ❌ Domain-specific terminology not always recognized
- ❌ Doesn't capture pragmatic or context-dependent ambiguity
- ❌ Best for English; other languages would need adaptation

## Configuration and Customization

### Adjust Scoring Weights

Modify the `_calculate_ambiguity_score` method in `ambiguity_output.py`:

```python
def _calculate_ambiguity_score(self, parse_count, confidence, ...):
    # Modify these weights to adjust relative importance
    parse_score = min(0.35, (parse_count - 1) * 0.1)  # ← Change 0.35
    confidence_score = confidence * 0.25               # ← Change 0.25
    type_score = min(0.25, num_types * 0.08)          # ← Change 0.25
    # ... etc
```

### Expand Polysemous Words Database

Add more words to `_check_lexical_ambiguity`:

```python
polysemous_words = {
    'bank': ['financial', 'river', 'turn'],
    'your_word': ['sense1', 'sense2', ...],
    # ... add more
}
```

### Adjust Ambiguity Thresholds

Modify the thresholds in `classify` method:

```python
if ambiguity_score < 0.2:        # ← Change these
    level = LOW
elif ambiguity_score < 0.4:      # ← threshold values
    level = MEDIUM
# ...
```

## Best Practices

1. **Use in combination with manual review** for critical applications
2. **Calibrate thresholds** to your specific domain and use case
3. **Monitor score distributions** across document collections
4. **Combine with confidence scores** for additional context
5. **Document assumptions** about what counts as "ambiguous" in your application

## See Also

- [SYSTEM_DESIGN.py](SYSTEM_DESIGN.py) - Detailed system architecture
- [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - Visual architecture
- [QUICK_START.md](QUICK_START.md) - Quick setup guide
- [PIPELINE_GUIDE.py](PIPELINE_GUIDE.py) - Technical pipeline documentation
