-- Schema for cbb application examples.

-- Games are the result of a single game
create table game (
    id            integer primary key autoincrement not null,
    date          date,
    winner        text,
    loser         text,
    winner_score  text,
    loser_score   text,
    location      text,
    comments      text
);
