"""Utility functions."""
from .types import (
    Account,
    AccountStore,
)


def account_name(account: Account, accounts: AccountStore) -> str:
    """Return full name."""
    if not account.parent_guid:
        return account._name
    parent_name = account_name(accounts[account.parent_guid], accounts)
    if parent_name == "Root Account":
        return account._name
    return parent_name + ":" + account._name
