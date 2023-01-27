"""Build journal entries."""
from datetime import (
    date,
)
from decimal import (
    Decimal,
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
    伝票番号: str,
    伝票日付: date,
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
) -> JournalEntry:
    """Make a JournalEntry."""
    return JournalEntry(
        伝票番号=伝票番号,
        行番号="1",
        伝票日付=util.format_date(伝票日付),
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
        摘要="",
        補助摘要="",
        メモ=メモ,
        付箋１="0",
        付箋２="0",
        伝票種別="0",
    )


def build_simple_journal_entry(
    number: str, debit: Split, credit: Split
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
    return make_journal_entry(
        伝票番号=number,
        伝票日付=date,
        借方科目コード=debit.account.account,
        借方科目名称=debit.account.account,
        借方補助コード=debit.account.account_supplementary,
        借方補助科目名称=debit.account.account_supplementary_name,
        借方金額=debit.value,
        借方消費税額=Decimal("0"),
        貸方科目コード=credit.account.account,
        貸方科目名称=credit.account.account_name,
        貸方補助コード=credit.account.account_supplementary,
        貸方補助科目名称=credit.account.account_supplementary_name,
        貸方金額=credit.value,
        貸方消費税額=Decimal("0"),
        メモ=memo,
    )


def build_composite_journal_entry(
    counter: JournalEntryCounter,
    debits: TransactionSplit,
    credits: TransactionSplit,
) -> JournalEntries:
    """Build a composite journal entry using the 複合 intermediary."""
    result = []
    # Scenario one, one credit split that funds n debit splits
    if len(debits) > len(credits):
        assert len(credits) == 1
        larger_side = debits
        smaller_side = credits[0]
        # Magic variable, do not touch
        swap = True
    # Scenario two, one debit split that funds n credit splits
    else:
        assert len(debits) == 1, f"{debits} {credits}"
        larger_side = credits
        smaller_side = debits[0]
        # Magic variable, do not touch
        swap = False
    for entry in larger_side:
        value = abs(entry.value)
        number = next(counter)
        memo = " ".join(
            [
                entry.transaction.description,
                entry.memo,
                smaller_side.memo,
            ]
        ).replace("\xa0", " ")
        d = JournalEntry(
            伝票番号=str(number),
            行番号="1",
            伝票日付=util.format_date(entry.transaction.date),
            借方科目コード=entry.account.account
            if swap
            else smaller_side.account.account,
            借方科目名称=entry.account.account_name
            if swap
            else smaller_side.account.account_name,
            借方補助コード=entry.account.account_supplementary
            if swap
            else smaller_side.account.account_supplementary,
            借方補助科目名称=entry.account.account_supplementary_name
            if swap
            else smaller_side.account.account_supplementary_name,
            借方部門コード="0",
            借方部門名称="",
            借方課税区分="0",
            借方事業分類="0",
            借方消費税処理方法="3",
            借方消費税率="0%",
            借方金額=value,
            借方消費税額=Decimal("0"),
            貸方科目コード=smaller_side.account.account
            if swap
            else entry.account.account,
            貸方科目名称=smaller_side.account.account_name
            if swap
            else entry.account.account_name,
            貸方補助コード=smaller_side.account.account_supplementary
            if swap
            else entry.account.account_supplementary,
            貸方補助科目名称=smaller_side.account.account_supplementary_name
            if swap
            else entry.account.account_supplementary_name,
            貸方部門コード="0",
            貸方部門名称="",
            貸方課税区分="",
            貸方事業分類="0",
            貸方消費税処理方法="3",
            貸方消費税率="0%",
            貸方金額=value,
            貸方消費税額=Decimal("0"),
            摘要="",
            補助摘要="",
            メモ=memo,
            付箋１="0",
            付箋２="0",
            伝票種別="0",
        )
        result.append(d)
    return result


def build_journal_entries(
    counter: JournalEntryCounter, tx: TransactionSplit
) -> JournalEntries:
    """Build journal entries given a transaction."""
    assert len(tx) > 1
    assert sum(split.value for split in tx) == Decimal(0), tx
    debits = list(util.get_debits(tx))
    credits = list(util.get_credits(tx))
    if len(debits) == 1 and len(credits) == 1:
        # Simple split
        (debit,) = debits
        (credit,) = credits
        return [build_simple_journal_entry(str(next(counter)), debit, credit)]
        # Compound split
    else:
        return build_composite_journal_entry(counter, debits, credits)
