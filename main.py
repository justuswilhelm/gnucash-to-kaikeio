#!/usr/bin/env python3
"""Main module."""
from collections import (
    defaultdict,
)
from itertools import (
    count,
)
from dataclasses import (
    asdict,
    dataclass,
)
from datetime import date
from decimal import Decimal
from pathlib import Path
import csv
import argparse
import sqlite3

from typing import (
    Dict,
    Iterable,
    Sequence,
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


out_dir = Path("out")


class KaikeoDialect(csv.Dialect):
    """CSV dialect for kaikeio."""

    delimiter = ","
    doublequote = True
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    lineterminator = "\r\n"


def dict_factory(cursor: sqlite3.Cursor, row: Sequence[str]) -> Dict[str, str]:
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@dataclass
class Account:
    """An account."""

    guid: str
    _name: str
    parent_guid: str
    account: str
    account_supplementary: str
    account_name: str
    account_supplementary_name: str

    @property
    def name(self) -> str:
        """Return full name."""
        if not self.parent_guid:
            return self._name
        if accounts[self.parent_guid].name == "Root Account":
            return self._name
        return accounts[self.parent_guid].name + ":" + self._name


@dataclass
class Transaction:
    """A transaction."""

    guid: str
    date: date
    description: str


@dataclass
class Split:
    """A split."""

    guid: str
    account: Account
    transaction: Transaction
    memo: str
    value: Decimal


@dataclass
class JournalEntry:
    """
    A journal entry.
    """

    伝票番号: str
    行番号: str
    伝票日付: str
    借方科目コード: str
    借方科目名称: str
    借方補助コード: str
    借方補助科目名称: str
    借方部門コード: str
    借方部門名称: str
    借方課税区分: str
    借方事業分類: str
    借方消費税処理方法: str
    借方消費税率: str
    借方金額: Decimal
    借方消費税額: Decimal
    貸方科目コード: str
    貸方科目名称: str
    貸方補助コード: str
    貸方補助科目名称: str
    貸方部門コード: str
    貸方部門名称: str
    貸方課税区分: str
    貸方事業分類: str
    貸方消費税処理方法: str
    貸方消費税率: str
    貸方金額: Decimal
    貸方消費税額: Decimal
    摘要: str
    補助摘要: str
    メモ: str
    付箋１: str
    付箋２: str
    伝票種別: str


accounts = {}
transactions = {}
splits = {}

accounts_to_read = []
accounts_to_read_names = []
accounts_to_read_struct: Dict[str, Dict[str, str]] = {}
accounts_to_export = []
accounts_to_export_names = []

transaction_splits = defaultdict(list)
account_journal = []


def get_accounts(con: sqlite3.Connection) -> None:
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
        if account.name in accounts_to_read_names:
            accounts_to_read.append(account)
        if account.name in accounts_to_export_names:
            accounts_to_export.append(account)
        account_additional = accounts_to_read_struct.get(account.name)
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


def get_transactions(con: sqlite3.Connection) -> None:
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        transactions[row["guid"]] = Transaction(
            guid=row["guid"],
            date=date.fromisoformat(row["post_date"].split(" ")[0]),
            description=row["description"],
        )


def get_splits(con: sqlite3.Connection) -> None:
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


def read_accounts() -> None:
    """Read in all accounts to export."""
    with open("accounts.csv") as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            accounts_to_read_struct[row["name"]] = row
            accounts_to_read_names.append(row["name"])
    with open("export.csv") as fd:
        for line in fd.readlines():
            accounts_to_export_names.append(line.strip())


def populate_transaction_splits() -> None:
    """Populate transaction_splits."""
    for split in splits.values():
        transaction_splits[split.transaction.guid].append(split)


def is_exportable(splits: Iterable[Split]) -> bool:
    """Decide whether a transaction with its splits is to be exported."""
    return any(split.account in accounts_to_export for split in splits)


def get_debits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all debits from a split."""
    return filter(lambda split: split.value > 0, splits)


def get_credits(splits: Iterable[Split]) -> Iterable[Split]:
    """Get all credits from a split."""
    return filter(lambda split: split.value < 0, splits)


def format_date(d: date) -> str:
    """Format date."""
    return d.strftime("%Y/%m/%d")


def main(args: argparse.Namespace) -> None:
    """Main function."""
    read_accounts()

    con: sqlite3.Connection = sqlite3.connect(args.infile)
    con.row_factory = dict_factory
    get_accounts(con)
    get_transactions(con)
    get_splits(con)
    populate_transaction_splits()

    counter = count(start=1)
    transaction_splits_values = list(transaction_splits.values())
    transaction_splits_values.sort(key=lambda tx: tx[0].transaction.date)
    for tx in transaction_splits_values:
        if not is_exportable(tx):
            continue
        assert len(tx) > 1
        assert sum(split.value for split in tx) == Decimal(0), tx
        debits = list(get_debits(tx))
        credits = list(get_credits(tx))
        # Scenario one, one credit split that funds n debit splits
        if len(debits) > len(credits):
            assert len(credits) == 1
            larger_side = debits
            smaller_side = credits[0]
            # Magic variable, do not touch
            swap = True
        # Scenario two, one debit split that funds n credit splits
        else:
            assert len(debits) == 1, tx
            larger_side = credits
            smaller_side = debits[0]
            # Magic variable, do not touch
            swap = False
        for entry in larger_side:
            value = abs(entry.value)
            number = next(counter)
            memo = " ".join(
                [
                    entry.transaction.description,
                    entry.memo,
                    smaller_side.memo,
                ]
            ).replace("\xa0", " ")
            d = JournalEntry(
                伝票番号=str(number),
                行番号="1",
                伝票日付=format_date(entry.transaction.date),
                借方科目コード=entry.account.account
                if swap
                else smaller_side.account.account,
                借方科目名称=entry.account.account_name
                if swap
                else smaller_side.account.account_name,
                借方補助コード=entry.account.account_supplementary
                if swap
                else smaller_side.account.account_supplementary,
                借方補助科目名称=entry.account.account_supplementary_name
                if swap
                else smaller_side.account.account_supplementary_name,
                借方部門コード="0",
                借方部門名称="",
                借方課税区分="0",
                借方事業分類="0",
                借方消費税処理方法="3",
                借方消費税率="0%",
                借方金額=value,
                借方消費税額=Decimal("0"),
                貸方科目コード=smaller_side.account.account
                if swap
                else entry.account.account,
                貸方科目名称=smaller_side.account.account_name
                if swap
                else entry.account.account_name,
                貸方補助コード=smaller_side.account.account_supplementary
                if swap
                else entry.account.account_supplementary,
                貸方補助科目名称=smaller_side.account.account_supplementary_name
                if swap
                else entry.account.account_supplementary_name,
                貸方部門コード="0",
                貸方部門名称="",
                貸方課税区分="",
                貸方事業分類="0",
                貸方消費税処理方法="3",
                貸方消費税率="0%",
                貸方金額=value,
                貸方消費税額=Decimal("0"),
                摘要="",
                補助摘要="",
                メモ=memo,
                付箋１="0",
                付箋２="0",
                伝票種別="0",
            )
            account_journal.append(d)

    account_journal.sort(key=lambda a: a.伝票日付)
    path = (out_dir / "output").with_suffix(".txt")
    entry_dicts = [asdict(e) for e in account_journal]
    with open(path, "w", encoding="shift_jis") as fd:
        writer = csv.DictWriter(
            fd,
            list(entry_dicts[0].keys()),
            dialect=KaikeoDialect,
        )
        writer.writeheader()
        for entry_dict in entry_dicts:
            writer.writerow(entry_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    args = parser.parse_args()
    main(args)
