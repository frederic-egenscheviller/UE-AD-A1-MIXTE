import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import json


class BookingServicer(booking_pb2_grpc.BookingServicer):

    def __init__(self):
        with open('{}/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def GetBookingByID(self, request, context):
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
        for booking in self.db:
            schedules_list = []
            for date_info in booking['dates']:
                date = date_info['date']
                movies = date_info['movies']

                movies_list = [booking_pb2.Movie(id=movie_id) for movie_id in movies]
                schedules_list.append(booking_pb2.Schedule(date=date, movies=movies_list))
            yield booking_pb2.BookingData(userId=booking['userid'], schedules=schedules_list)

    def CreateBooking(self, request, context):
        for booking in self.db:
            if booking['id'] == request.id:
                status = grpc.Status(grpc.StatusCode.INVALID_ARGUMENT, 'There is already a booking for this id')
                context.set_code(status.code)
                context.set_details(status.details)
                return booking_pb2.BookingData(id=request.id, date=request.date, movies=request.movies)
        self.db.append({'id': request.id, 'date': request.date, 'movies': request.movies})
        return booking_pb2.BookingData(id=request.id, date=request.date, movies=request.movies)

    def UpdateBooking(self, request, context):
        for booking in self.db:
            if booking['id'] == request.id:
                booking['date'] = request.date
                booking['movies'] = request.movies
                return booking_pb2.BookingData(id=request.id, date=request.date, movies=request.movies)
        status = grpc.Status(grpc.StatusCode.NOT_FOUND, 'There is no booking for this id')
        context.set_code(status.code)
        context.set_details(status.details)
        return booking_pb2.BookingData(id="", date="", movies="")

    def DeleteBooking(self, request, context):
        for booking in self.db:
            if booking['id'] == request.id:
                self.db.remove(booking)
                return booking_pb2.BookingData(id=request.id, date=request.date, movies=request.movies)
        status = grpc.Status(grpc.StatusCode.NOT_FOUND, 'There is no booking for this id')
        context.set_code(status.code)
        context.set_details(status.details)
        return booking_pb2.BookingData(id="", date="", movies="")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3201')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
