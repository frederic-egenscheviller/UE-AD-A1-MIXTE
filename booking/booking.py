import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import json


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
                schedules_list = []
                for date_info in booking['dates']:
                    date = date_info['date']
                    movies = date_info['movies']

                    movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in movies]
                    schedules_list.append(booking_pb2.Schedule(date=date, movies=movies_list))

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
            for date_info in booking['dates']:
                date = date_info['date']
                movies = date_info['movies']

                movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in movies]
                schedules_list.append(booking_pb2.Schedule(date=date, movies=movies_list))
            yield booking_pb2.BookingData(userId=booking['userid'], schedules=schedules_list)


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
