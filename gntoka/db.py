"""DB access functions."""
import sqlite3
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from pathlib import (
    Path,
)
from typing import (
    Mapping,
    Sequence,
    cast,
)

from .serialize import (
    SplitDict,
    deserialize_account,
    deserialize_transaction,
)
from .types import (
    AccountStore,
    Configuration,
    DbContents,
    Split,
    TransactionStore,
)


# Not exactly side effect free
# TODO decide if that is an issue
SQL_PATH = Path("gntoka/sql")
select_accounts = (SQL_PATH / "select_accounts.sql").read_text()
select_transactions = (SQL_PATH / "select_transactions.sql").read_text()
select_splits = (SQL_PATH / "select_splits.sql").read_text()


def dict_factory(
    cursor: sqlite3.Cursor,
    row: Sequence[str],
) -> Mapping[str, str]:
    """Package a cursor row in a dict."""
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def get_accounts(
    con: sqlite3.Connection,
) -> AccountStore:
    """Get all accounts and link them with Kaikeio information."""
    cur = con.cursor()
    cur.execute(select_accounts)
    accounts = (deserialize_account(r) for r in cur.fetchall())
    return {account.guid: account for account in accounts}


def get_transactions(
    con: sqlite3.Connection,
    start_date: date,
    end_date: date,
) -> TransactionStore:
    """Get all transactions."""
    cur = con.cursor()
    query = {
        "start_date": start_date,
        "end_date": end_date,
    }
    cur.execute(select_transactions, query)
    return {
        tx.guid: tx
        for tx in (deserialize_transaction(row) for row in cur.fetchall())
    }


def get_splits(
    con: sqlite3.Connection,
    db_contents: DbContents,
) -> None:
    """Get all splits."""
    cur = con.cursor()
    cur.execute(select_splits)
    for row in cur.fetchall():
        split_dict = cast(SplitDict, row)
        account = db_contents.account_store.get(split_dict["account_guid"])
        if account is None:
            raise ValueError(
                f"Expected to find account for {split_dict} with account_guid "
                f"{split_dict['account_guid']} among the imported GnuCash "
                "accounts"
            )
        transaction = db_contents.transaction_store.get(split_dict["tx_guid"])
        if transaction is None:
            continue
        split = Split(
            guid=split_dict["guid"],
            account=account,
            transaction=transaction,
            memo=split_dict["memo"],
            value=Decimal(split_dict["value_num"]),
        )
        db_contents.split_store[split.guid] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
