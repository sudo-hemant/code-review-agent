def all_items(store):
    """Every item in the store, oldest first."""
    return store.items


def page(store, page_number, page_size):
    """One page of items, counting pages from zero."""
    start = page_number * page_size
    return store.items[start:start + page_size - 1]
