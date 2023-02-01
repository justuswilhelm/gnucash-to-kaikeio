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
    Account,
    ConsumptionTaxRate,
    JournalEntries,
    JournalEntry,
    JournalEntryCounter,
    Split,
    TransactionSplit,
)


# Maybe we can have an account / amount tuple here?
def make_journal_entry(
    slip_number: int,
    line_number: int,
    slip_date: date,
    debit_account: Optional[Account],
    credit_account: Optional[Account],
    debit_amount: Optional[Decimal],
    credit_amount: Optional[Decimal],
    description: Optional[str],
    description_supplementary: Optional[str],
) -> JournalEntry:
    """Make a JournalEntry."""
    if debit_account:
        debit_code = debit_account.code
        debit_name = debit_account.name
        debit_supplementary_code = debit_account.supplementary_code
        debit_supplementary_name = debit_account.supplementary_name
    else:
        debit_code = None
        debit_name = None
        debit_supplementary_code = None
        debit_supplementary_name = None
    if credit_account:
        credit_code = credit_account.code
        credit_name = credit_account.name
        credit_supplementary_code = credit_account.supplementary_code
        credit_supplementary_name = credit_account.supplementary_name
    else:
        credit_code = None
        credit_name = None
        credit_supplementary_code = None
        credit_supplementary_name = None

    # XXX redundant
    if debit_amount:
        assert debit_amount >= 0
        debit_amount = debit_amount
    else:
        debit_amount = Decimal(0)
    if credit_amount:
        assert credit_amount >= 0
        credit_amount = credit_amount
    else:
        credit_amount = Decimal(0)

    memo = f"Exported {date.today().isoformat()} from GnuCash"

    return JournalEntry(
        slip_number=slip_number,
        line_number=line_number or 1,
        slip_date=slip_date,
        debit_code=debit_code,
        debit_name=debit_name,
        debit_supplementary_code=debit_supplementary_code,
        debit_supplementary_name=debit_supplementary_name,
        debit_department_code="0",
        debit_department_name="",
        debit_tax_class="0",
        debit_business_category="0",
        debit_consumption_tax_method="3",
        debit_consumption_tax_rate=ConsumptionTaxRate.ZERO,
        debit_amount=debit_amount,
        debit_consumption_tax_amount=Decimal("0"),
        credit_code=credit_code,
        credit_name=credit_name,
        credit_supplementary_code=credit_supplementary_code,
        credit_supplementary_name=credit_supplementary_name,
        credit_department_code="0",
        credit_department_name="",
        credit_tax_class="",
        credit_business_category="0",
        credit_consumption_tax_method="3",
        credit_consumption_tax_rate=ConsumptionTaxRate.ZERO,
        credit_amount=credit_amount,
        credit_consumption_tax_amount=Decimal("0"),
        summary=description,
        supplementary_summary=description_supplementary,
        memo=memo,
        # Set it to blue
        tag1="3",
        tag2="0",
        slip_type="0",
    )


def build_simple_journal_entry(
    slip_number: int,
    line_number: int,
    debit: Optional[Split],
    credit: Optional[Split],
) -> JournalEntry:
    """Build a simple journal entry."""
    description_supplementary_parts = []
    debit_account = None
    debit_amount = None
    credit_account = None
    credit_amount = None

    if debit:
        date = debit.transaction.date
        description = debit.transaction.description
        debit_account = debit.account
        debit_amount = debit.value
        if debit.memo:
            description_supplementary_parts.append(debit.memo)

    if credit:
        date = credit.transaction.date
        description = credit.transaction.description
        credit_account = credit.account
        credit_amount = abs(credit.value)
        if credit.memo:
            description_supplementary_parts.append(credit.memo)

    description_supplementary = util.clean_text(
        " ".join(description_supplementary_parts)
    )

    return make_journal_entry(
        slip_number=slip_number,
        line_number=line_number,
        slip_date=date,
        debit_account=debit_account,
        credit_account=credit_account,
        debit_amount=debit_amount,
        credit_amount=credit_amount,
        description=util.clean_text(description),
        description_supplementary=description_supplementary,
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
    assert len(tx) > 1, tx
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
