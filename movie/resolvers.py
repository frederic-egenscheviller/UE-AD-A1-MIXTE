import json


def movie_with_id(_, info, _id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return movie
        return Exception("Movie ID doesn't exists")


def movies_with_rating_better_than_rate(_, info, _rating):
    movies_list = []
    print("here")
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if float(movie['rating']) > float(_rating):
                movies_list.append(movie)
    return movies_list


def movies_with_title(_, info, _title):
    movies_list = []
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)
        for movie in movies['movies']:
            if movie['title'] == _title:
                movies_list.append(movie)
    return movies_list


def create_movie(_, info, _id, _title, _rating, _director):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                return Exception("Movie ID already exists")
        newmovie = {'title': _title, 'rating': _rating, 'director': _director, 'id': _id}
        movies['movies'].append(newmovie)
        newmovies = movies
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump(newmovies, wfile)
    return newmovie


def delete_movie(_, info, _id):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                newmovie = movie
                movies['movies'].remove(movie)
                newmovies = movies
    if newmovies != movies:
        with open('{}/data/movies.json'.format("."), "w") as wfile:
            json.dump(newmovies, wfile)
        return newmovie
    return Exception("Movie ID doesn't exists")


def update_movie_rate(_, info, _id, _rating):
    newmovies = {}
    newmovie = {}
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)
        for movie in movies['movies']:
            if movie['id'] == _id:
                movie['rating'] = _rating
                newmovie = movie
                newmovies = movies
    if newmovies != movies:
        with open('{}/data/movies.json'.format("."), "w") as wfile:
            json.dump(newmovies, wfile)
        return newmovie
    return Exception("Movie ID doesn't exists")


def actor_with_id(_, info, _id):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)
        for actor in actors['actors']:
            if actor['id'] == _id:
                return actor


def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        data = json.load(file)
        actors = [actor for actor in data['actors'] if movie['id'] in actor['films']]
        return actors
