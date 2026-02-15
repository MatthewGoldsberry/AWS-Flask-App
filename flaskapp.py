"""Flask app implementation."""

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug import Response

from environment import FLASK_DEBUG, FLASK_SECRET_KEY
from helpers import db_read_query, db_write_query

# type aliases to make return types clearer
type Rendering = str
type Redirect = Response

# create and configure the flask app
app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# sqlite setup -- ensuring username and email are unique
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

    db_username, db_password, first_name, last_name, email, address = db_read_query(
        "select * from users where username = ?",
        params=(username,),
    )

    if not db_username or db_password != password:
        flash("Invalid username or password.", "error")
        return redirect(url_for("index"))

    session["user_info"] = {
        "username": db_username,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "address": address,
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

    if existing != ("", "", "", "", "", ""):
        if existing[0] == username:
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


@app.route("/profile")
def profile() -> Rendering | Response:
    """Load user's data from session and uploads to html rendering.

    Sends error message to login page to be displayed when redirected in the event of no user data existing.

    Returns:
        Rendering of the user's profile info, or redirect to login with error message
    """
    if "user_info" not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("index"))

    return render_template("profile.html", user=session["user_info"])


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
