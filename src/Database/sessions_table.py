import psycopg2
from database import Database

class SessionsTable(Database):
    def __init__(self, host, port, database_name, user, password):
        super().__init__(host, port, database_name, user, password, 'sessions')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS sessions(
                    session_id SERIAL PRIMARY KEY,
                    term VARCHAR(250) NOT NULL,
                    year INTEGER NOT NULL
                );"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def insert_session_if_not_exists(self, term, year):
        existing_session_id = self.get_session_id(term, year)

        if existing_session_id is not None:
            return existing_session_id

        sql = """INSERT INTO sessions (term, year) 
                 VALUES (%s, %s);"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (term, year))
        cursor.close()

        self.connection.commit()

        return self.get_session_id(term, year)

    def get_session_id(self, term, year):
        sql = """SELECT session_id 
                        FROM sessions 
                        WHERE term = %s AND year = %s;"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (term, year))

        session_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            session_id = row[0]

        cursor.close()
        return session_id