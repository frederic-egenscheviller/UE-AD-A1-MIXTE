# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import movie_pb2
import movie_pb2_grpc

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

MOVIE_SERVICE_URL = "http://localhost:3200"
BOOKING_SERVICE_URL = "http://localhost:3201"

with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/user-bookings/<userid>", methods=['GET'])
def get_user_bookings(userid):
    booking_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{userid}")

    if booking_response.status_code == 200:
        user_bookings = booking_response.json()
        return make_response(jsonify(user_bookings), 200)
    else:
        return make_response(jsonify({"error": "User ID not found in Booking service"}), 400)


@app.route("/user-bookings/<userid>/detailed", methods=['GET'])
def get_detailed_userbookings(userid):
    booking_response = requests.get(f"{BOOKING_SERVICE_URL}/bookings/{userid}")

    if booking_response.status_code == 200:
        user_bookings = booking_response.json()
        movie_infos = []
        for booking in user_bookings["dates"]:
            for movie in booking["movies"]:
                movie_response = requests.get(f"{MOVIE_SERVICE_URL}/movies/{movie}")
                movie_infos.append(movie_response.json())

        movie_info_map = {movie['id']: movie for movie in movie_infos}
        for date_info in user_bookings['dates']:
            for i, movie_id in enumerate(date_info['movies']):
                date_info['movies'][i] = movie_info_map.get(movie_id, {})

        return make_response(jsonify(user_bookings), 200)
    else:
        return make_response(jsonify({"error": "User ID not found in Booking service"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
