from datetime import datetime
from urllib import response
from fastapi import Response
from flask import flash
from flask import Flask, jsonify, render_template, request, url_for, redirect, g
from pymongo import MongoClient
from bson import json_util, ObjectId
import os
import requests
import json

app = Flask(__name__)

client = MongoClient('localhost', 27017, username='root',password='rootpassword')
db = client.flask_db
reviews = db.reviews
movies = db.movies


#TODO FIX USERID
@app.route('/writereview', methods=['POST'])
def write_review():
    date = datetime.now().strftime("%x")
    data = request.get_json()
    reviews.insert_one({'review': data['review'], 'name': data['movie_name'], 'date': date, 'rating': data['rating']})
    data = []
    all_reviews = [doc for doc in reviews.find({})]
    for doc in all_reviews:
        doc['_id'] = str(doc['_id']) # This does the trick!
        data.append(doc)
    return jsonify(data)


#TODO TILFØJ USER ID FRA SESSION
@app.route('/user/getreviews/', methods=('GET', 'POST'))
def get_reviews():
    data = []
    all_reviews = [doc for doc in reviews.find({})]
    for doc in all_reviews:
        doc['_id'] = str(doc['_id']) # This does the trick!
        data.append(doc)
    return jsonify(data)

@app.route('/delete/<id>')
def delete(id):
    reviews.delete_one({"_id": ObjectId(id)})
    return "200"
    

if __name__ == "__main__":
    app.run(debug=True, port=5002)
    