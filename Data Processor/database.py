import psycopg2

class Database():
    def __init__(self, host='localhost', database_name='my_db', user='superuser', password='pass', table_name=''):
        self.connection = None
        self.host = host
        self.database_name = database_name
        self.user = user
        self.password = password
        self.table_name = table_name

    def start(self):
        print("Starting connection to database")
        self.connection = psycopg2.connect(host=self.host, database=self.database_name, user=self.user, password=self.password)
        print("Connected to database")

    def shutdown(self):
        print('Shutting down connection to server')
        if self.connection:
            self.connection.close()
        print('Shut down to server completed')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.shutdown()

    def clear_all_data(self):
        sql = 'DELETE FROM ' + self.table_name

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def drop_table(self):
        sql = 'DROP TABLE ' + self.table_name

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

class DeptsTable(Database):

    def __init__(self, host, database_name, user, password):
        super().__init__(host, database_name, user, password, 'depts')

    def create_table_if_not_exist(self):
        sql = """CREATE TABLE IF NOT EXISTS depts(
                    dept_id SERIAL PRIMARY KEY,
                    dept_code VARCHAR(250) NOT NULL
                );"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        cursor.close()

        self.connection.commit()

    def insert_dept_if_not_exists(self, dept_code):
        existing_dept_id = self.get_dept_id(dept_code)

        if existing_dept_id is not None:
            return existing_dept_id
        
        sql = """INSERT INTO depts (dept_code) 
                VALUES (%s);"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (dept_code, ))
        cursor.close()

        self.connection.commit()
        return self.get_dept_id(dept_code)

    def get_dept_id(self, dept_code):
        sql = """SELECT dept_id 
                        FROM depts
                        WHERE dept_code = %s;"""

        cursor = self.connection.cursor()
        cursor.execute(sql, (dept_code, ))

        dept_id = None
        row = cursor.fetchone()
        if row is not None and len(row) == 1:
            dept_id = row[0]

        cursor.close()
        return dept_id

class CoursesTable(Database):
    def __init__(self, host, database_name, user, password):
        super().__init__(host, database_name, user, password, 'courses')

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

class SessionsTable(Database):
    def __init__(self, host, database_name, user, password):
        super().__init__(host, database_name, user, password, 'sessions')

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