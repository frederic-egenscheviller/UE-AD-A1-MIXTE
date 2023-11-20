from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, make_response

import resolvers as r

PORT = 3001
HOST = '0.0.0.0'
app = Flask(__name__)

# Load GraphQL schema from file
type_defs = load_schema_from_path('movie.graphql')

# Define GraphQL types
query = QueryType()
mutation = MutationType()
movie = ObjectType('Movie')
actor = ObjectType('Actor')

# Set GraphQL query and mutation resolvers
query.set_field('movie_with_id', r.movie_with_id)
query.set_field('movies_with_title', r.movies_with_title)
query.set_field('movies_with_rating_better_than_rate', r.movies_with_rating_better_than_rate)
query.set_field('actor_with_id', r.actor_with_id)

mutation.set_field('create_movie', r.create_movie)
mutation.set_field('delete_movie', r.delete_movie)
mutation.set_field('update_movie_rate', r.update_movie_rate)

# Set GraphQL type fields and resolvers
movie.set_field('actors', r.resolve_actors_in_movie)

# Create executable schema
schema = make_executable_schema(type_defs, movie, query, mutation, actor)


# Root message
@app.route("/", methods=['GET'])
def home():
    """
    Home route to welcome users.

    Returns:
        Response: HTML response with a welcome message.
    """
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


# GraphQL entry points
@app.route('/graphql', methods=['GET'])
def playground():
    """
    GraphQL Playground route.

    Returns:
        Response: HTML response with the GraphQL Playground interface.
    """
    return PLAYGROUND_HTML, 200


@app.route('/graphql', methods=['POST'])
def graphql_server():
    """
    GraphQL server route.

    Returns:
        Response: JSON response with the result of the GraphQL query or mutation.
    """
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
