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
    AccountInfo,
    AccountSequence,
    Configuration,
    DbContents,
    Split,
    Transaction,
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
    account_info: AccountInfo,
    accounts_to_read: AccountSequence,
    accounts_to_export: AccountSequence,
    db_contents: DbContents,
) -> None:
    """Get all accounts."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        db_contents.account_store[row["guid"]] = Account(
            guid=row["guid"],
            _name=row["name"],
            parent_guid=row["parent_guid"],
            # Set them to empty for now
            account="",
            account_supplementary="",
            account_name="",
            account_supplementary_name="",
        )

    for account in db_contents.account_store.values():
        acc_name = account_name(account, db_contents.account_store)
        if acc_name in account_info.importable_account_names:
            accounts_to_read.append(account)
        if acc_name in account_info.exportable_account_names:
            accounts_to_export.append(account)
        account_additional = account_info.importable_account_links.get(
            acc_name
        )
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


def get_transactions(con: sqlite3.Connection, db_contents: DbContents) -> None:
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        db_contents.transaction_store[row["guid"]] = Transaction(
            guid=row["guid"],
            date=date.fromisoformat(row["post_date"].split(" ")[0]),
            description=row["description"],
        )


def get_splits(
    con: sqlite3.Connection,
    accounts_to_read: AccountSequence,
    db_contents: DbContents,
) -> None:
    """Get all splits."""
    cur = con.cursor()
    cur.execute(select_splits)
    for row in cur.fetchall():
        account = db_contents.account_store[row["account_guid"]]
        split = Split(
            guid=row["guid"],
            account=account,
            transaction=db_contents.transaction_store[row["tx_guid"]],
            memo=row["memo"],
            value=Decimal(row["value_num"]),
        )
        if account in accounts_to_read:
            db_contents.split_store[row["guid"]] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
