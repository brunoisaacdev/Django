from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template


register = template.Library()


@register.filter
def brl(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        amount = Decimal("0")

    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)

    integer_part, decimal_part = f"{amount:.2f}".split(".")
    groups = []

    while integer_part:
        groups.insert(0, integer_part[-3:])
        integer_part = integer_part[:-3]

    return f"R$ {sign}{'.'.join(groups)},{decimal_part}"
