import logging

log = logging.getLogger(__name__)


def push(client, record):
    client.send(record)


def push_all(client, records):
    """Send every record, carrying on past any that fail."""
    for record in records:
        try:
            client.send(record)
        except Exception:
            pass
