import json
import datetime
import sqlite3


app = Flask(____name____)
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

# Function for index 
@app.route('/')
def index():
  pizza, addons = load_data()
  cart = session.get('cart', {})
  selected_addons = session.get('selected_addons', {})
  total, pizza_subtotal, addon_subtotal, discount, discount_applied = calculate_total(cart, selected_addons)
  return render_template("index.html", pizzas=pizza_subtotal, addons=addons, cart=cart, total=total, selected_addons=selected_addons, 
                         pizza_subtotal=pizza_subtotal, addon_subtotal=addon_subtotal, discount= discount, discount_applied= discount_applied )


if_name_== '__main__':
initalise_database()
app.run(debug=True)