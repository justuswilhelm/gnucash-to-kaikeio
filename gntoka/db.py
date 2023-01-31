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

from .constants import (
    KAIKEIO_NO_ACCOUNT,
)
from .serialize import (
    SplitDict,
    deserialize_transaction,
)
from .types import (
    Account,
    AccountStore,
    Configuration,
    DbContents,
    GnuCashAccount,
    GnuCashAccountStore,
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


def fetch_gnucash_accounts(con: sqlite3.Connection) -> GnuCashAccountStore:
    """Fetch accounts in GnuCash."""
    cur = con.cursor()
    cur.execute(select_accounts)
    return {
        row["guid"]: GnuCashAccount(
            guid=row["guid"],
            code=row["code"],
            name=row["name"],
            parent_name=row["parent_name"],
            parent_code=row["parent_code"],
        )
        for row in cur.fetchall()
    }


def make_linked_account(
    account: GnuCashAccount,
) -> Account:
    """Link GnuCash and Kaikeio information in one account."""
    if account.parent_code:
        name = account.parent_name
        code = account.parent_code
        name_supplementary = account.name
        code_supplementary = account.code
    else:
        name = account.name
        code = account.code
        name_supplementary = ""
        code_supplementary = KAIKEIO_NO_ACCOUNT
    return Account(
        gnucash_account=account,
        account_code=code,
        account_supplementary_code=code_supplementary,
        account_name=name,
        account_supplementary_name=name_supplementary,
    )


def get_accounts(
    con: sqlite3.Connection,
) -> AccountStore:
    """Get all accounts and link them with Kaikeio information."""
    gnucash_account_store = fetch_gnucash_accounts(con)
    account_store = {
        account.guid: make_linked_account(
            account,
        )
        for account in gnucash_account_store.values()
    }
    return account_store


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
        split = Split(
            guid=split_dict["guid"],
            account=account,
            transaction=db_contents.transaction_store[split_dict["tx_guid"]],
            memo=split_dict["memo"],
            value=Decimal(split_dict["value_num"]),
        )
        db_contents.split_store[split.guid] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
