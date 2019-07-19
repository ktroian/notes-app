from flask_login import UserMixin
from datetime import datetime, timedelta
from . import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    pswd_hash = db.Column(db.String(128))


class Note(db.Model):
    notes_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer)
    name = db.Column(db.String(128), index=True)
    text = db.Column(db.String(1024))
    author = db.Column(db.String(64), index=True)
    created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    updated = db.Column(db.DateTime, index=True, default=datetime.utcnow)

