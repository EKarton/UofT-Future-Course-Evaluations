import psycopg2
from database import Database

class EvaluationsTable(Database):
    def __init__(self, host, database_name, user, password):
        super().__init__(host, database_name, user, password, 'evaluations')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS evaluations(
                    evaluation_id SERIAL PRIMARY KEY,
                    dept_id INTEGER REFERENCES depts(dept_id),
                    course_id INTEGER REFERENCES courses(course_id),
                    session_id INTEGER REFERENCES sessions(session_id),
                    instructor_id INTEGER REFERENCES instructors(instructor_id),
                    cat_1 float8 NOT NULL,
                    cat_2 float8 NOT NULL,
                    cat_3 float8 NOT NULL,
                    cat_4 float8 NOT NULL,
                    cat_5 float8 NOT NULL,
                    cat_6 float8 NOT NULL,
                    cat_7 float8 NOT NULL,
                    cat_8 float8 NOT NULL,
                    num_responded INTEGER NOT NULL,
                    num_invited INTEGER NOT NULL
                );"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def insert_evaluation(self, dept_id, course_id, session_id, instructor_id, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8, num_responded, num_invited):
        sql = """INSERT INTO evaluations (dept_id, course_id, session_id, instructor_id, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8, num_responded, num_invited) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (dept_id, course_id, session_id, instructor_id, cat_1, cat_2, cat_3, cat_4, cat_5, cat_6, cat_7, cat_8, num_responded, num_invited))
        cursor.close()

        self.connection.commit()