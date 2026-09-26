def get_by_id(db, user_id):
    return db.query("SELECT * FROM users WHERE id = ?", (user_id,))


def search(db, term):
    """Find users whose name contains the search term."""
    return db.query(f"SELECT * FROM users WHERE name LIKE '%{term}%'")
