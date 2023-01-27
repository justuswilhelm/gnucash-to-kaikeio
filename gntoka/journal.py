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
from .types import (
    JournalEntries,
    JournalEntry,
    JournalEntryCounter,
    Split,
    TransactionSplit,
)


def make_journal_entry(
    slip_number: int,
    slip_date: date,
    借方科目コード: str,
    借方科目名称: str,
    借方補助コード: str,
    借方補助科目名称: str,
    借方金額: Decimal,
    借方消費税額: Decimal,
    貸方科目コード: str,
    貸方科目名称: str,
    貸方補助コード: str,
    貸方補助科目名称: str,
    貸方金額: Decimal,
    貸方消費税額: Decimal,
    メモ: str,
    line_number: Optional[int] = None,
) -> JournalEntry:
    """Make a JournalEntry."""
    return JournalEntry(
        slip_number=slip_number,
        line_number=str(line_number) if line_number else "1",
        slip_date=util.format_date(slip_date),
        借方科目コード=借方科目コード,
        借方科目名称=借方科目名称,
        借方補助コード=借方補助コード,
        借方補助科目名称=借方補助科目名称,
        借方部門コード="0",
        借方部門名称="",
        借方課税区分="0",
        借方事業分類="0",
        借方消費税処理方法="3",
        借方消費税率="0%",
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
        貸方消費税率="0%",
        貸方金額=貸方金額,
        貸方消費税額=貸方消費税額,
        # XXX This should have the description
        摘要="",
        # XXX This should have the memo
        補助摘要="",
        メモ=メモ,
        付箋１="0",
        付箋２="0",
        伝票種別="0",
    )


def build_simple_journal_entry(
    number: int, debit: Split, credit: Split
) -> JournalEntry:
    """Build a simple journal entry."""
    date = credit.transaction.date
    memo = " ".join(
        [
            credit.transaction.description,
            credit.memo,
            debit.memo,
        ]
    ).replace("\xa0", " ")
    value = max(debit.value, credit.value)
    tax = Decimal("0")
    return make_journal_entry(
        slip_number=number,
        slip_date=date,
        借方科目コード=debit.account.account,
        借方科目名称=debit.account.account,
        借方補助コード=debit.account.account_supplementary,
        借方補助科目名称=debit.account.account_supplementary_name,
        借方金額=value,
        借方消費税額=tax,
        貸方科目コード=credit.account.account,
        貸方科目名称=credit.account.account_name,
        貸方補助コード=credit.account.account_supplementary,
        貸方補助科目名称=credit.account.account_supplementary_name,
        貸方金額=value,
        貸方消費税額=tax,
        メモ=memo,
    )


def build_composite_journal_entry(
    number: int,
    debits: TransactionSplit,
    credits: TransactionSplit,
) -> JournalEntries:
    """Build a composite journal entry using the 複合 intermediary."""
    line_number = count(1)
    result = []
    for debit in debits:
        # TODO
        # We can just use build_simple_journal_entry and substitute credit
        # for 複合
        memo = " ".join(
            [
                debit.transaction.description,
                debit.memo,
            ]
        )
        entry = make_journal_entry(
            slip_number=number,
            slip_date=debit.transaction.date,
            借方科目コード=debit.account.account,
            借方科目名称=debit.account.account,
            借方補助コード=debit.account.account_supplementary,
            借方補助科目名称=debit.account.account_supplementary_name,
            借方金額=debit.value,
            借方消費税額=Decimal("0"),
            貸方科目コード="",
            貸方科目名称="",
            貸方補助コード="",
            貸方補助科目名称="",
            貸方金額=debit.value,
            貸方消費税額=Decimal("0"),
            メモ=memo,
            line_number=next(line_number),
        )
        result.append(entry)
    for credit in debits:
        # TODO
        # We can just use build_simple_journal_entry and substitute credit
        # for 複合
        memo = " ".join(
            [
                credit.transaction.description,
                credit.memo,
            ]
        )
        entry = make_journal_entry(
            slip_number=number,
            slip_date=credit.transaction.date,
            借方科目コード=credit.account.account,
            借方科目名称=credit.account.account,
            借方補助コード=credit.account.account_supplementary,
            借方補助科目名称=credit.account.account_supplementary_name,
            借方金額=credit.value,
            借方消費税額=Decimal("0"),
            貸方科目コード="",
            貸方科目名称="",
            貸方補助コード="",
            貸方補助科目名称="",
            貸方金額=Decimal(0),
            貸方消費税額=Decimal("0"),
            メモ=memo,
            line_number=next(line_number),
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
    number = next(counter)
    if len(debits) == 1 and len(credits) == 1:
        # Simple split
        (debit,) = debits
        (credit,) = credits
        return [build_simple_journal_entry(number, debit, credit)]
        # Compound split
    else:
        return build_composite_journal_entry(number, debits, credits)
