import mysql.connector
from mysql.connector import errorcode

def create_database():
    try:
        cnx = mysql.connector.connect(user='root', password='')
        cursor = cnx.cursor()
        
        try:
            cursor.execute("CREATE DATABASE company_db DEFAULT CHARACTER SET 'utf8'")
            print("Database 'company_db' created successfully.")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DB_CREATE_EXISTS:
                print("Database 'company_db' already exists.")
            else:
                print(f"Failed creating database: {err}")
                exit(1)

        cnx.database = 'company_db'

        TABLES = {}
        TABLES['employees'] = (
            "CREATE TABLE IF NOT EXISTS `employees` ("
            "  `id` int(11) NOT NULL AUTO_INCREMENT,"
            "  `name` varchar(50) NOT NULL,"
            "  `department` varchar(50) NOT NULL,"
            "  `salary` int(11) NOT NULL,"
            "  `city` varchar(50) NOT NULL,"
            "  PRIMARY KEY (`id`)"
            ") ENGINE=InnoDB")

        for table_name in TABLES:
            table_description = TABLES[table_name]
            try:
                print(f"Creating table {table_name}: ", end='')
                cursor.execute(table_description)
                print("OK")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                    print("already exists.")
                else:
                    print(err.msg)
            else:
                print("OK")
        
        # Check if empty, insert data
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        if count == 0:
            print("Inserting sample data...")
            add_employee = ("INSERT INTO employees "
                           "(name, department, salary, city) "
                           "VALUES (%s, %s, %s, %s)")
            data_employees = [
                ('Alice Smith', 'HR', 60000, 'New York'),
                ('Bob Johnson', 'Engineering', 80000, 'San Francisco'),
                ('Charlie Brown', 'Sales', 55000, 'Chicago'),
                ('David Lee', 'Marketing', 65000, 'Los Angeles'),
                ('Eve Wilson', 'Engineering', 85000, 'Seattle'),
                ('Frank Miller', 'Sales', 52000, 'Boston'),
                ('Grace Davis', 'HR', 62000, 'Austin'),
                ('Hank Moore', 'Engineering', 78000, 'Denver'),
                ('Ivy Taylor', 'Marketing', 67000, 'Miami'),
                ('Jack White', 'Sales', 54000, 'Phoenix'),
                ('Liam Scott', 'Engineering', 90000, 'San Jose'),
                ('Mia Green', 'HR', 61000, 'Atlanta')
            ]
            cursor.executemany(add_employee, data_employees)
            cnx.commit()
            print("Sample data inserted.")
        else:
            print("Table already has data.")

        cursor.close()
        cnx.close()

    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")

if __name__ == "__main__":
    create_database()
