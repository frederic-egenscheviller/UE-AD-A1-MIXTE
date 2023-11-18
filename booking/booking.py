import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import json


class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetBookingByID(self, request, context):
        for booking in self.db:
            if booking['id'] == request.id:
                print("Booking found!")
                return booking_pb2.BookingData(id=booking['id'], date=booking['date'], movies=booking['movies'])
        return booking_pb2.BookingData(id="", date="", movies="")

    def GetListBookings(self, request, context):
        for booking in self.db:
            yield booking_pb2.BookingData(id=booking['id'], date=booking['date'], movies=booking['movies'])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3201')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
