from flask import Flask, jsonify, request

from dotenv import load_dotenv
from os import environ

from functools import wraps
from redis_util import get_connection, set_value, get_value
from models import db, Post, User


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


def login_required(fn):
    @wraps(fn)
    def inner_func(*args, **kwargs):
        if get_value(con, "logged_in")[1]:
            return fn(*args, **kwargs)
        else:
            return {"message": "Login Required"}
    return inner_func


@app.route("/user/register", methods=["POST"])
def register_user():
    if request.method == "POST":
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email and password:
            old_user = User.query.filter_by(email=email).first()
            if not old_user:
                new_user = User(email=email, password=password)
                db.session.add(new_user)
                db.session.commit()
                return {"message": "Account Created Successfully"}
            else:
                return {"message": "User Already present"}
        return {"message": "Please provide the email and password"}
    return {"message": "Method Not Allowed"}


@app.route("/user/login", methods=["POST"])
def login_user():
    if request.method == "POST":
        email = request.form.get("email", None)
        password = request.form.get("password", None)

        if email and password:
            user = User.query.filter_by(email=email).first()
            if user and user.get_password(password=password):
                set_value(con, "email", email)
                set_value(con,"user_id",user.user_id)
                set_value(con, "logged_in", True)
                return {"message": f"{email} have been logged In Successfully"}
            else:
                return {"message": "Invalid Credentials"}
        return {"message": "Please provide email and password"}
    return {"message": "Method Not Allowed"}


@app.route("/user/logout")
@login_required
def logout_user():
    set_value(con, "logged_in", False)
    set_value(con, "email", None)
    return {"message": "Logged Out Successfully"}


# get posts
@app.route("/posts")
@app.route("/posts/<int:id>", methods=["GET"])
@login_required
def get_post(id=None):
    if id is None:
        posts = Post.query.filter_by(user_id=get_value(con,"user_id")[1])
        return jsonify({'posts': [post.serialize() for post in posts]})
    else:
        post = Post.query.filter_by(post_id=id,user_id=get_value(con,"user_id")[1]).first()
        if post:
            return post.serialize()
    return {"error": "Please provide correct id"}

# create posts


@app.route("/posts", methods=["POST"])
@login_required
def create_post():
    title = request.form.get("title", None)
    if title is not None:
        post = Post(title=title,user_id=get_value(con,"user_id")[1])
        db.session.add(post)
        db.session.commit()
        return jsonify(post.serialize())
    return {"error": "Please provide title"}

# update post


@app.route("/posts/<int:id>", methods=["PUT"])
@login_required
def update_post(id):
    title = request.form.get("title", None)

    if title is not None and id is not None:
        oldpost = Post.query.filter_by(post_id=id,user_id=get_value(con,"user_id")[1]).first()
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
@login_required
def delete_post(id):
    if id is not None:
        deletedpost = Post.query.filter_by(post_id=id,user_id=get_value(con,"user_id")[1]).first()
        db.session.delete(deletedpost)
        db.session.commit()
        return jsonify(deletedpost.serialize())
    return {"error": "Please provide correct id"}


if __name__ == '__main__':
    app.run(debug=True)
