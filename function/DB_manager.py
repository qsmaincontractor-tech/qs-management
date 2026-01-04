import sqlite3
import os
import time

class DB_Manager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            # Simple connection without WAL mode for now
            self.conn = sqlite3.connect(self.db_path, timeout=30.0)
            self.conn.row_factory = sqlite3.Row  # Access columns by name
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None

    def close(self):
        if self.conn:
            try:
                self.conn.commit()  # Ensure any pending transactions are committed
                self.conn.close()
                print("Database connection closed.")
            except sqlite3.Error as e:
                print(f"Error closing database: {e}")

    def execute_query(self, query, params=(), max_retries=3):
        """Execute query with retry logic for database locks"""
        if not self.conn or not self.cursor:
            print("Database connection not available")
            return None
            
        for attempt in range(max_retries):
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return self.cursor
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e).lower():
                    if attempt < max_retries - 1:
                        print(f"Database locked, retrying in {0.5 * (attempt + 1)} seconds... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                        continue
                    else:
                        print(f"Error executing query after {max_retries} attempts: {query}\nParams: {params}\nError: {e}")
                        return None
                else:
                    print(f"Error executing query: {query}\nParams: {params}\nError: {e}")
                    return None
            except sqlite3.Error as e:
                print(f"Error executing query: {query}\nParams: {params}\nError: {e}")
                return None
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
        if not self.conn or not self.cursor:
            print("Database connection not available")
            return None
            
        columns = ', '.join([f'"{key}"' for key in data.keys()])
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO \"{table}\" ({columns}) VALUES ({placeholders})"
        result = self.execute_query(query, tuple(data.values()))
        if result:
            return self.cursor.lastrowid
        return None

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
            schema_content = f.read()
        
        # Remove comments (lines starting with --)
        lines = schema_content.split('\n')
        clean_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('--') and stripped:
                clean_lines.append(line)
        
        # Join back and split on semicolons
        clean_sql = '\n'.join(clean_lines)
        statements = [stmt.strip() for stmt in clean_sql.split(';') if stmt.strip()]
        
        for stmt in statements:
            if stmt:
                max_retries = 5  # More retries for schema creation
                for attempt in range(max_retries):
                    try:
                        self.cursor.execute(stmt)
                        self.conn.commit()
                        break
                    except sqlite3.OperationalError as e:
                        if "database is locked" in str(e).lower():
                            if attempt < max_retries - 1:
                                print(f"Database locked during schema creation, retrying in {1.0 * (attempt + 1)} seconds... (attempt {attempt + 1}/{max_retries})")
                                time.sleep(1.0 * (attempt + 1))
                                continue
                            else:
                                print(f"Failed to execute schema statement after {max_retries} attempts: {stmt[:100]}...\nError: {e}")
                                return
                        elif "already exists" in str(e).lower():
                            # Table already exists, skip
                            print(f"Table already exists, skipping: {stmt[:50]}...")
                            break
                        else:
                            print(f"Error executing schema statement: {stmt[:100]}...\nError: {e}")
                            return
                    except sqlite3.Error as e:
                        print(f"Error executing schema statement: {stmt[:100]}...\nError: {e}")
                        return
        
        print("Tables created successfully from schema.")
