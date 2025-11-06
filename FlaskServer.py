from flask import send_from_directory, Flask, render_template, request, redirect, url_for

app = Flask(__name__)

class FlaskServer:
    def __init__(
            self
    ):
       self

    @app.route('/')
    def home():
        # Get list of files in the folder
        files = os.listdir(DATA_DIR)

        return render_template('index.html', files=files)