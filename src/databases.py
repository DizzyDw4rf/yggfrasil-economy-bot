import sqlite3
from sqlite3 import Connection
from paths import DB_FILE


# Create connection to db file
def db_connection() -> Connection:
    conn = sqlite3.connect(DB_FILE)
    return conn

# Create User Table if not exists
def create_user_table() -> None:
    with db_connection() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS Users(
                id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                wallet INTEGER DEFAULT 500,
                bank INTEGER DEFAULT 500
            )
        """)

        conn.commit()

# Create Transaction Table if not exists
def create_transaction_table() -> None:
    with db_connection() as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS Transactions(
                TransactionsId INTEGER PRIMARY KEY AUTOINCREMENT,
                UserId INTEGER NOT NULL,
                Amount INTEGER NOT NULL,
                TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
                TransactionType TEXT NOT NULL, -- 'send' or 'receive'
                FOREIGN KEY (UserId) REFERENCES Users(id) ON DELETE CASCADE
            )"""
        )
        conn.commit()
