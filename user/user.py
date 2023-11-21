import grpc
from flask import Flask, render_template, request, jsonify, make_response
from google.protobuf.json_format import MessageToJson
import requests
import json
import booking_pb2
import booking_pb2_grpc

app = Flask(__name__)

# Configuration
PORT = 3203
HOST = '0.0.0.0'

# Movie service URL
MOVIE_SERVICE_URL = "http://localhost:3001"

# Load initial users data from a JSON file
with open('{}/data/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    """
    Home route to welcome users.

    Returns:
        Response: HTML response with a welcome message.
    """
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route("/user/<userid>", methods=['GET'])
def get_user_byid(userid):
    """
    Get user details by ID.

    Args:
        userid (str): The ID of the user.

    Returns:
        Response: JSON response with user details or an error message.
    """
    for user in users:
        if str(user["id"]) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "user ID not found"}), 400)


@app.route("/user", methods=['POST'])
def create_user():
    """
    Create a new user.

    Returns:
        Response: JSON response with the new user details or an error message.
    """
    req = request.get_json()

    if all(key in req for key in ["id", "name", "last_active"]):
        if req["id"] not in [user["id"] for user in users]:
            users.append(req)
            return make_response(jsonify(req), 200)
        else:
            return make_response(jsonify({"error": "user already exists"}), 400)

    return make_response(jsonify({"error": "invalid user object format"}), 400)


@app.route("/user/<userid>", methods=['PUT'])
def update_user(userid):
    """
    Update user details by ID.

    Args:
        userid (str): The ID of the user.

    Returns:
        Response: JSON response with the updated user details or an error message.
    """
    req = request.get_json()

    if all(key in req for key in ["id", "name", "last_active"]):
        for user in users:
            if str(user["id"]) == str(userid):
                user["name"] = req.get("name", user["name"])
                user["last_active"] = req.get("last_active", user["last_active"])
                return make_response(jsonify(req), 200)
        users.append(req)
    return make_response(jsonify({"error": "invalid user object format"}), 400)


@app.route("/user/<userid>", methods=['DELETE'])
def delete_user(userid):
    """
    Delete user by ID.

    Args:
        userid (str): The ID of the user.

    Returns:
        Response: JSON response with the deleted user details or an error message.
    """
    for user in users:
        if str(user["id"]) == str(userid):
            users.remove(user)
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({"error": "user ID not found"}), 400)


@app.route("/booking", methods=['POST'])
def create_booking():
    """
    Create a new booking using gRPC.

    Returns:
        Response: JSON response with the new booking details or an error message.
    """
    req = request.get_json()
    if all(key in req for key in ["userid", "dates"]):
        schedules_list = []
        for date in req["dates"]:
            movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in date["movies"]]
            schedules_list.append(booking_pb2.Schedule(date=date["date"], movies=movies_list))
        with grpc.insecure_channel('localhost:3201') as channel:
            booking_response = booking_pb2_grpc.BookingStub(channel).CreateBooking(
                booking_pb2.BookingData(userId=req['userid'], schedules=schedules_list))
            channel.close()
            response = json.loads(MessageToJson(booking_response))
            print(response)
            if response["userId"] == "Not add":
                return make_response(jsonify({"error": "one of selected movies is not available for these date"}),
                                     409)
            if response["userId"] == "A booking already exists for this user":
                return make_response(jsonify({"error": "booking already exists for this user"}), 400)

            return make_response(MessageToJson(booking_response), 200)
    return make_response(jsonify({"error": "invalid booking object format"}), 400)


@app.route("/user-bookings/<userid>", methods=['GET'])
def get_user_bookings(userid):
    """
    Get user bookings using gRPC.

    Args:
        userid (str): The ID of the user.

    Returns:
        Response: JSON response with user bookings or an error message.
    """
    with grpc.insecure_channel('localhost:3201') as channel:
        booking_response = booking_pb2_grpc.BookingStub(channel).GetBookingByID(booking_pb2.BookingID(id=userid))
        channel.close()
        if booking_response.userId != "":
            response = json.loads(MessageToJson(booking_response))
            booking_to_return = {"userid": response["userId"], "dates": []}
            for schedule in response["schedules"]:
                date_entry = {"date": schedule["date"], "movies": []}
                for movie in schedule["movies"]:
                    date_entry["movies"].append(movie["id"])
                booking_to_return["dates"].append(date_entry)
            return make_response(booking_to_return, 200)
        else:
            return make_response(jsonify({"error": "user ID not found in Booking service"}), 400)


@app.route("/user-bookings/<userid>/detailed", methods=['GET'])
def get_detailed_userbookings(userid):
    """
    Get detailed user bookings with movie information.

    Args:
        userid (str): The ID of the user.

    Returns:
        Response: JSON response with detailed user bookings or an error message.
    """
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
