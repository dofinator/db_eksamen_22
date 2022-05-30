from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient
from settings import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USER
from neo4j import GraphDatabase, basic_auth


app = Flask(__name__)
client = MongoClient('localhost', 27017, username='root',password='rootpassword')

db = client.flask_db
reviews = db.reviews
movies = db.movies

driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/movies/recommendations', methods=(['GET']))
def index():
    try:
        movies = request.get_json()
        recommended_movies = {}
        with driver.session() as neodb:
            for movie in movies['movies']:
                recommended_list = []
                similar_movies = neodb.run("MATCH (m:Movie)-[:IS_GENRE]->(g:Genre)<-[:IS_GENRE]-(rec:Movie)"
                                    "WHERE m.title = $title " 
                                    "WITH rec, COLLECT(g.name) AS genres, COUNT(*) AS commonGenres " 
                                    "RETURN rec.title " 
                                    "LIMIT 3 ",
                                    {"title": movie})
                for recommendation in similar_movies.values():
                    recommended_list.append(recommendation[0])
                recommended_movies[movie] = recommended_list
        return recommended_movies

    except:
        # traceback.print_exc()
        # error = traceback.format_exc()
        # with get_connection_postgres(CONNECTION_POSTGRES) as conn:
        #         with conn.cursor() as cursor:
        #             cursor.execute('INSERT INTO public.error_log (fk_user_id,error) values (%s,%s)', [user_id,error])
        # flash('Looks like something went wrong')
        return render_template('login.html')

@app.route('/getmovies/<movie>', methods=('GET', 'POST'))
def get_movies_search(movie):
    all_movies = []
    session = driver.session()
    for record in session.run("MATCH (m:Movie) WHERE toLower(m.title) CONTAINS toLower($title) RETURN m.title", {"title": movie}):
        all_movies.append(record["m.title"])
    return jsonify(all_movies)


if __name__ == "__main__":
    app.run(debug=True, port=5001)

                