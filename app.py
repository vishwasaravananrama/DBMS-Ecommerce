"""Mini E-Commerce Inventory & Order Management System (Flask + MySQL)."""
import os
from decimal import Decimal, InvalidOperation

import pymysql
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from pymysql.cursors import DictCursor

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")


# ---------------------------------------------------------------- DB helpers
def get_conn():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "mini_ecommerce_db"),
        cursorclass=DictCursor,
        autocommit=False,
    )


def query(sql, params=None, one=False):
    """Run a SELECT and return rows (or a single row)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            rows = cur.fetchall()
        return (rows[0] if rows else None) if one else rows
    finally:
        conn.close()


def execute(sql, params=None):
    """Run INSERT/UPDATE/DELETE, commit, return last inserted id."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            new_id = cur.lastrowid
        conn.commit()
        return new_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------- Dashboard
@app.route("/")
def dashboard():
    stats = {
        "products": query("SELECT COUNT(*) AS n FROM products", one=True)["n"],
        "customers": query("SELECT COUNT(*) AS n FROM customers", one=True)["n"],
        "orders": query("SELECT COUNT(*) AS n FROM orders", one=True)["n"],
        "stock": query("SELECT COALESCE(SUM(stock_quantity),0) AS n FROM products", one=True)["n"],
    }
    recent = query(
        """SELECT o.order_id, c.customer_name, o.order_date, o.total_amount, o.status
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id DESC LIMIT 5"""
    )
    chart = query(
        """SELECT c.category_name, COUNT(p.product_id) AS n
           FROM categories c LEFT JOIN products p ON c.category_id = p.category_id
           GROUP BY c.category_id, c.category_name"""
    )
    low = query("SELECT product_name, stock_quantity FROM products WHERE stock_quantity < 10 ORDER BY stock_quantity")
    return render_template("dashboard.html", stats=stats, recent=recent, chart=chart, low=low)


# ---------------------------------------------------------------- Categories
@app.route("/categories", methods=["GET", "POST"])
def categories():
    if request.method == "POST":
        name = request.form.get("category_name", "").strip()
        desc = request.form.get("description", "").strip()
        if not name:
            flash("Category name is required.", "danger")
        else:
            try:
                execute("INSERT INTO categories (category_name, description) VALUES (%s, %s)", (name, desc))
                flash("Category added.", "success")
            except pymysql.err.IntegrityError:
                flash("That category already exists.", "danger")
        return redirect(url_for("categories"))
    rows = query(
        """SELECT c.category_id, c.category_name, c.description, COUNT(p.product_id) AS product_count
           FROM categories c LEFT JOIN products p ON c.category_id = p.category_id
           GROUP BY c.category_id, c.category_name, c.description ORDER BY c.category_name"""
    )
    return render_template("categories.html", categories=rows)


# ---------------------------------------------------------------- Products
def read_product_form():
    """Validate product form. Returns (data, error)."""
    f = request.form
    name = f.get("product_name", "").strip()
    sku = f.get("sku", "").strip()
    if not name:
        return None, "Product name is required."
    if not sku:
        return None, "SKU is required."
    if not f.get("category_id"):
        return None, "Please choose a category."
    try:
        price = Decimal(f.get("price", ""))
        stock = int(f.get("stock_quantity", ""))
    except (InvalidOperation, ValueError):
        return None, "Price and stock must be valid numbers."
    if price < 0:
        return None, "Price cannot be negative."
    if stock < 0:
        return None, "Stock cannot be negative."
    return (name, sku, int(f["category_id"]), f.get("description", "").strip(), price, stock), None


@app.route("/products")
def products():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "").strip()
    sql = """SELECT p.*, c.category_name FROM products p
             JOIN categories c ON p.category_id = c.category_id WHERE 1=1"""
    params = []
    if q:
        sql += " AND (p.product_name LIKE %s OR p.sku LIKE %s)"
        params += [f"%{q}%", f"%{q}%"]
    if cat:
        sql += " AND p.category_id = %s"
        params.append(cat)
    sql += " ORDER BY p.product_id DESC"
    rows = query(sql, params)
    cats = query("SELECT * FROM categories ORDER BY category_name")
    return render_template("products.html", products=rows, categories=cats, q=q, cat=cat)


@app.route("/products/add", methods=["GET", "POST"])
def add_product():
    cats = query("SELECT * FROM categories ORDER BY category_name")
    if request.method == "POST":
        data, error = read_product_form()
        if error:
            flash(error, "danger")
            return render_template("product_form.html", product=request.form, categories=cats, mode="Add")
        try:
            execute(
                """INSERT INTO products (product_name, sku, category_id, description, price, stock_quantity)
                   VALUES (%s,%s,%s,%s,%s,%s)""",
                data,
            )
            flash("Product added.", "success")
            return redirect(url_for("products"))
        except pymysql.err.IntegrityError:
            flash("SKU already exists. Use a unique SKU.", "danger")
            return render_template("product_form.html", product=request.form, categories=cats, mode="Add")
    return render_template("product_form.html", product={}, categories=cats, mode="Add")


@app.route("/products/<int:pid>/edit", methods=["GET", "POST"])
def edit_product(pid):
    cats = query("SELECT * FROM categories ORDER BY category_name")
    product = query("SELECT * FROM products WHERE product_id=%s", (pid,), one=True)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("products"))
    if request.method == "POST":
        data, error = read_product_form()
        if error:
            flash(error, "danger")
            return render_template("product_form.html", product=request.form, categories=cats, mode="Edit")
        try:
            execute(
                """UPDATE products SET product_name=%s, sku=%s, category_id=%s, description=%s,
                   price=%s, stock_quantity=%s WHERE product_id=%s""",
                data + (pid,),
            )
            flash("Product updated.", "success")
            return redirect(url_for("products"))
        except pymysql.err.IntegrityError:
            flash("SKU already exists. Use a unique SKU.", "danger")
            return render_template("product_form.html", product=request.form, categories=cats, mode="Edit")
    return render_template("product_form.html", product=product, categories=cats, mode="Edit")


@app.route("/products/<int:pid>/delete", methods=["POST"])
def delete_product(pid):
    try:
        execute("DELETE FROM products WHERE product_id=%s", (pid,))
        flash("Product deleted.", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete: this product is used in existing orders.", "danger")
    return redirect(url_for("products"))


# ---------------------------------------------------------------- Customers
@app.route("/customers")
def customers():
    rows = query("SELECT * FROM customers ORDER BY customer_id DESC")
    return render_template("customers.html", customers=rows)


@app.route("/customers/add", methods=["GET", "POST"])
def add_customer():
    if request.method == "POST":
        f = request.form
        if not f.get("customer_name", "").strip() or not f.get("email", "").strip():
            flash("Name and email are required.", "danger")
            return render_template("customer_form.html", customer=f, mode="Add")
        try:
            execute(
                "INSERT INTO customers (customer_name, email, phone, address) VALUES (%s,%s,%s,%s)",
                (f["customer_name"].strip(), f["email"].strip(), f.get("phone", "").strip(), f.get("address", "").strip()),
            )
            flash("Customer added.", "success")
            return redirect(url_for("customers"))
        except pymysql.err.IntegrityError:
            flash("A customer with this email already exists.", "danger")
            return render_template("customer_form.html", customer=f, mode="Add")
    return render_template("customer_form.html", customer={}, mode="Add")


@app.route("/customers/<int:cid>/edit", methods=["GET", "POST"])
def edit_customer(cid):
    customer = query("SELECT * FROM customers WHERE customer_id=%s", (cid,), one=True)
    if not customer:
        flash("Customer not found.", "danger")
        return redirect(url_for("customers"))
    if request.method == "POST":
        f = request.form
        if not f.get("customer_name", "").strip() or not f.get("email", "").strip():
            flash("Name and email are required.", "danger")
            return render_template("customer_form.html", customer=f, mode="Edit")
        try:
            execute(
                "UPDATE customers SET customer_name=%s, email=%s, phone=%s, address=%s WHERE customer_id=%s",
                (f["customer_name"].strip(), f["email"].strip(), f.get("phone", "").strip(), f.get("address", "").strip(), cid),
            )
            flash("Customer updated.", "success")
            return redirect(url_for("customers"))
        except pymysql.err.IntegrityError:
            flash("A customer with this email already exists.", "danger")
            return render_template("customer_form.html", customer=f, mode="Edit")
    return render_template("customer_form.html", customer=customer, mode="Edit")


# ---------------------------------------------------------------- Orders
@app.route("/orders")
def orders():
    rows = query(
        """SELECT o.order_id, c.customer_name, o.order_date, o.total_amount, o.status
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           ORDER BY o.order_id DESC"""
    )
    return render_template("orders.html", orders=rows)


@app.route("/orders/new", methods=["GET", "POST"])
def create_order():
    custs = query("SELECT customer_id, customer_name FROM customers ORDER BY customer_name")
    prods = query("SELECT product_id, product_name, price, stock_quantity FROM products WHERE stock_quantity > 0 ORDER BY product_name")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        ids = request.form.getlist("product_id")
        qtys = request.form.getlist("quantity")

        # Merge duplicate products and validate numbers
        wanted = {}
        try:
            for pid, qty in zip(ids, qtys):
                if not pid:
                    continue
                qty = int(qty)
                if qty <= 0:
                    raise ValueError
                wanted[int(pid)] = wanted.get(int(pid), 0) + qty
        except ValueError:
            flash("Quantities must be positive whole numbers.", "danger")
            return render_template("create_order.html", customers=custs, products=prods)

        if not customer_id or not wanted:
            flash("Select a customer and at least one product.", "danger")
            return render_template("create_order.html", customers=custs, products=prods)

        conn = get_conn()
        try:
            with conn.cursor() as cur:  # one transaction for the whole order
                cur.execute(
                    "INSERT INTO orders (customer_id, total_amount, status) VALUES (%s, 0, 'Placed')",
                    (customer_id,),
                )
                order_id = cur.lastrowid
                total = Decimal("0")
                for pid, qty in wanted.items():
                    # lock the row so two orders cannot take the same stock
                    cur.execute(
                        "SELECT product_name, price, stock_quantity FROM products WHERE product_id=%s FOR UPDATE",
                        (pid,),
                    )
                    p = cur.fetchone()
                    if not p:
                        raise ValueError("A selected product no longer exists.")
                    if p["stock_quantity"] < qty:
                        raise ValueError(
                            f"Insufficient stock for '{p['product_name']}': "
                            f"requested {qty}, available {p['stock_quantity']}."
                        )
                    subtotal = p["price"] * qty
                    total += subtotal
                    cur.execute(
                        """INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                           VALUES (%s,%s,%s,%s,%s)""",
                        (order_id, pid, qty, p["price"], subtotal),
                    )
                    cur.execute(
                        "UPDATE products SET stock_quantity = stock_quantity - %s WHERE product_id=%s",
                        (qty, pid),
                    )
                cur.execute("UPDATE orders SET total_amount=%s WHERE order_id=%s", (total, order_id))
            conn.commit()
            flash(f"Order #{order_id} placed successfully. Total: ₹{total}", "success")
            return redirect(url_for("order_detail", oid=order_id))
        except ValueError as e:
            conn.rollback()  # nothing is saved, stock untouched
            flash(str(e), "danger")
        except Exception as e:
            conn.rollback()
            flash(f"Order failed and was rolled back: {e}", "danger")
        finally:
            conn.close()
        return render_template("create_order.html", customers=custs, products=prods)

    return render_template("create_order.html", customers=custs, products=prods)


@app.route("/orders/<int:oid>")
def order_detail(oid):
    order = query(
        """SELECT o.*, c.customer_name, c.email, c.phone, c.address
           FROM orders o JOIN customers c ON o.customer_id = c.customer_id
           WHERE o.order_id=%s""",
        (oid,),
        one=True,
    )
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("orders"))
    items = query(
        """SELECT p.product_name, p.sku, i.quantity, i.unit_price, i.subtotal
           FROM order_items i JOIN products p ON i.product_id = p.product_id
           WHERE i.order_id=%s""",
        (oid,),
    )
    return render_template("order_detail.html", order=order, items=items)


if __name__ == "__main__":
    app.run(debug=True)
