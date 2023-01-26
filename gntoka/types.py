"""Types used in application."""
from dataclasses import (
    dataclass,
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
)


@dataclass
class Account:
    """An account."""

    guid: str
    _name: str
    parent_guid: str
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


AccountStore = Dict[str, Account]
AccountSequence = List[Account]
TransactionStore = Dict[str, Transaction]
SplitStore = Dict[str, Split]
JournalEntries = List[JournalEntry]

NamesToRead = List[str]
WhatIsThis = Dict[str, Dict[str, str]]


@dataclass
class Configuration:
    """Store configuration variables."""

    gnucash_db: Path
    accounts_read_csv: Path
    accounts_export_csv: Path
    journal_out_csv: Path
