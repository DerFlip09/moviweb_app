import os
from flask import Flask
from datamanager.sqlite_datamanager import SQLiteDataManager

app = Flask(__name__)

# Get the absolute path to the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Configure the database URI and tracking modifications
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "storage", "movie_app.sqlite3")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

dataman = SQLiteDataManager(app)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)