import sqlite3
con = sqlite3.connect("db.sqlite")
cur = con.cursor()
cur.execute("create table if not exists notes(id integer primary key, body text)")
cur.execute("insert into notes(body) values (?)", ("Hello from SQLite via MCP!",))
con.commit()
con.close()
print("db.sqlite ready.")
