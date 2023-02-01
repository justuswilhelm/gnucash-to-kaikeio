"""Serialization methods."""
from datetime import (
    date,
)
from typing import (
    Optional,
    TypedDict,
)

from . import (
    types,
    util,
)
from .constants import (
    KAIKEIO_NO_ACCOUNT,
)
from .util import (
    length_sjis,
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
    # Indexing
    assert 0 <= value.slip_number <= 9_999_999, value.slip_number
    slip_number = str(value.slip_number)

    assert 0 < value.line_number <= 999, value.line_number
    line_number = str(value.line_number)

    slip_date = util.format_date(value.slip_date)

    # Debit
    # TODO Validate number here
    debit_code = value.debit_code or KAIKEIO_NO_ACCOUNT

    debit_name = value.debit_name or ""
    assert length_sjis(debit_name) <= 30, debit_name

    # TODO Validate number here
    debit_supplementary_code = (
        value.debit_supplementary_code or KAIKEIO_NO_ACCOUNT
    )

    debit_supplementary_name = value.debit_supplementary_name or ""
    assert (
        length_sjis(debit_supplementary_name) <= 30
    ), debit_supplementary_name

    # TODO Validate number here
    debit_department_code = value.debit_department_code or KAIKEIO_NO_ACCOUNT

    debit_department_name = value.debit_department_name or ""
    assert length_sjis(debit_department_name) <= 30, debit_department_name

    # TODO Validate further here
    debit_tax_class = value.debit_tax_class

    # TODO Validate number here
    debit_business_category = value.debit_business_category

    # TODO Validate here
    debit_consumption_tax_method = value.debit_consumption_tax_method

    # This one is valid by serialization
    debit_consumption_tax_rate = serialize_consumption_tax_rate(
        value.debit_consumption_tax_rate
    )

    if value.debit_amount:
        assert (
            -9_999_999_999 <= value.debit_amount <= 9_999_999_999
        ), value.debit_amount
    debit_amount = str(value.debit_amount or 0)

    assert (
        -9_999_999_999 <= value.debit_consumption_tax_amount <= 9_999_999_999
    ), value.debit_consumption_tax_amount
    debit_consumption_tax_amount = str(value.debit_consumption_tax_amount)

    # Credit
    # TODO Validate number here
    credit_code = value.credit_code or KAIKEIO_NO_ACCOUNT

    credit_name = value.credit_name or ""
    assert length_sjis(credit_name) <= 30, credit_name

    # TODO Validate number here
    credit_supplementary_code = (
        value.credit_supplementary_code or KAIKEIO_NO_ACCOUNT
    )

    credit_supplementary_name = value.credit_supplementary_name or ""
    assert (
        length_sjis(credit_supplementary_name) <= 30
    ), credit_supplementary_name

    # TODO Validate number here
    credit_department_code = value.credit_department_code or KAIKEIO_NO_ACCOUNT

    credit_department_name = value.credit_department_name
    assert length_sjis(credit_department_name) <= 30, credit_department_name

    # TODO Validate further here
    credit_tax_class = value.credit_tax_class

    # TODO Validate number here
    credit_business_category = value.credit_business_category

    # TODO Validate here
    credit_consumption_tax_method = value.credit_consumption_tax_method

    # This one is valid by serialization
    credit_consumption_tax_rate = serialize_consumption_tax_rate(
        value.credit_consumption_tax_rate
    )

    if value.credit_amount:
        assert (
            -9_999_999_999 <= value.credit_amount <= 9_999_999_999
        ), value.credit_amount
    credit_amount = str(value.credit_amount or 0)

    credit_consumption_tax_amount = str(value.credit_consumption_tax_amount)
    assert (
        -9_999_999_999 <= value.credit_consumption_tax_amount <= 9_999_999_999
    ), value.credit_consumption_tax_amount

    # Annotations
    append_to_memo: list[str] = []

    summary = value.summary or ""
    # Everything we couldn't add here we just cram into the memo
    CUTOFF = 15
    if len(summary) > CUTOFF:
        append_to_memo.append(summary)
        summary = summary[:CUTOFF]
    assert length_sjis(summary) <= 30, summary

    supplementary_summary = value.supplementary_summary or ""
    # Everything we couldn't add here we just cram into the memo
    if len(supplementary_summary) > CUTOFF:
        append_to_memo.append(supplementary_summary)
        supplementary_summary = supplementary_summary[:CUTOFF]
    assert length_sjis(supplementary_summary) <= 30, supplementary_summary

    original_memo = value.memo or ""
    # And here we join it into the memo
    memo = " ".join(append_to_memo + [original_memo])
    assert length_sjis(memo) <= 200, memo

    tag1 = value.tag1

    tag2 = value.tag2

    slip_type = value.slip_type

    return {
        "伝票番号": slip_number,
        "行番号": line_number,
        "伝票日付": slip_date,
        "借方科目コード": debit_code,
        "借方科目名称": debit_name,
        "借方補助コード": debit_supplementary_code,
        "借方補助科目名称": debit_supplementary_name,
        "借方部門コード": debit_department_code,
        "借方部門名称": debit_department_name,
        "借方課税区分": debit_tax_class,
        "借方事業分類": debit_business_category,
        "借方消費税処理方法": debit_consumption_tax_method,
        "借方消費税率": debit_consumption_tax_rate,
        "借方金額": debit_amount,
        "借方消費税額": debit_consumption_tax_amount,
        "貸方科目コード": credit_code,
        "貸方科目名称": credit_name,
        "貸方補助コード": credit_supplementary_code,
        "貸方補助科目名称": credit_supplementary_name,
        "貸方部門コード": credit_department_code,
        "貸方部門名称": credit_department_name,
        "貸方課税区分": credit_tax_class,
        "貸方事業分類": credit_business_category,
        "貸方消費税処理方法": credit_consumption_tax_method,
        "貸方消費税率": credit_consumption_tax_rate,
        "貸方金額": credit_amount,
        "貸方消費税額": credit_consumption_tax_amount,
        "摘要": summary,
        "補助摘要": supplementary_summary,
        "メモ": memo,
        "付箋１": tag1,
        "付箋２": tag2,
        "伝票種別": slip_type,
    }


# Deserializers
def deserialize_account(account: AccountDict) -> types.Account:
    """Deserialize an account fetched from GnuCash."""
    return types.Account(
        guid=account["guid"],
        code=account["code"],
        name=account["name"],
        supplementary_code=account["supplementary_code"],
        supplementary_name=util.clean_text(account["supplementary_name"]),
    )


def deserialize_transaction(transaction: types.CsvRow) -> types.Transaction:
    """Deserialize a transaction."""
    return types.Transaction(
        guid=transaction["guid"],
        # TODO Use string format based parsing instead
        date=date.fromisoformat(transaction["post_date"].split(" ")[0]),
        description=util.clean_text(transaction["description"]),
    )
