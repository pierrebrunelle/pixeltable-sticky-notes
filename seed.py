"""Seed a handful of sticky notes.

Usage:
    python seed.py            # seeds the local `notes` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'notes'
HERE = Path(__file__).resolve().parent

SEED = {
    'notes': [
        {'title': 'Groceries', 'body': 'oat milk, lemons, basil\nmaybe sourdough', 'tag': 'home'},
        {'title': 'Standup', 'body': 'Demo the notes API, then review the schema change', 'tag': 'work'},
        {'title': 'Gift ideas', 'body': 'Film camera for Sam; a good chef knife for Lee', 'tag': 'home'},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
