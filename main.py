#!/usr/bin/env python3
"""Main module."""
import argparse
from itertools import (
    count,
)
from pathlib import (
    Path,
)

import toml
from gntoka import (
    db,
    journal,
    serialize,
)
from gntoka.csv import (
    read_account_info,
    write_journal_entries,
)
from gntoka.db import (
    get_accounts,
    get_splits,
    get_transactions,
)
from gntoka.types import (
    Accounts,
    Configuration,
    DbContents,
    JournalEntries,
    JournalEntryCounter,
    TransactionSplits,
)


def populate_transaction_splits(db_contents: DbContents) -> None:
    """Populate transaction_splits."""
    for split in db_contents.split_store.values():
        db_contents.transaction_splits[split.transaction.guid].append(split)


def build_journal(
    accounts: Accounts, transaction_splits_values: TransactionSplits
) -> JournalEntries:
    """Build a journal."""
    account_journal: JournalEntries = []

    counter: JournalEntryCounter = count(start=1)

    for tx in transaction_splits_values:
        account_journal += journal.build_journal_entries(counter, tx)

    account_journal.sort(key=lambda a: a.伝票日付)
    return account_journal


def main(config: Configuration) -> None:
    """Run program."""
    con = db.open_connection(config)

    account_info = read_account_info(
        config,
    )

    db_contents = DbContents()

    accounts = get_accounts(
        con,
        account_info,
        db_contents,
    )
    get_transactions(con, db_contents)
    get_splits(
        con,
        accounts,
        db_contents,
    )
    populate_transaction_splits(db_contents)

    transaction_splits_values: TransactionSplits
    transaction_splits_values = sorted(
        db_contents.transaction_splits.values(),
        key=lambda tx: tx[0].transaction.date,
    )

    account_journal: JournalEntries = build_journal(
        accounts,
        transaction_splits_values,
    )
    entry_dicts = [
        serialize.serialize_journal_entry(e) for e in account_journal
    ]
    write_journal_entries(config, entry_dicts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    args = parser.parse_args()
    config_path = Path(args.config)
    with config_path.open() as fd:
        config_dict = toml.load(fd)
    config_path_parent = config_path.parent
    configuration = Configuration(
        gnucash_db=Path(config_path_parent / config_dict["gnucash_db"]),
        account_links_csv=Path(
            config_path_parent / config_dict["account_links_csv"]
        ),
        journal_out_csv=Path(
            config_path_parent / config_dict["journal_out_csv"]
        ),
    )
    main(configuration)
