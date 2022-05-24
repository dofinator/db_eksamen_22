#app.py
from flask import Flask, request, session, redirect, url_for, render_template, flash
import re
import requests 
import traceback
from utils import get_connection_postgres
from settings import CONNECTION_POSTGRES, SECRET
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = SECRET
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)

 
@app.route('/')
def home():
    try:
        # Check if user is loggedin
        if 'loggedin' in session and session['loggedin'] == True:
            # User is loggedin show them the home page
            return render_template('home.html', account=session)
        # User is not loggedin redirect to login page
        
        return redirect(url_for('login'))
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO public.error_log (error) values (%s)', [error])
        flash('Looks like something went wrong')
        return redirect(url_for('logout'))
        

    
@app.route('/movies/recommendations', methods=['GET'])
def movies():
    if 'loggedin' in session and session['loggedin'] == True:
        movies = requests.get('http://127.0.0.1:5001/movies/recommendations')
        if movies.status_code == 200:
            movies = movies.json()
            session['movies'] = movies        
            return render_template('movies.html', account=session)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Check if "username" and "password" POST requests exist (user submitted form)
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            password = request.form['password']
            email = request.form['email']
            # Check if account exists using MySQL
            try:
                with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT id,email,password,name FROM users WHERE email = %s', [email])
                # Fetch one record and return result
                        account = cursor.fetchone()
            except:
                traceback.print_exc()
                error = traceback.format_exc()
                with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute('INSERT INTO public.error_log (error) values (%s)', [error])
                flash('Looks like something went wrong')
                return render_template('login.html')
            if account:
                print(account)
                user_id, user_email, user_password_rs, user_name = account
                # If account exists in users table in out database
                if check_password_hash(user_password_rs, password):
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = user_id
                    session['name'] = user_name
                    session['email'] = user_email
                    #Redirect to home page
                    return redirect(url_for('home'))
                else:
                    # Account doesnt exist or username/password incorrect
                    flash('Incorrect username/password')
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        return render_template('login.html')
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO public.error_log (fk_user_id,error) values (%s,%s)', [user_id,error])
        flash('Looks like something went wrong')
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if 'loggedin' in session and session['loggedin'] == True:
            flash('You cannot register a new user when u are logged in')
            return render_template('profile.html', account=session)
        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
            name = request.form['name']
            password = request.form['password']
            password2 = request.form['password2']
            email = request.form['email']

            # Does the passwords match ?
            if not password == password2:
                flash('Please make sure your passwords match')
                return render_template('register.html')

            _hashed_password = generate_password_hash(password)
    
            #Check if account exists
        
            with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM users WHERE email = %s', [email])
                    account = cursor.fetchone()
        
            # If account exists show error and validation checks
            if account:
                flash('Account already exists!')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                flash('Invalid email address!')
            elif not re.match(r'[A-Za-z0-9]+', name):
                flash('name must contain only characters and numbers!')
            elif not name or not password or not email:
                flash('Please fill out the form!')
            else:
                # Else if account doesnt exists and form data input is valid, then insert new account into public.users table
                with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("INSERT INTO users (name, password, email) VALUES (%s,%s,%s)", (name, _hashed_password, email))
                flash('You have successfully registered!')
        # empty filed in register from
        elif request.method == 'POST':
            flash('Please fill out the form!')
        # Show registration form with message (if any)
        return render_template('register.html')
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO public.error_log (error) values (%s)', [error])
        flash('Looks like something went wrong')
        return render_template('register.html')

@app.route('/logout')
def logout():
    try:
        # Remove session data, this will log the user out
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('name', None)
        session.pop('email', None)
        # Redirect to login page
        return redirect(url_for('login'))
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO public.error_log (error) values (%s)', [error])
        return redirect(url_for('login'))
  
@app.route('/profile')
def profile(): 
    # Check if user is loggedin
    try:
        if 'loggedin' in session and session['loggedin'] == True:
            
            with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
                    results = cursor.fetchone()
                    account = {}
                    account['name'] = results[3]
                    account['email'] = results[1]
                    print('ACCOUNT _____ ',account)
            # Show the profile page with account info
            return render_template('profile.html', account=account)
        # User is not loggedin redirect to login page
        return redirect(url_for('login'))
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        user_id = session['id']
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO public.error_log (fk_user_id,error) values (%s,%s)', [user_id,error])
        flash('Looks like something went wrong and u have been logged out')
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000)