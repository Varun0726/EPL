DROP TABLE IF EXISTS matches_staging;

CREATE TABLE matches_staging (
    match_date_text TEXT,
    match_time TEXT,
    comp TEXT,
    round TEXT,
    day TEXT,
    venue TEXT,
    result TEXT,
    gf TEXT,
    ga TEXT,
    opponent TEXT,
    poss TEXT,
    attendance TEXT,
    captain TEXT,
    formation TEXT,
    opp_formation TEXT,
    referee TEXT,
    match_report TEXT,
    notes TEXT,
    team_name TEXT
);


Select *
From matches_staging

