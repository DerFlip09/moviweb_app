import os
import dotenv
import requests
from typing import List, Optional, Any
from datamanager.data_manager import DataManagerInterface
from datamanager.data_models import db, User, Movie, user_movies


class SQLiteDataManager(DataManagerInterface):
    """
    A class for managing movie and user data using an SQLite database.
    """
    omdb_key = dotenv.get_key(os.path.join(os.getcwd(), '.env'), 'API_KEY')
    omdb_url = f"http://www.omdbapi.com/?apikey={omdb_key}"

    def __init__(self, app):
        """
        Initialize the SQLiteDataManager.

        :param app: The Flask application instance.
        """
        self.db = db
        db.init_app(app)
        with app.app_context():
            self.db.create_all()

    def fetch_api_data(self, title: str, release_year: Optional[int]) -> Optional[dict]:
        """
        Fetch movie data from the OMDB API.

        :param title: The title of the movie to fetch.
        :param release_year: The release year of the movie (optional).
        :returns: A dictionary containing movie data, or None if not found.
        """
        if release_year:
            api_query = self.omdb_url + f'&t={title}' + f'&y={release_year}'
        else:
            api_query = self.omdb_url + f'&t={title}'
        response = requests.get(api_query).json()
        if response.get('Response') == 'False':
            return None
        return response

    def get_all_users(self) -> List['User']:
        """
        Retrieve all users from the database.

        :returns: A list of User objects.
        """
        users = User.query.all()
        return users

    def get_user(self, user_id: int) -> 'User':
        """
        Retrieve a user by their ID.

        :param user_id: The ID of the user to retrieve.
        :returns: The User object.
        """
        user = User.query.get(user_id)
        return user

    def get_user_movies(self, user_id: int) -> Optional[List['Movie']] | Any:
        """
        Retrieve movies associated with a specific user.

        :param user_id: The ID of the user.
        :returns: A list of movies with additional details (notes and ratings).
        """
        movies = self.db.session.query(Movie, user_movies.c.notes, user_movies.c.user_rating) \
            .join(user_movies, user_movies.c.movie_id == Movie.id) \
            .filter(user_movies.c.user_id == user_id) \
            .all()
        return movies

    def get_user_movie(self, user_id: int, movie_id: int) -> 'Movie':
        """
        Retrieve a specific movie associated with a user.

        :param user_id: The ID of the user.
        :param movie_id: The ID of the movie.
        :returns: The Movie object along with notes and user rating.
        """
        movie = self.db.session.query(Movie, user_movies.c.notes, user_movies.c.user_rating) \
            .join(user_movies, user_movies.c.movie_id == Movie.id) \
            .filter(user_movies.c.user_id == user_id, user_movies.c.movie_id == movie_id) \
            .first()
        return movie

    def add_user(self, name: str) -> 'User':
        """
        Add a new user to the database.

        :param name: The name of the user.
        :returns: The created User object.
        """
        new_user = User(name=name)
        self.db.session.add(new_user)
        self.db.session.commit()
        return new_user

    def update_user(self, user_id: int, name: Optional[str] = None) -> bool:
        """
        Update an existing user's details.

        :param user_id: The ID of the user to update.
        :param name: The new name for the user (optional).
        :returns: True if the update was successful, False otherwise.
        """
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
        """
        Delete a user from the database.

        :param user_id: The ID of the user to delete.
        :returns: True if the deletion was successful, False otherwise.
        """
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
                  notes: Optional[str] = None) -> Optional[bool]:
        """
        Add a movie to a user's list.

        :param user_id: The ID of the user.
        :param title: The title of the movie.
        :param release_year: The release year of the movie (optional).
        :param user_rating: The user's rating for the movie (optional).
        :param notes: Notes about the movie (optional).
        :returns: True if the movie was added, False if already exists, or None if not found in API.
        """
        movie_data = self.fetch_api_data(title, release_year)
        if not movie_data:
            print(f"Movie '{title}' not found.")
            return None

        existing_user_movies = (
            self.db.session.query(Movie)
            .join(user_movies, Movie.id == user_movies.c.movie_id)
            .filter(user_movies.c.user_id == user_id)
            .all())
        existing_movie = next((movie for movie in existing_user_movies if movie.title.lower() == title.lower()), None)
        if existing_movie:
            return False

        movie = (
            self.db.session.query(Movie)
            .filter(Movie.title.ilike(title))
            .first())
        if not movie:
            movie = Movie(
                title=title,
                director=movie_data['Director'],
                release_year=release_year,
                rating=movie_data['imdbRating'],
                poster=movie_data['Poster']
            )
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
        return True

    def update_movie(self, user_id: int, movie_id: int, user_rating: float = None,
                     notes: str = None) -> bool:
        """
        Update movie details for a specific user.

        :param user_id: The ID of the user.
        :param movie_id: The ID of the movie.
        :param user_rating: The new rating for the movie (optional).
        :param notes: The new notes for the movie (optional).
        :returns: True if the update was successful, False otherwise.
        """
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
        """
        Remove a movie from a user's list.

        :param user_id: The ID of the user.
        :param movie_id: The ID of the movie.
        :returns: True if the deletion was successful, False otherwise.
        """
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
