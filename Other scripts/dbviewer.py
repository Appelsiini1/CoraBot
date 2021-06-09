import sqlite3

def main():
    with sqlite3.connect("Databases/database.db") as conn:
        c = conn.cursor()

        table = input("Table to search from: ")
        whereToSearch = input("Search paramiters: ")
        toFile = input("Print output to file? Y/N: ").upper()

        SQL_clause = f"SELECT * FROM {table.strip()}"
        if whereToSearch.strip() != "":
            SQL_clause += f" WHERE {whereToSearch.strip()}"

        c.execute(SQL_clause)
        result = c.fetchall()

        if toFile.strip() == "Y":
            with open("result.txt", "w", encoding="utf-8") as fi:
                for r in result:
                    for t in r:
                        fi.write(str(t) + ";")
                        fi.write("\n")

        else:
            for r in result:
                print(r)


main()