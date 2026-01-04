import sqlite3
import os

class DB_Manager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def execute_query(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor
        except sqlite3.Error as e:
            print(f"Error executing query: {query}\nParams: {params}\nError: {e}")
            return None

    def fetch_all(self, query, params=()):
        cursor = self.execute_query(query, params)
        if cursor:
            return [dict(row) for row in cursor.fetchall()]
        return []

    def fetch_one(self, query, params=()):
        cursor = self.execute_query(query, params)
        if cursor:
            row = cursor.fetchone()
            return dict(row) if row else None
        return None

    def insert(self, table, data):
        """
        Insert a dictionary of data into a table.
        """
        columns = ', '.join([f'"{key}"' for key in data.keys()])
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO \"{table}\" ({columns}) VALUES ({placeholders})"
        self.execute_query(query, tuple(data.values()))
        return self.cursor.lastrowid

    def update(self, table, data, where_clause, where_params):
        """
        Update a table with a dictionary of data based on a where clause.
        Returns number of rows affected.
        """
        set_clause = ', '.join([f'"{key}" = ?' for key in data.keys()])
        query = f"UPDATE \"{table}\" SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(where_params)
        cursor = self.execute_query(query, params)
        rowcount = cursor.rowcount if cursor else 0
        return rowcount

    def delete(self, table, where_clause, where_params):
        """
        Delete rows from a table based on a where clause.
        """
        query = f"DELETE FROM \"{table}\" WHERE {where_clause}"
        self.execute_query(query, tuple(where_params))

    def create_tables_from_schema(self, schema_file_path):
        if not os.path.exists(schema_file_path):
            print(f"Schema file not found: {schema_file_path}")
            return

        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        try:
            self.cursor.executescript(schema_sql)
            self.conn.commit()
            print("Tables created successfully from schema.")
        except sqlite3.Error as e:
            print(f"Error creating tables: {e}")
