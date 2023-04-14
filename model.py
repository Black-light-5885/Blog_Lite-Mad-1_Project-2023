from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.sql import func
db = SQLAlchemy()


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, autoincrement = True,
    primary_key = True)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = True)
    user_name = db.Column(db.String(), unique = True)
    password = db.Column(db.String(), unique = False)
    gender = db.Column(db.String(), nullable = False)
    picture = db.Column(db.LargeBinary(), nullable = True)
    blogs = db.relationship('Blogs', backref = 'user',cascade = 'all, delete')
    followers = db.relationship('Followers', backref = 'user',cascade = 'all, delete',
        primaryjoin = 'Followers.user_1==User.id')
    followee = db.relationship('Followers', backref = 'user_followee',cascade = 'all, delete',
        primaryjoin = 'Followers.user_2==User.id')
    comments = db.relationship('Comments', backref = 'user_',cascade = 'all, delete')



class Blogs(db.Model):
    id = db.Column(db.Integer(), autoincrement = True,
    primary_key = True)
    tittle = db.Column(db.String(), nullable = False)
    content = db.Column(db.String(10000), nullable = True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable = False)
    created_on = db.Column(db.DateTime(timezone = True),default = func.now())
    privacy = db.Column(db.Boolean, default=False)
    likes = db.Column(db.Integer(), default = 0)
    image = db.Column(db.LargeBinary(), nullable = True)
    image_name = db.Column(db.String(), nullable = True)
    comments = db.relationship('Comments', backref = 'blogs',cascade = 'all, delete')

class Followers(db.Model):
    user_1 = db.Column(db.Integer(),db.ForeignKey('user.id'),primary_key = True)
    user_2 = db.Column(db.Integer(), db.ForeignKey('user.id'), primary_key = True)

class Comments(db.Model):
    id = db.Column(db.Integer(),autoincrement = True, primary_key = True)
    user = db.Column(db.Integer(),db.ForeignKey('user.id'), nullable = False)
    blog = db.Column(db.Integer(), db.ForeignKey('blogs.id'), nullable = False)
    comment = db.Column(db.String(), nullable = False)

