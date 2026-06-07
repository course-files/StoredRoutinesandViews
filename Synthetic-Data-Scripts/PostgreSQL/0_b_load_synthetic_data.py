"""
0_b_load_synthetic_data.py
===========================

Loads a SQL file into a PostgreSQL database,
executing each statement in sequence and reporting progress.

Usage:
    pip install psycopg2-binary python-dotenv

    
You can also set environment variables directly in your shell if you prefer not to use a .env file:

Linux/macOS:
    export DB_HOST=localhost
    export DB_PORT=5432
    export DB_USER=siwaka_dishes_db_admin
    export DB_PASSWORD=your_password
    export DB_NAME=siwaka_dishes

Windows PowerShell:
    $env:DB_HOST="localhost"
    $env:DB_PORT="5432"
    $env:DB_USER="siwaka_dishes_db_admin"
    $env:DB_PASSWORD="your_password"
    $env:DB_NAME="siwaka_dishes"

Run:
    python 0_b_load_synthetic_data.py <sql_file>

Example:
    python 0_b_load_synthetic_data.py 1_b_generate_employee_data.sql
"""

import os
import sys
import psycopg2

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from .env file
# ---------------------------------------------------------------------------

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Read database connection details
# ---------------------------------------------------------------------------

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# ---------------------------------------------------------------------------
# Validate required environment variables
# ---------------------------------------------------------------------------

required_vars = {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_USER": DB_USER,
    "DB_PASSWORD": DB_PASSWORD,
    "DB_NAME": DB_NAME
}

missing = [key for key, value in required_vars.items() if not value]

if missing:

    print("ERROR: Missing environment variables:")

    for var in missing:
        print(f" - {var}")

    sys.exit(1)

# ---------------------------------------------------------------------------
# Create PostgreSQL connection
# ---------------------------------------------------------------------------
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    dbname=DB_NAME
)

cursor = conn.cursor()

# ---------------------------------------------------------------------------
# Execute SQL file
# ---------------------------------------------------------------------------

def execute_sql_file(filename: str) -> None:
    """
    Read a SQL file and execute each semicolon-delimited statement.
    """

    with open(filename, "r", encoding="utf-8") as fh:
        raw = fh.read()

    statements = [
        s.strip()
        for s in raw.split(";")
        if s.strip()
    ]

    total = len(statements)

    for i, statement in enumerate(statements, start=1):

        try:
            cursor.execute(statement)

            conn.commit()

            print(f"[{i}/{total}] OK")

        except psycopg2.Error as err:

            print(f"[{i}/{total}] ERROR:")
            print(err)

            conn.rollback()

# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage:")
        print("python 0_b_load_synthetic_data.py <sql_file>")

        sys.exit(1)

    sql_file = sys.argv[1]

    execute_sql_file(sql_file)

    cursor.close()
    conn.close()

    print("SQL file execution completed.")