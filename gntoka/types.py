"""Types used in application."""
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
    List,
    Mapping,
    Set,
)


CsvRow = Mapping[str, str]


@dataclass
class GnuCashAccount:
    """GnuCash representation of an account."""

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
    account_supplementary: str
    account_name: str
    account_supplementary_name: str


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


@dataclass
class JournalEntry:
    """A journal entry."""

    伝票番号: str
    行番号: str
    伝票日付: str
    借方科目コード: str
    借方科目名称: str
    借方補助コード: str
    借方補助科目名称: str
    借方部門コード: str
    借方部門名称: str
    借方課税区分: str
    借方事業分類: str
    借方消費税処理方法: str
    借方消費税率: str
    借方金額: Decimal
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
    貸方消費税率: str
    貸方金額: Decimal
    貸方消費税額: Decimal
    摘要: str
    補助摘要: str
    メモ: str
    付箋１: str
    付箋２: str
    伝票種別: str


GnuCashAccountStore = Dict[str, GnuCashAccount]
AccountStore = Dict[str, Account]
AccountIds = Set[str]
TransactionStore = Dict[str, Transaction]
SplitStore = Dict[str, Split]
JournalEntries = List[JournalEntry]
TransactionSplits = List[List[Split]]

AccountNames = List[str]


@dataclass
class Configuration:
    """Store configuration variables."""

    gnucash_db: Path
    accounts_read_csv: Path
    accounts_export_csv: Path
    journal_out_csv: Path


@dataclass
class DbContents:
    """Store everything we have read from GnuCash."""

    gnucash_account_store: GnuCashAccountStore = field(default_factory=dict)
    account_store: AccountStore = field(default_factory=dict)
    transaction_store: TransactionStore = field(default_factory=dict)
    split_store: SplitStore = field(default_factory=dict)
    transaction_splits: Dict[str, List[Split]] = field(
        default_factory=lambda: defaultdict(list)
    )


@dataclass
class AccountLink:
    """Links GnuCash and Kaikeio accounts."""

    name: str
    account: str
    account_supplementary: str
    account_name: str
    account_supplementary_name: str


AccountLinks = Mapping[str, AccountLink]


@dataclass
class AccountInfo:
    """Contains information about accounts to process and export."""

    importable_account_names: AccountNames = field(default_factory=list)
    exportable_account_names: AccountNames = field(default_factory=list)
    importable_account_links: AccountLinks = field(default_factory=dict)


@dataclass
class Accounts:
    """Contains all accounts."""

    accounts_to_read: AccountIds = field(default_factory=set)
    accounts_to_export: AccountIds = field(default_factory=set)
