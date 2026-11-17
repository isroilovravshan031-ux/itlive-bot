"""Create a consistent SQLite snapshot, including committed WAL records."""
import argparse
import sqlite3
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("destination", type=Path)
args = parser.parse_args()
source = args.source.resolve(strict=True)
destination = args.destination.resolve()
if source == destination or destination.exists():
    raise SystemExit("Choose a new destination file; existing data is never overwritten.")
destination.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as origin:
    with sqlite3.connect(destination) as target:
        origin.backup(target)
print("Consistent SQLite snapshot created.")
