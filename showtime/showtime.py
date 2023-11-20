import grpc
from grpc import StatusCode
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json


class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):

    # Load initial showtimes data from a JSON file
    def __init__(self):
        with open('{}/data/times.json'.format('.'), 'r') as jsf:
            self.db = json.load(jsf)['schedule']

    def GetTimetable(self, request, context):
        """
        Get the entire showtime timetable.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Yields:
            showtime_pb2.Schedule: gRPC response object containing the showtime schedule.
        """
        for showtime in self.db:
            yield showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])

    def GetTimetableByDate(self, request, context):
        """
        Get the showtime timetable for a specific date.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Returns:
            showtime_pb2.Schedule: gRPC response object containing the showtime schedule for the given date.
        """
        for showtime in self.db:
            if showtime['date'] == request.date:
                return showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])
        return showtime_pb2.Schedule(date='', movies=[])

    def GetTimetableByTitle(self, request, context):
        """
        Get the showtime timetable for a specific movie title.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Returns:
            showtime_pb2.Schedule: gRPC response object containing the showtime schedule for the given movie title.
        """
        for showtime in self.db:
            for movie in showtime['movies']:
                if movie['title'] == request.title:
                    return showtime_pb2.Schedule(date=showtime['date'], movies=showtime['movies'])
        return showtime_pb2.Schedule(date='', movies=[])

    def CreateTimetable(self, request, context):
        """
        Create a new showtime timetable entry.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Returns:
            showtime_pb2.Schedule: gRPC response object containing the created showtime schedule entry.
        """
        for showtime in self.db:
            if showtime['date'] == request.date:
                status = grpc.Status(StatusCode.INVALID_ARGUMENT, 'There is already a schedule for this date')
                context.set_code(status.code)
                context.set_details(status.details)
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        self.db.append({'date': request.date, 'movies': request.movies})
        return showtime_pb2.Schedule(date=request.date, movies=request.movies)

    def UpdateTimetable(self, request, context):
        """
        Update an existing showtime timetable entry.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Returns:
            showtime_pb2.Schedule: gRPC response object containing the updated showtime schedule entry.
        """
        for showtime in self.db:
            if showtime['date'] == request.date:
                showtime['movies'] = request.movies
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        status = grpc.Status(StatusCode.NOT_FOUND, 'There is no schedule for this date')
        context.set_code(status.code)
        context.set_details(status.details)
        return showtime_pb2.Schedule(date='', movies=[])

    def DeleteTimetable(self, request, context):
        """
        Delete an existing showtime timetable entry.

        Args:
            request: gRPC request object.
            context: gRPC service context.

        Returns:
            showtime_pb2.Schedule: gRPC response object containing the deleted showtime schedule entry.
        """
        for showtime in self.db:
            if showtime['date'] == request.date:
                self.db.remove(showtime)
                return showtime_pb2.Schedule(date=request.date, movies=request.movies)
        status = grpc.Status(StatusCode.NOT_FOUND, 'There is no schedule for this date')
        context.set_code(status.code)
        context.set_details(status.details)
        return showtime_pb2.Schedule(date='', movies=[])


def serve():
    """
    Start the gRPC server.

    This function initializes the gRPC server, adds the ShowtimeServicer to it, and starts the server.

    Returns:
        None
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3202')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
