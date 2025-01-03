from .database import db
from datetime import datetime
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.String(), nullable=False, default='general')
    is_active = db.Column(db.Boolean(), nullable=False, default=True) 
    max_books_allowed = db.Column(db.Integer(), default=5)
    transactions = db.relationship("Transactions", backref='user')

class Books(db.Model):
    id =  db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    filename = db.Column(db.String(), nullable=False)
    covername = db.Column(db.String(), nullable=False, default='default.jpg')
    authors = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False,  default='available')
    is_active = db.Column(db.Boolean(), nullable=False, default=True)
    search = db.Column(db.String(), nullable=False,  default='some text')
    transactions = db.relationship('Transactions', backref='book')
    sections = db.relationship("Sections", secondary='sections_books', backref='books')

class Transactions(db.Model):
    id =  db.Column(db.Integer(), primary_key=True)
    status = db.Column(db.String(), nullable=False, default = "requested")
    request_date = db.Column(db.DateTime, default=datetime(2000, 1, 1), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime(2000, 1, 1), nullable=False)
    return_date = db.Column(db.DateTime, default=datetime(2000, 1, 1), nullable=False)
    revoke_date = db.Column(db.DateTime, default=datetime(2000, 1, 1), nullable=False)
    duration = db.Column(db.Integer(), default=7, nullable=False)
    feedback = db.Column(db.String(), default="no feedback")
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"))
    book_id = db.Column(db.Integer(), db.ForeignKey("books.id"))

class Sections(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)
    description = db.Column(db.String(), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime(2000, 1, 1), nullable=False)
    search = db.Column(db.String(), nullable=False)




class SectionsBooks(db.Model):
    __tablename__ = 'sections_books'
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)
