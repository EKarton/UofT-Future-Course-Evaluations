import psycopg2
from database import Database

class CoursesTable(Database):
    def __init__(self, host, port, database_name, user, password):
        super().__init__(host, port, database_name, user, password, 'courses')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS courses(
                    course_id SERIAL PRIMARY KEY,
                    course_code VARCHAR(10) NOT NULL
                );"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

    def insert_course_if_not_exists(self, course_code):
        existing_course_id = self.get_course_id(course_code)

        if existing_course_id is not None:
            return existing_course_id

        sql = """INSERT INTO courses (course_code) 
                 VALUES (%s);"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (course_code, ))
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

        return self.get_course_id(course_code)

    def get_course_id(self, course_code):
        sql = """SELECT course_id 
                        FROM courses 
                        WHERE course_code = %s;"""

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (course_code, ))

        course_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            course_id = row[0]

        cursor.close()
        self.put_back_connection(connection)

        return course_id

