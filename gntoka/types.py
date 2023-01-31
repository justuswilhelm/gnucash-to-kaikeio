"""Types used in application."""
import enum
from collections import (
    defaultdict,
)
from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from pathlib import (
    Path,
)
from typing import (
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Set,
)


CsvRow = Mapping[str, str]


@dataclass
class GnuCashAccount:
    """GnuCash representation of an account."""

    code: str
    guid: str
    _name: str
    parent_guid: str


# TODO use composition, not inheritance
# Eventually we should store a composite containing GnuCashAccount and
# AccountLink
@dataclass
class Account(GnuCashAccount):
    """An account."""

    account: str
    # TODO This should be Optional
    account_supplementary: str
    account_name: str
    # TODO This should be Optional
    account_supplementary_name: str
    parent: Optional[GnuCashAccount]


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


class ConsumptionTaxRate(enum.Enum):
    """Encode the applicable tax rate."""

    ZERO = enum.auto()
    EIGHT_REDUCED = enum.auto()
    TEN = enum.auto()


@dataclass
class JournalEntry:
    """A journal entry."""

    slip_number: int
    line_number: int
    slip_date: date
    借方科目コード: str
    借方科目名称: str
    借方補助コード: str
    借方補助科目名称: str
    借方部門コード: str
    借方部門名称: str
    借方課税区分: str
    借方事業分類: str
    借方消費税処理方法: str
    借方消費税率: ConsumptionTaxRate
    借方金額: Optional[Decimal]
    借方消費税額: Decimal
    貸方科目コード: str
    貸方科目名称: str
    貸方補助コード: str
    貸方補助科目名称: str
    貸方部門コード: str
    貸方部門名称: str
    貸方課税区分: str
    貸方事業分類: str
    貸方消費税処理方法: str
    貸方消費税率: ConsumptionTaxRate
    貸方金額: Optional[Decimal]
    貸方消費税額: Decimal
    摘要: str
    補助摘要: str
    メモ: str
    # XXX investigate whether unicode normalization got to us here...
    付箋１: str
    付箋２: str
    伝票種別: str


GnuCashAccountStore = Dict[str, GnuCashAccount]
AccountStore = Dict[str, Account]
AccountIds = Set[str]
TransactionStore = Dict[str, Transaction]
SplitStore = Dict[str, Split]
JournalEntries = List[JournalEntry]
TransactionSplit = List[Split]
TransactionSplits = List[TransactionSplit]

AccountNames = List[str]

JournalEntryCounter = Iterator[int]


@dataclass
class Configuration:
    """Store configuration variables."""

    gnucash_db: Path
    journal_out_csv: Path
    start_date: date
    # Inclusive
    end_date: date


@dataclass
class DbContents:
    """Store everything we have read from GnuCash."""

    account_store: AccountStore
    transaction_store: TransactionStore
    split_store: SplitStore = field(default_factory=dict)
    transaction_splits: Dict[str, List[Split]] = field(
        default_factory=lambda: defaultdict(list)
    )
