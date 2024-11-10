import os
import dotenv
import requests
from typing import List, Optional, Any
from datamanager.data_manager import DataManagerInterface
from datamanager.data_models import db, User, Movie, user_movies


class SQLiteDataManager(DataManagerInterface):
    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'API_KEY')
    omdb_url = f"http://www.omdbapi.com/?apikey={omdb_key}"

    def __init__(self, app):
        self.db = db

        db.init_app(app)

        with app.app_context():
            self.db.create_all()

    def fetch_api_data(self, title: str, release_year: Optional[int]) -> Optional[dict]:
        if release_year:
            api_query = self.omdb_url + f'&t={title}' + f'&y={release_year}'
        else:
            api_query = self.omdb_url + f'&t={title}'
        response = requests.get(api_query).json()
        if response.get('Response') == 'False':
            return None
        return response

    def get_all_users(self) -> List['User']:
        users = User.query.all()
        return users

    def get_user(self, user_id: int) -> 'User':
        user = User.query.get(user_id)
        return user

    def get_user_movies(self, user_id: int) -> Optional[List['Movie']] | Any:
        movies = self.db.session.query(Movie, user_movies.c.notes, user_movies.c.user_rating) \
            .join(user_movies, user_movies.c.movie_id == Movie.id) \
            .filter(user_movies.c.user_id == user_id) \
            .all()
        return movies

    def get_user_movie(self, user_id: int, movie_id: int) -> 'Movie':
        movie = self.db.session.query(Movie, user_movies.c.notes, user_movies.c.user_rating) \
            .join(user_movies, user_movies.c.movie_id == Movie.id) \
            .filter(user_movies.c.user_id == user_id, user_movies.c.movie_id == movie_id) \
            .first()
        return movie

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

    def add_movie(self, user_id: int, title: str,
                  release_year: Optional[int], user_rating: Optional[float] = None,
                  notes: Optional[str] = None) -> Optional['Movie']:
        movie_data = self.fetch_api_data(title, release_year)
        if not movie_data:
            print(f"Movie '{title}' not found.")
            return None
        movies = self.db.session.query(Movie).all()
        existing_movie = next((movie for movie in movies if movie.title.lower() == title.lower()), None)
        if existing_movie:
            movie = existing_movie
        else:
            movie = Movie(title=title,
                          director=movie_data['Director'],
                          release_year=release_year,
                          rating=movie_data['imdbRating'],
                          poster=movie_data['Poster'])
            self.db.session.add(movie)
            self.db.session.commit()

        insert_query = user_movies.insert().values(
            user_id=user_id,
            movie_id=movie.id,
            notes=notes,
            user_rating=user_rating
        )
        self.db.session.execute(insert_query)
        self.db.session.commit()
        return movie

    def update_movie(self, user_id: int, movie_id: int, user_rating: float = None,
                     notes: str = None) -> bool:
        try:
            stmt = db.update(user_movies). \
                where(user_movies.c.user_id == user_id). \
                where(user_movies.c.movie_id == movie_id)

            if user_rating is not None:
                stmt = stmt.values(user_rating=user_rating)
            if notes is not None:
                stmt = stmt.values(notes=notes)

            self.db.session.execute(stmt)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            print(f"Error updating Movie {movie_id}: {e}")
            return False

    def delete_movie(self, user_id: int, movie_id: int) -> bool:
        try:
            stmt = db.delete(user_movies).where(
                user_movies.c.user_id == user_id,
                user_movies.c.movie_id == movie_id
            )
            self.db.session.execute(stmt)
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            print(f"Error deleting Movie {movie_id}: {e}")
            return False
