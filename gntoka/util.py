"""Utility functions."""
from datetime import (
    date,
)
from typing import (
    Iterable,
)

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


def clean_text(txt: str) -> str:
    """Remove or replace characters that Kaikeio does not like."""
    return txt.replace("\xa0", " ")
