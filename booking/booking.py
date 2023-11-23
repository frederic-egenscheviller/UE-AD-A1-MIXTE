import grpc
from concurrent import futures

from google.protobuf.json_format import MessageToJson

import booking_pb2
import booking_pb2_grpc
import json

import showtime_pb2_grpc
import showtime_pb2


class BookingServicer(booking_pb2_grpc.BookingServicer):

    # Load initial bookings data from a JSON file
    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetBookingByID(self, request, context):
        """
        Get booking details by user ID.

        Args:
            request (booking_pb2.GetBookingByIDRequest): Request object containing the user ID.
            context (grpc.ServicerContext): gRPC service context.

        Returns:
            booking_pb2.BookingData: Response object containing the booking details.
        """
        for booking in self.db:
            if booking['userid'] == request.id:
                print("Booking found!")
                # List used to store the schedules
                schedules_list = []
                # Iterate over the dates in the booking
                for date_info in booking['dates']:
                    date = date_info['date']
                    movies = date_info['movies']
                    # Get all the movies id in the date
                    movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in movies]
                    # Create a schedule object and add it to the list
                    schedules_list.append(booking_pb2.Schedule(date=date, movies=movies_list))
                # Create a booking object and return it with the schedules list
                return booking_pb2.BookingData(userId=booking['userid'], schedules=schedules_list)
        return booking_pb2.BookingData(userId="", schedules=[])

    def GetListBookings(self, request, context):
        """
        Get a list of all bookings.

        Args:
            request (booking_pb2.GetListBookingsRequest): Request object.
            context (grpc.ServicerContext): gRPC service context.

        Yields:
            booking_pb2.BookingData: Response object containing booking details.
        """
        for booking in self.db:
            schedules_list = []
            # Iterate over the dates in the booking
            for date_info in booking['dates']:
                date = date_info['date']
                movies = date_info['movies']
                # Get all the movies id in the date
                movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in movies]
                # Create a schedule object and add it to the list
                schedules_list.append(booking_pb2.Schedule(date=date, movies=movies_list))
            # Return the bookings objects one by one
            yield booking_pb2.BookingData(userId=booking['userid'], schedules=schedules_list)


    def CreateBooking(self, request, context):
        """
        Create a new booking.

        Args:
            request (booking_pb2.BookingData): Request object containing the booking details.
            context (grpc.ServicerContext): gRPC service context.

        Returns:
            booking_pb2.BookingData: Response object containing the booking details.
        """
        req = json.loads(MessageToJson(request))
        # Check if the user already has a booking
        if req["userId"] not in [booking["userid"] for booking in self.db]:
            with grpc.insecure_channel('localhost:3202') as channel:
                for schedule in req["schedules"]:
                    showtime_response = showtime_pb2_grpc.ShowtimeStub(channel).GetTimetableByDate(
                        showtime_pb2.Date(date=schedule["date"]))
                    showtime_response = json.loads(MessageToJson(showtime_response))
                    # Check if the movies are available for the given date
                    for movie in schedule["movies"]:
                        if movie["id"] not in [movieScheduled for movieScheduled in showtime_response["movies"]]:
                            # If one of the movies is not available, return an error message Not add
                            return booking_pb2.BookingData(userId="Not add", schedules=[])
                channel.close()
            # Create a booking dictionary with correct format
            booking_to_insert = {"userid": req["userId"], "dates": []}
            for schedule in req["schedules"]:
                date_entry = {"date": schedule["date"], "movies": []}
                for movie in schedule["movies"]:
                    date_entry["movies"].append(movie["id"])
                booking_to_insert["dates"].append(date_entry)
            # Add the booking to the database
            self.db.append(booking_to_insert)
            print("Booking created!")
            return request

        else:
            return booking_pb2.BookingData(userId="A booking already exists for this user", schedules=[])


def serve():
    """
    Start the gRPC server.

    This function initializes the gRPC server, adds the BookingServicer to it, and starts the server.

    Returns:
        None
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3201')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
