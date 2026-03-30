"""
LDC dataset loader helpers

This module provides simple utilities to load sentences from an LDC dataset
directory (e.g., LDC99T42) after you download it from the LDC catalog.

Important: LDC data is licensed; this script does NOT download any files.
Put the extracted dataset under `nlp_project/data/LDC99T42/` (or another path)
and call `get_sentences_from_ldc(path)` to iterate sentences.

Functions:
- iter_trees_from_mrg(file): yields nltk.Tree objects from a .mrg file
- get_sentences_from_ldc(data_dir): yields sentence strings (tokenized) from dataset

Usage example:
    from ldc_loader import get_sentences_from_ldc
    for sent in get_sentences_from_ldc('nlp_project/data/LDC99T42'):
        print(sent)

"""
from pathlib import Path
from typing import Iterator, List, Optional
import re

try:
    from nltk import Tree
except Exception:  # pragma: no cover - fallback if nltk isn't installed
    Tree = None


def _balanced_parentheses_blocks(text: str) -> Iterator[str]:
    """Yield top-level parenthesized blocks from text (handles multi-line trees).
    Accumulates characters until parentheses balance back to zero.
    """
    buf = []
    depth = 0
    for ch in text:
        buf.append(ch)
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                yield ''.join(buf).strip()
                buf = []
    # yield leftover if any
    if buf:
        s = ''.join(buf).strip()
        if s:
            yield s


def iter_trees_from_mrg(file_path: str) -> Iterator['Tree']:
    """Iterate over bracketed trees in a .mrg/treebank file.

    This attempts to be robust when trees span multiple lines.
    Requires NLTK `Tree` to be available; yields raw text blocks otherwise.
    """
    p = Path(file_path)
    if not p.exists():
        return
    text = p.read_text(encoding='utf-8', errors='ignore')
    for block in _balanced_parentheses_blocks(text):
        if Tree is not None:
            try:
                yield Tree.fromstring(block)
            except Exception:
                # If parsing fails, skip this block
                continue
        else:
            yield block


def iter_sentences_from_text(file_path: str) -> Iterator[str]:
    """Yield sentences (one per line or naive split) from a plain text file."""
    p = Path(file_path)
    if not p.exists():
        return
    for line in p.read_text(encoding='utf-8', errors='ignore').splitlines():
        s = line.strip()
        if not s:
            continue
        yield s


def get_sentences_from_ldc(data_dir: str, max_sentences: Optional[int] = None) -> Iterator[str]:
    """Recursively scan `data_dir` and yield sentence strings.

    - For `.mrg` files: extract leaves from bracketed trees and join with spaces.
    - For `.txt` files: yield non-empty lines.

    Note: This is a lightweight helper. Modify to match the specific LDC dataset
    file layout (some LDC releases use other formats).
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    count = 0
    for p in data_path.rglob('*'):
        # treat PTB files like MRG treebank files (bracketed trees)
        if p.suffix.lower() in {'.mrg', '.mrp', '.ptb'}:
            for tree in iter_trees_from_mrg(str(p)):
                if Tree is not None and hasattr(tree, 'leaves'):
                    leaves = tree.leaves()
                    sent = ' '.join(leaves)
                    yield sent
                    count += 1
                else:
                    # if Tree unavailable, yield raw block
                    yield str(tree)
                    count += 1
                if max_sentences and count >= max_sentences:
                    return
        elif p.suffix.lower() in {'.txt', '.text'}:
            for s in iter_sentences_from_text(str(p)):
                yield s
                count += 1
                if max_sentences and count >= max_sentences:
                    return
        else:
            # skip other file types by default
            continue


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Simple LDC dataset sentence iterator (local only).')
    parser.add_argument('data_dir', help='Path to downloaded LDC dataset directory')
    parser.add_argument('--max', type=int, default=20, help='Max sentences to print')
    args = parser.parse_args()

    try:
        for i, sent in enumerate(get_sentences_from_ldc(args.data_dir, max_sentences=args.max), 1):
            print(f"{i}: {sent}")
    except FileNotFoundError as e:
        print(e)
        print('\nNote: LDC data must be downloaded manually from the LDC catalog and placed in the given path.')
