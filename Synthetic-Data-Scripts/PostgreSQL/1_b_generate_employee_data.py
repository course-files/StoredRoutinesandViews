"""
1_b_generate_employee_data.py
==============================
Generates 56 synthetic employee records, inserts them into the
PostgreSQL `employee` table, then randomly assigns a manager to every
employee via the `reports_to` column.  Every INSERT and UPDATE statement
is also written to  1_c_DML_employee_data.sql  for reference.

Usage:
    pip install psycopg2-binary python-dotenv
    python 1_b_generate_employee_data.py
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
# Reference data
# ---------------------------------------------------------------------------
first_names = [
    'Mwangi', 'Achieng', 'Kamau', 'Wanjiku', 'Otieno', 'Njeri', 'Kiptoo', 'Wambui', 'Mutiso', 'Amina',
    'Jean', 'Marie', 'Claude', 'Patrick', 'Emmanuel', 'Joseph', 'Paul', 'Pierre', 'Jacques', 'Michel',
    'Felix', 'Alain', 'Jeanne', 'Claudine', 'Patricia', 'Emmanuelle', 'Josephine', 'Pauline',
    'Pierrette', 'Jacqueline', 'Michelle', 'Felicite', 'Alaine', 'Kwame', 'Chinua', 'Ngozi', 'Thabo', 'Zanele',
    'Bongani', 'Kofi', 'Adebayo', 'Fatou', 'Lerato', 'Adisa', 'Binta', 'Chiamaka', 'Dayo', 'Ebele',
    'Femi', 'Gbemisola', 'Hawa', 'Ifeanyi', 'Jelani',
]

last_names = [
    'Omondi', 'Kiplagat', 'Mutua', 'Wanyama', 'Odhiambo', 'Kariuki', 'Njoroge', 'Ochieng', 'Muthoni', 'Mwangi',
    'Mugisha', 'Ndayishimiye', 'Nkurunziza', 'Kagame', 'Bizimana', 'Mukasa', 'Kabongo', 'Mutombo', 'Kabila',
    'Lumumba', 'Munee', 'Munyao', 'Munyoki', 'Munyua', 'Munyui', 'Munyuli', 'Munywe', 'Munzala',
    'Hassan', 'Mohammed', 'Ali', 'Abdi', 'Omar', 'Osman', 'Hussein', 'Ahmed', 'Ibrahim', 'Adan', 'Yusuf',
    'Abdullahi',
]

job_titles = [
    'Manager', 'Assistant Manager', 'Chef', 'Sous Chef', 'Cook',
    'Waiter', 'Waitress', 'Bartender', 'Host', 'Hostess',
    'Dishwasher', 'Cleaner', 'Cashier', 'Receptionist', 'Security Guard',
]

# ---------------------------------------------------------------------------
# Clear the output SQL file (so re-runs don't append to stale data)
# ---------------------------------------------------------------------------
open('1_c_DML_employee_data.sql', 'w').close()

# ---------------------------------------------------------------------------
# Generate and insert 56 employees
# ---------------------------------------------------------------------------
INSERT_EMPLOYEE = """
INSERT INTO employee
    (first_name, last_name, email, branch_code, job_title)
VALUES
    ( %s, %s, %s, %s, %s)
""".strip()

for i in range(56):
    first_name      = random.choice(first_names)
    last_name       = random.choice(last_names)
    # Unique-ish email using a random suffix
    email           = (f'{first_name[0].lower()}{last_name.lower()}'
                       f'{random.randint(1, 100)}@siwakadishes.co.ke')
    branch_code     = random.randint(1, 10)
    job_title       = random.choice(job_titles)

    params = (first_name, last_name, email, branch_code, job_title)

    # mogrify() returns the fully-bound SQL as bytes — decode for file writing
    sql_bytes = cursor.mogrify(INSERT_EMPLOYEE, params)
    cursor.execute(sql_bytes)

    with open('1_c_DML_employee_data.sql', 'a', encoding='utf-8') as f:
        f.write(sql_bytes.decode('utf-8') + ';\n')

conn.commit()
print(f"Inserted 56 employees.")

# ---------------------------------------------------------------------------
# Retrieve managers (for the reports_to assignment)
# ---------------------------------------------------------------------------
cursor.execute("""
    SELECT employee_number
    FROM   employee
    WHERE  job_title IN ('Manager', 'Assistant Manager', 'Chef', 'Sous Chef')
""")
managers = [row[0] for row in cursor.fetchall()]

# ---------------------------------------------------------------------------
# Retrieve all employee numbers
# ---------------------------------------------------------------------------
cursor.execute("SELECT employee_number FROM employee")
employees = [row[0] for row in cursor.fetchall()]

# ---------------------------------------------------------------------------
# Assign a random manager to every employee
# ---------------------------------------------------------------------------
UPDATE_EMPLOYEE = "UPDATE employee SET reports_to = %s WHERE employee_number = %s"

with open('1_c_DML_employee_data.sql', 'a', encoding='utf-8') as f:
    for emp_no in employees:
        manager_no = random.choice(managers)
        params     = (manager_no, emp_no)

        sql_bytes = cursor.mogrify(UPDATE_EMPLOYEE, params)
        cursor.execute(sql_bytes)
        f.write(sql_bytes.decode('utf-8') + ';\n')

conn.commit()
print(f"Assigned managers to {len(employees)} employees.")

cursor.close()
conn.close()
print("Done. SQL written to 1_c_DML_employee_data.sql")
