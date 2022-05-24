from datetime import datetime
from flask import Flask, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

from neo4j import (
    GraphDatabase,
    basic_auth,
)
app = Flask(__name__)

client = MongoClient('localhost', 27018, username='root',password='rootpassword')

db = client.flask_db
reviews = db.reviews
movies = db.movies

neo4j_version = os.getenv("NEO4J_VERSION", "4")
NEO4J_URI="neo4j://localhost:7687 "
NEO4J_DATABASE="neo4j" 
NEO4J_USER="neo4j" 
NEO4J_PASSWORD="password"
port = os.getenv("PORT", 8080)

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

def get_movies(driver, movie):
    all_movies = []
    session = driver.session()
    for record in session.run("MATCH (m:Movie) WHERE toLower(m.title) CONTAINS toLower($title) RETURN m.title", {"title": movie}):
        all_movies.append(record["m.title"])
    return all_movies

@app.route('/', methods=('GET', 'POST'))
def write_review():
    all_reviews = reviews.find()

    if request.method=='POST' and 'movie' in request.form:
        movie = request.form.get("movie")
        searched_movies = get_movies(driver, movie)
        return render_template('reviews.html', movies = searched_movies)

    if request.method=='POST' and "review_text" in request.form:
        review = request.form['review_text']
        movie_name = request.form['movie_name']
        rating = request.form['rating']
        date = datetime.now().strftime("%x")
        reviews.insert_one({'review': review, 'name': movie_name, 'date': date, 'rating': rating})
        return redirect(url_for('write_review'))
   
    return render_template('reviews.html', reviews = all_reviews)

@app.route('/<id>/delete/')
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('write_review'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
    