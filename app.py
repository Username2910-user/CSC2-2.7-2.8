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

# Function for Menu page

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
def load_data():
    try:
        with open('pizza.json') as file:
            pizzas = json.load(file)
        with open('addons.json') as file:
            addons = json.load(file)
        return pizzas, addons
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading data: {e}")
        flash("Unable to load pizza data.")
        return {}, {}
    
# Function 2 for the add to cart function

def add_to_cart():
    pizza = request.form.get("pizza")
    quantity = int(request.form.get("quantity"))
    pizzas, addons = load_data()
    cart = session.get("cart", {})

    if pizza not in pizzas:
        flash("Selected pizza is invalid.")
        return redirect(url_for("menu"))
    
    available_dough = pizzas[pizza]['dough']
    current_quantity = cart[pizza]['quantity', 0] if pizzas in cart else 0

    if available_dough <= 0:
        flash(f"Sorry, {pizza} is out of dough.")
        return redirect(url_for("menu"))

    if current_quantity + quantity > available_dough:
        flash(f"Sorry, you can only order {available_dough - current_quantity} more of {pizza}.")
        return redirect(url_for("menu"))
    


if __name__ == '__main__': 
      initialise_database()
      app.run(debug=True)