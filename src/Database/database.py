import psycopg2

class Database():
    def __init__(self, host='localhost', port=5432, database_name='my_db', user='superuser', password='pass', table_name=''):
        self.connection = None
        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.table_name = table_name

    def start(self):
        print("Starting connection to database", self.user)
        self.connection = psycopg2.connect(host=self.host, port=self.port, database=self.database_name, user=self.user, password=self.password)
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

    def execute_sql(self, sql_script, values):
        print(self.connection)
        cursor = self.connection.cursor()
        cursor.execute(sql_script, values)

        cursor_results = cursor.fetchall()

        records = []
        for record in cursor_results:
            records.append(record)

        cursor.close()
        return records



        