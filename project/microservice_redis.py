import redis
from flask import Flask

# make redis
redis_cache = redis.Redis(host='localhost', port=6379, db=0, password="redis_password")

# make flask app
app = Flask(__name__)


@app.route('/user/setreviews')
def set(user_id, reviews):
    if redis_cache(user_id):
        pass
    else:
        redis_cache.set(user_id, reviews)
    return "OK"


@app.route('/user/getreviews')
def get(user_id):
    if redis_cache.exists(user_id):
        return redis_cache.get(user_id)
    else:
        return f"{user_id} is not exists"

if __name__ == "__main__":
    app.run(debug=True, port=5003)
    