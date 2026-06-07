"""
6_a_generate_customerfeedback_data.py
=======================================
For every customer order, generates a feedback row with ratings drawn
from a normal distribution biased by the customer's activity status
(active customers tend to rate higher; dormant ones tend to rate lower).
Writes PostgreSQL-compatible INSERT statements to
6_b_DML_customer_feedback_data.sql.

Converted from MySQL (mysql-connector-python) to PostgreSQL (psycopg2).

Key changes from the MySQL version:
  - Driver      : psycopg2  (replaces mysql-connector-python)
  - dbname      : psycopg2 uses 'dbname' not 'database'
  - Port        : 5432  (MySQL used 3306)
  - Schema prefix removed: 'siwaka_dishes.customerfeedback' → 'customer_feedback'
  - Single-quote escaping delegated to psycopg2's adapt() for safety

Dependencies:
    pip install psycopg2-binary python-dotenv numpy

Usage:
    python 6_a_generate_customerfeedback_data.py
"""

import os
import random
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import adapt
import numpy as np

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Feedback comment pools
# ---------------------------------------------------------------------------
positive_feedback_comments = [
    "Great food and service!", "Loved the ambiance.", "Excellent value for money.",
    "Staff were very friendly.", "Will visit again.", "Clean and tidy.",
    "Menu had good variety.", "Perfect for families.", "Desserts were amazing.",
    "Loved the decor.", "Quick and efficient service.", "Food was delicious.",
    "Highly recommend this place.", "Amazing experience overall.", "Very comfortable seating.",
    "Fresh ingredients used.", "Attentive staff.", "Enjoyed every bite.",
    "Great for groups.", "Lovely presentation of dishes.",
    "The chef came to greet us personally.", "Kids loved the play area.",
    "Everything was perfect from start to finish.", "The music was just right.",
    "Our server made great recommendations.", "The view from our table was beautiful.",
    "Loved the complimentary appetizers.", "Very accommodating to dietary needs.",
    "The reservation process was smooth.", "Loved the seasonal menu options.",
    "Food arrived hot and fresh.", "Great place for celebrations.",
    "The outdoor seating was wonderful.", "Loved the eco-friendly packaging.",
    "The loyalty program is rewarding.", "Staff remembered our preferences.",
    "The soup was outstanding.", "Loved the open kitchen concept.",
    "Great selection of wines.", "The dessert platter was a highlight.",
]

negative_feedback_comments = [
    "Average experience.", "Would not recommend.", "Food was cold.",
    "Too noisy.", "Portions were small.", "Waited too long for food.",
    "Overpriced for the quality.", "Not impressed.", "Drinks selection was poor.",
    "Service was slow.", "Uncomfortable chairs.", "Food lacked flavor.",
    "Staff seemed uninterested.", "Dirty tables.", "Order was incorrect.",
    "Long wait for bill.", "Ambiance was dull.", "Food was undercooked.",
    "Limited vegetarian options.", "Parking was a hassle.",
    "The restroom was not clean.", "Reservation was lost.", "Noisy children disturbed our meal.",
    "The air conditioning was too cold.", "The bread was stale.",
    "Waiter forgot our order.", "The table was sticky.", "Too many flies around.",
    "The bill was incorrect.", "The lighting was too dim.",
    "Food was too salty.", "The sauce was watery.", "The steak was overcooked.",
    "No gluten-free options.", "The salad was wilted.", "The coffee was burnt.",
    "The menu was confusing.", "The cutlery was dirty.", "Noisy kitchen staff.",
    "The table was in a drafty spot.",
]

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
# Fetch orders with their customer status
# ---------------------------------------------------------------------------
cursor.execute("""
    SELECT customer_order.order_number,
           customer.status
    FROM   customer
    INNER JOIN customer_order
        ON customer_order.customer_number = customer.customer_number
""")
order_status_list = cursor.fetchall()   # list of (order_number, status)

# ---------------------------------------------------------------------------
# Clear the output file
# ---------------------------------------------------------------------------
open('6_b_DML_customer_feedback_data.sql', 'w').close()

INSERT_SQL = (
    "INSERT INTO customer_feedback "
    "(food_quality, service_quality, price_to_value, ambiance, order_number, comment) "
    "VALUES ({food_quality}, {service_quality}, {price_to_value}, {ambiance}, "
    "        {order_number}, {comment});"
)

# ---------------------------------------------------------------------------
# Generate feedback rows
# ---------------------------------------------------------------------------
for order_number, status in order_status_list:

    if status == 0:
        # Dormant customer: mostly negative, rarely positive
        if random.random() < 0.95:
            base_rating = np.random.normal(loc=2, scale=1)
            comment     = random.choice(negative_feedback_comments)
        else:
            base_rating = np.random.normal(loc=4, scale=1)
            comment     = random.choice(positive_feedback_comments)
    else:
        # Active customer: mostly positive, occasionally negative
        if random.random() < 0.90:
            base_rating = np.random.normal(loc=4, scale=1)
            comment     = random.choice(positive_feedback_comments)
        else:
            base_rating = np.random.normal(loc=2, scale=1)
            comment     = random.choice(negative_feedback_comments)

    # Clip all ratings to the 1–5 range
    def jitter(base):
        return int(np.clip(round(base + np.random.normal(0, 0.5)), 1, 5))

    food_quality    = int(np.clip(round(base_rating), 1, 5))
    service_quality = jitter(base_rating)
    price_to_value  = jitter(base_rating)
    ambiance        = jitter(base_rating)

    # Use psycopg2's adapt() to safely quote the comment string
    comment_quoted = adapt(comment).getquoted().decode('utf-8')

    sql_statement = INSERT_SQL.format(
        food_quality    = food_quality,
        service_quality = service_quality,
        price_to_value  = price_to_value,
        ambiance        = ambiance,
        order_number    = order_number,
        comment         = comment_quoted,
    )

    with open('6_b_DML_customer_feedback_data.sql', 'a', encoding='utf-8') as f:
        f.write(sql_statement + '\n')

conn.commit()
cursor.close()
conn.close()
print("Done. SQL written to 6_b_DML_customer_feedback_data.sql")
