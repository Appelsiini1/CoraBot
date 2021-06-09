# This script is used to alter the database during development so that alterations to things like tables can be made easily.


import sqlite3

with sqlite3.connect("Databases/database.db") as conn:
    c = conn.cursor()
    c.execute(
        """ALTER TABLE RolePolls_Votes
        ADD COLUMN Timestamp TEXT;"""
        )
    c.execute(
        """ALTER TABLE RolePolls
        ADD COLUMN Timestamp TEXT;"""
        )
    conn.commit()
