from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")  # same name in docker compose
db = client.site_db
num_users = db['UserNum']

num_users.insert_one(
    {
        'num_of_users': 0
    }
)


class Visit(Resource):
    def get(self):
        views_num = num_users.find({})[0]['num_of_users'] + 1
        num_users.update_one({}, {"$set": {"num_of_users": views_num}})
        return str(f"Hello user {views_num}")


@app.route('/')
def hello_word():
    return 'Hello Word'


def get_data():
    try:
        post_data = request.get_json()

        x = float(post_data['x'])
        y = float(post_data['y'])
    except Exception as e:
        print(e)
        return None, None, 301, str(e)

    return x, y, 200, ''


class Add(Resource):
    def post(self):
        # if i'm here, the resource add was requested using the method POST

        # Step 1: get the json data and manage errors
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        # Step 3: do the calculation
        result = x + y

        # step 4: Create Json response and send
        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Subtract(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x - y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Multiply(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x * y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


class Divide(Resource):
    def post(self):
        x, y, status_code, error_message = get_data()

        if y == 0:
            status_code = 302
            error_message = 'y is equal to zero, you cannot divide a number by 0'

        if status_code != 200:
            json_data = {
                "Message": error_message,
                "Status Code": status_code,
            }
            return jsonify(json_data)

        result = x / y

        json_data = {
            "Message": result,
            "Status Code": status_code,
        }
        return jsonify(json_data)


api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/divide")
api.add_resource(Visit, "/visit")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
