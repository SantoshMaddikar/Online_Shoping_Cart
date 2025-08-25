import mysql.connector

# Database connection details
db_config = {
    'user': 'root',
    'password': 'jamssy@1432',
    'host': 'localhost',
    'database': 'shopping_cart'
}

# Connect to the database
def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return None

# Create database tables
def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS shopping_cart")
    cursor.execute("USE shopping_cart")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role ENUM('user', 'admin') NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_id INT,
        quantity INT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )
    """)
    connection.commit()
    print("Tables created successfully.")

# Initialize admin user if not exists
def initialize_admin(connection):
    cursor = connection.cursor()
    cursor.execute("USE shopping_cart")
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", ('admin', 'admin_pass', 'admin'))
        connection.commit()
        print("Admin user created.")

# Register a new user
def register_user(connection, username, password):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password, 'user'))
    connection.commit()
    print("User registered SUCCESSFULLY.")

# User login
def login(connection, username, password):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()
    return user

# Add a product (admin only)
def add_product(connection, name, description, price):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO products (name, description, price) VALUES (%s, %s, %s)", (name, description, price))
    connection.commit()
    print("Product added SUCCESSFULLY.")

# View all products
def view_products(connection):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

# Place an order (user only)
def place_order(connection, user_id, products):
    cursor = connection.cursor()
    for product_id, quantity in products:
        cursor.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s)", (user_id, product_id, quantity))
    connection.commit()
    print("Order placed SUCCESSFULLY.")

# View user orders
def view_orders(connection, user_id):
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
    SELECT orders.id, products.name, orders.quantity
    FROM orders
    JOIN products ON orders.product_id = products.id
    WHERE orders.user_id = %s
    """, (user_id,))
    return cursor.fetchall()

def main():
    connection = create_connection()
    if connection:
        print("Connected to the database.")
        
        # Create tables and initialize admin if needed
        create_tables(connection)
        initialize_admin(connection)
        
        while True:
            print("1. Login")
            print("2. Register")
            print("3. Exit")
            choice = input("Enter your choice: ")
            
            if choice == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")
                user = login(connection, username, password)
                
                if user:
                    print(f"Welcome {user['username']}! Role: {user['role']}")
                    
                    if user['role'] == 'admin':
                        while True:
                            print("1. Add Product")
                            print("2. View Products")
                            print("3. Logout")
                            admin_choice = input("Enter your choice: ")
                            
                            if admin_choice == '1':
                                name = input("Enter product name: ")
                                description = input("Enter product description: ")
                                price = float(input("Enter product price: "))
                                add_product(connection, name, description, price)
                            elif admin_choice == '2':
                                products = view_products(connection)
                                for product in products:
                                    print(product)
                            elif admin_choice == '3':
                                break
                            else:
                                print("Invalid choice. Try again.")
                    
                    elif user['role'] == 'user':
                        while True:
                            print("1. View Products")
                            print("2. Place Order")
                            print("3. View Orders")
                            print("4. Logout")
                            user_choice = input("Enter your choice: ")
                            
                            if user_choice == '1':
                                products = view_products(connection)
                                for product in products:
                                    print(product)
                            elif user_choice == '2':
                                products = []
                                while True:
                                    product_id = int(input("Enter product ID to add to order (0 to finish): "))
                                    if product_id == 0:
                                        break
                                    quantity = int(input("Enter quantity: "))
                                    products.append((product_id, quantity))
                                place_order(connection, user['id'], products)
                            elif user_choice == '3':
                                orders = view_orders(connection, user['id'])
                                for order in orders:
                                    print(order)
                            elif user_choice == '4':
                                break
                            else:
                                print("Invalid choice. Try again.")
                else:
                    print("Invalid credentials. Try again.")
            
            elif choice == '2':
                username = input("Enter new username: ")
                password = input("Enter new password: ")
                register_user(connection, username, password)
            
            elif choice == '3':
                break
            
            else:
                print("Invalid choice. Try again.")
        
        connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()