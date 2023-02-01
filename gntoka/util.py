"""Utility functions."""
from datetime import (
    date,
)
from typing import (
    Iterable,
    Optional,
)

import mojimoji

from .types import (
    Split,
)


def format_date(d: date) -> str:
    """Format date."""
    return d.strftime("%Y/%m/%d")


def get_debits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all debits from a split."""
    return filter(lambda split: split.value > 0, splits)


def get_credits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all credits from a split."""
    return filter(lambda split: split.value < 0, splits)


def clean_text(txt: Optional[str]) -> Optional[str]:
    """Remove or replace characters that Kaikeio does not like."""
    if not txt:
        return None
    tr = str.maketrans(
        {
            "\xa0": " ",
            "　": " ",
        },
    )
    replaced = txt.translate(tr)
    # Ensure we can still get this to shift-jis
    replaced = mojimoji.zen_to_han(replaced)
    assert replaced.encode("shift-jis")
    return replaced


def length_sjis(txt: str) -> int:
    """Validate the length of a string when converted to Shift_JIS."""
    return len(txt.encode("shift-jis"))
