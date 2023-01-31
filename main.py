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
)
from gntoka.csv import (
    write_journal_entries,
)
from gntoka.db import (
    get_accounts,
    get_splits,
    get_transactions,
)
from gntoka.types import (
    Configuration,
    DbContents,
    JournalEntries,
    JournalEntryCounter,
    TransactionSplits,
)


# TODO when we receive all splits in one big query (instead of 3) from the db,
# we should just group them by transaction uid here.
def populate_transaction_splits(db_contents: DbContents) -> None:
    """Populate transaction_splits."""
    for split in db_contents.split_store.values():
        db_contents.transaction_splits[split.transaction.guid].append(split)


def build_journal(
    transaction_splits_values: TransactionSplits,
    start_num: int,
) -> JournalEntries:
    """Build a journal."""
    account_journal: JournalEntries = []

    counter: JournalEntryCounter = count(start=start_num)

    # TODO we could rewrite this as a sorted(.flatten)
    for tx in transaction_splits_values:
        account_journal += journal.build_journal_entries(counter, tx)

    account_journal.sort(key=lambda a: a.slip_date)
    return account_journal


def main(config: Configuration) -> None:
    """Run program."""
    con = db.open_connection(config)

    db_contents = DbContents(
        account_store=get_accounts(con),
        transaction_store=get_transactions(
            con,
            config.start_date,
            config.end_date,
        ),
    )
    get_splits(con, db_contents)
    populate_transaction_splits(db_contents)

    transaction_splits_values: TransactionSplits
    transaction_splits_values = sorted(
        db_contents.transaction_splits.values(),
        key=lambda tx: tx[0].transaction.date,
    )

    account_journal: JournalEntries = build_journal(
        transaction_splits_values, config.start_num
    )
    write_journal_entries(config, account_journal)


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
        journal_out_csv=Path(
            config_path_parent / config_dict["journal_out_csv"]
        ),
        start_date=config_dict["start_date"],
        end_date=config_dict["end_date"],
        start_num=config_dict["start_num"],
    )
    main(configuration)
