#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=["GET", "POST"])
def campers():
    campers =[]
    if request.method == "GET":
        for camper in Camper.query.all():
            camper_dict = {
                "id": camper.id,
                "name": camper.name,
                "age": camper.age
            }
            campers.append(camper_dict)
        response = make_response(
            jsonify(campers),
            200
        )
        return response
    elif request.method == "POST":
        try:
            camper_data = request.json
            camper = Camper(name = camper_data['name'], age=camper_data['age'])
####
            db.session.add(camper)
            db.session.commit()

            response_body = {
                "id": camper.id,
                "name": camper.name,
                "age": camper.age
            }

            response = make_response(
                jsonify(response_body),
                201
            )
            return response
        except Exception as e:
            response_body = {
                "errors": ["validation errors"]
            }

            response = make_response(
                jsonify(response_body),
                400
            )
            return response



@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def camper_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()
    if camper:
        if request.method == 'GET':
            signups = [
                {
                    "activity": {
                        "difficulty": signup.activities.difficulty, 
                        "id": signup.activities.id, 
                        "name": signup.activities.name
                    }
                } 
                for signup in camper.signups]
            camper_dict = {
                "age": camper.age,
                "id": camper.id,
                "name": camper.name,
                "signups": signups
            }
            response = make_response(
                jsonify(camper_dict),
                200
            )
            return response
        elif request.method == 'PATCH':
            data = request.get_json()
            if 'name' in data and data['name'] != '':
                camper.name = data.get('name', camper.name)

                age = data.get('age', camper.age)
                if 8 <= age <= 18:
                    camper.age = age
                else:
                    response_dict = {
                        "errors": ["validation errors"]
                    }
                    response = make_response(
                        jsonify(response_dict),
                        400
                    )
                    return response

                db.session.commit()

                camper_dict = {
                    "id": camper.id,
                    "name": camper.name,
                    "age": camper.age
                }

                response = make_response(
                    jsonify(camper_dict),
                    202
                )
                return response
            else:
                response_dict = {
                    "errors": ["validation errors"]
                }
                response = make_response(
                    jsonify(response_dict),
                    400
                )
                return response
    else:
        response_dict = {
            "error": "Camper not found"
        }
        response = make_response(
            jsonify(response_dict),
            404
        )
    return response


@app.route('/activities')
def activities():
    activities =[]
    for activity in Activity.query.all():
        activity_dict = {
            "id": activity.id,
            "name": activity.name,
            "difficulty": activity.difficulty
        }
        activities.append(activity_dict)
    response = make_response(
        jsonify(activities),
        200
    )
    return response

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity(id):
    activity = Activity.query.filter(Activity.id == id).first()
    if activity:
        db.session.delete(activity)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Activity has been deleted."
        }
        response = make_response(
            jsonify(response_body),
            204
        )
        return response
    else:
        response_dict = {
            "error": "Activity not found"
        }
        response = make_response(
            jsonify(response_dict),
            404
        )
        return response
    
@app.route('/signups', methods=['POST'])
def signups():
    signup_data = request.json

    try:
        signup = Signup(camper_id = signup_data['camper_id'], activity_id = signup_data['activity_id'], time = signup_data['time'])

        db.session.add(signup)
        db.session.commit()

        response_body = {
            "id": signup.id,
            "camper_id": signup.camper_id,
            "activity_id": signup.activity_id,
            "time": signup.time,
            "activity": {
                "difficulty": signup.activities.difficulty,
                "id": signup.activities.id,
                "name": signup.activities.name
            },
            "camper": {
                "age": signup.campers.age,
                "id": signup.campers.id,
                "name": signup.campers.name
            }
        }
        response = make_response(
            jsonify(response_body),
            201
        )
        return response
    except ValueError:

        response_dict = {
            "errors": ["validation errors"] 
        }
        response = make_response(
            response_dict,
            400
        )
        return response
    # else:
    #     response_dict = {
    #         "error": "Signup not found"
    #     }
    #     response = make_response(
    #         jsonify(response_dict),
    #         404
    #     )
    # return response


if __name__ == '__main__':
    app.run(port=5555, debug=True)
