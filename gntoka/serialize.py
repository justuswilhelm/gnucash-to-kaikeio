"""Serialization methods."""
from dataclasses import (
    asdict,
)
from typing import (
    Mapping,
    TypedDict,
    cast,
)

from . import (
    types,
)


# Dictionaries
class JournalEntryDict(TypedDict):
    """A journal entry dict."""

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
    借方金額: str
    借方消費税額: str
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
    貸方金額: str
    貸方消費税額: str
    摘要: str
    補助摘要: str
    メモ: str
    付箋１: str
    付箋２: str
    伝票種別: str


journal_entry_columns = (
    "伝票番号",
    "行番号",
    "伝票日付",
    "借方科目コード",
    "借方科目名称",
    "借方補助コード",
    "借方補助科目名称",
    "借方部門コード",
    "借方部門名称",
    "借方課税区分",
    "借方事業分類",
    "借方消費税処理方法",
    "借方消費税率",
    "借方金額",
    "借方消費税額",
    "貸方科目コード",
    "貸方科目名称",
    "貸方補助コード",
    "貸方補助科目名称",
    "貸方部門コード",
    "貸方部門名称",
    "貸方課税区分",
    "貸方事業分類",
    "貸方消費税処理方法",
    "貸方消費税率",
    "貸方金額",
    "貸方消費税額",
    "摘要",
    "補助摘要",
    "メモ",
    "付箋１",
    "付箋２",
    "伝票種別",
)


class AccountLinkDict(TypedDict):
    """Encode account link information."""

    name: str
    account: str
    account_supplementary: str
    account_name: str
    account_supplementary_name: str


# Serializers
def serialize_journal_entry(value: types.JournalEntry) -> JournalEntryDict:
    """Serialize a journal entry."""
    d: Mapping[str, str] = {k: str(v) for k, v in asdict(value).items()}
    return cast(JournalEntryDict, d)


# Deserializers
def deserialize_account_link(account_link: types.CsvRow) -> types.AccountLink:
    """Deserialize an account link."""
    return types.AccountLink(
        name=account_link["name"],
        account=account_link["account"],
        account_supplementary=account_link["account_supplementary"],
        account_name=account_link["account_name"],
        account_supplementary_name=account_link["account_supplementary_name"],
    )
