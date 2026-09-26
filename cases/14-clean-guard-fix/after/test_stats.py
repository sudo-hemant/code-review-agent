from stats import average


def test_average():
    assert average([2, 4]) == 3


def test_average_of_nothing_is_none():
    assert average([]) is None
