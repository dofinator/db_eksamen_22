from flask import Flask, render_template, request, url_for, redirect, g, flash
from pymongo import MongoClient
import os
import traceback
from utils import get_connection_postgres
from settings import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from neo4j import GraphDatabase, basic_auth


app = Flask(__name__)
client = MongoClient('localhost', 27018, username='root',password='rootpassword')

db = client.flask_db
reviews = db.reviews
movies = db.movies

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/movies/recommendations', methods=(['GET']))
def index():
    try:
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

            return render_template('recommendations.html', movies=return_recommened_movies)
    except:
        # traceback.print_exc()
        # error = traceback.format_exc()
        # with get_connection_postgres(CONNECTION_POSTGRES) as conn:
        #         with conn.cursor() as cursor:
        #             cursor.execute('INSERT INTO public.error_log (fk_user_id,error) values (%s,%s)', [user_id,error])
        # flash('Looks like something went wrong')
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True, port=5001)

                