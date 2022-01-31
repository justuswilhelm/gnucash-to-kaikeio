#!/usr/bin/env python3
"""Main module."""
from collections import defaultdict
from dataclasses import (
    asdict,
    dataclass,
)
from datetime import date
from decimal import Decimal
from pathlib import Path
import argparse
import csv
import sqlite3

query = """
SELECT * FROM splits
INNER JOIN transactions ON transactions.guid = splits.tx_guid
INNER JOIN accounts ON splits.account_guid = accounts.guid
"""

select_accounts = """
SELECT * FROM accounts
"""

select_transactions = """
SELECT * FROM transactions
"""

select_splits = """
SELECT * FROM splits
"""


out_dir = Path('out')


def dict_factory(cursor, row):
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

    @property
    def name(self):
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
    enter_date: date
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

    通番: str
    伝票番号: str
    行番号: str
    伝票日付: date
    作成者: str
    仕訳作成日付: date
    取引区分コード: str
    取引区分名称: str
    借方科目コード: str
    借方科目名称: str
    借方補助コード: str
    借方補助科目名称: str
    借方部門コード: str
    借方部門名称: str
    借方課税区分コード: str
    借方課税区分名称: str
    借方事業分類コード: str
    借方事業分類名称: str
    借方税処理コード: str
    借方税処理名称: str
    借方税率: Decimal
    借方金額: Decimal
    借方消費税: Decimal
    貸方科目コード: str
    貸方科目名称: str
    貸方補助コード: str
    貸方補助科目名称: str
    貸方部門コード: str
    貸方部門名称: str
    貸方課税区分コード: str
    貸方課税区分名称: str
    貸方事業分類コード: str
    貸方事業分類名称: str
    貸方税処理コード: str
    貸方税処理名称: str
    貸方税率: Decimal
    貸方金額: Decimal
    貸方消費税: Decimal
    取引摘要コード: str
    取引摘要: str
    補助摘要コード: str
    補助摘要: str
    メモ: str
    付箋１: str
    付箋２: str
    数量: str
    伝票種別: str


accounts = {}
transactions = {}
splits = {}

accounts_to_read = []
accounts_to_read_names = []
accounts_to_export = []
accounts_to_export_names = []

transaction_splits = defaultdict(list)
account_journal = []


def get_accounts(con):
    """Get all accounts."""
    cur = con.cursor()
    cur.execute(select_accounts)
    for row in cur.fetchall():
        accounts[row['guid']] = Account(
            guid=row['guid'],
            _name=row['name'],
            parent_guid=row['parent_guid'],
        )

    for account in accounts.values():
        if account.name in accounts_to_read_names:
            accounts_to_read.append(account)
        if account.name in accounts_to_export_names:
            accounts_to_export.append(account)


def get_transactions(con):
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        transactions[row['guid']] = Transaction(
            guid=row['guid'],
            date=date.fromisoformat(row['post_date'].split(' ')[0]),
            enter_date=date.fromisoformat(row['enter_date'].split(' ')[0]),
            description=row['description'],
        )



def get_splits(con):
    """Get all splits."""
    cur = con.cursor()
    cur.execute(select_splits)
    for row in cur.fetchall():
        account = accounts[row['account_guid']]
        split = Split(
            guid=row['guid'],
            account=account,
            transaction=transactions[row['tx_guid']],
            memo=row['memo'],
            value=Decimal(row['value_num'])
        )
        if account in accounts_to_read:
            splits[row['guid']] = split


def read_accounts():
    """Read in all accounts to export."""
    with open("accounts.csv") as fd:
        for line in fd.readlines():
            accounts_to_read_names.append(line.strip())
    with open("export.csv") as fd:
        for line in fd.readlines():
            accounts_to_export_names.append(line.strip())


def populate_transaction_splits():
    """Populate transaction_splits."""
    for split in splits.values():
        transaction_splits[split.transaction.guid].append(split)


def is_exportable(splits):
    """Decide whether a transaction with its splits is to be exported."""
    return any(
        split.account in accounts_to_export for split in splits
    )


def get_debits(splits):
    """Get all debits from a split."""
    return filter(lambda split: split.value > 0, splits)


def get_credits(splits):
    """Get all credits from a split."""
    return filter(lambda split: split.value < 0, splits)


def main(args):
    """Main function."""
    read_accounts()

    con = sqlite3.connect(args.infile)
    con.row_factory = dict_factory
    get_accounts(con)
    get_transactions(con)
    get_splits(con)
    populate_transaction_splits()

    for tx in transaction_splits.values():
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
            d = JournalEntry(
                通番=entry.transaction.guid,
                伝票番号=entry.transaction.guid,
                行番号="1",
                伝票日付=entry.transaction.date,
                作成者="ADMINISTRATOR",
                仕訳作成日付=entry.transaction.enter_date,
                取引区分コード="0",
                取引区分名称="決算取引",
                借方科目コード=entry.account.guid if swap else smaller_side.account.guid,
                借方科目名称=entry.account.name if swap else smaller_side.account.name,
                借方補助コード="0",
                借方補助科目名称="",
                借方部門コード="0",
                借方部門名称="",
                借方課税区分コード="0",
                借方課税区分名称="",
                借方事業分類コード="0",
                借方事業分類名称="",
                借方税処理コード="3",
                借方税処理名称="税込",
                借方税率="0%",
                借方金額=value,
                借方消費税="0",
                貸方科目コード=smaller_side.account.guid if swap else entry.account.guid,
                貸方科目名称=smaller_side.account.name if swap else entry.account.name,
                貸方補助コード="0",
                貸方補助科目名称="",
                貸方部門コード="0",
                貸方部門名称="",
                貸方課税区分コード="0",
                貸方課税区分名称="",
                貸方事業分類コード="0",
                貸方事業分類名称="",
                貸方税処理コード="3",
                貸方税処理名称="税込",
                貸方税率="0%",
                貸方金額=value,
                貸方消費税="0",
                取引摘要コード="",
                取引摘要=entry.transaction.description + " " + entry.memo + " " + smaller_side.memo,
                補助摘要コード="",
                補助摘要="",
                メモ=entry.transaction.description + " " + entry.memo + " " + smaller_side.memo,
                付箋１="0",
                付箋２="0",
                数量="0.00",
                伝票種別="0",
            )
            account_journal.append(d)
            # d = JournalEntry(
            #     date=entry.transaction.date,
            #     guid=entry.transaction.guid,
            #     amount=-entry.value,
            #     debit=smaller_side.account.name,
            #     credit=entry.account.name,
            #     memo=smaller_side.transaction.description
            #     + " " + smaller_side.memo,
            # )
            # account_journal[smaller_side.account.guid].append(d)

    account_journal.sort(key=lambda a: a.伝票日付)
    path = (out_dir / "output").with_suffix('.csv')
    with open(path, 'w') as fd:
        first_entry = account_journal[0]
        writer = csv.DictWriter(
            fd,
            asdict(first_entry).keys()
        )
        writer.writeheader()
        for entry in account_journal:
            writer.writerow(asdict(entry))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    main(args)
