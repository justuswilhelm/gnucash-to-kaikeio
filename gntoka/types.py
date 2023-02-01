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
class Account:
    """An account."""

    guid: str
    code: str
    name: str
    supplementary_code: Optional[str]
    supplementary_name: Optional[str]


@dataclass
class Transaction:
    """A transaction."""

    guid: str
    date: date
    description: Optional[str]


@dataclass
class Split:
    """A split."""

    guid: str
    account: Account
    transaction: Transaction
    memo: Optional[str]
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
    借方科目コード: Optional[str]
    借方科目名称: Optional[str]
    借方補助コード: Optional[str]
    借方補助科目名称: Optional[str]
    借方部門コード: Optional[str]
    借方部門名称: str
    借方課税区分: str
    借方事業分類: str
    借方消費税処理方法: str
    借方消費税率: ConsumptionTaxRate
    借方金額: Optional[Decimal]
    借方消費税額: Decimal
    貸方科目コード: Optional[str]
    貸方科目名称: Optional[str]
    貸方補助コード: Optional[str]
    貸方補助科目名称: Optional[str]
    貸方部門コード: Optional[str]
    貸方部門名称: str
    貸方課税区分: str
    貸方事業分類: str
    貸方消費税処理方法: str
    貸方消費税率: ConsumptionTaxRate
    貸方金額: Optional[Decimal]
    貸方消費税額: Decimal
    摘要: Optional[str]
    補助摘要: Optional[str]
    メモ: Optional[str]
    # XXX investigate whether unicode normalization got to us here...
    付箋１: str
    付箋２: str
    伝票種別: str


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
    start_num: int


@dataclass
class DbContents:
    """Store everything we have read from GnuCash."""

    account_store: AccountStore
    transaction_store: TransactionStore
    split_store: SplitStore = field(default_factory=dict)
    transaction_splits: Dict[str, List[Split]] = field(
        default_factory=lambda: defaultdict(list)
    )
