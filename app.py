import os
from typing import List

from flask import Flask, render_template, request, redirect, url_for

from datamanager.data_models import Movie
from datamanager.sqlite_datamanager import SQLiteDataManager

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configure the database URI and tracking modifications
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "storage", "movie_app.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

dataman = SQLiteDataManager(app)


@app.route('/users', methods=['GET'])
def list_users():
    users = dataman.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>', methods=['GET'])
def user_movies(user_id):
    user_movies_list = dataman.get_user_movies(user_id)
    user = dataman.get_user(user_id)
    return render_template('user_movies.html', movies=user_movies_list, user=user)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        dataman.add_user(name)
        return redirect(url_for('list_users', success=True), 302)
    return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movies = dataman.get_user_movies(user_id)
        title = request.form.get('title')
        existing_titles = [movie.title for movie in movies]
        if title not in existing_titles:
            release_year = request.form.get('release_year')
            notes = request.form.get('notes')
            dataman.add_movie(user_id, title, release_year, notes)
            return redirect(url_for('add_movie',user_id=user_id, success=True))
        else:
            return redirect(url_for('add_movie', user_id=user_id, success=False))
    user = dataman.get_user(user_id)
    return render_template('add_movie.html', user=user)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    pass


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    pass


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
