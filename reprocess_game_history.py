#!/usr/bin/env python

import sys

from sqlalchemy.orm import with_expression

from rcon.models import enter_session
from rcon.utils import MapsHistory
from rcon.workers import _record_stats

with enter_session() as sess:
    if not sys.argv[-1] == 'skiperase':
        sess.execute('truncate table map_history cascade')
        sess.commit()
    for m in MapsHistory():
        try:
            if m['start'] and m['end']:
                _record_stats(m)
        except Exception as e:
            print(f"Unable to process stats for {m}: {repr(2)}")
