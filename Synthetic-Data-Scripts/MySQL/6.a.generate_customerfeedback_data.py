import random
import mysql.connector
import numpy as np

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
    "Great selection of wines.", "The dessert platter was a highlight."
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
    "The table was in a drafty spot."
]

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='student',
    password='5trathm0re',
    database='siwaka_dishes'
)
cursor = conn.cursor()

# Get all orderNumbers and their customer status
cursor.execute("""
    SELECT customerorder.orderNumber, customer.status
    FROM customer
    INNER JOIN customerorder ON customerorder.customerNumber = customer.customerNumber
""")
order_status_list = cursor.fetchall()  # List of (orderNumber, status)

# Generate feedback for each orderNumber
for orderNumber, status in order_status_list:
    if status == 0:
        # Dormant: mostly low, but allow some high ratings
        if random.random() < 0.95:
            rating = np.random.normal(loc=2, scale=1)  # mean 2, stddev 1
            comment = random.choice(negative_feedback_comments)
        else:
            rating = np.random.normal(loc=4, scale=1)
            comment = random.choice(positive_feedback_comments)
    else:
        # Active: mostly high, but allow some low ratings
        if random.random() < 0.9:
            rating = np.random.normal(loc=4, scale=1)
            comment = random.choice(positive_feedback_comments)
        else:
            rating = np.random.normal(loc=2, scale=1)
            comment = random.choice(negative_feedback_comments)
    # Clip ratings to 1-5 and round
    foodquality = int(np.clip(round(rating), 1, 5))
    servicequality = int(np.clip(round(rating + np.random.normal(0, 0.5)), 1, 5))
    pricetovalue = int(np.clip(round(rating + np.random.normal(0, 0.5)), 1, 5))
    ambiance = int(np.clip(round(rating + np.random.normal(0, 0.5)), 1, 5))

    sql_statement = (
        "INSERT INTO siwaka_dishes.customerfeedback "
        "(foodquality, servicequality, pricetovalue, ambiance, orderNumber, comment) "
        "VALUES (%d, %d, %d, %d, %d, '%s');"
        % (foodquality, servicequality, pricetovalue, ambiance, orderNumber, comment.replace("'", "''"))
    )

    with open('6.b.DML_customerfeedback_data.sql', 'a') as f:
        f.write(sql_statement + '\n')

conn.commit()
cursor.close()
conn.close()