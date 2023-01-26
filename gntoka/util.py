"""Utility functions."""
from datetime import (
    date,
)
from typing import (
    Iterable,
)

from .types import (
    Account,
    AccountStore,
    Split,
)


def account_name(account: Account, accounts: AccountStore) -> str:
    """Return full name."""
    if not account.parent_guid:
        return account._name
    parent_name = account_name(accounts[account.parent_guid], accounts)
    if parent_name == "Root Account":
        return account._name
    return parent_name + ":" + account._name


def format_date(d: date) -> str:
    """Format date."""
    return d.strftime("%Y/%m/%d")


def get_debits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all debits from a split."""
    return filter(lambda split: split.value > 0, splits)


def get_credits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all credits from a split."""
    return filter(lambda split: split.value < 0, splits)
