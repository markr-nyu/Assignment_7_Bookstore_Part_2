from flask import Flask, render_template, request, url_for
import os
import sqlite3

app = Flask(__name__)

# -----------------------------
# DB CONNECTION
# -----------------------------
def get_db_connection():
    conn = sqlite3.connect('bookstore.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_categories():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return rows

# -----------------------------
# ROUTES
# -----------------------------
@app.route('/')
def home():
    categories = get_categories()
    return render_template("index.html", categories=categories)

@app.route('/category')
def category():
    category_id = request.args.get("categoryId", type=int)
    
    conn = get_db_connection()
    selected_books = conn.execute(
        "SELECT * FROM books WHERE categoryId = ?",
        (category_id,)
    ).fetchall()
    conn.close()

    return render_template(
        "category.html",
        selectedCategory=category_id,
        categories=get_categories(),
        books=selected_books
    )

@app.route('/search', methods=["POST"])
def search():
    term = request.form.get("search", "").strip()

    conn = get_db_connection()
    results = conn.execute(
        "SELECT * FROM books WHERE lower(title) LIKE lower(?)",
        (f"%{term}%",)
    ).fetchall()
    conn.close()

    return render_template(
        "category.html",
        selectedCategory=None,
        categories=get_categories(),
        books=results,
        searchTerm=term,
        nothingFound=(len(results) == 0)
    )

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute("""
        SELECT books.*, categories.name AS categoryName
        FROM books
        JOIN categories ON categories.id = books.categoryId
        WHERE books.id = ?
    """, (book_id,)).fetchone()
    conn.close()

    if book is None:
        return render_template("error.html", error="Book not found")

    return render_template(
        "book_detail.html",
        book=book,
        categories=get_categories()
    )


@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

