import os
from datamanager.data_models import Movie
from flask import Flask, render_template, request, redirect, url_for
from datamanager.sqlite_datamanager import SQLiteDataManager

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configure the database URI and tracking modifications
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "storage", "movie_app.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

dataman = SQLiteDataManager(app)


@app.route('/', methods=['GET'])
def home():
    """
    Displays the home page with a list of all movies.

    :returns: Rendered HTML template for the homepage.
    """
    movies = Movie.query.all()
    return render_template('home.html', movies=movies)


@app.route('/users', methods=['GET'])
def list_users():
    """
    Displays a list of all users.

    :returns: Rendered HTML template showing all users.
    """
    users = dataman.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    """
    Displays a specific user's movies.

    :param user_id: The ID of the user whose movies are to be displayed.
    :type user_id: int
    :returns: Rendered HTML template showing the user's movies.
    """
    user_movies_list = dataman.get_user_movies(user_id)
    user = dataman.get_user(user_id)
    return render_template('user_movies.html', movies=user_movies_list, user=user)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Adds a new user to the system.

    - **GET**: Displays the form for adding a new user.
    - **POST**: Processes the form and adds the user to the database.

    :returns:
        - Redirect to the users list page on success.
        - Rendered HTML template for adding a user on failure.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        dataman.add_user(name)
        return redirect(url_for('list_users', success=True), 302)
    return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Adds a movie to a specific user's collection.

    - **GET**: Displays the form for adding a movie.
    - **POST**: Processes the form, validates the movie, and adds it to the user's collection.

    :param user_id: The ID of the user adding the movie.
    :type user_id: int
    :returns:
        - Rendered HTML template for adding a movie.
        - Redirect with success status after adding the movie.
    """
    if request.method == 'POST':
        title = request.form.get('title')
        release_year = request.form.get('release_year')
        notes = request.form.get('notes')
        success = dataman.add_movie(user_id, title, release_year, notes=notes)

        if success is None:
            return redirect(url_for('add_movie', user_id=user_id, success='not_found'))
        elif not success:
            return redirect(url_for('add_movie', user_id=user_id, success='False'))
        else:
            return redirect(url_for('add_movie', user_id=user_id, success='True'))

    user = dataman.get_user(user_id)
    success = request.args.get('success')
    return render_template('add_movie.html', user=user, success=success)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Updates a movie in a specific user's collection.

    - **GET**: Displays the form for updating the movie's rating and notes.
    - **POST**: Processes the form and updates the movie details.

    :param user_id: The ID of the user who owns the movie.
    :type user_id: int
    :param movie_id: The ID of the movie to be updated.
    :type movie_id: int
    :returns:
        - Rendered HTML template for updating the movie.
        - Redirect to the user's movie list after successful update.
    """
    movie, notes, user_rating = dataman.get_user_movie(user_id, movie_id)
    user = dataman.get_user(user_id)
    if request.method == 'POST':
        user_rating = request.form.get('update_rating')
        notes = request.form.get('update_notes')
        dataman.update_movie(user_id, movie_id, float(user_rating), notes)
        movies = dataman.get_user_movies(user_id)
        return redirect(url_for('user_movies', user_id=user_id, movies=movies))
    return render_template('update_movie.html', movie=movie,
                           notes=notes, user_rating=user_rating, user=user)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """
    Deletes a movie from a specific user's collection.

    :param user_id: The ID of the user whose movie is to be deleted.
    :type user_id: int
    :param movie_id: The ID of the movie to be deleted.
    :type movie_id: int
    :returns: Redirect to the user's movie list with success status.
    """
    success = dataman.delete_movie(user_id, movie_id)
    return redirect(url_for("user_movies", user_id=user_id, success=success))


@app.errorhandler(404)
def page_not_found(e):
    """
    Handles 404 errors.

    :param e: The exception that triggered the 404 error.
    :type e: Exception
    :returns: Rendered HTML template for the 404 error page.
    """
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

