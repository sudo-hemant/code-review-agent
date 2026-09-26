import json


def parse_line(line):
    return json.loads(line)


def load_errors(path):
    """Every error entry in a log file."""
    lines = open(path).read().splitlines()
    return [parse_line(line) for line in lines if '"error"' in line]
