import redis
import json
from datetime import datetime
from flask import flash
from flask import Flask, jsonify, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson import ObjectId
import traceback

app = Flask(__name__)


redis_cache = redis.Redis(host='localhost', port=6379)

client = MongoClient('localhost', 27117, username='root',password='rootpassword')
db = client.flask_db
reviews = db.reviews
movies = db.movies
 

@app.route('/writereview', methods=['POST'])
def write_review():
    headers = request.headers
    auth = headers.get('X-Api-Key')
    if auth == 'somethingElseInProduction':
        data = []
        date = datetime.now().strftime("%x")
        body = request.get_json()
        reviews.insert_one({'user_id': body['id'], 'review': body['review'], 'name': body['movie_name'], 'date': date, 'rating': body['rating']})
        print(body['id'])
        print(type(body['id']))

        all_reviews = [doc for doc in reviews.find({"user_id": int(body['id'])})]
        for doc in all_reviews:
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        redis_cache.set(body['id'], json.dumps(data))
        print(redis_cache.get(4))
        return "200"
    else: return jsonify("some status code")

@app.route('/user/getreviews/<user_id>', methods=('GET', 'POST'))
def get_reviews(user_id):
    headers = request.headers
    auth = headers.get('X-Api-Key')
    print(auth)
    if auth == 'somethingElseInProduction':
        try:
            data = []
            if redis_cache.get(user_id):
                value = redis_cache.get(user_id)
                return jsonify(json.loads(value))
            else:
                all_reviews = [doc for doc in reviews.find({"user_id": int(user_id)})]
                for doc in all_reviews:
                    doc['_id'] = str(doc['_id']) 
                    data.append(doc)
                redis_cache.set(user_id, json.dumps(data))
                return jsonify(data)
        except:
            traceback.print_exc()
    else: return jsonify("some status code")

@app.route('/delete/<id>/<user_id>')
def delete(id, user_id):
    headers = request.headers
    auth = headers.get('X-Api-Key')
    if auth == 'somethingElseInProduction':
        data = []
        reviews.delete_one({"_id": ObjectId(id)})
        all_reviews = [doc for doc in reviews.find({"user_id": int(user_id)})]
        for doc in all_reviews:
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        redis_cache.set(user_id, json.dumps(data))
        return "200"
    else: return jsonify("some status code")
    
if __name__ == "__main__":
    app.run(debug=True, port=5002)
    
