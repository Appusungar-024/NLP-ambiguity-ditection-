"""
Compute ambiguity statistics per GUM genre using the induced PCFG parser.

Outputs:
- nlp_project/ambiguity_stats.csv
- nlp_project/ambiguity_examples.json (sample ambiguous sentences per genre)

Usage:
    python3 nlp_project/compute_ambiguity_stats.py --gum-dir nlp_project/gum --pcfg nlp_project/gum.pcfg.pickle --max-per-genre 200
"""
from pathlib import Path
import argparse
import csv
import json
from collections import defaultdict

# allow importing project modules when script is run directly
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import parsing_ambiguity as pa
from ldc_loader import iter_trees_from_mrg


def genre_from_filename(name: str) -> str:
    # filenames are like GUM_conversation_artist.ptb -> genre "conversation"
    base = Path(name).stem
    parts = base.split('_')
    if len(parts) >= 2 and parts[0] == 'GUM':
        return parts[1]
    # fallback
    return base


def iterate_genre_sentences(gum_dir: str, genre: str, max_sentences=None):
    p = Path(gum_dir) / 'const'
    files = sorted(p.glob(f'GUM_{genre}_*.ptb'))
    count = 0
    for f in files:
        for tree in iter_trees_from_mrg(str(f)):
            if hasattr(tree, 'leaves'):
                sent = ' '.join(tree.leaves())
            else:
                sent = str(tree)
            yield str(f.name), sent
            count += 1
            if max_sentences and count >= max_sentences:
                return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gum-dir', default='nlp_project/gum')
    parser.add_argument('--pcfg', default='nlp_project/gum.pcfg.pickle')
    parser.add_argument('--max-per-genre', type=int, default=500, help='Max sentences per genre')
    parser.add_argument('--topk', type=int, default=3)
    args = parser.parse_args()

    ok, info = pa.load_pcfg_and_set_parser(args.pcfg)
    if not ok:
        print('Could not load PCFG:', info)
        return

    const_dir = Path(args.gum_dir) / 'const'
    # gather genres from const filenames
    genres = set()
    for p in const_dir.glob('GUM_*.ptb'):
        stem = p.stem
        parts = stem.split('_')
        if len(parts) >= 2:
            genres.add(parts[1])
    genres = sorted(genres)

    stats = []
    examples = defaultdict(list)

    for genre in genres:
        total = parsed_single = ambiguous = unparsable = 0
        for fname, sent in iterate_genre_sentences(args.gum_dir, genre, max_sentences=args.max_per_genre):
            total += 1
            # Fast pass: use the ChartParser (non-probabilistic) to detect >1 parses quickly
            try:
                tokens, trees = pa.detect_ambiguity(sent, pa.parser, probabilistic=False, topk=args.topk)
            except Exception:
                tokens, trees = [], []
            n = len(trees)
            if n == 0:
                unparsable += 1
            elif n == 1:
                parsed_single += 1
            else:
                ambiguous += 1
                # For ambiguous sentences, compute probabilistic top parses (slower, but only for examples)
                if len(examples[genre]) < 5:
                    try:
                        _, ptrees = pa.detect_ambiguity(sent, None, probabilistic=True, topk=args.topk)
                    except Exception:
                        ptrees = trees[:args.topk]
                    # compute top parse probabilities when possible (use log-prob for stability)
                    best_log = None
                    second_log = None
                    probs_info = None
                    try:
                        import math
                        logps = []
                        for t in ptrees:
                            lp = pa.compute_tree_logprob(t)
                            logps.append(lp)
                        # filter out None
                        logps_valid = [lp for lp in logps if lp is not None]
                        logps_valid.sort(reverse=True)
                        if logps_valid:
                            best_log = logps_valid[0]
                        if len(logps_valid) >= 2:
                            second_log = logps_valid[1]
                        if best_log is not None:
                            best_prob = math.exp(best_log)
                        else:
                            best_prob = None
                        if best_log is not None and second_log is not None:
                            ratio = math.exp(second_log - best_log)
                        else:
                            ratio = None
                        probs_info = {
                            'best_logprob': best_log,
                            'best_prob': best_prob,
                            'second_logprob': second_log,
                            'top2_ratio': ratio
                        }
                    except Exception:
                        probs_info = None

                    entry = {
                        'file': fname,
                        'sentence': sent,
                        'tokens': tokens,
                        'parses': min(n, args.topk),
                        'prob_parses_count': len(ptrees),
                    }
                    if probs_info:
                        entry.update(probs_info)
                    examples[genre].append(entry)

        stats.append({
            'genre': genre,
            'total': total,
            'parsed_single': parsed_single,
            'ambiguous': ambiguous,
            'unparsable': unparsable,
            'ambiguous_rate': ambiguous / total if total else 0.0
        })
        print(f'Genre {genre}: total={total}, parsed_single={parsed_single}, ambiguous={ambiguous}, unparsable={unparsable}')

    out_csv = Path(__file__).resolve().parent / 'ambiguity_stats.csv'
    with open(out_csv, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['genre','total','parsed_single','ambiguous','unparsable','ambiguous_rate'])
        writer.writeheader()
        for r in stats:
            writer.writerow(r)

    out_examples = Path(__file__).resolve().parent / 'ambiguity_examples.json'
    with open(out_examples, 'w', encoding='utf-8') as fh:
        json.dump(examples, fh, indent=2)

    print('Wrote', out_csv)
    print('Wrote', out_examples)


if __name__ == '__main__':
    main()
