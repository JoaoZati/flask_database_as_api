"""
Registration of a User
Each user get 10 tokens 
Sotore a sentece for 1 token
Retrive his stored sentence on our database for 1 token
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient
from debugger import initialize_debugger

import bcrypt

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")  # same name in docker compose
db = client.SentenceDatabase
users = db["Users"]


def get_data():
    status_code = 200
    message = ''
    
    try:
        post_data = request.get_json()

        username = str(post_data['username'])
        password = str(post_data['password'])
    except Exception as e:
        username, password = '', ''
        status_code = 303
        message = str(e)

    return username, password, status_code, message


class Register(Resource):
    def post(self):
        username, password, status_code, message = get_data()

        if status_code != 200:
            json_data = {
                "Message": message,
                "status": status_code,
            }
            return jsonify(json_data)

        try:
            if users.find({}, {"Username": username})[0]['Username'] == username:
                return jsonify(
                    {"message": "Username already exists",
                    "status": 304}
                )
        except Exception as e:
            print(e)

        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())

        users.insert_one(
            {
                "Username": username,
                "Password": hashed_pw,
                "Sentence": ""
            }
        )

        result = {
            "status": status_code,
            "message": "You seccesfully signed up for the API"
            }

        return jsonify(result)


@app.route('/')
def hello_word():
    return 'Hello Word'


api.add_resource(Register, "/register")


if __name__ == '__main__':

    initialize_debugger()

    app.run(host='0.0.0.0', port=5000, debug=True)
