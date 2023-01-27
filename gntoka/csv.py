"""CSV related functionality."""
import csv
from typing import (
    Iterable,
    Mapping,
)

from . import (
    serialize,
)
from .types import (
    AccountInfo,
    AccountLink,
    AccountNames,
    Configuration,
)


class KaikeoDialect(csv.Dialect):
    """CSV dialect for kaikeio."""

    delimiter = ","
    doublequote = True
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    lineterminator = "\r\n"


def read_account_links(config: Configuration) -> Mapping[str, AccountLink]:
    """Read names and options of accounts that are to be imported."""
    with config.accounts_read_csv.open() as fd:
        reader = csv.DictReader(fd)
        account_links = (
            serialize.deserialize_account_link(row) for row in reader
        )
        return {
            account_link.name: account_link for account_link in account_links
        }


def read_exportable_accounts(config: Configuration) -> AccountNames:
    """Read names of accounts that are to be exported."""
    with config.accounts_export_csv.open() as fd:
        reader = csv.DictReader(fd)
        return [row["name"] for row in reader]


def read_account_info(
    config: Configuration,
) -> AccountInfo:
    """Read in all accounts to export."""
    account_links = read_account_links(config)

    account_info = AccountInfo(
        exportable_account_names=read_exportable_accounts(config),
        importable_account_links=account_links,
        importable_account_names=list(account_links.keys()),
    )

    return account_info


def write_journal_entries(
    config: Configuration, entry_dicts: Iterable[serialize.JournalEntryDict]
) -> None:
    """Write the journal entries."""
    with config.journal_out_csv.open("w", encoding="shift_jis") as fd:
        writer = csv.DictWriter(
            fd,
            serialize.journal_entry_columns,
            dialect=KaikeoDialect,
        )
        writer.writeheader()
        for entry_dict in entry_dicts:
            writer.writerow(entry_dict)
