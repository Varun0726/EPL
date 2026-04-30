import psycopg2
from pathlib import Path

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "dbname": "All_matches",
    "user": "postgres",
    "password": "V@run8118"
}

CSV_FILE = Path("data/all_matches.csv")

def import_csv():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        with open(CSV_FILE, "r", encoding="utf-8") as f:
            sql = """
                COPY matches_staging (
                    match_date_text,
                    match_time,
                    comp,
                    round,
                    day,
                    venue,
                    result,
                    gf,
                    ga,
                    opponent,
                    poss,
                    attendance,
                    captain,
                    formation,
                    opp_formation,
                    referee,
                    match_report,
                    notes,
                    team_name
                )
                FROM STDIN
                WITH (FORMAT CSV, HEADER true)
            """
            cur.copy_expert(sql, f)

        conn.commit()
        print("CSV imported successfully into matches_staging.")

    except Exception as e:
        if conn:
            conn.rollback()
        print("Import failed:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    import_csv()
