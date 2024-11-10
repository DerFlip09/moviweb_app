from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


db = SQLAlchemy(model_class=Base)

# Join Table for User-Movie Relationship
user_movies = db.Table('user_movies',
                       db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
                       db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
                       db.Column('notes', db.String, nullable=True),
                       db.Column('user_rating', db.Float, nullable=True)
                       )


class User(db.Model):
    __tablename__ = 'users'

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    name: db.Mapped[str] = db.mapped_column(nullable=False)
    date_of_creation: db.Mapped[str] = db.mapped_column(
        default=lambda: datetime.now().strftime('%d-%m-%Y'))

    movies: db.Mapped[list['Movie']] = db.relationship('Movie', secondary=user_movies, back_populates='users')

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"

    def __str__(self):
        return f"{self.id}. {self.name} (created on {self.date_of_creation})"


class Movie(db.Model):
    __tablename__ = 'movies'

    id: db.Mapped[int] = db.mapped_column(primary_key=True, autoincrement=True)
    title: db.Mapped[str] = db.mapped_column(nullable=False)
    director: db.Mapped[str] = db.mapped_column()
    release_year: db.Mapped[int] = db.mapped_column(nullable=False)
    rating: db.Mapped[float] = db.mapped_column(db.Float, nullable=False)
    poster: db.Mapped[str] = db.mapped_column(nullable=True)

    users: db.Mapped[list['User']] = db.relationship('User', secondary=user_movies, back_populates='movies')

    __table_args__ = (
        CheckConstraint('rating BETWEEN 0 AND 10', name='check_rating_between_0_and_10'),
    )

    def __repr__(self):
        return f"Movie(id={self.id}, title={self.title})"

    def __str__(self):
        return f"{self.id}. {self.title} {self.rating}/10 (released on {self.release_year})"
