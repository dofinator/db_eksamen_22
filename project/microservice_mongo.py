from datetime import datetime
from flask import Flask, jsonify, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import requests

app = Flask(__name__)

client = MongoClient('localhost', 27017, username='root',password='rootpassword')
db = client.flask_db
reviews = db.reviews
movies = db.movies


#TODO FIX USERID
@app.route('/writereview/', methods=['POST'])
def write_review():
    print('****************************')
    date = datetime.now().strftime("%x")
    print('Ø*********',request.data)
    #reviews.insert_one({'review': review_dict['review'], 'name': review_dict['movie_name'], 'date': date, 'rating': review_dict['rating']})
    #all_reviews = reviews.find()
    return jsonify({'asd': 'asd'})


#TODO TILFØJ USER ID FRA SESSION
@app.route('/user/getreviews/<user_id>', methods=('GET', 'POST'))
def get_reviews():
    movies = db.reviews.find({"rating":"Good"},{ "_id": 0, "name": 1 }).limit(5)
    return movies

@app.route('/<id>/delete/')
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('write_review'))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
    