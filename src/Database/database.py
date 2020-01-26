import psycopg2
from psycopg2 import pool

class Database():
    def __init__(self, 
                 host='localhost', 
                 port=5432, 
                 database_name='my_db', 
                 user='superuser', 
                 password='pass', 
                 table_name='', 
                 min_connections=1, 
                 max_connections=2):

        self.host = host
        self.port = port
        self.database_name = database_name
        self.user = user
        self.password = password
        self.table_name = table_name
        self.min_connections = min_connections
        self.max_connections = max_connections

    def start(self):
        print("Starting connection pool to database")
        self.connection_pool = pool.ThreadedConnectionPool(minconn=self.min_connections, 
                                                           maxconn=self.max_connections, 
                                                           host=self.host, 
                                                           port=self.port, 
                                                           database=self.database_name, 
                                                           user=self.user, 
                                                           password=self.password)
        print("Created connection pool to database")

    def shutdown(self):
        print('Shutting down connection to server')
        if self.connection_pool:
            self.connection_pool.closeall()
        print('Shut down to server completed')

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.shutdown()

    def clear_all_data(self):
        sql = 'DELETE FROM ' + self.table_name

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

    def drop_table(self):
        sql = 'DROP TABLE ' + self.table_name

        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql)
        cursor.close()

        connection.commit()
        self.put_back_connection(connection)

    def get_connection(self):
        return self.connection_pool.getconn()

    def put_back_connection(self, connection):
        self.connection_pool.putconn(connection)

    def execute_sql(self, sql_script, values):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(sql_script, values)

        cursor_results = cursor.fetchall()

        records = []
        for record in cursor_results:
            records.append(record)

        cursor.close()
        self.put_back_connection(connection)

        return records



        