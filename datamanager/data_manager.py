from abc import ABC, abstractmethod
from typing import List, Optional
from datamanager.data_models import User, Movie


# Abstract base class
class DataManagerInterface(ABC):
    """Abstract DataManager class for managing Users and Movies in the database."""

    @abstractmethod
    def get_all_users(self) -> List['User']:
        """Retrieve all users from the database."""
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> 'User':
        pass
    @abstractmethod
    def get_user_movies(self, user_id: int) -> List['Movie']:
        """Retrieve all movies associated with a user."""
        pass

    @abstractmethod
    def add_user(self, name: str) -> 'User':
        """Add a new user to the database."""
        pass

    @abstractmethod
    def update_user(self, user_id: int, name: Optional[str] = None) -> bool:
        """Update an existing user's details."""
        pass

    @abstractmethod
    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the database."""
        pass

    @abstractmethod
    def add_movie(self, user_id: int, title: str, release_year: Optional[int], notes: Optional[str]) -> 'Movie':
        """Add a new movie to the database."""
        pass

    @abstractmethod
    def update_movie(self, movie_id: int,
                     notes: Optional[str] = None) -> bool:
        """Update an existing movie's details."""
        pass

    @abstractmethod
    def delete_movie(self, movie_id: int) -> bool:
        """Delete a movie from the database."""
        pass
