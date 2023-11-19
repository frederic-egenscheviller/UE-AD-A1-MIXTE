import grpc
from grpc import StatusCode
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json


class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    def __init__(self):
        with open('{}/data/times.json'.format('.'), 'r') as jsf:
            self.db = json.load(jsf)['schedule']

    def GetTimetable(self, request, context):
        for showtime in self.db:
            yield showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])

    def GetTimetableByDate(self, request, context):
        for showtime in self.db:
            if showtime['date'] == request.date:
                return showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])
        return showtime_pb2.Schedule(date='', movies=[])

    def GetTimetableByTitle(self, request, context):
        for showtime in self.db:
            for movie in showtime['movies']:
                if movie['title'] == request.title:
                    return showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])
        return showtime_pb2.Schedule(date='', movies=[])

    def CreateTimetable(self, request, context):
        for showtime in self.db:
            if showtime['date'] == request.date:
                status = grpc.Status(StatusCode.INVALID_ARGUMENT, 'There is already a schedule for this date')
                context.set_code(status.code)
                context.set_details(status.details)
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        self.db.append({'date': request.date, 'movies': request.movies})
        return showtime_pb2.Schedule(date=request.date, movies=request.movies)

    def UpdateTimetable(self, request, context):
        for showtime in self.db:
            if showtime['date'] == request.date:
                showtime['movies'] = request.movies
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        status = grpc.Status(StatusCode.NOT_FOUND, 'There is no schedule for this date')
        context.set_code(status.code)
        context.set_details(status.details)
        return showtime_pb2.Schedule(date='', movies=[])

    def DeleteTimetable(self, request, context):
        for showtime in self.db:
            if showtime['date'] == request.date:
                self.db.remove(showtime)
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        status = grpc.Status(StatusCode.NOT_FOUND, 'There is no schedule for this date')
        context.set_code(status.code)
        context.set_details(status.details)
        return showtime_pb2.Schedule(date='', movies=[])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3202')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
