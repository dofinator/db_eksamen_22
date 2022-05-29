import redis
import json
from datetime import datetime
from flask import flash
from flask import Flask, jsonify, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson import ObjectId


app = Flask(__name__)

redis_cache = redis.Redis(host='localhost', port=6379, db=0)

client = MongoClient('localhost', 27017, username='root',password='rootpassword')
db = client.flask_db
reviews = db.reviews
movies = db.movies

@app.route('/testredis/<user_id>', methods=['GET'])
def test_redis(user_id):
    data = []
    if redis_cache.get(user_id):
        print('HIT')
        value = redis_cache.get(user_id)
        print(value)
        return jsonify("ost")
    else:
        id = int(user_id)
        all_reviews = [doc for doc in reviews.find({"user_id": id})]
        for doc in all_reviews:
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        redis_cache.set(user_id, json.dumps(data))
        print('MISSED')
    return jsonify(data)


@app.route('/writereview', methods=['POST'])
def write_review():
    date = datetime.now().strftime("%x")
    data = request.get_json()
    id = int(data['id'])
    reviews.insert_one({'user_id': data['id'], 'review': data['review'], 'name': data['movie_name'], 'date': date, 'rating': data['rating']})
    
    data = []
    all_reviews = [doc for doc in reviews.find({"user_id": id})]
    for doc in all_reviews:
        doc['_id'] = str(doc['_id']) 
        data.append(doc)
    return jsonify(data)

@app.route('/user/getreviews/<user_id>', methods=('GET', 'POST'))
def get_reviews(user_id):
    data = []
    id = int(user_id)
    all_reviews = [doc for doc in reviews.find({"user_id": id})]
    for doc in all_reviews:
        doc['_id'] = str(doc['_id']) 
        data.append(doc)
    return jsonify(data)

@app.route('/delete/<id>')
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return "200"
    
if __name__ == "__main__":
    app.run(debug=True, port=5002)
    