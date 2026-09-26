from pricing import subtotal


def test_subtotal_adds_up():
    items = [{"price": 10, "quantity": 2}, {"price": 5, "quantity": 1}]
    assert subtotal(items) == 25
