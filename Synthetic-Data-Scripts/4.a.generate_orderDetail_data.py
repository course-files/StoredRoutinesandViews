import mysql.connector
import random

# Connect to the database
conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='student',
    password='5trathm0re',
    database='siwaka_dishes'
)
cursor = conn.cursor()

# Retrieve existing Customer Order Numbers and Product Codes
cursor.execute("SELECT orderNumber FROM customerorder")
customerOrder = cursor.fetchall()

cursor.execute("SELECT productCode FROM product")
products = cursor.fetchall()

# Function to generate random order details
def generate_order_details():
    for order in customerOrder:
        orderNumber = order[0]

        # Create 1 to 3 order details for each customer order
        num_order_details = random.randint(1, 3)
        
        for _ in range(num_order_details):
            # For each order detail, randomly select a product and generate a random quantity
            # between 1 and 8
            productCode = random.choice(products)[0]
            quantity = random.randint(1, 8)

            cursor.execute("SELECT sellingPrice FROM product WHERE productCode = %s", (productCode,))
            sellingPrice = cursor.fetchone()[0]
            
            # cursor.execute("""
            #     INSERT INTO orderdetail (orderNumber, productCode, quantityOrdered, priceEach)
            #     VALUES (%s, %s, %s, %s)
            # """, (orderNumber, productCode, quantity, sellingPrice))

            sql_statement = """INSERT INTO orderdetail (orderNumber, productCode, quantityOrdered, priceEach) VALUES (%s, '%s', %s, %s);""" % (orderNumber, productCode, quantity, sellingPrice)

            with open('4.b.DML_orderDetail_data.sql', 'a') as f:
                f.write(sql_statement + '\n')

# Generate and insert order details
generate_order_details()

# Commit the transaction and close the connection
conn.commit()
conn.close()