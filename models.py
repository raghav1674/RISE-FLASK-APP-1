from flask_sqlalchemy import SQLAlchemy

# database 
db = SQLAlchemy()


# post model
class Post(db.Model):

    post_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    def serialize(self):
        return {"_id":self.post_id,"title":self.title}