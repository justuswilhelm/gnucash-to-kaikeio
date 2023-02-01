"""Test util."""
import pytest
from gntoka import (
    util,
)


def test_clean_text() -> None:
    """Test clean_text."""
    assert util.clean_text("hello\xa0") == "hello "
    assert util.clean_text("ヴ") == "ヴ"


@pytest.mark.parametrize(
    "txt, length",
    [
        ("ｱ" * 30, 30),
        ("A" * 30, 30),
        ("金" * 15, 30),
        ("Ａ" * 15, 30),
    ],
)
def test_length_sjis(txt: str, length: int) -> None:
    """Test lengt_sjis."""
    assert util.length_sjis(txt) == length
