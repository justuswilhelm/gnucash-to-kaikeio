"""Serialization methods."""
from datetime import (
    date,
)
from typing import (
    Optional,
    TypedDict,
)

from . import (
    constants,
    types,
    util,
)


# Dictionaries
JournalEntryDict = TypedDict(
    "JournalEntryDict",
    {
        "伝票番号": str,
        "行番号": str,
        "伝票日付": str,
        "借方科目コード": str,
        "借方科目名称": str,
        "借方補助コード": str,
        "借方補助科目名称": str,
        "借方部門コード": str,
        "借方部門名称": str,
        "借方課税区分": str,
        "借方事業分類": str,
        "借方消費税処理方法": str,
        "借方消費税率": str,
        "借方金額": str,
        "借方消費税額": str,
        "貸方科目コード": str,
        "貸方科目名称": str,
        "貸方補助コード": str,
        "貸方補助科目名称": str,
        "貸方部門コード": str,
        "貸方部門名称": str,
        "貸方課税区分": str,
        "貸方事業分類": str,
        "貸方消費税処理方法": str,
        "貸方消費税率": str,
        "貸方金額": str,
        "貸方消費税額": str,
        "摘要": str,
        "補助摘要": str,
        "メモ": str,
        "付箋１": str,
        "付箋２": str,
        "伝票種別": str,
    },
)

# XXX I wish we could use __required_keys__ here, but it is not guaranteed to
# be ordered
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


class AccountDict(TypedDict):
    """Encode GnuCash account information."""

    guid: str
    code: str
    name: str
    supplementary_code: Optional[str]
    supplementary_name: Optional[str]


class TransactionDict(TypedDict):
    """Encode GnuCash transaction information."""

    guid: str
    post_date: str
    description: str


class SplitDict(TypedDict):
    """Encode GnuCash split."""

    guid: str
    tx_guid: str
    account_guid: str
    memo: str
    value_num: str


# Serializers
def serialize_consumption_tax_rate(value: types.ConsumptionTaxRate) -> str:
    """Serialize consumption tax rate."""
    if value == types.ConsumptionTaxRate.ZERO:
        return "0%"
    elif value == types.ConsumptionTaxRate.EIGHT_REDUCED:
        return "8%軽"
    elif value == types.ConsumptionTaxRate.TEN:
        return "10%"
    assert False, f"{value} is unexpected"


def serialize_journal_entry(value: types.JournalEntry) -> JournalEntryDict:
    """Serialize a journal entry."""
    return {
        "伝票番号": str(value.slip_number),
        "行番号": str(value.line_number),
        "伝票日付": util.format_date(value.slip_date),
        "借方科目コード": value.借方科目コード,
        "借方科目名称": value.借方科目名称,
        "借方補助コード": value.借方補助コード,
        "借方補助科目名称": value.借方補助科目名称,
        "借方部門コード": value.借方部門コード,
        "借方部門名称": value.借方部門名称,
        "借方課税区分": value.借方課税区分,
        "借方事業分類": value.借方事業分類,
        "借方消費税処理方法": value.借方消費税処理方法,
        "借方消費税率": serialize_consumption_tax_rate(value.借方消費税率),
        "借方金額": str(value.借方金額),
        "借方消費税額": str(value.借方消費税額),
        "貸方科目コード": value.貸方科目コード,
        "貸方科目名称": value.貸方科目名称,
        "貸方補助コード": value.貸方補助コード,
        "貸方補助科目名称": value.貸方補助科目名称,
        "貸方部門コード": value.貸方部門コード,
        "貸方部門名称": value.貸方部門名称,
        "貸方課税区分": value.貸方課税区分,
        "貸方事業分類": value.貸方事業分類,
        "貸方消費税処理方法": value.貸方消費税処理方法,
        "貸方消費税率": serialize_consumption_tax_rate(value.貸方消費税率),
        "貸方金額": str(value.貸方金額),
        "貸方消費税額": str(value.貸方消費税額),
        "摘要": value.摘要,
        "補助摘要": value.補助摘要,
        "メモ": value.メモ,
        "付箋１": value.付箋１,
        "付箋２": value.付箋２,
        "伝票種別": value.伝票種別,
    }


# Deserializers
def deserialize_account(account: AccountDict) -> types.Account:
    """Deserialize an account fetched from GnuCash."""
    return types.Account(
        guid=account["guid"],
        code=account["code"],
        name=account["name"],
        supplementary_code=account["supplementary_code"]
        or constants.KAIKEIO_NO_ACCOUNT,
        supplementary_name=account["supplementary_name"] or "",
    )


def deserialize_transaction(transaction: types.CsvRow) -> types.Transaction:
    """Deserialize a transaction."""
    return types.Transaction(
        guid=transaction["guid"],
        # TODO Use string format based parsing instead
        date=date.fromisoformat(transaction["post_date"].split(" ")[0]),
        description=transaction["description"],
    )
