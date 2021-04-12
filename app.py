from flask import Flask, jsonify, request

from dotenv import load_dotenv
from os import environ


from redis_util import get_connection, set_value, get_value
from models import db, Post


# loading the environtmental variables from .env file
load_dotenv()

# redis connection
is_connected, con = get_connection(
    host=environ['REDIS_HOST'], port=environ['REDIS_PORT'], password=environ['REDIS_PASSWORD'])


# init app
app = Flask(__name__)

# configure db uri
app.config['SQLALCHEMY_DATABASE_URI'] = environ['SQL_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db and create tables
db.init_app(app)
db.create_all(app=app)

# get posts


@app.route("/posts")
@app.route("/posts/<int:id>", methods=["GET"])
def get_post(id=None):
    if id is None:
        posts = Post.query.all()
        return jsonify({'posts': [post.serialize() for post in posts]})
    else:
        post = Post.query.filter_by(post_id=id).first()
        if post:
            return post.serialize()
    return {"error": "Please provide correct id"}

# create posts


@app.route("/posts", methods=["POST"])
def create_post():
    title = request.form.get("title", None)
    if title is not None:
        post = Post(title=title)
        db.session.add(post)
        db.session.commit()
        return jsonify(post.serialize())

    return {"error": "Please provide title"}

# update post


@app.route("/posts/<int:id>", methods=["PUT"])
def update_post(id):
    title = request.form.get("title", None)

    if title is not None and id is not None:
        oldpost = Post.query.filter_by(post_id=id).first()
        if oldpost:
            oldpost.title = title
            db.session.add(oldpost)
            db.session.commit()
            return jsonify(oldpost.serialize())
        else:
            return {"error": "Please provide correct id"}
    else:
        return {"error": "Please provide title"}


# delete post
@app.route("/posts/<int:id>", methods=["DELETE"])
def delete_post(id):
    if id is not None:
        deletedpost = Post.query.filter_by(post_id=id).first()
        db.session.delete(deletedpost)
        db.session.commit()
        return jsonify(deletedpost.serialize())
    return {"error": "Please provide correct id"}


if __name__ == '__main__':
    app.run(debug=True)
