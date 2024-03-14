import sqlite3

with sqlite3.connect('maintenance.db') as db:
    cur = db.cursor()
    id = 1
    cur.execute("""SELECT * FROM report WHERE report_id=%d""" % int(id))
for db in cur.fetchall():
    print(db)
