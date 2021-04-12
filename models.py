from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
# database
db = SQLAlchemy()


# post model
class Post(db.Model):

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'user.user_id'), nullable=False)

    def __init__(self, title,user_id):
        self.title = title
        self.user_id = user_id 

    def __str__(self):
        return f'{self.title}'

    def __repr__(self):
        return f'{self.title}'

    def serialize(self):
        return {"_id": self.post_id, "title": self.title}


class User(db.Model):

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # posts = db.relationship('Post', backref='user', lazy=True)
    
    def __init__(self, email, password):

        self.email = email
        self.password = self.set_password(password)

    def set_password(self, password):
        return generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)

    def __str__(self):
        return f'{self.email}'

    def __repr__(self):
        return f'{self.email}'
