from datetime import datetime
from flask import flash
from flask import Flask, jsonify, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson import json_util, ObjectId

app = Flask(__name__)

client = MongoClient('localhost', 27017, username='root',password='rootpassword')
db = client.flask_db
reviews = db.reviews
movies = db.movies


@app.route('/writereview', methods=['POST'])
def write_review():
    date = datetime.now().strftime("%x")
    data = request.get_json()
    id = int(data['id'])
    reviews.insert_one({'user_id': data['id'], 'review': data['review'], 'name': data['movie_name'], 'date': date, 'rating': data['rating']})
    
    data = []
    all_reviews = [doc for doc in reviews.find({"user_id": id})]
    for review in all_reviews:
        review['_id'] = str(review['_id']) 
        data.append(review)
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
    