import sqlite3
from sqlite3 import Error


def create_connection():
    db_file = r"user_dim_tables.db"
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def sql_table_statment(conn):
    user_dim_done = """ CREATE TABLE IF NOT EXISTS user_dim_done (
                                  id integer PRIMARY KEY,
                                  id_user integer NOT NULL,
                                  id_dim integer NOT NULL,
                                  difficulty varchar
                                  );
                                  """
    dim_dif = """CREATE TABLE IF NOT EXISTS dim_difficulty(
                    id_user integer,
                    id_dim integer,
                    PRIMARY KEY(id_user,id_dim)
                    );"""
    try:
        deploy_tables(conn, user_dim_done)
        deploy_tables(conn, dim_dif)
    except Error as e:
        print(e)
    print("tabelle create")


def is_user_dif_on_db(conn, id_user, id_dim) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM dim_difficulty WHERE ? = id_user AND ? = id_dim", (id_user, id_dim))
    value = cur.fetchall()
    if value[0][0] == 1:
        return True
    return False


def insert_user_dif(conn, id_user, id_dim):
    sql = "INSERT INTO dim_difficulty VALUES(?,?)"
    deploy_commit(conn, sql, (id_user, id_dim))


def update_user_difficulty(conn, id_user, id_dim):
    if is_user_dif_on_db(conn, id_user, id_dim):
        sql = "DELETE from dim_difficulty WHERE ? = id_user AND ? = id_dim"
        deploy_commit(conn, sql, (id_user, id_dim))
        return False
    else:
        insert_user_dif(conn, id_user, id_dim)
        return True


def is_user_dim_done(conn, id_user, id_dim) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) FROM user_dim_done WHERE ? = id_user AND ? = id_dim", (id_user, id_dim))
    value = cur.fetchall()
    if value[0][0] >= 1:
        return True
    return False


def insert_user_dim_into_db(conn, id_user, id_dim):
    sql = '''INSERT INTO user_dim_done(id_user,id_dim) VALUES(?,?) '''
    deploy_commit(conn, sql, (id_user, id_dim))


def get_difficult_dim(conn,id_user):
    cur = conn.cursor()
    cur.execute("SELECT id_dim FROM dim_difficulty WHERE ? = id_user ", (id_user,))
    return cur.fetchall()


def get_done_dim(conn, id_user) -> list:
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT id_dim FROM user_dim_done WHERE ? = id_user ", (id_user,))
    return cur.fetchall()


def delete_user_dim(conn, id_user):
    sql = "DELETE from user_dim_done where id_user = ?"
    deploy_commit(conn, sql, (id_user,))


def execute_sql_without_commit(conn, sql, obg):
    """
    :param conn:
    :param sql: query
    :param obg: tuple with value to insert into the query
    :return: the list fetched
    """
    cur = conn.cursor()
    cur.execute(sql, obg)
    return cur.fetchall()


def deploy_commit(conn, sql, obg):
    cur = conn.cursor()
    cur.execute(sql, obg)
    conn.commit()


def deploy_tables(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
    except Error as e:
        print(e)


def call_create_tables():
    conn = create_connection()
    if conn is not None:
        print("sto creando le tabelle")
        sql_table_statment(conn)
    else:
        print("Error! cannot create the database connection.")
