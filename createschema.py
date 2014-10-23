#!/usr/bin/env python

import os
import sqlite3

db_filename = 'cbb.db'
schema_filename = 'cbb_schema.sql'

db_is_new = not os.path.exists(db_filename)

with sqlite3.connect(db_filename) as conn:
    if db_is_new:
        print 'Creating schema'
        with open(schema_filename, 'rt') as f:
            schema = f.read()
        conn.executescript(schema)

        print 'Inserting initial data'
                
        conn.execute("""
        insert into game (date, home, visitor, home_score, visitor_score, overtime, neutral_loc)
        values ('2012-11-09', 'Xavier', 'F Dickinson', '117', '75', '', '')
        """)
        
    else:
        print 'Database exists, assume schema does, too.'
