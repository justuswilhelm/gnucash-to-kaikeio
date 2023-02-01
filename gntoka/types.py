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
    debit_code: Optional[str]
    debit_name: Optional[str]
    debit_supplementary_code: Optional[str]
    debit_supplementary_name: Optional[str]
    debit_department_code: Optional[str]
    debit_department_name: str
    debit_tax_class: str
    debit_business_category: str
    debit_consumption_tax_method: str
    debit_consumption_tax_rate: ConsumptionTaxRate
    debit_amount: Optional[Decimal]
    debit_consumption_tax_amount: Decimal
    credit_code: Optional[str]
    credit_name: Optional[str]
    credit_supplementary_code: Optional[str]
    credit_supplementary_name: Optional[str]
    credit_department_code: Optional[str]
    credit_department_name: str
    credit_tax_class: str
    credit_business_category: str
    credit_consumption_tax_method: str
    credit_consumption_tax_rate: ConsumptionTaxRate
    credit_amount: Optional[Decimal]
    credit_consumption_tax_amount: Decimal
    summary: Optional[str]
    supplementary_summary: Optional[str]
    memo: Optional[str]
    tag1: str
    tag2: str
    slip_type: str


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
