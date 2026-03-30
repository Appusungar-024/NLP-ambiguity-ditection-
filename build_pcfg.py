"""
Build a PCFG from PTB-style constituent files (e.g., GUM `const/*.ptb`).

Usage:
    python3 nlp_project/build_pcfg.py --gum-dir nlp_project/gum --out nlp_project/gum.pcfg --max-files 200

This script reads bracketed trees, collects productions, induces a PCFG
(using NLTK's `induce_pcfg`) and writes the grammar to a file.
"""
from pathlib import Path
import argparse
from collections import Counter

from nltk import Nonterminal, induce_pcfg
from ldc_loader import iter_trees_from_mrg


def collect_productions_from_const(gum_dir: str, max_files: int | None = None, max_trees: int | None = None):
    p = Path(gum_dir) / 'const'
    files = sorted(p.glob('*.ptb'))
    prod_list = []
    trees_seen = 0
    files_seen = 0
    for f in files:
        files_seen += 1
        for tree in iter_trees_from_mrg(str(f)):
            try:
                prods = tree.productions()
            except Exception:
                continue
            prod_list.extend(prods)
            trees_seen += 1
            if max_trees and trees_seen >= max_trees:
                return prod_list, files_seen, trees_seen
        if max_files and files_seen >= max_files:
            break
    return prod_list, files_seen, trees_seen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gum-dir', default='nlp_project/gum', help='GUM root directory in project')
    parser.add_argument('--out', default='nlp_project/gum.pcfg', help='Output grammar file')
    parser.add_argument('--max-files', type=int, default=None, help='Max number of files to read')
    parser.add_argument('--max-trees', type=int, default=None, help='Max number of trees to read')
    args = parser.parse_args()

    print('Collecting productions from', args.gum_dir)
    prods, files_seen, trees_seen = collect_productions_from_const(args.gum_dir, args.max_files, args.max_trees)
    print(f'Files scanned: {files_seen}, Trees collected: {trees_seen}, Productions: {len(prods)}')

    if not prods:
        print('No productions found; check that the `const` directory contains PTB files.')
        return

    # Choose start symbol as 'S' by default if present, otherwise the LHS of first production
    start = Nonterminal('S')
    lhs_counts = Counter(p.lhs() for p in prods)
    if start not in lhs_counts:
        # fallback
        start = prods[0].lhs()
    print('Using start symbol:', start)

    grammar = induce_pcfg(start, prods)

    out_path = Path(args.out)
    out_path.write_text(str(grammar), encoding='utf-8')
    print('PCFG written to', out_path)

    # also write a pickled copy for robust re-loading
    try:
        import pickle
        pkl_path = out_path.with_suffix(out_path.suffix + '.pickle')
        pkl_path.write_bytes(pickle.dumps(grammar))
        print('Pickled PCFG written to', pkl_path)
    except Exception as e:
        print('Warning: could not write pickled PCFG:', e)


if __name__ == '__main__':
    main()
