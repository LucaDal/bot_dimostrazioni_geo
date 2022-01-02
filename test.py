import dataBase as db
import os
import sys


def delete_table():
    os.remove("user_dim_tables.db")
    print("ok")


def print_t():
    conn = db.create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_dim_done")
    value = cur.fetchall()
    for val in value:
        print(val)
    cur.execute("SELECT * FROM dim_difficulty")
    value = cur.fetchall()
    for val in value:
        print(val)


def create():
    if not os.path.exists("./user_dim_tables.db"):
        f = open('user_dim_tables.db', 'w')
        f.close()
        db.call_create_tables()


def query():
    conn = db.create_connection()
    if conn is None:
        print("connessione non riuscita")
    cur = conn.cursor()
    to_debug = "DELETE from user_dim_done where id_user = 461718130"
    try:
        cur.execute(to_debug)
    except db.Error as er:
        print(er)
    val = cur.fetchall()
    print("risultati: ")
    print(val)
    conn.commit()
    cur.close()
    conn.close()


def main():
    arguments = sys.argv
    if len(arguments) != 2:
        exit(1)
    try:
        print(globals().get(arguments[1])())
    except:
        exit(1)


if __name__ == "__main__":
    main()
