"""Flask app implementation."""

import uuid
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug import Response

from environment import FLASK_DEBUG, FLASK_SECRET_KEY
from helpers import db_read_query, db_write_query

# type aliases to make return types clearer
type Rendering = str
type Redirect = Response

# create and configure the flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# sqlite setup
UPLOAD_FOLDER = Path("uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
Path.mkdir(UPLOAD_FOLDER, exist_ok=True)

db_write_query(
    """
        create table if not exists users (
                username text unique not null,
                password text not null,
                firstname text not null,
                lastname text not null,
                email text unique not null,
                address text not null
            )
        """,
)
db_write_query(
    """
    create table if not exists files (
            username text not null,
            original_filename text not null,
            stored_filename text not null,
            word_count integer not null,
            foreign key(username) references users(username)
        )
    """,
)


@app.route("/")
def index() -> Rendering:
    """Landing Page for the Flask App.

    Returns:
        Rendering of the login.html file
    """
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login() -> Redirect:
    """Try to log in user with provided credentials, raising an error if invalid.

    Returns:
        Redirect to profile page if login is correct, else back to login.
    """
    username = request.form.get("username")
    password = request.form.get("password")

    results = db_read_query(
        "select * from users where username = ?",
        params=(username,),
    )

    if not results or results[0][1] != password:
        flash("Invalid username or password.", "error")
        return redirect(url_for("index"))

    user_info = results[0]
    session["user_info"] = {
        "username": user_info[0],
        "first_name": user_info[1],
        "last_name": user_info[2],
        "email": user_info[3],
        "address": user_info[4],
    }

    return redirect(url_for("profile"))


@app.route("/signup")
def signup() -> Rendering:
    """Render signup page to gather user info."""
    return render_template("signup.html")


@app.route("/registered", methods=["POST"])
def registered() -> Redirect:
    """Read user inputs and injects into database.

    If the username or email already exists in the database, a error flash is created and the user
    is redirected to the sign up page.

    Returns:
        Redirect to login page if successful, else to the sign up page
    """
    username: str = request.form.get("username")  # ty:ignore[invalid-assignment]
    password: str = request.form.get("password")  # ty:ignore[invalid-assignment]
    first_name: str = request.form.get("firstName")  # ty:ignore[invalid-assignment]
    last_name: str = request.form.get("lastName")  # ty:ignore[invalid-assignment]
    email: str = request.form.get("email")  # ty:ignore[invalid-assignment]
    address: str = request.form.get("address")  # ty:ignore[invalid-assignment]

    existing = db_read_query(
        "select username, email from users where username = ? or email = ?",
        params=(username, email),
    )

    if existing:
        if existing[0][0] == username:
            flash("This username is already taken", "error")
        else:
            flash("This email is already registered", "error")
        return redirect(url_for("signup"))

    db_write_query(
        "insert into users (username, password, firstname, lastname, email, address) values (?, ?, ?, ?, ?, ?)",
        params=(username, password, first_name, last_name, email, address),
    )

    flash("New account successfully created! Sign in to continue.", "success")

    return redirect(url_for("index"))


@app.route("/upload", methods=["POST"])
def upload() -> Redirect:
    """Process file uploads to store the data in the database.

    Returns:
        Redirect to the profile page after upload
    """
    if "user_info" not in session:
        return redirect(url_for("index"))

    username = session["user_info"]["username"]
    upload_files = request.files.getlist("files")

    # iterate over files the user uploaded
    for file in upload_files:
        # if there is not file or filename continue to next object
        if not (file and file.filename):
            continue

        original_filename = file.filename
        unique_filename = f"{uuid.uuid4()}.txt"
        file_path: Path = Path.joinpath(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(file_path)

        # word counter
        with file_path.open(errors="ignore") as f:
            word_count = len(f.read().split())

        db_write_query(
            "insert into files (username, original_filename, stored_filename, word_count) values (?, ?, ?, ?)",
            params=(username, original_filename, unique_filename, word_count),
        )

    flash("Files uploaded successfully!", "success")
    return redirect(url_for("profile"))


@app.route("/profile")
def profile() -> Rendering | Redirect:
    """Load user's data from session and uploads to html rendering.

    Sends error message to login page to be displayed when redirected in the event of no user data existing.

    Returns:
        Rendering of the user's profile info, or redirect to login with error message
    """
    if "user_info" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("index"))

    username = session["user_info"]["username"]

    files = db_read_query(
        "select original_filename, word_count, stored_filename from files where username = ?",
        params=(username,),
    )

    return render_template("profile.html", user=session["user_info"], files=files)


@app.route("/download/<stored_filename>")
def download_file(stored_filename: str) -> Redirect:
    """Retrieve a stored file from the database to send to the user.

    Args:
        stored_filename (str): The unique UUID filename stored on the disk

    Returns:
        Redirect to the current page while triggering the file download
    """
    if "user_info" not in session:
        return redirect(url_for("index"))

    results = db_read_query("select original_filename from files where stored_filename = ?", params=(stored_filename,))

    if not results:
        return "File Not found", 404

    original_filename = results[0][0]
    file_path = Path.joinpath(app.config["UPLOAD_FOLDER"], stored_filename)

    return send_file(file_path, as_attachment=True, download_name=original_filename)


@app.route("/logout")
def logout() -> Redirect:
    """Upon logout, clear session and return to landing page.

    Returns:
        Redirect to landing page
    """
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG)
