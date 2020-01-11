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

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def insert_course_if_not_exists(self, course_code):
        existing_course_id = self.get_course_id(course_code)

        if existing_course_id is not None:
            return existing_course_id

        sql = """INSERT INTO courses (course_code) 
                 VALUES (%s);"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (course_code, ))
        cursor.close()

        self.connection.commit()

        return self.get_course_id(course_code)

    def get_course_id(self, course_code):
        sql = """SELECT course_id 
                        FROM courses 
                        WHERE course_code = %s;"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (course_code, ))

        course_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            course_id = row[0]

        cursor.close()
        return course_id

