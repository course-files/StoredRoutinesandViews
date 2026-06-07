"""
3_a_generate_customerOrder_data.py
====================================
Generates 2,500 synthetic customer order records by reading existing
customer_number, order_status_id, and branch_code values from the database,
then writes PostgreSQL-compatible INSERT statements to
3_b_DML_customer_order_data.sql.

Converted from MySQL (mysql-connector-python) to PostgreSQL (psycopg2).

Key changes from the MySQL version:
  - Driver      : psycopg2  (replaces mysql-connector-python)
  - dbname      : psycopg2 uses 'dbname' not 'database'
  - Port        : 5432  (MySQL used 3306)
  - Backtick identifier quoting removed: `customerorder` → customer_order
    (backticks are MySQL-only; PostgreSQL uses double quotes if needed,
     but lowercase unquoted names are fine here)
  - NULL handling: Python None → bare NULL in the SQL string
  - Datetime formatting: PostgreSQL accepts ISO 8601 strings as-is

Usage:
    pip install psycopg2-binary python-dotenv
    python 3_a_generate_customerOrder_data.py
"""

import os
import random
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_NAME:", os.getenv("DB_NAME"))

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    dbname=os.getenv('DB_NAME')
)
cursor = conn.cursor()

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def random_date(start: datetime, end: datetime) -> datetime:
    """Return a random datetime between start and end (inclusive)."""
    delta          = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


# ---------------------------------------------------------------------------
# Fetch reference data from the database
# ---------------------------------------------------------------------------
cursor.execute("SELECT customer_number FROM customer")
customer_numbers = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT order_status_id FROM order_status")
order_status_ids = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT branch_code FROM branch")
branch_codes = [row[0] for row in cursor.fetchall()]

# ---------------------------------------------------------------------------
# Generate orders and write to SQL file
# ---------------------------------------------------------------------------
start_date = datetime(2022, 1, 1)
end_date   = datetime(2026, 4, 30)

INSERT_SQL = (
    "INSERT INTO customer_order "
    "(order_date, required_date, dispatch_date, order_status_id, customer_number, branch_code) "
    "VALUES (%s, %s, %s, %s, %s, %s);"
)

# Clear the output file before writing
open('3_b_DML_customer_order_data.sql', 'w').close()

for _ in range(2500):
    order_date    = random_date(start_date, end_date)
    required_date = order_date + timedelta(
        days    = random.randint(0, 4),
        hours   = random.randint(0, 23),
        minutes = random.randint(5, 59),
        seconds = random.randint(0, 59),
    )

    # 80 % of orders have a dispatch date
    if random.choices([True, False], weights=[0.8, 0.2])[0]:
        dispatch_date = order_date + timedelta(
            days    = random.randint(0, 5),
            hours   = random.randint(0, 23),
            minutes = random.randint(5, 59),
            seconds = random.randint(0, 59),
        )
    else:
        dispatch_date = None

    order_status_id = random.choice(order_status_ids)
    customer_number = random.choice(customer_numbers)
    branch_code     = random.choice(branch_codes)

    sql_bytes = cursor.mogrify(
        INSERT_SQL,
        (
            order_date,
            required_date,
            dispatch_date,
            order_status_id,
            customer_number,
            branch_code,
        )
    )

    with open('3_b_DML_customer_order_data.sql', 'a', encoding='utf-8') as f:
        f.write(sql_bytes.decode('utf-8') + '\n')

conn.commit()
cursor.close()
conn.close()
print("Done. SQL written to 3_b_DML_customer_order_data.sql")
