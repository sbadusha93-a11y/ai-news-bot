import sqlite3

conn = sqlite3.connect("data/bot.db")
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
for t in tables:
    print(f"Table: {t[0]}")
    cur.execute(f"PRAGMA table_info(\"{t[0]}\")")
    cols = cur.fetchall()
    for c in cols:
        print(f"  {c[1]} ({c[2]})")
    print()

conn.close()
