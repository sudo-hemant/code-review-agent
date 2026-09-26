import logging

log = logging.getLogger(__name__)


def push(client, record):
    client.send(record)
