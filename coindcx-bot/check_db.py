import sqlite3

conn = sqlite3.connect("data/bot.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM trades")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM trades WHERE status='open'")
open_ = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM trades WHERE status='closed'")
closed = cur.fetchone()[0]
print(f"Trades: {total} total, {open_} open, {closed} closed")

cur.execute("SELECT COUNT(*) FROM trade_logs")
print(f"Trade logs: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM performance_metrics")
print(f"Performance metrics: {cur.fetchone()[0]}")

conn.close()
