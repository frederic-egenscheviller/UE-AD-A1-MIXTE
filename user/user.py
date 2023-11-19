# REST API
import grpc
from flask import Flask, render_template, request, jsonify, make_response
from google.protobuf.json_format import MessageToJson
import requests
import json
import booking_pb2
import booking_pb2_grpc

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

MOVIE_SERVICE_URL = "http://localhost:3001"

with open('{}/data/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/user-bookings/<userid>", methods=['GET'])
def get_user_bookings(userid):
    with grpc.insecure_channel('localhost:3201') as channel:
        booking_response = booking_pb2_grpc.BookingStub(channel).GetBookingByID(booking_pb2.BookingID(id=userid))
        channel.close()
        if booking_response.userId != "":
            return make_response(MessageToJson(booking_response), 200)
        else:
            return make_response(jsonify({"error": "user ID not found in Booking service"}), 400)


@app.route("/user-bookings/<userid>/detailed", methods=['GET'])
def get_detailed_userbookings(userid):
    with grpc.insecure_channel('localhost:3201') as channel:
        booking_response = booking_pb2_grpc.BookingStub(channel).GetBookingByID(booking_pb2.BookingID(id=userid))
        channel.close()
        if booking_response.userId != "":
            user_bookings = MessageToJson(booking_response)
            movie_infos = []
            user_bookings = json.loads(user_bookings)
            for booking in user_bookings["schedules"]:
                for movie in booking["movies"]:
                    movie_response = requests.post(f"{MOVIE_SERVICE_URL}/graphql",
                                                   json={"query": "{ movie_with_id(_id: \"%s\") { id title director "
                                                                  "rating actors {id firstname"
                                                                  " lastname birthyear films} } }" % movie.get('id',
                                                                                                               '')})
                    movie_infos.append(movie_response.json())
            movie_infos = [movie['data']['movie_with_id'] for movie in movie_infos]
            movie_info_map = {movie['id']: movie for movie in movie_infos}
            for date_info in user_bookings['schedules']:
                movies_list = date_info.get('movies', [])
                movie_ids = [movie.get('id', '') for movie in movies_list]
                date_info['movies'] = movie_ids
                for i, movie_id in enumerate(date_info['movies']):
                    date_info['movies'][i] = movie_info_map.get(movie_id, {})
            return make_response(jsonify(user_bookings), 200)
        else:
            return make_response(jsonify({"error": "user ID not found in Booking service"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % PORT)
    app.run(host=HOST, port=PORT)
