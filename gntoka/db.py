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
    AccountSequence,
    AccountStore,
    Configuration,
    NamesToRead,
    Split,
    SplitStore,
    Transaction,
    TransactionStore,
    WhatIsThis,
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
    accounts_to_read_names: NamesToRead,
    accounts_to_export: AccountSequence,
    accounts_to_export_names: NamesToRead,
    accounts_to_read_struct: WhatIsThis,
    accounts: AccountStore,
) -> None:
    """Get all accounts."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        accounts[row["guid"]] = Account(
            guid=row["guid"],
            _name=row["name"],
            parent_guid=row["parent_guid"],
            # Set them to empty for now
            account="",
            account_supplementary="",
            account_name="",
            account_supplementary_name="",
        )

    for account in accounts.values():
        acc_name = account_name(account, accounts)
        if acc_name in accounts_to_read_names:
            accounts_to_read.append(account)
        if acc_name in accounts_to_export_names:
            accounts_to_export.append(account)
        account_additional = accounts_to_read_struct.get(acc_name)
        if not account_additional:
            continue
        account.account = account_additional["account"]
        account.account_supplementary = account_additional[
            "account_supplementary"
        ]
        account.account_name = account_additional["account_name"]
        account.account_supplementary_name = account_additional[
            "account_supplementary_name"
        ]


def get_transactions(
    con: sqlite3.Connection, transactions: TransactionStore
) -> None:
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        transactions[row["guid"]] = Transaction(
            guid=row["guid"],
            date=date.fromisoformat(row["post_date"].split(" ")[0]),
            description=row["description"],
        )


def get_splits(
    con: sqlite3.Connection,
    accounts_to_read: AccountSequence,
    accounts: AccountStore,
    transactions: TransactionStore,
    splits: SplitStore,
) -> None:
    """Get all splits."""
    cur = con.cursor()
    cur.execute(select_splits)
    for row in cur.fetchall():
        account = accounts[row["account_guid"]]
        split = Split(
            guid=row["guid"],
            account=account,
            transaction=transactions[row["tx_guid"]],
            memo=row["memo"],
            value=Decimal(row["value_num"]),
        )
        if account in accounts_to_read:
            splits[row["guid"]] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
