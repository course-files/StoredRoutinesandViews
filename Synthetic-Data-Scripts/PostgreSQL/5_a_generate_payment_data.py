"""
5_a_generate_payment_data.py
==============================
For each customer order, calculates the expected total from orderdetail,
then generates 1–3 partial payments using random payment methods and
random dates on or after the order date.  An extra top-up payment is
added when the cumulative payments fall below 80 % of the order total.

Writes PostgreSQL-compatible INSERT statements to
5_b_DML_payment_data.sql.

Converted from MySQL (mysql-connector-python) to PostgreSQL (psycopg2).

Key changes from the MySQL version:
  - Driver      : psycopg2  (replaces mysql-connector-python)
  - dbname      : psycopg2 uses 'dbname' not 'database'
  - Port        : 5432  (MySQL used 3306)
  - Table names without backticks
  - Decimal arithmetic preserved (psycopg2 returns NUMERIC columns as
    Python Decimal objects, same as the original)
  - Bug fix: the original top-up block wrote amount_paid instead of
    additional_payment, and the final accumulator line had no effect.
    Both are corrected here.

Usage:
    pip install psycopg2-binary python-dotenv
    python 5_a_generate_payment_data.py
"""

import os
import random
import decimal
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
# Fetch reference data
# ---------------------------------------------------------------------------
cursor.execute("SELECT order_number, order_date FROM customer_order")
customer_orders = cursor.fetchall()   # list of (order_number, order_date)

cursor.execute("SELECT payment_method_id FROM payment_method")
payment_methods = [row[0] for row in cursor.fetchall()]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_date(start: datetime, end: datetime) -> datetime:
    delta          = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

end_date = datetime(2026, 4, 30)

INSERT_SQL = (
    "INSERT INTO payment "
    "(order_number, payment_method_id, amount, payment_date) "
    "VALUES (%s, %s, %s, %s);"
)

# ---------------------------------------------------------------------------
# Clear the output file
# ---------------------------------------------------------------------------
open('5_b_DML_payment_data.sql', 'w').close()

# ---------------------------------------------------------------------------
# Generate payments
# ---------------------------------------------------------------------------
for order_number, order_date in customer_orders:

    # Total expected for this order
    cursor.execute("""
        SELECT SUM(quantity_ordered * price_each)
        FROM   order_detail
        WHERE  order_number = %s
    """, (order_number,))
    row = cursor.fetchone()
    if row is None or row[0] is None:
        continue

    total_expected   = decimal.Decimal(row[0])
    num_payments     = random.randint(1, 3)
    total_paid       = decimal.Decimal(0)

    # Ensure order_date is a datetime (psycopg2 may return date or datetime)
    if not isinstance(order_date, datetime):
        order_date = datetime.combine(order_date, datetime.min.time())

    with open('5_b_DML_payment_data.sql', 'a', encoding='utf-8') as f:

        for payment_idx in range(num_payments):
            payment_method_id = random.choice(payment_methods)
            remaining         = total_expected - total_paid

            if payment_idx == num_payments - 1:
                # Last payment: pay whatever remains (up to the full balance)
                max_payment = remaining
            else:
                max_payment = remaining * decimal.Decimal(random.uniform(0.1, 0.5))

            amount_paid  = round(
                decimal.Decimal(random.uniform(
                    float(remaining) * 0.1,
                    float(max_payment)
                )), 2
            )
            total_paid   += amount_paid
            payment_date  = random_date(order_date, end_date)

            sql_bytes = cursor.mogrify(
                INSERT_SQL,
                (order_number, payment_method_id, amount_paid, payment_date)
            )
            f.write(sql_bytes.decode('utf-8') + '\n')

        # Top-up if total paid is still below 80 % of the order total
        if total_paid < total_expected * decimal.Decimal('0.8'):
            additional_payment = total_expected * decimal.Decimal('0.8') - total_paid
            additional_payment = round(additional_payment, 2)   # Bug fix: was writing amount_paid
            payment_method_id  = random.choice(payment_methods)
            payment_date       = random_date(order_date, end_date)

            sql_bytes = cursor.mogrify(
                INSERT_SQL,
                (order_number, payment_method_id, additional_payment, payment_date)
            )
            f.write(sql_bytes.decode('utf-8') + '\n')
            total_paid += additional_payment  # Bug fix: accumulator now actually updates

conn.commit()
conn.close()
print("Done. SQL written to 5_b_DML_payment_data.sql")
