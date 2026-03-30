"""
Parsing Ambiguity Detection — minimal demo using NLTK ChartParser

Run:
    pip install -r requirements.txt
    python3 parsing_ambiguity.py

This script shows how to detect ambiguous parses (multiple parse trees)
for sentences given a context-free grammar.
"""
from nltk import CFG, ChartParser
import argparse

# optional import: the loader is provided in the project and will be used when available
try:
    from ldc_loader import get_sentences_from_ldc
except Exception:  # if not available (e.g., user hasn't downloaded dataset), keep None
    get_sentences_from_ldc = None

GRAMMAR = CFG.fromstring(r"""
S -> NP VP
VP -> V NP | VP PP
NP -> Det N | NP PP | 'i'
PP -> P NP
Det -> 'the' | 'a'
N -> 'man' | 'telescope' | 'park' | 'dog'
V -> 'saw' | 'chased'
P -> 'with' | 'in'
""")

parser = ChartParser(GRAMMAR)

# For probabilistic parsing we lazily construct a Viterbi parser if a PCFG is loaded
_viterbi_parser = None
_prob_parser = None
_pcfg_grammar = None
_prod_prob_map = None

def load_pcfg_and_set_parser(pcfg_path: str):
    """Load a PCFG from `pcfg_path` and set parsers for probabilistic parsing.

    Creates both a Viterbi parser and an Inside-Chart (probabilistic chart) parser
    so we can obtain n-best parses and probabilities.
    """
    global _viterbi_parser, _prob_parser
    try:
        import pickle
        # if user passed a pickle file, load it directly
        if pcfg_path.endswith('.pickle') or pcfg_path.endswith('.pkl'):
            grammar = pickle.loads(open(pcfg_path, 'rb').read())
            from nltk.parse import ViterbiParser
            from nltk.parse.pchart import InsideChartParser
            _viterbi_parser = ViterbiParser(grammar)
            _prob_parser = InsideChartParser(grammar)
            return True, grammar
        # else try to find companion .pickle file first
        p = Path(pcfg_path)
        pkl_candidate = p.with_suffix(p.suffix + '.pickle')
        if pkl_candidate.exists():
            grammar = pickle.loads(pkl_candidate.read_bytes())
            from nltk.parse import ViterbiParser
            from nltk.parse.pchart import InsideChartParser
            _viterbi_parser = ViterbiParser(grammar)
            _prob_parser = InsideChartParser(grammar)
            return True, grammar

        from nltk import PCFG
        from nltk.parse import ViterbiParser
        from nltk.parse.pchart import InsideChartParser
        text = open(pcfg_path, encoding='utf-8').read()
        # filter out header lines like 'Grammar with ...' and keep only production lines
        lines = [l.strip() for l in text.splitlines() if '->' in l]
        grammar_text = '\n'.join(lines)
        grammar = PCFG.fromstring(grammar_text)
        _viterbi_parser = ViterbiParser(grammar)
        _prob_parser = InsideChartParser(grammar)
        # build production -> prob map using (lhs, rhs_tuple) keys for robust matching
        global _pcfg_grammar, _prod_prob_map
        _pcfg_grammar = grammar
        _prod_prob_map = {}
        for p in grammar.productions():
            lhs = str(p.lhs())
            rhs = tuple(str(s) for s in p.rhs())
            _prod_prob_map[(lhs, rhs)] = getattr(p, 'prob', lambda: None)()
        return True, grammar
    except Exception as e:
        return False, str(e)

EXAMPLES = [
    "i saw the man with the telescope",
    "i saw the man in the park",
    "i saw a dog with the telescope"
]


from nltk.tokenize import word_tokenize
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
except Exception:
    pass

def simple_tokenize(sentence):
    # Use NLTK word_tokenize to properly handle punctuation and words
    try:
        tokens = word_tokenize(sentence)
    except Exception:
        # Fallback to simple split if word_tokenize fails
        import re
        tokens = re.findall(r"\b\w+\b|[^\w\s]", sentence)
    return [word.lower() for word in tokens]


import math

def detect_ambiguity(sentence, parser, probabilistic=False, topk=5):
    tokens = simple_tokenize(sentence)
    try:
        if probabilistic and _prob_parser is not None:
            # use probabilistic inside-chart parser to enumerate parses with probabilities
            parses = list(_prob_parser.parse(tokens))
            # sort by probability descending if prob available
            try:
                parses.sort(key=lambda t: getattr(t, 'prob', lambda: 0)(), reverse=True)
            except Exception:
                pass
            trees = parses[:topk]
        elif probabilistic and _viterbi_parser is not None:
            parses = list(_viterbi_parser.parse(tokens))
            trees = parses[:topk]
        else:
            trees = list(parser.parse(tokens))
    except ValueError:
        # grammar doesn't cover some tokens (out-of-vocabulary); treat as unparsable
        trees = []
    except Exception:
        trees = []
    return tokens, trees


def compute_tree_logprob(tree):
    """Return the log-probability of `tree` under the loaded PCFG (sum of log rule probs), or None if not available."""
    if _prod_prob_map is None:
        return None
    logp = 0.0
    for pr in tree.productions():
        key = (str(pr.lhs()), tuple(str(s) for s in pr.rhs()))
        pval = _prod_prob_map.get(key)
        if pval is None:
            return None
        if pval <= 0:
            return None
        logp += math.log(pval)
    return logp


def run_on_sentences(sent_iter, parser, max_sentences=None, only_ambiguous=False, show_trees=False, skip_unparsable=True, probabilistic=False, topk=5):
    """Run ambiguity detection on an iterator of sentence strings."""
    nk = 0
    for sent in sent_iter:
        if max_sentences and nk >= max_sentences:
            break
        nk += 1
        tokens, trees = detect_ambiguity(sent, parser, probabilistic=probabilistic, topk=topk)
        nparses = len(trees)
        if nparses == 0 and skip_unparsable:
            continue
        if only_ambiguous and nparses <= 1:
            continue
        print(f"Sentence {nk}: {sent}")
        print(f"Tokens: {tokens}")
        print(f"Number of parses: {nparses}")
        if nparses > 1:
            print("This sentence is ambiguous (multiple valid parses).")
            if show_trees:
                print(f"Showing up to first {topk} parse trees (probabilities shown if PCFG mode):")
                for i, t in enumerate(trees[:topk], 1):
                    print(f"--- Parse {i} ---")
                    # compute probability using the loaded PCFG production probability map if available
                    try:
                        logp = compute_tree_logprob(t)
                        if logp is not None:
                            prob = math.exp(logp)
                            print(f"Log-prob: {logp:.6g}")
                            # print prob in scientific if very small
                            print(f"Prob: {prob:.6g}")
                        else:
                            print("No reliable probability (missing production probs)")
                    except Exception:
                        pass
                    print(t)
        elif nparses == 1:
            print("No ambiguity detected (single parse).")
            if show_trees:
                print("Parse:")
                print(trees[0])
        else:
            print("No valid parses under current grammar.")
        print('\n' + '=' * 60 + '\n')


def main():
    parser_arg = argparse.ArgumentParser(description='Parsing ambiguity demo and LDC reader integration')
    parser_arg.add_argument('--ldc-dir', help='Path to LDC dataset directory (download separately).')
    parser_arg.add_argument('--pcfg', help='Path to a PCFG grammar file; if provided the script will use probabilistic parsing')
    parser_arg.add_argument('--max', type=int, default=50, help='Max sentences to process (default: 50)')
    parser_arg.add_argument('--only-ambiguous', action='store_true', help='Only display ambiguous sentences')
    parser_arg.add_argument('--show-trees', action='store_true', help='Display parse trees for ambiguous sentences')
    parser_arg.add_argument('--topk', type=int, default=5, help='Number of top parses to consider for probabilistic parsing')
    parser_arg.add_argument('--skip-unparsable', action='store_true', help='Skip sentences that get zero parses under the grammar')
    args = parser_arg.parse_args()

    print("Grammar:")
    print(GRAMMAR)
    print('\nRunning ambiguity detection...\n')

    if args.pcfg:
        ok, info = load_pcfg_and_set_parser(args.pcfg)
        if not ok:
            print('Failed to load PCFG:', info)
            return
        probabilistic = True
    else:
        probabilistic = False

    if args.ldc_dir:
        if get_sentences_from_ldc is None:
            print('LDC loader is not available or you have not downloaded the dataset. See README for instructions.')
            return
        from pathlib import Path
        data_path = Path(args.ldc_dir)
        if not data_path.exists():
            print(f"Data directory not found: {args.ldc_dir}")
            print("Please download the dataset from https://catalog.ldc.upenn.edu/LDC99T42 and extract it to this path, or provide the correct path to your local copy.")
            print("You can test the loader with: python3 nlp_project/ldc_loader.py <your-path> --max 10")
            return
        try:
            sent_iter = get_sentences_from_ldc(args.ldc_dir, max_sentences=None)
        except FileNotFoundError as e:
            print(e)
            print('See README for instructions on how to obtain LDC datasets.')
            return
        run_on_sentences(sent_iter, parser, max_sentences=args.max, only_ambiguous=args.only_ambiguous, show_trees=args.show_trees, skip_unparsable=args.skip_unparsable)
    else:
        # default: run on built-in examples
        run_on_sentences(EXAMPLES, parser, max_sentences=args.max, only_ambiguous=args.only_ambiguous, show_trees=args.show_trees, skip_unparsable=args.skip_unparsable)


if __name__ == '__main__':
    main()
