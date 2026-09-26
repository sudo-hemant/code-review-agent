def spend_for(db, user_id):
    row = db.query("SELECT COALESCE(SUM(amount), 0) AS total FROM orders WHERE user_id = ?", (user_id,))
    return row["total"]
