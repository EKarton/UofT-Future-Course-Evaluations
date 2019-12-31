import psycopg2
from database import Database

class InstructorsTable(Database):
    def __init__(self, host, database_name, user, password):
        super().__init__(host, database_name, user, password, 'instructors')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS instructors(
                    instructor_id SERIAL PRIMARY KEY,
                    full_instructor_name VARCHAR(250) NOT NULL,
                    abbrev_instructor_name VARCHAR(250) NOT NULL
                );"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def insert_instructor_if_not_exist(self, full_instructor_name, abbrev_instructor_name):
        existing_instructor_id = self.get_instructor_id(full_instructor_name, abbrev_instructor_name)

        if existing_instructor_id is not None:
            return existing_instructor_id

        sql = """INSERT INTO instructors (full_instructor_name, abbrev_instructor_name) 
                 VALUES (%s, %s);"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (full_instructor_name, abbrev_instructor_name))
        cursor.close()

        self.connection.commit()

        return self.get_instructor_id(full_instructor_name, abbrev_instructor_name)

    def get_instructor_id(self, full_instructor_name, abbrev_instructor_name):
        sql = """SELECT instructor_id 
                        FROM instructors 
                        WHERE full_instructor_name = %s AND abbrev_instructor_name = %s;"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (full_instructor_name, abbrev_instructor_name))

        instructor_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            instructor_id = row[0]

        cursor.close()
        return instructor_id