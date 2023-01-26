"""CSV related functionality."""
import csv
from typing import (
    Iterable,
)

from . import (
    serialize,
)
from .types import (
    AccountInfo,
    AccountLink,
    Configuration,
)


class KaikeoDialect(csv.Dialect):
    """CSV dialect for kaikeio."""

    delimiter = ","
    doublequote = True
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    lineterminator = "\r\n"


def read_account_info(
    config: Configuration,
) -> AccountInfo:
    """Read in all accounts to export."""
    account_info = AccountInfo()

    with open(config.accounts_read_csv) as fd:
        reader = csv.DictReader(fd)
        for row in reader:
            account_info.accounts_to_read_struct[row["name"]] = AccountLink(
                account=row["account"],
                account_supplementary=row["account_supplementary"],
                account_name=row["account_name"],
                account_supplementary_name=row["account_supplementary_name"],
            )
            account_info.accounts_to_read_names.append(row["name"])
    with open(config.accounts_export_csv) as fd:
        for line in fd.readlines():
            account_info.accounts_to_export_names.append(line.strip())

    return account_info


def write_journal_entries(
    config: Configuration, entry_dicts: Iterable[serialize.JournalEntryDict]
) -> None:
    """Write the journal entries."""
    with open(config.journal_out_csv, "w", encoding="shift_jis") as fd:
        writer = csv.DictWriter(
            fd,
            serialize.journal_entry_columns,
            dialect=KaikeoDialect,
        )
        writer.writeheader()
        for entry_dict in entry_dicts:
            writer.writerow(entry_dict)
