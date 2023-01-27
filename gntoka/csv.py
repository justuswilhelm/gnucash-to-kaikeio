"""CSV related functionality."""
import csv
from typing import (
    Iterable,
)

from . import (
    serialize,
)
from .types import (
    Configuration,
)


class KaikeoDialect(csv.Dialect):
    """CSV dialect for kaikeio."""

    delimiter = ","
    doublequote = True
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    lineterminator = "\r\n"


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
