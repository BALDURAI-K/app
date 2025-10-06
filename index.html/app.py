import streamlit as st
import mysql.connector
from datetime import date
import pandas as pd
import numpy as np

# --- Database Connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # Your MySQL username
        password="root",       # Your MySQL password
        database="store_db"
    )

# --- Add Product ---
def add_product(name, price, stock):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("INSERT INTO products (name, price, stock) VALUES (%s,%s,%s)",
                   (name, price, stock))
    db.commit()
    cursor.close()
    db.close()

# --- View Products ---
def fetch_products():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    data = cursor.fetchall()
    db.close()
    return pd.DataFrame(data, columns=['ID', 'Name', 'Price', 'Stock'])

# --- Record Sale ---


def record_sale(product_id, quantity):
    # Convert to standard Python int
    product_id = int(product_id)
    quantity = int(quantity)
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT stock FROM products WHERE id=%s", (product_id,))
    stock = cursor.fetchone()[0]

    if stock >= quantity:
        cursor.execute(
            "INSERT INTO sales (product_id, quantity, date) VALUES (%s, %s, NOW())",
            (product_id, quantity)
        )
        cursor.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s",
            (quantity, product_id)
        )
        db.commit()
        print("Sale recorded successfully.")
    else:
        print("Not enough stock.")

        st.success("✅ Sale recorded and stock updated!")
    cursor.close()
    db.close()

# --- Fetch Sales ---
def fetch_sales():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT s.sale_id, p.name, s.quantity, p.price, (s.quantity*p.price) as total, s.date
        FROM sales s JOIN products p ON s.product_id = p.id
        ORDER BY s.date DESC
    """)
    data = cursor.fetchall()
    db.close()
    return pd.DataFrame(data, columns=['Sale ID', 'Product', 'Quantity', 'Price', 'Total', 'Date'])

# --- Streamlit App ---
st.title("🛒 Online Store Inventory Management System")

menu = ["Home", "Add Product", "View Products", "Record Sale", "Sales Report"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Home":
    st.subheader("Welcome to the Inventory Management System")
    st.write("Use the menu on the left to manage products and sales.")

elif choice == "Add Product":
    st.subheader("Add New Product")
    name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0.0)
    stock = st.number_input("Stock", min_value=0)
    if st.button("Add Product"):
        if name:
            add_product(name, price, stock)
            st.success(f"Product '{name}' added successfully!")
        else:
            st.error("Please enter a product name.")

elif choice == "View Products":
    st.subheader("All Products")
    df = fetch_products()
    st.dataframe(df)

elif choice == "Record Sale":
    st.subheader("Record a Sale")
    df = fetch_products()
    product_list = df['Name'].tolist()
    product_choice = st.selectbox("Select Product", product_list)
    quantity = st.number_input("Quantity Sold", min_value=1, value=1)

    if st.button("Record Sale"):
        product_id = df[df['Name'] == product_choice]['ID'].values[0]
        record_sale(product_id, quantity)

elif choice == "Sales Report":
    st.subheader("Sales Report")
    df = fetch_sales()
    st.dataframe(df)
    if not df.empty:
        total_sales = df['Total'].sum()
        st.write(f"💰 Total Sales Amount: ₹{total_sales}")
