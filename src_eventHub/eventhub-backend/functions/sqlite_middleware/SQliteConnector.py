import sqlite3
from sqlite3 import Error


class SQliteConnector:

    def __init__(self):
        self.connection = None

    def create_connection(self, db_file=r"C:\dev\consistencyManager\src_eventHub\eventhub-backend\eventhub-db.db"):
        """ create a database connection to the SQLite database
            specified by the db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print(e)

        self.connection = conn
        return conn

    def run_sql_command(self, command: str):
        """
        Query tasks by priority
        :param command:
        :return:
        """
        with self.connection as con:
            cur = con.cursor()
            cur.execute(command)

            rows = cur.fetchall()

        return rows

    def close_connection(self):
        self.connection = None
        # ToDo: To be refined.
