"""DB access functions."""
import sqlite3
from decimal import (
    Decimal,
)
from pathlib import (
    Path,
)
from typing import (
    Mapping,
    Optional,
    Sequence,
    cast,
)

from .serialize import (
    SplitDict,
    deserialize_transaction,
)
from .types import (
    Account,
    Configuration,
    DbContents,
    GnuCashAccount,
    GnuCashAccountStore,
    Split,
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


def fetch_gnucash_accounts(
    con: sqlite3.Connection, db_contents: DbContents
) -> None:
    """Fetch accounts in GnuCash."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        db_contents.gnucash_account_store[row["guid"]] = GnuCashAccount(
            guid=row["guid"],
            code=row["code"],
            _name=row["name"],
            parent_guid=row["parent_guid"],
        )


def make_linked_account(
    account: GnuCashAccount,
    parent: Optional[GnuCashAccount],
) -> Account:
    """Link GnuCash and Kaikeio information in one account."""
    if parent and parent.code:
        name = parent._name
        code = parent.code
        name_supplementary = account._name
        code_supplementary = account.code
    else:
        name = account._name
        code = account.code
        name_supplementary = ""
        code_supplementary = ""
    return Account(
        guid=account.guid,
        code=account.code,
        _name=account._name,
        parent_guid=account.parent_guid,
        account=code,
        account_supplementary=code_supplementary,
        account_name=name,
        account_supplementary_name=name_supplementary,
        parent=parent,
    )


# Can we do this in SQL? We could just join the account with its parent
def find_parent(
    accounts: GnuCashAccountStore, account: GnuCashAccount
) -> Optional[GnuCashAccount]:
    """Find the parent for an account."""
    return accounts.get(account.parent_guid)


def get_accounts(con: sqlite3.Connection, db_contents: DbContents) -> None:
    """Get all accounts and link them with Kaikeio information."""
    fetch_gnucash_accounts(con, db_contents)

    for account in db_contents.gnucash_account_store.values():
        parent = find_parent(db_contents.gnucash_account_store, account)

        # Annotate link to kaikeio
        db_contents.account_store[account.guid] = make_linked_account(
            account,
            parent,
        )


def get_transactions(con: sqlite3.Connection, db_contents: DbContents) -> None:
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        tx = deserialize_transaction(row)
        db_contents.transaction_store[tx.guid] = tx


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
