from flask import Flask, render_template
from functions import create_db_connection, create_db_connection_moment_logistics
from mysql.connector import Error
from flask import Flask, redirect, url_for, render_template, session, request, send_from_directory , jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from decimal import Decimal


app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
def index():

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    connection = create_db_connection()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()


    query = "SELECT * FROM todo WHERE reciver_id = %s"
    cursor.execute(query, (user_id,))
    todos = cursor.fetchall()

    return render_template('index.html', user=user, todos=todos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    id = session.get('user_id')
    if id:
        return redirect(url_for('index'))

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        connection = create_db_connection()
        if connection is None:
            return "Error connecting to the database"

        cursor = connection.cursor(dictionary=True)

        # Fetch user data from the database
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            new_user_id = user['id']
            session['user_id'] = new_user_id

            connection.commit()
            cursor.close()
            connection.close()

            return redirect(url_for('index'))

        return render_template("signin.html", invalid = True)


    return render_template('signin.html')


@app.route('/registeradmin', methods=['GET', 'POST'])
def register():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Process registration form data
        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        password = request.form['password']
        role = "client"

        # Connect to the database
        connection = create_db_connection()
        if connection is None:
            return "Error connecting to the database"

        cursor = connection.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return "This email is already in use."

        # Hash the password for security
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        insert_query = """
        INSERT INTO users (name, surname, email, password)
        VALUES (%s, %s ,%s, %s)
        """
        cursor.execute(insert_query, (name, surname, email, hashed_password))

        # Retrieve the ID of the newly inserted user
        cursor.execute("SELECT LAST_INSERT_ID()")
        new_user_id = cursor.fetchone()[0]

        session['user_id'] = new_user_id

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/assignadmin', methods=['GET', 'POST'])
def assign():

    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    connection = create_db_connection()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()


    if request.method == 'POST':
        # Process registration form data
        reciver_id = request.form['reciver_id']
        message = request.form['message']
        status = request.form['status']
        sender_id = user[0]
        sender_name = user[7]
        sender_surname = user[8]


        # Connect to the database
        connection = create_db_connection()
        if connection is None:
            return "Error connecting to the database"

        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (reciver_id,))
        reciver_rough = cursor.fetchone()

        # Insert new user into the database
        insert_query = """
        INSERT INTO todo (sender_id, sender_name, sender_surname, message, reciver_id, status, receiver_name)
        VALUES (%s, %s ,%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (sender_id, sender_name, sender_surname, message, reciver_id, status, reciver_rough[7]))


        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('assign'))

    return render_template('assign.html')


@app.route('/logout')
def logout():

    session.clear()
    return redirect(url_for('login'))


@app.route('/users')
def users():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    connection = create_db_connection()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()

    query = "SELECT * FROM users"
    cursor.execute(query)
    users = cursor.fetchall()

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    return render_template('users.html',users=users, user=user)



@app.route('/assignments')
def assignments():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    connection = create_db_connection()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()

    query = "SELECT * FROM todo"
    cursor.execute(query)
    todo = cursor.fetchall()

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()

    return render_template('todo.html',todo=todo, user=user)


@app.route('/delete_todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):

    connection = create_db_connection()
    if connection is None:
        return "Error connecting to the database"
    cursor = connection.cursor()
    query = "DELETE FROM todo WHERE id = %s"
    cursor.execute(query, (todo_id,))
    connection.commit()

    connection.commit()
    cursor.close()
    connection.close()


    return redirect(url_for('assignments'))


@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    # Logic to delete user
    return redirect(url_for('index'))

@app.route('/promote_user/<int:user_id>')
def promote_user(user_id):
    # Logic to promote user
    return redirect(url_for('index'))

@app.route('/demote_user/<int:user_id>')
def demote_user(user_id):
    # Logic to demote user
    return redirect(url_for('index'))


@app.route('/exhibitions')
def exhibitions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    connection = create_db_connection_moment_logistics()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()

    query = "SELECT * FROM exhibitions_en"
    cursor.execute(query)
    exhibitions = cursor.fetchall()

    return render_template('exhibitions.html', exhibitions=exhibitions)

@app.route('/add_exhibition', methods=['GET', 'POST'])
def add_exhibition():
    if request.method == 'POST':
        event_name = request.form['event_name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        city = request.form['city']
        venue = request.form['venue']
        host = request.form['host']
        organizer = request.form['organizer']
        sector = request.form['sector']
        phone = request.form['phone']
        email = request.form['email']
        website = request.form['website']

        # Connect to the database
        connection = create_db_connection_moment_logistics()
        if connection is None:
            return "Error connecting to the database"

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO exhibitions_en (event_name, start_date, end_date, city, venue, host, organizer, sector, phone, email, website)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (event_name, start_date, end_date, city, venue, host, organizer, sector, phone, email, website))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('add_exhibition'))

    return redirect(url_for('exhibitions'))

@app.route('/delete_exhibition', methods=['POST'])
def delete_exhibition():
    exhibition_id = request.form['id']

    connection = create_db_connection_moment_logistics()
    if connection is None:
        return "Error connecting to the database"

    cursor = connection.cursor()
    cursor.execute("DELETE FROM exhibitions_en WHERE id = %s", (exhibition_id,))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('exhibitions'))



if __name__ == '__main__':
    app.run(debug=True)
