"""DB access functions."""
import sqlite3
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from typing import (
    Dict,
    Sequence,
)

from .types import (
    Account,
    AccountLinks,
    AccountNames,
    AccountSequence,
    AccountStore,
    Configuration,
    Split,
    SplitStore,
    Transaction,
    TransactionStore,
)
from .util import (
    account_name,
)


select_accounts = """
SELECT * FROM accounts
"""

select_transactions = """
SELECT * FROM transactions
"""

select_splits = """
SELECT * FROM splits
"""


def dict_factory(cursor: sqlite3.Cursor, row: Sequence[str]) -> Dict[str, str]:
    """Package a cursor row in a dict."""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_accounts(
    con: sqlite3.Connection,
    accounts_to_read: AccountSequence,
    importable_account_names: AccountNames,
    accounts_to_export: AccountSequence,
    exportable_account_names: AccountNames,
    importable_account_links: AccountLinks,
    account_store: AccountStore,
) -> None:
    """Get all accounts."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        account_store[row["guid"]] = Account(
            guid=row["guid"],
            _name=row["name"],
            parent_guid=row["parent_guid"],
            # Set them to empty for now
            account="",
            account_supplementary="",
            account_name="",
            account_supplementary_name="",
        )

    for account in account_store.values():
        acc_name = account_name(account, account_store)
        if acc_name in importable_account_names:
            accounts_to_read.append(account)
        if acc_name in exportable_account_names:
            accounts_to_export.append(account)
        account_additional = importable_account_links.get(acc_name)
        if not account_additional:
            continue
        account.account = account_additional.account
        account.account_supplementary = (
            account_additional.account_supplementary
        )
        account.account_name = account_additional.account_name
        account.account_supplementary_name = (
            account_additional.account_supplementary_name
        )


def get_transactions(
    con: sqlite3.Connection, transaction_store: TransactionStore
) -> None:
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        transaction_store[row["guid"]] = Transaction(
            guid=row["guid"],
            date=date.fromisoformat(row["post_date"].split(" ")[0]),
            description=row["description"],
        )


def get_splits(
    con: sqlite3.Connection,
    accounts_to_read: AccountSequence,
    account_store: AccountStore,
    transaction_store: TransactionStore,
    split_store: SplitStore,
) -> None:
    """Get all splits."""
    cur = con.cursor()
    cur.execute(select_splits)
    for row in cur.fetchall():
        account = account_store[row["account_guid"]]
        split = Split(
            guid=row["guid"],
            account=account,
            transaction=transaction_store[row["tx_guid"]],
            memo=row["memo"],
            value=Decimal(row["value_num"]),
        )
        if account in accounts_to_read:
            split_store[row["guid"]] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
