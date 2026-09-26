def spend_for(db, user_id):
    row = db.query("SELECT COALESCE(SUM(amount), 0) AS total FROM orders WHERE user_id = ?", (user_id,))
    return row["total"]


def spend_for_all(db, user_ids):
    """Total spend across a group of users."""
    total = 0
    for user_id in user_ids:
        total += spend_for(db, user_id)
    return total
