# AI Natural Language to SQL Assistant

This project is a web-based AI assistant that converts natural language queries into SQL using the Hugging Face `flan-t5-small` model and executes them on a local MySQL database.

## Prerequisites

1.  **Python 3.8+**
2.  **XAMPP** (or any MySQL server)
3.  **Basic understanding of SQL**

## Installation

1.  **Clone/Download** the project.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This will install PyTorch and Transformers, which might take some time.*

## Database Setup

1.  Start **Apache** and **MySQL** in XAMPP control panel.
2.  Open **phpMyAdmin** (usually `http://localhost/phpmyadmin`).
3.  Import `database.sql` or copy-paste its content into the SQL execution tab.
    -   Creates `company_db` database.
    -   Creates `employees` table with `id` as `AUTO_INCREMENT PRIMARY KEY`.
    -   Inserts sample data.

**Important**: If you encounter "Duplicate entry '0' for key 'PRIMARY'" errors, the table may have been created without AUTO_INCREMENT. Run `python setup_db.py` to recreate the table with the correct schema.

## Configuration

If your MySQL settings differ from the defaults (User: `root`, Password: ``), update `db_handler.py`:

```python
self.host = "localhost"
self.user = "root"
self.password = ""
self.database = "company_db"
```

## Running the Application

1.  Run the Flask app:
    ```bash
    python app.py
    ```
2.  Wait for the model to load (first time will download ~300MB).
3.  Open your browser and search: `http://127.0.0.1:5000`

## Usage Examples

Type queries like:
- "Show all employees"
- "Add employee John in HR with salary 50000 and city Boston" ✅
- "Add employee John in Sales with salary 70000 and city Chicago" ❌ (Duplicate name)
- "Update salary of Alice to 65000"
- "Delete employee Bob"
- "Show employees in IT"

**Note**: The system prevents duplicate employee names. If you try to add an employee with a name that already exists, you'll get an error message.

## Security

-   The application allows **SELECT, INSERT, UPDATE, DELETE** queries.
-   Dangerous operations like **DROP, ALTER, TRUNCATE, CREATE, GRANT** are blocked.
-   **Duplicate Prevention**: INSERT operations check for existing employee names and prevent duplicates.
-   All queries are validated before execution.

## Architecture

-   **Frontend**: HTML/CSS/JS (Fetch API)
-   **Backend**: Flask
-   **AI Model**: Google FLAN-T5 Small (via Hugging Face Transformers)
-   **Database**: MySQL
"# Natural_language_to_sql_converter_v1" 
