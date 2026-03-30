import os
from pathlib import Path
import textwrap

import pytest

from nlp_project import ldc_loader


def test_balanced_parentheses_blocks_multiline():
    # two trees, one spans multiple lines
    text = """
    (S
      (NP (NNP John))
      (VP (VBD saw) (NP (NNP Mary)))) (S (NP (NNP Alice)) (VP (VBD left)))
    """
    blocks = list(ldc_loader._balanced_parentheses_blocks(text))
    assert len(blocks) == 2
    assert blocks[0].startswith("(S")
    assert "John" in blocks[0]
    assert "Alice" in blocks[1]


def test_iter_sentences_from_text(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("\nHello world\n\nThis is a test\n")
    out = list(ldc_loader.iter_sentences_from_text(str(p)))
    assert out == ["Hello world", "This is a test"]


def test_iter_trees_from_mrg_returns_raw_blocks_when_tree_missing(tmp_path, monkeypatch):
    # ensure behavior when nltk.Tree is not available: yields raw text blocks
    monkeypatch.setattr(ldc_loader, "Tree", None)
    p = tmp_path / "test.mrg"
    p.write_text(textwrap.dedent("""
    (S (NP (NNP John))
       (VP (VBD saw) (NP (NNP Mary))))
    (S (NP (NNP Alice)) (VP (VBD left)))
    """))
    blocks = list(ldc_loader.iter_trees_from_mrg(str(p)))
    assert len(blocks) == 2
    assert blocks[0].strip().startswith("(S")
    assert "John" in blocks[0]


def test_get_sentences_from_ldc_with_mrg_and_txt(tmp_path):
    # create a small dataset dir with one .mrg and one .txt
    data_dir = tmp_path / "LDCTEST"
    data_dir.mkdir()
    mrg = data_dir / "a.mrg"
    mrg.write_text("(S (NP (NNP John)) (VP (VBD saw) (NP (NNP Mary))))\n")
    txt = data_dir / "lines.txt"
    txt.write_text("Hello world\n\nAnother line\n")

    # Use the real Tree if available; if not, we expect raw blocks from .mrg
    sents = list(ldc_loader.get_sentences_from_ldc(str(data_dir)))
    # must contain the lines from txt
    assert "Hello world" in sents
    assert "Another line" in sents

    # check that max_sentences truncates
    sents2 = list(ldc_loader.get_sentences_from_ldc(str(data_dir), max_sentences=1))
    assert len(sents2) == 1


@pytest.mark.parametrize("tree_text,expected_leaves", [
    ("(S (NP (NNP John)) (VP (VBD saw) (NP (NNP Mary))))", ["John", "saw", "Mary"]),
    ("(S (NP (DT The) (NN dog)) (VP (VBD barked)))", ["The", "dog", "barked"]),
])
def test_iter_trees_from_mrg_parses_to_tree_when_nltk_available(tmp_path, tree_text, expected_leaves):
    # This test requires nltk.Tree to be present; skip if not
    if getattr(ldc_loader, "Tree", None) is None:
        pytest.skip("nltk.Tree not available in this environment")
    p = tmp_path / "one.mrg"
    p.write_text(tree_text)
    trees = list(ldc_loader.iter_trees_from_mrg(str(p)))
    assert len(trees) == 1
    t = trees[0]
    assert hasattr(t, "leaves")
    leaves = t.leaves()
    # ensure expected leaves are subset of leaves (case differences possible)
    assert all(any(e == l or e.lower() == l.lower() for l in leaves) for e in expected_leaves)
