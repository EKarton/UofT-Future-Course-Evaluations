import csv

import sys
sys.path.append('../Database')

from instructors_table import InstructorsTable
from depts_table import DeptsTable
from courses_table import CoursesTable
from sessions_table import SessionsTable
from evaluations_table import EvaluationsTable

import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load credentials from the .env file
    load_dotenv()

    # Load the DB
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    database_name = os.getenv("DATABASE_NAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")

    with DeptsTable(host, port, database_name, user, password) as depts_table:
        with CoursesTable(host, port, database_name, user, password) as courses_table:
            with InstructorsTable(host, port, database_name, user, password) as instructors_table:
                with SessionsTable(host, port, database_name, user, password) as sessions_table:
                    with EvaluationsTable(host, port, database_name, user, password) as evaluations_table:

                        # Drop all the tables
                        evaluations_table.drop_table()
                        depts_table.drop_table()
                        courses_table.drop_table()
                        instructors_table.drop_table()
                        sessions_table.drop_table()

                        # Create the tables
                        depts_table.create_table_if_not_exist()
                        courses_table.create_table_if_not_exist()
                        instructors_table.create_table_if_not_exist()                        
                        sessions_table.create_table_if_not_exist()
                        evaluations_table.create_table_if_not_exist()

                        # Dump the data to the database
                        with open('data/database-data.csv') as csv_file:
                            csv_reader = csv.DictReader(csv_file)
                            for row in csv_reader:
                                dept_id = depts_table.insert_dept_if_not_exists(row['dept'])
                                course_id = courses_table.insert_course_if_not_exists(row['course'])
                                instructor_id = instructors_table.insert_instructor_if_not_exist(row['instructor'], row['abbrev_instructor'])
                                session_id = sessions_table.insert_session_if_not_exists(row['term'], row['year'])

                                evaluations_table.insert_evaluation(
                                    dept_id, course_id, session_id, instructor_id,
                                    row['cat1'], row['cat2'], row['cat3'], row['cat4'], row['cat5'], row['cat6'], row['cat7'], row['cat8'],
                                    row['num_responded'], row['num_invited']
                                )
