from flask_sqlalchemy import SQLAlchemy
from app import app

db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    date = db.Column(db.DateTime)

    def __init__(self, text, date):
        self.text = text
        self.date = date