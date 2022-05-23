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
#port = os.getenv("PORT", 8080)
driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/movies/recommendations', methods=('GET', 'POST'))
def index():
    return_recommened_movies = []
    movies = db.reviews.find({"rating":"Good"},{ "_id": 0, "name": 1 }).limit(5)
    with driver.session() as session:
        for movie in movies:
            recommended_movies = []
            recommended_dict = {}
            similar_movies = session.run("MATCH (m:Movie)-[:IS_GENRE]->(g:Genre)<-[:IS_GENRE]-(rec:Movie)"
                                "WHERE m.title = $title " 
                                "WITH rec, COLLECT(g.name) AS genres, COUNT(*) AS commonGenres " 
                                "RETURN rec.title, genres " 
                                "LIMIT 2 ",
                                {"title": movie['name']})
            [recommended_movies.append(movie.values()) for movie in similar_movies]
            recommended_dict[movie.get("name")] = recommended_movies
            return_recommened_movies.append(recommended_dict)
        print(return_recommened_movies)

        return render_template('recommendations.html', movies=recommended_movies)

if __name__ == "__main__":
    app.run(debug=True, port=5001)

                