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
    cast,
)

from .serialize import (
    SplitDict,
)
from .types import (
    Account,
    AccountInfo,
    AccountLink,
    Accounts,
    Configuration,
    DbContents,
    GnuCashAccount,
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


def fetch_gnucash_accounts(
    con: sqlite3.Connection, db_contents: DbContents
) -> None:
    """Fetch accounts in GnuCash."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        db_contents.gnucash_account_store[row["guid"]] = GnuCashAccount(
            guid=row["guid"],
            _name=row["name"],
            parent_guid=row["parent_guid"],
        )


def make_linked_account(
    account: GnuCashAccount, account_link: AccountLink
) -> Account:
    """Link GnuCash and Kaikeio information in one account."""
    return Account(
        guid=account.guid,
        _name=account._name,
        parent_guid=account.parent_guid,
        account=account_link.account,
        account_supplementary=account_link.account_supplementary,
        account_name=account_link.account_name,
        account_supplementary_name=account_link.account_supplementary_name,
    )


def get_accounts(
    con: sqlite3.Connection,
    account_info: AccountInfo,
    db_contents: DbContents,
) -> Accounts:
    """Get all accounts and link them with Kaikeio information."""
    accounts = Accounts()

    fetch_gnucash_accounts(con, db_contents)

    for account in db_contents.gnucash_account_store.values():
        acc_name = account_name(account, db_contents.gnucash_account_store)
        if acc_name in account_info.importable_account_names:
            accounts.accounts_to_read.add(account.guid)
        if acc_name in account_info.exportable_account_names:
            accounts.accounts_to_export.add(account.guid)
        account_link = account_info.importable_account_links.get(acc_name)

        if not account_link:
            continue

        # Annotate link to kaikeio
        db_contents.account_store[account.guid] = make_linked_account(
            account,
            account_link,
        )

    return accounts


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
    accounts: Accounts,
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
        if account.guid in accounts.accounts_to_read:
            db_contents.split_store[split.guid] = split


def open_connection(config: Configuration) -> sqlite3.Connection:
    """Open a connection to the db."""
    con = sqlite3.connect(config.gnucash_db)
    con.row_factory = dict_factory
    return con
