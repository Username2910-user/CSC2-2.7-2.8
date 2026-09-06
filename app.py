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

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about_us.html")

@app.route("/menu")
def menu():
    pizzas, addons = load_data()
    cart = session.get("cart", {})
    selected_addons = session.get("selected_addons", {})
    total, pizza_subtotal, addon_subtotal, discount, discount_applied = calculate_total(cart, selected_addons)
    return render_template("menu.html",pizzas=pizzas, addons=addons, cart=cart, total=total,
                           selected_addons=selected_addons, pizza_subtotal=pizza_subtotal,
                           addon_subtotal=addon_subtotal, discount=discount, discount_applied=discount_applied,)
        
def calculate_total(cart, selected_addons):
    pizza_subtotal = sum(item["price"] * item["quantity"] for item in cart.values())
    addon_subtotal = sum(selected_addons.values())

    discount = 0
    discount_applied = False
    if pizza_subtotal >= 60:
        discount = pizza_subtotal * 0.10
        discount_applied = True

    total = addon_subtotal + pizza_subtotal - discount
    return total, pizza_subtotal, addon_subtotal, discount, discount_applied




if __name__ == '__main__': 
      initialise_database()
      app.run(debug=True)