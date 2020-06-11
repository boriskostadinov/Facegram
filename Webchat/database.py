import sqlite3

DB_NAME = 'webchat.db'

conn = sqlite3.connect(DB_NAME)

conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS users 
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        name TEXT NOT NULL UNIQUE,
        address TEXT NOT NULL,
        mobile TEXT NOT NULL
    )
''')

conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS follow 
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL ,
        user_id2 INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (user_id2) REFERENCES users(id)
        
    )
''')

conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS advertisements
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL,
        date TEXT NOT NULL,
        active INTEGER NOT NULL,
        buyer_id INTEGER,
        seller_id INTEGER NOT NULL,
        FOREIGN KEY(buyer_id) REFERENCES users(id),
        FOREIGN KEY(seller_id) REFERENCES users(id)
    )
''')



conn.commit()

class DB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
