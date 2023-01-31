"""CSV related functionality."""
import csv

from . import (
    serialize,
)
from .types import (
    Configuration,
    JournalEntries,
)


class KaikeoDialect(csv.Dialect):
    """CSV dialect for kaikeio."""

    delimiter = ","
    doublequote = True
    quotechar = '"'
    quoting = csv.QUOTE_ALL
    lineterminator = "\r\n"


# This should handle serialization directly
def write_journal_entries(
    config: Configuration,
    entries: JournalEntries,
) -> None:
    """Write the journal entries."""
    with config.journal_out_csv.open("w", encoding="shift_jis") as fd:
        writer = csv.DictWriter(
            fd,
            serialize.journal_entry_columns,
            dialect=KaikeoDialect,
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(serialize.serialize_journal_entry(entry))
