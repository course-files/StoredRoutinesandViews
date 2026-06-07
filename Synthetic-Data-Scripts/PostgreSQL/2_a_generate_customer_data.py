"""
2_a_generate_customer_data.py
==============================
Generates 770 synthetic customer records and writes them as
PostgreSQL-compatible INSERT statements to 2_b_DML_customer_data.sql.

Converted from MySQL (mysql-connector-python) to PostgreSQL (psycopg2).

Key changes from the MySQL version:
  - Driver      : psycopg2  (replaces mysql-connector-python)
  - dbname      : psycopg2 uses 'dbname' not 'database'
  - Port        : 5432  (MySQL used 3306)
  - Schema prefix removed: 'siwaka_dishes.customer' → 'customer'
  - The original script built raw SQL strings using %-formatting with
    string values — this is kept for the output SQL file, but values
    are properly escaped using psycopg2's adapt() so the written SQL
    is safe and PostgreSQL-compatible.
  - No backtick-quoted identifiers (those are MySQL-only); PostgreSQL
    uses double quotes for identifiers when quoting is needed.

Note: This script only writes to a SQL file; it does not INSERT rows
directly into the database.  Run the output file through
0_b_load_synthetic_data.py to load it.

Usage:
    pip install psycopg2-binary python-dotenv
    python 2_a_generate_customer_data.py
"""

import os
import random
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import adapt   # safe value quoting for file output

# ---------------------------------------------------------------------------
# Load environment variables from .env
# ---------------------------------------------------------------------------
load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
first_names = [
    'Mwangi', 'Achieng', 'Kamau', 'Wanjiku', 'Otieno', 'Njeri', 'Kiptoo', 'Wambui', 'Mutiso', 'Amina',
    'Jean', 'Marie', 'Claude', 'Patrick', 'Emmanuel', 'Joseph', 'Paul', 'Pierre', 'Jacques', 'Michel',
    'Felix', 'Alain', 'Jeanne', 'Claudine', 'Patricia', 'Emmanuelle', 'Josephine', 'Pauline',
    'Pierrette', 'Jacqueline', 'Michelle', 'Felicite', 'Alaine',
]
last_names = [
    'Omondi', 'Kiplagat', 'Mutua', 'Wanyama', 'Odhiambo', 'Kariuki', 'Njoroge', 'Ochieng', 'Muthoni', 'Mwangi',
    'Mugisha', 'Ndayishimiye', 'Nkurunziza', 'Kagame', 'Bizimana', 'Mukasa', 'Kabongo', 'Mutombo', 'Kabila',
    'Lumumba', 'Munee', 'Munyao', 'Munyoki', 'Munyua', 'Munyui', 'Munyuli', 'Munywe', 'Munzala',
    'Hassan', 'Mohammed', 'Ali', 'Abdi', 'Omar', 'Osman', 'Hussein', 'Ahmed', 'Ibrahim', 'Adan', 'Yusuf',
    'Abdullahi',
]
streets = [
    'Nairobi St', 'Mombasa Rd', 'Kisumu Ave', 'Eldoret Ln', 'Nakuru Blvd',
    'Thika Rd', 'Langata Rd', 'Ngong Rd', 'Jogoo Rd', 'Kenyatta Ave', 'Moi Ave',
    'Haile Selassie Ave', 'Uhuru Hwy', 'Waiyaki Way', 'Limuru Rd', 'Kiambu Rd',
    'Mbagathi Way', 'Dennis Pritt Rd', 'James Gichuru Rd', 'Riverside Dr',
    'State House Rd', 'Koinange St', 'Tom Mboya St', 'Mama Ngina St', 'Kimathi St',
    'Kilimani Rd', 'Kileleshwa Rd', 'Lavington Rd', 'Karen Rd', 'Runda Dr',
    'Gigiri Rd', 'Westlands Rd', 'Parklands Rd', 'Eastleigh Rd',
    'South B Rd', 'South C Rd', 'Embakasi Rd', 'Donholm Rd', 'Buruburu Rd',
]
counties = [
    'Nairobi', 'Mombasa', 'Kisumu', 'Eldoret', 'Nakuru',
    'Machakos', 'Kiambu', 'Muranga', 'Nyeri', 'Meru',
    'Embu', 'Kitui', 'Garissa', 'Wajir', 'Mandera',
    'Marsabit', 'Isiolo', 'Tharaka-Nithi', 'Laikipia', 'Baringo',
]
sub_counties = [
    'Westlands', 'Kasarani', 'Embakasi', 'Langata', 'Dagoretti',
    'Nyali', 'Likoni', 'Changamwe', 'Kisauni', 'Jomvu',
    'Kisumu Central', 'Kisumu East', 'Kisumu West', 'Nyando', 'Muhoroni',
    'Eldoret East', 'Eldoret West', 'Kesses', 'Moiben', 'Turbo',
    'Nakuru Town', 'Naivasha', 'Gilgil', 'Molo', 'Subukia',
]
business_prefixes = [
    'Safari', 'Serena', 'Sarova', 'Fairmont', 'InterContinental', 'Hilton',
    'Villa Rosa', 'Ole Sereni', 'Boma', 'PrideInn', 'Nyali', 'Diani',
    'Hemingways', 'Tamarind', 'Swahili', 'Baobab', 'Voyager',
    'Leopard Beach', 'Severin', 'Neptune',
]
business_suffixes = [
    'Hotel', 'Resort', 'Lodge', 'Suites', 'Inn',
    'Retreat', 'Haven', 'Palace', 'Manor', 'Residences',
]


# ---------------------------------------------------------------------------
# Helper — safely quote a string for a PostgreSQL SQL file
# Handles embedded single quotes and other special characters.
# ---------------------------------------------------------------------------
def pg_quote(value: str) -> str:
    """Return value wrapped in single quotes with internal quotes escaped."""
    return adapt(value).getquoted().decode('utf-8')


# ---------------------------------------------------------------------------
# Database connection (kept for structural consistency; not used for INSERT
# in this script — all output goes to the SQL file)
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

# Clear output file on each run
open('2_b_DML_customer_data.sql', 'w').close()

INSERT_SQL = (
    "INSERT INTO customer "
    "(customer_name, contact_first_name, contact_last_name, phone, "
    " address_line1, address_line2, postal_code, county, sub_county, status) "
    "VALUES ({customer_name}, {first_name}, {last_name}, {phone}, "
    "        {address_line1}, {address_line2}, {postal_code}, "
    "        {county}, {sub_county}, {status});"
)

for _ in range(300):
    if random.choice([True, False]):
        first_name    = random.choice(first_names)
        last_name     = random.choice(last_names)
        customer_name = f'{first_name} {last_name}'
    else:
        customer_name = (f'[Business] {random.choice(business_prefixes)} '
                         f'{random.choice(business_suffixes)}')
        first_name    = random.choice(first_names)
        last_name     = random.choice(last_names)

    phone         = '07' + ''.join(str(random.randint(0, 9)) for _ in range(8))
    address_line1 = f'{random.randint(1, 999)} {random.choice(streets)}'
    address_line2 = f'Apt {random.randint(1, 100)}'
    postal_code   = str(random.randint(100, 90600))
    county        = random.choice(counties)
    sub_county    = random.choice(sub_counties)
    status        = 1 if random.random() < 0.51 else 0

    sql_statement = INSERT_SQL.format(
        customer_name = pg_quote(customer_name),
        first_name    = pg_quote(first_name),
        last_name     = pg_quote(last_name),
        phone         = pg_quote(phone),
        address_line1 = pg_quote(address_line1),
        address_line2 = pg_quote(address_line2),
        postal_code   = pg_quote(postal_code),
        county        = pg_quote(county),
        sub_county    = pg_quote(sub_county),
        status        = status,
    )

    with open('2_b_DML_customer_data.sql', 'a', encoding='utf-8') as f:
        f.write(sql_statement + '\n')

conn.close()
print("Done. SQL written to 2_b_DML_customer_data.sql")
