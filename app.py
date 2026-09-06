import json
import datetime
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash


app = Flask(__name__)

app.secret_key = "pizzaria_pizza"

def initialise_database():
  with sqlite3.connect('pizzaria.db') as conn:
    cursor = conn.cursor()
    cursor.execute(''' 
      CREATE TABLE IF NOT EXISTS orders ( 
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT,
        customer_name TEXT,
        items TEXT,
        addons TEXT,
        total REAL, 
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    ''')
    conn.commit()

def save_order(customer_name, product_name, quantity, total_price):
    """INSERT one row into the orders table. Called when checkout happens."""
    connection = sqlite3.connect('pizzaria.db')
    connection.execute(
        "INSERT INTO orders (customer_name, product_name, quantity, total_price) VALUES (?, ?, ?, ?)",
        (customer_name, product_name, quantity, total_price),
    )
    connection.commit()

@app.route('/about')
def about():
  return render_template('menu.html')


# Function for index 
@app.route('/')
def index():


if __name__ == '__main__': 
      
    initialise_database()
    app.run(debug=True)