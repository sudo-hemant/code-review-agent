def subtotal(items):
    return sum(item["price"] * item["quantity"] for item in items)


def apply_discount(total, code):
    """Knock money off a total according to a discount code."""
    if code == "HALF":
        return total / 2
    if code == "TENNER":
        return max(total - 10, 0)
    return total
