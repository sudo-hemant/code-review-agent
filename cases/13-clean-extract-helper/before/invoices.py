def net_total(lines):
    return sum(line["amount"] for line in lines if not line["voided"])


def vat_total(lines):
    return sum(line["amount"] * 0.2 for line in lines if not line["voided"])
