from pathlib import Path

UPLOAD_DIR = Path("/srv/uploads")


def list_uploads():
    return sorted(p.name for p in UPLOAD_DIR.iterdir())


def read_upload(filename):
    """Return the contents of an uploaded file by name."""
    return (UPLOAD_DIR / filename).read_text()
