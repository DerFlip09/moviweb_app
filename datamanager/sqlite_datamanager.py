from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager import DataManagerInterface
from datamanager.data_models import db, User, Movie


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        self.db = db

        db.init_app(app)

        with app.app_context():
            self.db.create_all()

    def get_all_users(self) -> List['User']:
        users = User.query.all()
        return users

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

    def add_movie(self, title: str, director: Optional[str],
                  release_year: int, rating: float,
                  notes: Optional[str] = None) -> 'Movie':
        new_movie = Movie(title=title,
                          director=director,
                          release_year=release_year,
                          rating=rating,
                          notes=notes)
        self.db.session.add(new_movie)
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
