import psycopg2
from database import Database

class DeptsTable(Database):

    def __init__(self, host, port, database_name, user, password):
        super().__init__(host, port, database_name, user, password, 'depts')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS depts(
                    dept_id SERIAL PRIMARY KEY,
                    dept_code VARCHAR(250) NOT NULL
                );"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

    def insert_dept_if_not_exists(self, dept_code):
        existing_dept_id = self.get_dept_id(dept_code)

        if existing_dept_id is not None:
            return existing_dept_id
        
        sql = """INSERT INTO depts (dept_code) 
                VALUES (%s);"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (dept_code, ))
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

        return self.get_dept_id(dept_code)

    def get_dept_id(self, dept_code):
        sql = """SELECT dept_id 
                        FROM depts
                        WHERE dept_code = %s;"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (dept_code, ))

        dept_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            dept_id = row[0]

        cursor.close()
        self.put_back_connection(connection)
        
        return dept_id

