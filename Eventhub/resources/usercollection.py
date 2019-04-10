from flask_restful import Resource, Api


from sqlalchemy.exc import IntegrityError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, Response, current_app
from .useritem import UserItem
from ..models import Event,LoginUser, User
from ..utils import InventoryBuilder, MasonBuilder, create_user_error_response
import json
from Eventhub import db
from jsonschema import validate, ValidationError

LINK_RELATIONS_URL = "/eventhub/link-relations/"
USER_PROFILE = "/profiles/user/"
ERROR_PROFILE = "/profiles/error/"
MASON = "application/vnd.mason+json"

USER_PROFILE = "/profiles/USER/"
ERROR_PROFILE = "/profiles/error/"


class UserCollection(Resource):

    def get(self):
        api = Api(current_app)

        try:
            users = User.query.all()
            body = InventoryBuilder(items=[])
            for j in users:
                events= []
                for i in j.joined_events:
                    event = {}
                    event["id"]=i.id
                    event["name"] = i.name
                    events.append(event)
                item = MasonBuilder(id=j.id, name=j.name, place=j.location, joined_events=events)
                item.add_control("self", api.url_for(
                    UserItem, id=j.id))
                item.add_control("profile", "/profiles/user/")
                body["items"].append(item)
            body.add_namespace("eventhub", LINK_RELATIONS_URL)
            body.add_control_all_users()
            body.add_control_add_user()
            print(body)

            return Response(json.dumps(body), 200, mimetype=MASON)
        except (KeyError, ValueError):
            abort(400)

    def post(self):
        api = Api(current_app)
        if not request.json:
            return create_user_error_response(415, "Unsupported media type",
                                               "Requests must be JSON"
                                               )
        try:
            validate(request.json, InventoryBuilder.user_schema())
        except ValidationError as e:
            return create_user_error_response(400, "Invalid JSON document", str(e))
        
        loginuser = LoginUser(username=request.json['username'])
        loginuser.hash_password(request.json['password'])
        user = User(name=request.json['name'])

        loginuser.user = user

        users = User.query.all()

        user.id = len(users) + 1

        try:

            body = InventoryBuilder()
                    
            db.session.add(user)
            db.session.add(loginuser)
            db.session.commit()


        except IntegrityError:
            return create_user_error_response(409, "Already exists",
                                               "Product with handle '{}' already exists.".format(user.id)
                                               )
    
        return Response(status=201, headers={
            "Location": api.url_for(UserItem, id=user.id)
        })
