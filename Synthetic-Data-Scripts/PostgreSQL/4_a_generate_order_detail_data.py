"""
4_a_generate_orderDetail_data.py
==================================
For every existing customer order, generates between 1 and 3 order-detail
rows (random product, random quantity 1–8, price from the product table).
Writes PostgreSQL-compatible INSERT statements to
4_b_DML_order_detail_data.sql.

Converted from MySQL (mysql-connector-python) to PostgreSQL (psycopg2).

Key changes from the MySQL version:
  - Driver      : psycopg2  (replaces mysql-connector-python)
  - dbname      : psycopg2 uses 'dbname' not 'database'
  - Port        : 5432  (MySQL used 3306)
  - Table names: no backticks; plain lowercase names work in PostgreSQL
  - %s placeholder: psycopg2 uses %s for all types, consistent with
    the parameterised queries already in the original

Usage:
    pip install psycopg2-binary python-dotenv
    python 4_a_generate_orderDetail_data.py
"""

import os
import random
import psycopg2
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
# Fetch reference data
# ---------------------------------------------------------------------------
cursor.execute("SELECT order_number FROM customer_order")
customer_orders = [row[0] for row in cursor.fetchall()]

cursor.execute("SELECT product_code FROM product")
products = [row[0] for row in cursor.fetchall()]

# ---------------------------------------------------------------------------
# Clear the output file
# ---------------------------------------------------------------------------
open('4_b_DML_order_detail_data.sql', 'w').close()

INSERT_SQL = (
    "INSERT INTO order_detail "
    "(order_number, product_code, quantity_ordered, price_each) "
    "VALUES (%s, %s, %s, %s);"
)

# ---------------------------------------------------------------------------
# Generate order details
# ---------------------------------------------------------------------------
for order_number in customer_orders:
    num_lines = random.randint(1, 3)

    for _ in range(num_lines):
        product_code = random.choice(products)
        quantity     = random.randint(1, 8)

        # Fetch the selling price for this product
        cursor.execute(
            "SELECT selling_price FROM product WHERE product_code = %s",
            (product_code,)
        )
        row = cursor.fetchone()
        if row is None:
            continue
        selling_price = row[0]

        # mogrify gives the fully-bound SQL as bytes — safe for file writing
        sql_bytes = cursor.mogrify(
            INSERT_SQL,
            (order_number, product_code, quantity, selling_price)
        )

        with open('4_b_DML_order_detail_data.sql', 'a', encoding='utf-8') as f:
            f.write(sql_bytes.decode('utf-8') + '\n')

conn.commit()
conn.close()
print("Done. SQL written to 4_b_DML_order_detail_data.sql")
