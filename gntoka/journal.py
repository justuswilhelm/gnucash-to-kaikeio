"""Build journal entries."""
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from itertools import (
    count,
)
from typing import (
    Optional,
)

from . import (
    util,
)
from .constants import (
    KAIKEIO_NO_ACCOUNT,
)
from .types import (
    Account,
    ConsumptionTaxRate,
    JournalEntries,
    JournalEntry,
    JournalEntryCounter,
    Split,
    TransactionSplit,
)


def make_journal_entry(
    slip_number: int,
    line_number: int,
    slip_date: date,
    debit_account: Optional[Account],
    credit_account: Optional[Account],
    debit_amount: Optional[Decimal],
    credit_amount: Optional[Decimal],
    description: str,
    description_supplementary: str,
) -> JournalEntry:
    """Make a JournalEntry."""
    if debit_account:
        借方科目コード = debit_account.account
        借方科目名称 = debit_account.account_name
        借方補助コード = debit_account.account_supplementary
        借方補助科目名称 = debit_account.account_supplementary_name
    else:
        借方科目コード = KAIKEIO_NO_ACCOUNT
        借方科目名称 = ""
        借方補助コード = KAIKEIO_NO_ACCOUNT
        借方補助科目名称 = ""
    if credit_account:
        貸方科目コード = credit_account.account
        貸方科目名称 = credit_account.account_name
        貸方補助コード = credit_account.account_supplementary
        貸方補助科目名称 = credit_account.account_supplementary
    else:
        貸方科目コード = KAIKEIO_NO_ACCOUNT
        貸方科目名称 = ""
        貸方補助コード = KAIKEIO_NO_ACCOUNT
        貸方補助科目名称 = ""

    # XXX redundant
    if debit_amount:
        assert debit_amount >= 0
        借方金額 = debit_amount
    else:
        借方金額 = Decimal(0)
    if credit_amount:
        assert credit_amount >= 0
        貸方金額 = credit_amount
    else:
        貸方金額 = Decimal(0)

    return JournalEntry(
        slip_number=slip_number,
        line_number=line_number or 1,
        slip_date=slip_date,
        借方科目コード=借方科目コード,
        借方科目名称=借方科目名称,
        借方補助コード=借方補助コード,
        借方補助科目名称=借方補助科目名称,
        借方部門コード="0",
        借方部門名称="",
        借方課税区分="0",
        借方事業分類="0",
        借方消費税処理方法="3",
        借方消費税率=ConsumptionTaxRate.ZERO,
        借方金額=借方金額,
        借方消費税額=Decimal("0"),
        貸方科目コード=貸方科目コード,
        貸方科目名称=貸方科目名称,
        貸方補助コード=貸方補助コード,
        貸方補助科目名称=貸方補助科目名称,
        貸方部門コード="0",
        貸方部門名称="",
        貸方課税区分="",
        貸方事業分類="0",
        貸方消費税処理方法="3",
        貸方消費税率=ConsumptionTaxRate.ZERO,
        貸方金額=貸方金額,
        貸方消費税額=Decimal("0"),
        # XXX This should have the description
        摘要=description,
        # XXX This should have the memo
        補助摘要=description_supplementary,
        # Maybe insert the conversion date here?
        メモ="",
        付箋１="0",
        付箋２="0",
        伝票種別="0",
    )


def build_simple_journal_entry(
    slip_number: int,
    line_number: int,
    debit: Optional[Split],
    credit: Optional[Split],
) -> JournalEntry:
    """Build a simple journal entry."""
    memo_parts = []
    if debit:
        date = debit.transaction.date
        description = debit.transaction.description
        amount = debit.value
        memo_parts.append(debit.memo)
    elif credit:
        date = credit.transaction.date
        description = credit.transaction.description
        amount = abs(credit.value)
        memo_parts.append(credit.memo)
    # TODO figure out how to check this at compile time
    else:
        raise ValueError("Either debit or credit must not be None")
    memo = util.clean_text(" ".join(memo_parts))

    return make_journal_entry(
        slip_number=slip_number,
        line_number=line_number,
        slip_date=date,
        debit_account=debit.account if debit else None,
        credit_account=credit.account if credit else None,
        debit_amount=amount,
        credit_amount=amount,
        description=description,
        description_supplementary=memo,
    )


def build_composite_journal_entry(
    slip_number: int,
    debits: TransactionSplit,
    credits: TransactionSplit,
) -> JournalEntries:
    """Build a composite journal entry using the 複合 intermediary."""
    line_number = count(1)
    result = []
    for debit in debits:
        entry = build_simple_journal_entry(
            slip_number=slip_number,
            line_number=next(line_number),
            debit=debit,
            credit=None,
        )
        result.append(entry)
    for credit in credits:
        entry = build_simple_journal_entry(
            slip_number=slip_number,
            line_number=next(line_number),
            debit=None,
            credit=credit,
        )
        result.append(entry)
    return result


def build_journal_entries(
    counter: JournalEntryCounter, tx: TransactionSplit
) -> JournalEntries:
    """Build journal entries given a transaction."""
    assert len(tx) > 1
    assert sum(split.value for split in tx) == Decimal(0), tx
    debits = list(util.get_debits(tx))
    credits = list(util.get_credits(tx))
    slip_number = next(counter)
    if len(debits) == 1 and len(credits) == 1:
        # Simple split
        (debit,) = debits
        (credit,) = credits
        return [build_simple_journal_entry(slip_number, 1, debit, credit)]
        # Compound split
    else:
        return build_composite_journal_entry(slip_number, debits, credits)
