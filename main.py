#!/usr/bin/env python3
"""Main module."""
from collections import defaultdict
from dataclasses import dataclass
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
    """A journal entry."""

    date: date
    amount: Decimal
    debit: str
    credit: str
    memo: str


accounts = {}
transactions = {}
splits = {}

accounts_to_read = []
accounts_to_read_names = []
accounts_to_export = []
accounts_to_export_names = []

transaction_splits = defaultdict(list)
account_journals = defaultdict(list)


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
    for split in splits:
        if split.account in accounts_to_export:
            return True
    return False


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
        if len(tx) == 1:
            continue
        if not is_exportable(tx):
            continue
        assert sum(split.value for split in tx) == Decimal(0), tx
        debits = list(get_debits(tx))
        credits = list(get_credits(tx))
        if len(debits) > len(credits):
            assert len(credits) == 1
            larger_side = debits
            smaller_side = credits[0]
        else:
            assert len(debits) == 1, tx
            larger_side = credits
            smaller_side = debits[0]
        for entry in larger_side:
            d = JournalEntry(
                date=entry.transaction.date,
                amount=entry.value,
                debit=entry.account.name,
                credit=smaller_side.account.name,
                memo=entry.transaction.description + " " + entry.memo,
            )
            account_journals[entry.account.guid].append(d)
            d = JournalEntry(
                date=entry.transaction.date,
                amount=-entry.value,
                debit=smaller_side.account.name,
                credit=entry.account.name,
                memo=smaller_side.transaction.description
                + " " + smaller_side.memo,
            )
            account_journals[smaller_side.account.guid].append(d)

    for guid, account_journal in account_journals.items():
        account_name = accounts[guid].name.replace(':', '_').replace(' ', '_')
        account_journal = sorted(account_journal, key=lambda entry: entry.date)
        path = (out_dir / account_name).with_suffix('.csv')
        with open(path, 'w') as fd:
            writer = csv.DictWriter(
                fd,
                ['date', 'amount', 'debit', 'credit', 'memo'],
            )
            writer.writeheader()
            for entry in account_journal:
                writer.writerow(
                    {
                        'date': entry.date,
                        'amount': entry.amount,
                        'debit': entry.debit,
                        'credit': entry.credit,
                        'memo': entry.memo,
                    }
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    args = parser.parse_args()
    main(args)
