#!/usr/bin/env python
"""
Parse a text file of college basketball scores.

<game> ::= <date> <winner> <loser> <opt-comment> <EOL>
<date> ::= <year>-<month>-<day>
<winner> ::= <opt-home> <team> <score>
<loser> ::= <opt-home> <team> <score>
<team> ::= <name> | <name> <sep> <team>

"""

from pyparsing import CharsNotIn, Word, delimitedList, Literal, Group, Optional
from pyparsing import lineEnd, nums, alphas, alphanums, printables, Suppress, ParseException

SPACE_CHARS = ' \t'
word = CharsNotIn(SPACE_CHARS)
space = Word(SPACE_CHARS, exact=1)
num = Word(nums)
home = Literal("@")

name = delimitedList(word, delim=space, combine=True)

date = delimitedList(num, delim='-', combine=True)
team = Group(Optional(home) + name + num)
comment = Optional(Word(alphanums, printables+" "))

game = date + team + team + comment + Suppress(lineEnd)

def parse(input, bnf=game):
  try:
    return bnf.parseString(input)
  except ParseException, err:
    print err.line
    print " "*(err.column-1) + "^"
    print err

def test():

    scores = """
2012-11-09  Connecticut              66  Michigan St              62         Armed Forces Classic Ramstein, Germany
2012-11-09 @St Bonaventure           65  Bethune-Cookman          55
2012-11-09 @Kent                     66  Drexel                   62 O1
2012-11-09  Bucknell                 70 @Purdue                   65
2012-11-09  St Peter's               56 @Rutgers                  52          
2012-11-09 @William & Mary           69  Hampton                  51
""".strip()

    print scores
    for line in scores.split('\n'):
        tokens = parse(line, game)
        print "tokens = ", tokens


if __name__ == "__main__":

    import os
    import sqlite3

    db_filename = 'cbb.db'
    schema_filename = 'cbb_schema.sql'
    file_name = 'cb2013'

    insert_txt = 'insert into game (date, winner, loser, winner_score, loser_score, location, comments) values ("%s", "%s", "%s", "%s", "%s", "%s", "%s")'

    db_is_new = not os.path.exists(db_filename)

    with sqlite3.connect(db_filename) as conn:
        if db_is_new:
            print 'Creating schema'
            with open(schema_filename, 'rt') as f:
                schema = f.read()
            conn.executescript(schema)        
        else:
            print 'Database exists, assume schema does, too.'

        with open(file_name, "r") as f:
            for line in f:
                tokens = parse(line, game)
                date = tokens.pop(0)
                winner = tokens.pop(0)
                loser = tokens.pop(0)
                comments = None
                if tokens:
                    comments = tokens.pop()

                location = 'Neutral'
                if len(winner) == 3:
                    winner.pop(0)
                    location = winner[0]
                
                if len(loser) == 3:
                    loser.pop(0)
                    location = loser[0]

                    
                winning_team, winning_score = winner
                losing_team, losing_score = loser

                insert = insert_txt % (date, winning_team, losing_team, winning_score, losing_score, location, comments)
                print insert

                conn.execute(insert)
    
    