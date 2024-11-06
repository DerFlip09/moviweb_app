import os
import dotenv
import requests
from typing import List, Optional
from datamanager.data_manager import DataManagerInterface
from datamanager.data_models import db, User, Movie


class SQLiteDataManager(DataManagerInterface):

    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'API_KEY')
    omdb_url = f"http://www.omdbapi.com/?apikey={omdb_key}"

    def __init__(self, app):
        self.db = db

        db.init_app(app)

        with app.app_context():
            self.db.create_all()

    def get_all_users(self) -> List['User']:
        users = User.query.all()
        return users

    def get_user(self, user_id: int) -> 'User':
        user = User.query.get(user_id)
        return user

    def get_user_movies(self, user_id: int) -> List['Movie']:
        user = User.query.get(user_id)
        return user.movies

    def add_user(self, name: str) -> 'User':
        new_user = User(name=name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    def update_user(self, user_id: int, name: Optional[str] = None) -> bool:
        user = User.query.get(user_id)
        if name:
            try:
                user.name = name
                self.db.session.commit()
                return True
            except Exception as e:
                print(f"Error updating User {user_id}: {e}")
                self.db.session.rollback()
                return False
        return False

    def delete_user(self, user_id: int) -> bool:
        user = User.query.get(user_id)
        try:
            self.db.session.delete(user)
            self.db.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting User {user_id}: {e}")
            self.db.session.rollback()
            return False

    def add_movie(self, user_id: int, title: str, release_year: Optional[int], notes: Optional[str]) -> Optional['Movie']:
        if release_year:
            api_query = self.omdb_url + f'&t={title}' + f'&y={release_year}'
        else:
            api_query = self.omdb_url + f'&t={title}'
        response = requests.get(api_query).json()
        if response.get('Response') == 'False':
            print(f"Movie '{title}' not found.")
            return None
        new_movie = Movie(title=title,
                          director=response['Director'],
                          release_year=release_year,
                          rating=response['imdbRating'],
                          poster=response['Poster'],
                          notes=notes)
        self.db.session.add(new_movie)
        user = User.query.get(user_id)
        user.movies.append(new_movie)
        self.db.session.commit()
        return new_movie

    def update_movie(self, movie_id: int,
                     notes: Optional[str] = None) -> bool:
        movie = Movie.query.get(movie_id)
        if notes:
            try:
                movie.notes = notes
                self.db.session.commit()
                return True
            except Exception as e:
                self.db.session.rollback()
                print(f"Error updating Movie {movie_id}: {e}")
                return False
        return False

    def delete_movie(self, movie_id: int) -> bool:
        movie = Movie.query.get(movie_id)
        try:
            self.db.session.delete(movie)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            print(f"Error deleting Movie {movie_id}: {e}")
            return False
