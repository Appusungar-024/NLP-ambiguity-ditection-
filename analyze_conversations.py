"""
Analyze GUM conversation subset for parseability and ambiguity using the demo CFG.

Usage:
    python3 nlp_project/analyze_conversations.py --max 200 --show-examples 10

This script prints summary stats and up to N example ambiguous sentences.
"""
from pathlib import Path
from collections import Counter
import argparse
import sys

# make local `nlp_project` modules importable when running this script directly
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from ldc_loader import iter_trees_from_mrg
import parsing_ambiguity as pa


def iterate_conversation_sentences(gum_dir: str, max_sentences=None):
    p = Path(gum_dir) / 'const'
    files = sorted(p.glob('GUM_conversation_*.ptb'))
    count = 0
    for f in files:
        for tree in iter_trees_from_mrg(str(f)):
            if hasattr(tree, 'leaves'):
                sent = ' '.join(tree.leaves())
            else:
                sent = str(tree)
            yield sent
            count += 1
            if max_sentences and count >= max_sentences:
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gum-dir', default='nlp_project/gum', help='Path to GUM dataset in project')
    parser.add_argument('--max', type=int, default=500, help='Max sentences to process')
    parser.add_argument('--show-examples', type=int, default=10, help='How many ambiguous examples to show')
    args = parser.parse_args()

    sent_iter = iterate_conversation_sentences(args.gum_dir, max_sentences=args.max)

    stats = Counter()
    ambiguous_examples = []

    for i, sent in enumerate(sent_iter, 1):
        tokens, trees = pa.detect_ambiguity(sent, pa.parser)
        nparses = len(trees)
        stats['total'] += 1
        if nparses == 0:
            stats['unparsable'] += 1
        elif nparses == 1:
            stats['parsed_single'] += 1
        else:
            stats['ambiguous'] += 1
            if len(ambiguous_examples) < args.show_examples:
                ambiguous_examples.append((sent, tokens, nparses, trees[:3]))

    print('GUM conversation subset analysis')
    print('Processed sentences:', stats['total'])
    print('Unparsable under demo grammar:', stats.get('unparsable', 0))
    print('Parsed (single parse):', stats.get('parsed_single', 0))
    print('Ambiguous (>1 parse):', stats.get('ambiguous', 0))
    print('\nExamples of ambiguous sentences (up to first {})'.format(args.show_examples))
    for sent, tokens, nparses, trees in ambiguous_examples:
        print('\nSentence:', sent)
        print('Tokens:', tokens)
        print('Parses:', nparses)
        for i, t in enumerate(trees, 1):
            print('--- Parse', i, '---')
            print(t)


if __name__ == '__main__':
    main()
