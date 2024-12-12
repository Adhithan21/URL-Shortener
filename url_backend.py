from flask import Flask, request, jsonify, redirect
import sqlite3
import string
import random

app = Flask(__name__)

# Database setup
DATABASE = 'urls.db'


# Function to execute SQL commands
def execute_query(query, args=(), fetch=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        if fetch:
            return cursor.fetchall()
        conn.commit()


# Initialize the database
def init_db():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS URL (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_url TEXT UNIQUE NOT NULL
    );
    """
    execute_query(create_table_query)


# Function to generate a unique short URL
def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choices(characters, k=6))
        query = "SELECT 1 FROM URL WHERE short_url = ?"
        if not execute_query(query, (short_url,), fetch=True):
            return short_url


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    original_url = data.get('url')
    custom_alias = data.get('custom_alias')

    if not original_url:
        return jsonify({'error': 'Original URL is required'}), 400

    if custom_alias:
        # Check if the custom alias is already in use
        query = "SELECT 1 FROM URL WHERE short_url = ?"
        if execute_query(query, (custom_alias,), fetch=True):
            return jsonify({'error': 'Custom alias already in use'}), 400
        short_url = custom_alias
    else:
        short_url = generate_short_url()

    # Insert the new URL mapping into the database
    insert_query = "INSERT INTO URL (original_url, short_url) VALUES (?, ?)"
    execute_query(insert_query, (original_url, short_url))

    return jsonify({'short_url': short_url}), 201


@app.route('/<short_url>', methods=['GET'])
def redirect_to_url(short_url):
    query = "SELECT original_url FROM URL WHERE short_url = ?"
    result = execute_query(query, (short_url,), fetch=True)
    if result:
        return redirect(result[0][0])  # Redirect to the original URL
    return jsonify({'error': 'URL not found'}), 404


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
