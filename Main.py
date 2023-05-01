import psycopg2
import datetime

def create_account(email, name, conn):
    cur = conn.cursor()
    query = f"INSERT INTO USERS (Email, Name) VALUES ('{email}', '{name}');"
    cur.execute(query)
    conn.commit()

def create_renter(conn):
    email = input("Enter your email address: ")
    name = input("Enter your name: ")
    move_in_date = input("Enter your desired move in date (YYYY-MM-DD): ")
    # Convert string to datetime object
    date_obj = datetime.datetime.strptime(move_in_date, '%Y-%m-%d')
    location = input("Enter your desired location: ")
# Format date as string for SQL
    sql_date = date_obj.strftime('%Y-%m-%d')
    budget = input("Enter your estimated budget: ")
    cur = conn.cursor()
    query1 = f"INSERT INTO USERS (Email, Name) VALUES ('{email}', '{name}');"
    cur.execute(query1)
    query2 = f"INSERT INTO RENTER (Email, Name, Desired_move_in_date, Preferred_location, Budget) VALUES ('{email}', '{name}', '{sql_date}', '{location}', {budget});"
    cur.execute(query2)
    conn.commit()

def create_agent(conn):
    email = input("Enter your email address: ")
    name = input("Enter your name: ")
    real_estate_agency = input("Enter the name of the Real Estate Agency that you work for: ")
    
    job_title = input("Enter your job title: ")

    contact_info = input("Enter your contact info: ")
    cur = conn.cursor()
    query1 = f"INSERT INTO USERS (Email, Name) VALUES ('{email}', '{name}');"
    cur.execute(query1)
    query2 = f"INSERT INTO AGENT (Email, Name, job_title, real_estate_agency, contact_info) VALUES ('{email}', '{name}', '{real_estate_agency}', '{job_title}', '{contact_info}');"
    cur.execute(query2)
    conn.commit()


def search_properties(conn):
    cur = conn.cursor()
    city = input("Enter the city you want to search for properties in: ")

    query = f"SELECT * FROM PROPERTY WHERE City = '{city}';"
    cur.execute(query)
    results = cur.fetchall()

    if not results:
        print(f"No properties found in {city}.")
    else:
        print(f"Properties found in {city}:")
        for row in results:
            print(f"""
Property ID: {row[0]}
City: {row[1]}
State: {row[2]}
Description: {row[3]}
Address: {row[4]}
Neighborhood Postcode: {row[5]}
Neighborhood Name: {row[6]}
Price: ${row[7]:,.2f}
Rental Price: ${row[8]:,.2f}
Is In Rent: {row[9]}
Is In Sale: {row[10]}
Type: {row[11]}
Availability: {row[12]}
Square Footage: {row[13]:,.2f} sq ft
Agent Email: {row[14]}
""")

def add_address_payment(conn):
    cur = conn.cursor()
    
    # Get user email
    email = input("Please enter your email address: ")

    # Check if the user exists
    query = f"SELECT * FROM users WHERE email = '{email}';"
    cur.execute(query)
    existing_user = cur.fetchone()

    if existing_user is None:
        print("Invalid user. Please enter a valid email.")
        return

    # Get credit card details
    card_number = input("Enter the card number: ")
    expiration = input("Enter the expiration date (YYYY-MM-DD): ")
    cvv = input("Enter the CVV: ")

    # Get address details
    street = input("Enter the street: ")
    postcode = input("Enter the postcode: ")
    city = input("Enter the city: ")
    state = input("Enter the state: ")

    # Check if the address already exists
    query = f"SELECT * FROM address WHERE street = '{street}' AND postcode = '{postcode}';"
    cur.execute(query)
    existing_address = cur.fetchone()

    # If the address doesn't exist, insert it into the address table
    if existing_address is None:
        query = f"""
            INSERT INTO address (street, postcode, city, state)
            VALUES ('{street}', '{postcode}', '{city}', '{state}');
        """
        cur.execute(query)
        conn.commit()

    # Check if the credit card already exists
    query = f"SELECT * FROM credit_card WHERE number = '{card_number}';"
    cur.execute(query)
    existing_card = cur.fetchone()

    # If the credit card doesn't exist, insert it into the credit_card table
    if existing_card is None:
        query = f"""
            INSERT INTO credit_card (number, expiration, cvv, street, postcode, email)
            VALUES ('{card_number}', '{expiration}', '{cvv}', '{street}', '{postcode}', '{email}');
        """
        cur.execute(query)
        conn.commit()
        print("Credit card and address added successfully.")
    else:
        print("Credit card already exists.")

def modify_address_payment(conn):
    cur = conn.cursor()
    # Get user email
    email = input("Please enter your email address: ")

    # Check if the user exists
    query = f"SELECT * FROM users WHERE email = '{email}';"
    cur.execute(query)
    existing_user = cur.fetchone()

    if existing_user is None:
        print("Invalid user. Please enter a valid email.")
        return
    
    # Fetch the user's credit cards
    query = f"SELECT * FROM credit_card WHERE email = '{email}';"
    cur.execute(query)
    cards = cur.fetchall()

    if len(cards) == 0:
        print("No credit cards found for this email.")
        return

    # Display credit cards
    print("Credit cards for this email:")
    for card in cards:
        print(f"Card number: {card[0]}, Expiration: {card[1]}, CVV: {card[2]}, Street: {card[3]}, Postcode: {card[4]}")

    # Select a credit card to modify
    card_number = input("Enter the card number of the credit card you want to modify: ")

    # Get the attribute to modify
    attribute = input("Which attribute do you want to modify? (expiration/cvv/street/postcode): ")

    if attribute not in ["expiration", "cvv", "street", "postcode"]:
        print("Invalid attribute selected.")
        return

    # Get the new value for the attribute
    new_value = input(f"Enter the new value for {attribute}: ")

    # If the attribute is 'street' or 'postcode', insert the new address into the address table
    if attribute in ["street", "postcode"]:
        current_street, current_postcode = None, None
        for card in cards:
            if str(card[0]) == card_number:
                current_street, current_postcode = card[3], card[4]
                break

        new_street = new_value if attribute == "street" else current_street
        new_postcode = new_value if attribute == "postcode" else current_postcode

        query = f"SELECT city, state FROM address WHERE street = '{current_street}' AND postcode = '{current_postcode}';"
        cur.execute(query)
        city, state = cur.fetchone()

        query = f"SELECT * FROM address WHERE street = '{new_street}' AND postcode = '{new_postcode}';"
        cur.execute(query)
        existing_address = cur.fetchone()

        if existing_address is None:
            query = f"""
                INSERT INTO address (street, postcode, city, state)
                VALUES ('{new_street}', '{new_postcode}', '{city}', '{state}');
            """
            cur.execute(query)
            conn.commit()

    # Build the update query
    query = f"UPDATE credit_card SET {attribute} = %s WHERE number = %s AND email = %s;"

    # Execute the update query
    cur.execute(query, (new_value, card_number, email))
    conn.commit()

    print("Credit card details updated successfully.")



def modify_property(conn):
    cur = conn.cursor()

    agent_email = input("Enter your agent email address: ")
    property_id = input("Enter the property ID you want to modify: ")

    # Retrieve the current property details
    cur.execute(f"SELECT * FROM property WHERE PropertyID = {property_id} AND email = '{agent_email}';")
    property_details = cur.fetchone()

    if not property_details:
        print("No property found with the specified ID or the agent email is incorrect.")
        return

    print("Current property details:")
    print("PropertyID:", property_details[0])
    print("City:", property_details[1])
    print("State:", property_details[2])
    print("Description:", property_details[3])
    print("Address:", property_details[4])
    print("Neigh_postcode:", property_details[5])
    print("Neigh_name:", property_details[6])
    print("Price:", property_details[7])
    print("Rental_price:", property_details[8])
    print("IsInRent:", property_details[9])
    print("IsInSale:", property_details[10])
    print("Type:", property_details[11])
    print("Availability:", property_details[12])
    print("Square_footage:", property_details[13])

    # Update the property details
    city = input("Enter the new city or leave empty to keep the current value: ") or property_details[1]
    state = input("Enter the new state or leave empty to keep the current value: ") or property_details[2]
    description = input("Enter the new description or leave empty to keep the current value: ") or property_details[3]
    address = input("Enter the new address or leave empty to keep the current value: ") or property_details[4]
    neigh_postcode = int(input("Enter the new neighborhood postcode or leave empty to keep the current value: ") or property_details[5])
    neigh_name = input("Enter the new neighborhood name or leave empty to keep the current value: ") or property_details[6]
    price = float(input("Enter the new price or leave empty to keep the current value: ") or property_details[7])
    rental_price = float(input("Enter the new rental price or leave empty to keep the current value: ") or property_details[8])
    is_in_rent = input("Enter the new 'IsInRent' value (True/False) or leave empty to keep the current value: ") or property_details[9]
    is_in_sale = input("Enter the new 'IsInSale' value (True/False) or leave empty to keep the current value: ") or property_details[10]
    property_type = input("Enter the new property type or leave empty to keep the current value: ") or property_details[11]
    availability = input("Enter the new availability value (True/False) or leave empty to keep the current value: ") or property_details[12]
    square_footage = float(input("Enter the new square footage or leave empty to keep the current value: ") or property_details[13])
    query = f"""
    UPDATE property
    SET city = '{city}', state = '{state}', description = '{description}', address = '{address}',
        neigh_postcode = {neigh_postcode}, neigh_name = '{neigh_name}', price = {price},
        rental_price = {rental_price}, isinrent = {is_in_rent}, isinsale = {is_in_sale},
        type = '{property_type}', availability = {availability}, square_footage = {square_footage}
    WHERE PropertyID = {property_id} AND email = '{agent_email}';
    """

    cur.execute(query)
    conn.commit()

    print("Property updated successfully.")


def delete_property(conn):
    cur = conn.cursor()
    property_id = input("Enter your propertyID of the property you want to delete: ")
    query = f"DELETE FROM PROPERTY WHERE PropertyID = '{property_id}';"
    cur.execute(query)
    conn.commit()


def book_property(conn):
    cur = conn.cursor()

    renter_email = input("Enter your email address: ")
    property_id = input("Enter the property ID you want to book: ")
    cur.execute(f"SELECT availability FROM property WHERE propertyid = {property_id};")
    availability = cur.fetchall()
    print('Availability', availability)
    print(type(availability[0][0]))
    if availability[0][0] == False:
        print('Sorry, this property is not available.')
    else:
        # Retrieve available credit cards for the renter
        cur.execute(f"SELECT Number FROM CREDIT_CARD WHERE Email = '{renter_email}';")
        credit_cards = cur.fetchall()

        if not credit_cards:
            print("No credit cards found for this email address. Please add a credit card first.")
            return

        print("Available credit cards:")
        for card in credit_cards:
            print(card[0])

        card_number = input("Enter the credit card number you want to use for this booking: ")

        # Retrieve the next booking_id
        cur.execute("SELECT MAX(booking_id) FROM bookings;")
        max_booking_id = cur.fetchone()[0]
        booking_id = max_booking_id + 1 if max_booking_id is not None else 1

        # Check if the renter has a rewards_id
        cur.execute(f"SELECT reward_id FROM reward_program WHERE email = '{renter_email}';")
        rewards_id = cur.fetchone()[0]

        # Insert the booking into the bookings table
        query = f"""
        INSERT INTO bookings (cardnumber, email, propertyid, booking_id, rewards_id)
        VALUES ({card_number}, '{renter_email}', {property_id}, {booking_id}, {rewards_id if rewards_id is not None else 'NULL'});
        """

        cur.execute(query)

        # Update the property's availability
        cur.execute(f"UPDATE property SET Availability = FALSE WHERE PropertyID = {property_id};")

        conn.commit()

        print(f"Booking successful! Your booking ID is {booking_id}.")


def main(user='postgres', password='aitaroman'):
    conn = None
    try:
        conn = psycopg2.connect(host="localhost", database="realestate", user=user, password=password)
        
        while True:
            print("\nSelect an option:")
            print("1. Create an account")
            print("2. Add/modify address/payment information")
            print("4. Add a property (agents only)")
            print("5. Modify a property (agents only)")
            print("6. Delete a property (agents only)")
            print("7. Search for properties")
            print("8. Book a property (renters only)")
            print("9. WRITE QUERY")

            option = int(input("\nEnter your option: "))

            if option == 1:
                
                create_renter(conn)


            elif option == 2: # 2. Add/modify address information
                print("1. Add")
                print("2. Modify")
                option = int(input("Which action do you wanna take?"))

                if option == 1:
                    add_address_payment(conn)
                elif option == 2:
                    print('In')
                    modify_address_payment(conn)

            elif option == 7:
                search_properties(conn)

            elif option == 8:
                book_property(conn)

            elif option == 9:
                cur = conn.cursor()
                query = input("\nEnter your QUERY: ")
                cur.execute(query)
                print('where am I')
                conn.commit()
                
            
    

            else:
                print("Invalid option, please try again.")

    except Exception as e:
        print("Exception:", e)
    finally:
        if conn is not None:
            conn.close()
            print("DB connection closed.")

if __name__ == '__main__':
    main()
