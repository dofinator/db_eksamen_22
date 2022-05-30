#app.py
from ftplib import all_errors
import re
from flask import Flask, jsonify, request, session, redirect, url_for, render_template, flash
import requests
import traceback
import json
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
        # checks when accessiong /home is the user is already logged in
        if 'loggedin' in session and session['loggedin'] == True:
            return redirect(url_for('get_reviews'))
        else:
            return redirect(url_for('login'))
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO public.error_log (error) values (%s)', [error])
        flash('Looks like something went wrong')
        return redirect(url_for('logout'))

# ??        
@app.route('/reviews', methods=['GET'])
def get_reviews():
    try:
        if 'loggedin' in session and session['loggedin'] == True:
            user_id = str(session['id'])
            user_reviews = requests.get(f'http://127.0.0.1:5002/user/getreviews/{user_id}')
            if user_reviews.status_code == 200:
                user_reviews = user_reviews.json()
                session['movies'] = user_reviews        
                return render_template('reviews.html', reviews=user_reviews, account=session)
        return redirect(url_for('login'))
    except:
        traceback.print_exc()
        error = traceback.format_exc()
        with get_connection_postgres(CONNECTION_POSTGRES) as conn:
            with conn.cursor() as cursor:
                cursor.execute('INSERT INTO public.error_log (error, ) values (%s)', [error])
        flash('Looks like something went wrong')
        return redirect(url_for('logout'))


# Search for a specific movie, calls microservice_neo to retreive all movies related to the input of the user
@app.route('/reviews', methods=['POST'])
def search_movie():
    if 'loggedin' in session and session['loggedin'] == True:
        if request.method=='POST' and 'movie' in request.form:
            user_id = session['id']
            movie = request.form.get("movie")
            searched_movies = requests.get('http://127.0.0.1:5001/getmovies/'+ movie)
            user_reviews = requests.get(f'http://127.0.0.1:5002/user/getreviews/{user_id}')
            if searched_movies.status_code == 200 and user_reviews.status_code == 200:
                searched_movies = searched_movies.json()
                user_reviews = user_reviews.json()
                return render_template('reviews.html', movies=searched_movies, account=session, reviews=user_reviews)
            else:
                flash('To search for a movie you need to enter a movie name')
                return redirect(url_for('get_reviews'))
        else:
            print('*****************')
            return redirect('home')
    else:
        return redirect(url_for('login'))
# 
@app.route('/writereview', methods=['GET', 'POST'])
def write_review():
    if 'loggedin' in session and session['loggedin'] == True:
        if request.method=='POST' and 'rating' in request.form and 'movie_name' in request.form and 'review_text' in request.form:
            id = session['id']
            review = request.form['review_text']
            movie_name = request.form['movie_name']
            rating = request.form['rating']
            requests.post('http://127.0.0.1:5002/writereview', json={"id": id,"review": review, "movie_name": movie_name, "rating": rating})
            return redirect(url_for('get_reviews'))
        else:
            flash('Missing fields in movie review')
            return redirect(url_for('get_reviews'))
    else:
        return redirect(url_for('login'))

@app.route('/deletereview/<id>/<user_id>', methods=['GET', 'POST'])
def delete_review(id, user_id):
    user_id = str(session['id'])
    requests.get(f'http://127.0.0.1:5002/delete/{id}/{user_id}')
    return redirect(url_for('get_reviews'))

@app.route('/recommendations', methods=['GET'])
def recommendations():
    if 'loggedin' in session and session['loggedin'] == True:
        movies = []
        for movie in session['movies']:
            movies.append(movie['name'])
        recommended_movies = requests.get('http://127.0.0.1:5001/movies/recommendations', json={'movies': movies})
        
        if recommended_movies.status_code == 200:
            recommended_movies = recommended_movies.json()
            print(recommended_movies)
            return render_template('recommendations.html', recommendations=recommended_movies, account=session)
        return redirect(url_for('get_reviews'))
    else:
        return redirect(url_for('login'))
# Logs in the user
@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if 'loggedin' in session and session['loggedin'] == True:
            return redirect(url_for('home'))
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
                user_id, user_email, user_password_rs, user_name = account
                # If account exists in users table in out database
                if check_password_hash(user_password_rs, password):
                    # Create session data, we can access this data in other routes
                    session['loggedin'] = True
                    session['id'] = user_id
                    session['name'] = user_name
                    session['email'] = user_email
                    #Redirect to home page
                    return redirect(url_for('get_reviews'))
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
            return redirect(url_for('get_review'))
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)