# This script is used to add the 'Tracked' table to the bots database as the bot needs the table before it can initialize the others.
# Execute this before starting the bot. This only needs to be done once though.


import sqlite3

with sqlite3.connect("Databases/database.db") as conn:
    c = conn.cursor()
    c.execute(
            """CREATE TABLE IF NOT EXISTS Tracked(
            Channel_ID INT,
            Guild_ID INT,
            Type INT,
            PRIMARY KEY (Channel_ID)
        );"""
        )
    # c.execute(
    #     """ALTER TABLE Quotes
    #     ADD COLUMN Quote_text TEXT;"""
    #     )
    conn.commit()
