#!/usr/bin/env python3
"""Main module."""
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
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
    description: str


@dataclass
class Split:
    """A split."""

    guid: str
    account: Account
    transaction: Transaction
    memo: str
    value: Decimal


accounts = {}
transactions = {}
splits = {}

accounts_to_read = []
accounts_to_read_names = []

account_splits = defaultdict(list)
transaction_splits = defaultdict(list)


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


def get_transactions(con):
    """Get all transactions."""
    cur = con.cursor()
    cur.execute(select_transactions)
    for row in cur.fetchall():
        transactions[row['guid']] = Transaction(
            guid=row['guid'],
            date=date.fromisoformat(row['post_date'].split(' ')[0]),
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


def populate_account_splits():
    """Populate account_splits."""
    for split in splits.values():
        account_splits[split.account.guid].append(split)


def populate_transaction_splits():
    """Populate transaction_splits."""
    for split in splits.values():
        transaction_splits[split.transaction.guid].append(split)


def main(args):
    """Main function."""
    read_accounts()

    con = sqlite3.connect(args.infile)
    con.row_factory = dict_factory
    get_accounts(con)
    get_transactions(con)
    get_splits(con)
    populate_account_splits()
    populate_transaction_splits()

    for tx in transaction_splits.values():
        if len(tx) == 1:
            continue
        print(tx)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    main(args)
