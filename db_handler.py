import mysql.connector
from mysql.connector import Error
import re

class DBHandler:
    def __init__(self):
        # Configuration for XAMPP MySQL (default user: root, no password)
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "company_db"

    def connect(self):
        """Establishes a connection to the database."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None

    def validate_sql(self, sql_query):
        """
        Validates the SQL query to ensure safety.
        Allows SELECT, INSERT, UPDATE, DELETE but rejects dangerous operations.
        """
        if not sql_query:
            return False, "Empty query."
        
        # Normalize query for checking
        normalized_query = sql_query.strip().upper()
        
        # Reject dangerous operations
        forbidden_keywords = ["DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE", "SHUTDOWN"]
        for keyword in forbidden_keywords:
            if keyword in normalized_query:
                return False, f"Security Alert: '{keyword}' statements are not allowed."
        
        # Allow only CRUD operations
        allowed_starts = ["SELECT", "INSERT", "UPDATE", "DELETE"]
        query_starts_with_allowed = any(normalized_query.startswith(keyword) for keyword in allowed_starts)
        
        if not query_starts_with_allowed:
            return False, "Security Alert: Only SELECT, INSERT, UPDATE, DELETE queries are allowed."

        return True, "Valid SQL."

    def _extract_employee_name_from_insert(self, sql_query):
        """
        Extract employee name from INSERT INTO employees query.
        Expected format: INSERT INTO employees (name, department, salary, city) VALUES ('Name', 'Dept', salary, 'City');
        """
        try:
            # Find the VALUES clause
            values_match = re.search(r'VALUES\s*\(\s*\'([^\']+)\'', sql_query, re.IGNORECASE)
            if values_match:
                return values_match.group(1).strip()
        except:
            pass
        return None

    def _check_duplicate_employee(self, cursor, name):
        """
        Check if an employee with the given name already exists.
        Returns True if duplicate exists, False otherwise.
        """
        try:
            cursor.execute("SELECT id FROM employees WHERE name = %s", (name,))
            result = cursor.fetchone()
            return result is not None
        except Error:
            return False

    def execute_query(self, sql_query):
        """
        Executes a safe SQL query and returns the results.
        For SELECT: returns columns and data
        For INSERT/UPDATE/DELETE: commits and returns success message
        For INSERT: checks for duplicate employee names first
        """
        is_valid, message = self.validate_sql(sql_query)
        if not is_valid:
            return None, message

        connection = self.connect()
        if not connection:
            return None, "Database connection failed."

        try:
            cursor = connection.cursor()
            
            # Determine query type
            query_type = sql_query.strip().upper()[:6]
            
            if query_type == "SELECT":
                cursor.execute(sql_query)
                # Fetch all results
                result = cursor.fetchall()
                # Get column names
                column_names = [i[0] for i in cursor.description] if cursor.description else []
                
                cursor.close()
                connection.close()
                
                return {"columns": column_names, "data": result}, None
            
            elif query_type == "INSERT":
                # Check for duplicate employee name before inserting
                employee_name = self._extract_employee_name_from_insert(sql_query)
                if employee_name:
                    if self._check_duplicate_employee(cursor, employee_name):
                        cursor.close()
                        connection.close()
                        return None, "Employee with this name already exists."
                
                # Proceed with INSERT
                cursor.execute(sql_query)
                connection.commit()
                
                # Get affected rows count
                affected_rows = cursor.rowcount
                
                cursor.close()
                connection.close()
                
                return {"message": f"Successfully inserted {affected_rows} row(s)."}, None
            
            else:
                # For UPDATE, DELETE
                cursor.execute(sql_query)
                connection.commit()
                
                # Get affected rows count
                affected_rows = cursor.rowcount
                
                cursor.close()
                connection.close()
                
                operation = "updated" if query_type == "UPDATE" else "deleted"
                return {"message": f"Successfully {operation} {affected_rows} row(s)."}, None

        except Error as e:
            if connection.is_connected():
                connection.close()
            return None, f"SQL Execution Error: {e}"
