from __future__ import annotations

from netops.domain.validation import normalize_multiline_text


def test_normalize_multiline_text_preserves_internal_newlines_and_spacing():
    value = "  First line\n  indented line\nFinal line  "

    assert normalize_multiline_text(value) == "First line\n  indented line\nFinal line"


def test_normalize_multiline_text_allows_long_pasted_text():
    value = "A" * 2100 + "\n" + "B" * 2100

    assert normalize_multiline_text(value) == value
