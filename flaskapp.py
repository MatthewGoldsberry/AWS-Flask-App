"""Flask app implementation."""

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug import Response

from environment import FLASK_DEBUG, FLASK_SECRET_KEY
from helpers import db_read_query, db_write_query

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# sqlite setup
db_write_query(
    """
        create table if not exists users (
                username text,
                password text,
                firstname text,
                lastname text,
                email text
            )
        """,
)


@app.route("/")
def index() -> str:
    """Landing Page for the Flask App.

    Returns:
        Rendering of the login.html file
    """
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login() -> Response:
    """Try to log in user with provided credentials, raising an error if invalid.

    Returns:
        Redirect to profile page if login is correct, else back to login.
    """
    username = request.form.get("username")
    password = request.form.get("password")

    db_username, db_password, first_name, last_name, email = db_read_query(
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
    }

    return redirect(url_for("profile"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/registered", methods=["POST"])
def registered():
    username = request.form.get("username")
    password = request.form.get("password")
    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")
    email = request.form.get("email")

    db_write_query(
        "insert into users (username, password, firstname, lastname, email) values (?, ?, ?, ?, ?)",
        params=(username, password, first_name, last_name, email),
    )

    return redirect(url_for("index"))


@app.route("/profile")
def profile() -> str:
    """Load user's data from session and uploads to html rendering.

    Returns:
        Rendering of the user's profile info.
    """
    user_info = session.get("user_info")

    if not user_info:
        return redirect(url_for("index"))

    return render_template("profile.html", user=user_info)


@app.route("/logout")
def logout() -> Response:
    """Upon logout, clear session and return to landing page.

    Returns:
        Redirect to landing page
    """
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG)
