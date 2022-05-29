import redis
import json
from flask import flash
from flask import Flask, jsonify
# make redis
redis_cache = redis.Redis(host='localhost', port=6379, db=0, password="redis_password")

# make flask app
app = Flask(__name__)


@app.route('/testredis/<user_id>', methods=['GET'])
def test_redis(user_id):
    data = []
    if redis_cache.get(user_id):
        print('HIT')
        value = redis_cache.get(user_id)
        return jsonify(json.loads(value))
    else:
        all_reviews = [doc for doc in reviews.find({"user_id": int(user_id)})]
        for doc in all_reviews:
            doc['_id'] = str(doc['_id']) 
            data.append(doc)
        redis_cache.set(user_id, json.dumps(data))
        print('MISSED')
    return jsonify(data)
    