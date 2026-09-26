VAT_RATE = 0.2


def _live_lines(lines):
    """The lines that still count, ignoring anything voided."""
    return [line for line in lines if not line["voided"]]


def net_total(lines):
    return sum(line["amount"] for line in _live_lines(lines))


def vat_total(lines):
    return sum(line["amount"] * VAT_RATE for line in _live_lines(lines))
