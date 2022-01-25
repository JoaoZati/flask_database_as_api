"""
Registration of a User
Each user get 10 tokens 
Sotore a sentece for 1 token
Retrive his stored sentence on our database for 1 token
"""

from shutil import ExecError
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


def get_data(sentence=False, tokens=False):
    status_code = 200
    message = ''
    
    try:
        post_data = request.get_json()

        username = str(post_data['username'])
        password = str(post_data['password'])
        if sentence:
            sentence = str(post_data['sentence'])
    except Exception as e:
        username, password = '', ''
        status_code = 303
        message = str(e)

    list_return = [username, password, status_code, message]
    if sentence:
        list_return.append(sentence)

    return list_return


def verify_pw(username, password):
    try:
        hash_password = str(users.find({}, {"Username": username, "Password": 1})[0]["Password"])
        if bcrypt.hashpw(password, hash_password) == hash_password:
            return True
    except Exception as e:
        print(e)

    return False


def verify_tokens(username):
    try:
        tokens = int(users.find({}, {"Username": username, "tokens": 1})[0]["tokens"])
    except Exception as e:
        print(e)
        tokens = 0
    
    return tokens


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
                "Sentence": "",
                "tokens": 10
            }
        )

        result = {
            "status": status_code,
            "message": "You seccesfully signed up for the API"
            }

        return jsonify(result)


class Store(Resource):
    def post(self):
        username, password, status_code, message, sentence = get_data(sentence=True)

        if status_code != 200:
            json_data = {
                "Message": message,
                "status": status_code,
            }
            return jsonify(json_data)

        correct_pw = verify_pw(username, password)

        if not correct_pw:
            result = {
                "message": "Wrong username or password",
                "status": 301
            }
            return jsonify(result)
        
        tokens = verify_tokens(username)

        if tokens <= 1:
            result = {
                "message": "Your dont have enouth tokes to change the sentence",
                "status": 302
            }
            return jsonify(result)
        
        users.update_one(
            {"Username": username},
            {
                "$set": {
                    "Sentence": sentence,
                    "tokens": tokens - 1
                    }
            } 
        )

        result = {
            "message": "Ok, your sentence was sucessfully updated",
            "tokens": f"you have: {tokens - 1} tokens",
            "new_sentece": sentence,
            "status": status_code,
        }
        return jsonify(result)


class Get(Resource):
    def get(self):
        username, password, status_code, message = get_data()

        if status_code != 200:
            json_data = {
                "Message": message,
                "status": status_code,
            }
            return jsonify(json_data)
        
        correct_pw = verify_pw(username, password)

        if not correct_pw:
            result = {
                "message": "Wrong username or password",
                "status": 301
            }
            return jsonify(result)
        
        tokens = verify_tokens(username)

        if tokens < 1:
            result = {
                "message": "Your dont have enouth tokes to change the sentence",
                "status": 302
            }
            return jsonify(result)
        
        sentence = users.find({}, {"Username": username, "Sentence": 1})[0]["Sentence"]

        users.update_one(
            {"Username": username},
            {
                "$set": {
                    "tokens": tokens - 1
                    }
            }
        )

        result = {
            "message": "Ok, you successfuly got your sentence",
            "tokens": f"you have: {tokens - 1} tokens",
            "sentece": sentence,
            "status": status_code,
        }
        return jsonify(result)


class AddTokens(Resource):
    def post(self):
        username, password, status_code, message = get_data()

        if status_code != 200:
            json_data = {
                "Message": message,
                "status": status_code,
            }
            return jsonify(json_data)
        
        correct_pw = verify_pw(username, password)

        if not correct_pw:
            result = {
                "message": "Wrong username or password",
                "status": 301
            }
            return jsonify(result)
        
        tokens = verify_tokens(username)
        
        users.update_one(
            {"Username": username},
            {
                "$set": {
                    "tokens": tokens + 5
                    }
            } 
        )

        result = {
            "message": "Ok, you seccesfuly have add 5 tokens",
            "tokens": f"you have: {tokens + 5} tokens",
            "status": status_code,
        }
        return jsonify(result)

@app.route('/')
def hello_word():
    return 'Hello Word'


api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Get, "/get")
api.add_resource(AddTokens, "/add-tokens")

if __name__ == '__main__':
    initialize_debugger()

    app.run(host='0.0.0.0', port=5000, debug=True)
