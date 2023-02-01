"""Test util."""
from gntoka import (
    util,
)


def test_clean_text() -> None:
    """Test clean_text."""
    assert util.clean_text("hello\xa0") == "hello "
    assert util.clean_text("ヴ") == "ヴ"
