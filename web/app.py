"""
Registration of a User
Each user get 10 tokens 
Sotore a sentece for 1 token
Retrive his stored sentence on our database for 1 token
"""

from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

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
        usarname, password, status_code, message = get_data()

        if status_code != 200:
            json_data = {
                "Message": message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        return jsonify(
            {
            "Message": "Ok",
            "Status Code": status_code
            }
        )


@app.route('/')
def hello_word():
    return 'Hello Word'


api.add_resource(Register, "/register")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
