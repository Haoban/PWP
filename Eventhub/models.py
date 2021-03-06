import math
import os
import json
from flask import Flask, request, abort, jsonify, url_for

from passlib.hash import pbkdf2_sha256 as sha256

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import datetime

from Eventhub import db

users = db.Table("joinedusers",
                 db.Column("user_id", db.Integer, db.ForeignKey(
                           "user.id"), primary_key=True),
                 db.Column("event_id", db.Integer, db.ForeignKey(
                           "event.id"), primary_key=True)
                 )

"""
Table Event
----------------------
Columns:
- id, INTEGER, PRIMARY KEY
- name, STRING, 
- description, STRING
- place, STRING
- time, DATATIME
- creator, RELATIONSHIP with User
- creator_id, INTEGER
- joined_users, RELATIONSHIP with User
"""

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=False)
    description = db.Column(db.String(256), nullable=False)
    place = db.Column(db.String(32), nullable=True)
    time = db.Column(db.String(32), nullable=True)
    creator = db.relationship("User", back_populates="events")
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    joined_users = db.relationship(
        "User", secondary=users, back_populates="joined_events")

"""
Table User
----------------------
Columns:
- id, INTEGER, PRIMARY KEY
- picture, STRING
- name, STRING, 
- location, STRING
- events, RELATIONSHIP with Event
- loginuser, RELATIONSHIP with LoginUser
- joined_events, RELATIONSHIP with Event
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.String(256), nullable=True)
    name = db.Column(db.String(32), nullable=False, unique=False)
    location = db.Column(db.String(32), nullable=True, unique=False)
    events = db.relationship("Event", back_populates="creator")
    loginuser = db.relationship("LoginUser", back_populates='user', passive_deletes=True)
    joined_events = db.relationship(
        "Event", secondary=users, back_populates="joined_users")

# model for logining in, going go hash the password with hash_password methods and also verify the password with verify_password


"""
Table LoginUser
----------------------
Columns:
- id, INTEGER, PRIMARY KEY, Foreingnkey of User.id
- username, STRING
- password_hash, STRING, 
- user, RELATIONSHIP with User
"""
class LoginUser(db.Model):
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(120), nullable = False)
    user = db.relationship("User", back_populates='loginuser', uselist=False, cascade = "delete")

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)
    
    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


# @app.route('/api/users/', methods=['POST'])
# def new_user():
#     username = request.json.get('username')
#     password = request.json.get('password')
#     if username is None or password is None:
#         abort(400)  # missing arguments
#     if LoginUser.query.filter_by(username=username).first() is not None:
#         abort(400)  # existing user
#     user = LoginUser(username=username)
#     user.hash_password(password)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({'username': user.username, 'password': user.password_hash}), 201

# @app.route("/user/add/", methods=["POST"])
# def add_user():
#     # This branch happens when client submits the JSON document

#     if not request.content_type == 'application/json':
#         return 'Request content type must be JSON', 415

#     try:

#         name = request.json["name"]
#         location = request.json["location"]
#         exist = User.query.filter_by(name=name).first()

#         if (exist == None):
#             pro = User(
#                 name=name,
#                 location=location

#             )
#             db.session.add(pro)
#             db.session.commit()
#             return "successful", 201
#         elif (exist != None):
#             return "Handle already exists", 409
#         else:
#             abort(404)
#     except (KeyError, ValueError, IntegrityError):

#         abort(400)

#     except (TypeError):
#         return 'Request content type must be JSON', 415

db.create_all()
