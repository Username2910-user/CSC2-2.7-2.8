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
@app.route("/add_to_cart", methods=["POST"])
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

    if pizza in cart:
        cart[pizza]["quantity"] += quantity
    else:
        cart[pizza] = {"price": pizzas[pizza]["price"], "quantity": quantity}

    session["cart"] = cart
    session.modified = True
    flash(f"{quantity} {pizza}(s) added to cart.")
    return redirect(url_for("menu"))

# Function 3 for the remove from cart function

@app.route("/remove_from_cart/<item>")  
def remove_from_cart(item):
    cart = session.get("cart", {})
    if item in cart:
        del cart[item]
        session["cart"] = cart
        session.modified = True
        flash(f"Removed {item} from the cart.")
    else:
        flash("Item not found in cart.")
    return redirect(url_for("menu"))

# Function 4 for the selected addon function 

@app.route("/select_addon", methods=["POST"])
def select_addon():
    pizzas, addons = load_data()
    selected_keys = request.form.getlist("addons")
    selected_addons = {}

    for addon in selected_keys:
        if addon in addons:
            selected_addons[addon] = float(addons[addon]["price"])

    session["selected_addons"] = selected_addons
    session.modified = True
    flash(f"{len(selected_addons)} add-on(s) selected.")
    return redirect(url_for("menu"))    

# Function 5  cancel order function
@app.route("/cancel_order", methods=["POST"])
def cancel_order():
    session.pop("cart", None)
    session.pop("selected_addons", None)
    flash("Order is canceled.")
    return redirect(url_for("menu")) 

# Function 6 for the checkout function

@app.route("/checkout", methods=["POST"])
def checkout():
    customer_name = request.form["customer_name"].strip().title()
    if not customer_name:
        flash("Customer name is required.")
        return redirect(url_for("menu"))

    cart = session.get("cart", {})
    selected_addons = session.get("selected_addons", {})

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for("menu"))
    
    # Calculate totals and generate invoice number

    total, pizza_subtotal, addon_subtotal, discount, discount_applied = calculate_total(cart, selected_addons)
    invoice_date = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    invoice_number = f"INV_{customer_name.replace(' ', '_')}_{invoice_date}"

    # Save order to database pizzaria
    with sqlite3.connect ('pizzaria.db') as conn:
     cursor = conn.cursor()
     cursor.execute('''
      INSERT INTO orders (invoice_number, customer_name, items, addons, total)
      VALUES (?, ?, ?, ?, ?)
    ''', (invoice_number, customer_name, json.dumps(cart),  json.dumps(selected_addons), total))
    conn.commit()

    with open('data/pizza.json', "r") as file:
        pizza_data = json.load(file)

    for pizza_name, details in cart.items():
        if pizza_name in pizza_data:
            pizza_data[pizza_name]["dough"] -= details["quantity"]
            if pizza_data[pizza_name]["dough"] < 0:
                pizza_data[pizza_name]["dough"] = 0

    try:
        with open('data/pizza.json', "w") as file:
            json.dump(pizza_data, file, indent=4)

    except OSError as e:
        print(f"Dough update error: {e}")
        flash("Could not update dough file.")

    # Invoice file 

    invoice_filename = f"{invoice_number}.txt"

    with open(invoice_filename, "w") as f:
        f.write("----- Neapolina Pizzaria Invoice -----\n\n")
        f.write(f"Invoice Number: {invoice_number}\n")
        f.write(f"Customer Name: {customer_name}\n")
        f.write(f"Date: {invoice_date}\n\n")
        f.write("Items:\n")

        for item, details in cart.items():
            f.write(f"- {item}: {details['quantity']} x ${details['price']} = ${details['quantity'] * details['price']:.2f}\n")

        if selected_addons:
            f.write("\nAdd-Ons:\n")
            for addon, price in selected_addons.items():
                f.write(f"- {addon}: ${price:.2f}\n"
                        )
        f.write(f"\nTotal: ${total:.2f}\n")

    # Function to clear the cart and the rest of items after checkout is finished

    session.pop("cart", None)
    session.pop("selected_addons", None)
    session.modified = True

    return render_template(
        "invoice.html", customer_name=customer_name, total=total,
        invoice_date=invoice_date, invoice_number=invoice_number, cart=cart,
        pizza_subtotal=pizza_subtotal, addon_subtotal=addon_subtotal,
        selected_addons=selected_addons, discount=discount, discount_applied=discount_applied,
    )

# Function 7: Order or Order History function

app.route("/orders")
def orders_history():
    with sqlite3.connect('pizzaria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY date DESC")
        rows = cursor.fetchall()

    orders = []
    for row in rows:
        orders.append({
            "order_id": row[0],
            "invoice_number": row[1],
            "customer_name": row[2],
            "items": json.loads(row[3]),
            "addons": json.loads(row[4]),
            "total": row[5],
            "date": row[6],
        })

    return render_template("order_history.html", orders=orders)

# Function 8: Cancel Saved Order function

@app.route('/cancel_saved_order/<int:order_id>', methods=['POST'])
def cancel_saved_order(order_id):
    with sqlite3.connect('pizzaria.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = ?",(order_id,))
        flash(f"Order #{order_id} cancelled.")
        conn.commit()
    return redirect(url_for('order_history'))

if __name__ == '__main__': 
      initialise_database()
      app.run(debug=True)