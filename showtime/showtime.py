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
            yield showtime_pb2.Schedules(date=showtime['date'], movies=showtime['movies'])

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
                print('Showtime found!')
                return showtime_pb2.Schedules(date=showtime['date'], movies=showtime['movies'])
        return showtime_pb2.Schedules(date='', movies=[])

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
