
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

# Initialize the Flask app
app = Flask(__name__)

# Database connection
conn = sqlite3.connect('todo.db')
c = conn.cursor()

# Home page route
@app.route('/')
def index():
    # Get all todo lists
    lists = c.execute('SELECT * FROM lists').fetchall()
    return render_template('index.html', lists=lists)

# Login/Registration route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if user exists
        user = c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        if user:
            return redirect(url_for('index'))
        else:
            # Register the user
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect(url_for('index'))
    return render_template('login.html')

# Specific todo list route
@app.route('/list/<int:list_id>', methods=['GET', 'PUT', 'DELETE'])
def list(list_id):
    if request.method == 'GET':
        # Get the list and its items
        list_data = c.execute('SELECT * FROM lists WHERE id=?', (list_id,)).fetchone()
        items = c.execute('SELECT * FROM items WHERE list_id=?', (list_id,)).fetchall()
        return render_template('list.html', list_data=list_data, items=items)
    elif request.method == 'PUT':
        # Update the list
        data = request.get_json()
        c.execute('UPDATE lists SET name=? WHERE id=?', (data['name'], list_id))
        conn.commit()
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        # Delete the list and its items
        c.execute('DELETE FROM lists WHERE id=?', (list_id,))
        c.execute('DELETE FROM items WHERE list_id=?', (list_id,))
        conn.commit()
        return jsonify({'success': True})

# User settings route
@app.route('/settings', methods=['GET', 'PUT'])
def settings():
    if request.method == 'GET':
        # Get the user's settings
        user_data = c.execute('SELECT * FROM users WHERE id=?', (1,)).fetchone()
        return render_template('settings.html', user_data=user_data)
    elif request.method == 'PUT':
        # Update the user's settings
        data = request.get_json()
        c.execute('UPDATE users SET username=?, password=?, profile_image=? WHERE id=?',
                  (data['username'], data['password'], data['profile_image'], 1))
        conn.commit()
        return jsonify({'success': True})

# API endpoint for all todo lists
@app.route('/api/v1/lists')
def api_lists():
    lists = c.execute('SELECT * FROM lists').fetchall()
    return jsonify(lists)

# API endpoint for a specific todo list
@app.route('/api/v1/lists/<int:list_id>')
def api_list(list_id):
    list_data = c.execute('SELECT * FROM lists WHERE id=?', (list_id,)).fetchone()
    items = c.execute('SELECT * FROM items WHERE list_id=?', (list_id,)).fetchall()
    return jsonify({'list': list_data, 'items': items})

# API endpoint for creating, editing, or deleting todo list items
@app.route('/api/v1/items', methods=['POST', 'PUT', 'DELETE'])
def api_items():
    if request.method == 'POST':
        # Create a new item
        data = request.get_json()
        c.execute('INSERT INTO items (list_id, name, priority, due_date, reminder) VALUES (?, ?, ?, ?, ?)',
                  (data['list_id'], data['name'], data['priority'], data['due_date'], data['reminder']))
        conn.commit()
        return jsonify({'success': True})
    elif request.method == 'PUT':
        # Update an existing item
        data = request.get_json()
        c.execute('UPDATE items SET name=?, priority=?, due_date=?, reminder=? WHERE id=?',
                  (data['name'], data['priority'], data['due_date'], data['reminder'], data['id']))
        conn.commit()
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        # Delete an item
        data = request.get_json()
        c.execute('DELETE FROM items WHERE id=?', (data['id'],))
        conn.commit()
        return jsonify({'success': True})

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
