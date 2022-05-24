
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

client = MongoClient('localhost', 27017)

db = client.flask_db
reviews = db.reviews
movies = db.movies

neo4j_version = os.getenv("NEO4J_VERSION", "4")
NEO4J_URI="neo4j://localhost:7687 "
NEO4J_DATABASE="neo4j" 
NEO4J_USER="neo4j" 
NEO4J_PASSWORD="Sumit2630"
port = os.getenv("PORT", 8080)

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

test = db.reviews.find({"rating":"Good"},{ "_id": 0, "name": 1 })
for x in test:
    print(x["name"])
    

def get_movies(driver):
    all_movies = []
    session = driver.session()
    for record in session.run("MATCH(m:Movie) return m.title LIMIT 10"):
        all_movies.append(record["m.title"])
    return all_movies

@app.route('/movies/review', methods=('GET', 'POST'))
def index():
    all_movies = get_movies(driver)
    if request.method=='POST':
        review = request.form['review_text']
        movie_name = request.form['movie_name']
        rating = request.form['rating']
        print(rating)
        date = datetime.now().strftime("%x")
        reviews.insert_one({'review': review, 'name': movie_name, 'date': date, 'rating': rating})
        return redirect(url_for('index'))

    all_reviews = reviews.find()
   
    return render_template('index.html', reviews=all_reviews, movies=all_movies)

@app.route('/<id>/delete/')
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
    