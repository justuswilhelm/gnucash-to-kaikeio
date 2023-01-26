#!/usr/bin/env python3
"""Main module."""
import argparse
from decimal import (
    Decimal,
)
from itertools import (
    count,
)
from pathlib import (
    Path,
)
from typing import (
    Iterable,
)

import toml
from gntoka import (
    db,
    serialize,
    util,
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
    JournalEntry,
    Split,
    TransactionSplits,
)


def populate_transaction_splits(db_contents: DbContents) -> None:
    """Populate transaction_splits."""
    for split in db_contents.splits.values():
        db_contents.transaction_splits[split.transaction.guid].append(split)


def is_exportable(accounts: Accounts, splits: Iterable[Split]) -> bool:
    """Decide whether a transaction with its splits is to be exported."""
    return any(
        split.account in accounts.accounts_to_export for split in splits
    )


def build_journal(
    accounts: Accounts, transaction_splits_values: TransactionSplits
) -> JournalEntries:
    """Build a journal."""
    account_journal: JournalEntries = []

    counter = count(start=1)

    for tx in transaction_splits_values:
        if not is_exportable(accounts, tx):
            continue
        assert len(tx) > 1
        assert sum(split.value for split in tx) == Decimal(0), tx
        debits = list(util.get_debits(tx))
        credits = list(util.get_credits(tx))
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
                伝票日付=util.format_date(entry.transaction.date),
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
    return account_journal


def main(config: Configuration) -> None:
    """Run program."""
    con = db.open_connection(config)

    accounts = Accounts()

    account_info = read_account_info(
        config,
    )

    db_contents = DbContents()

    get_accounts(
        con,
        accounts.accounts_to_read,
        account_info.accounts_to_read_names,
        accounts.accounts_to_export,
        account_info.exportable_account_names,
        account_info.accounts_to_read_struct,
        db_contents.accounts,
    )
    get_transactions(con, db_contents.transactions)
    get_splits(
        con,
        accounts.accounts_to_read,
        db_contents.accounts,
        db_contents.transactions,
        db_contents.splits,
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
        accounts_read_csv=Path(
            config_path_parent / config_dict["accounts_read_csv"]
        ),
        accounts_export_csv=Path(
            config_path_parent / config_dict["accounts_export_csv"]
        ),
        journal_out_csv=Path(
            config_path_parent / config_dict["journal_out_csv"]
        ),
    )
    main(configuration)
