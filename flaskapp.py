"""Flask app implementation."""

from flask import Flask, flash, redirect, render_template, request, url_for
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
def login() -> Response | str:
    """Try to log in user with provided credentials, raising an error if invalid.

    Returns:
        Rendering of profile page if correct credentials, else redirect to login page with error message
    """
    username = request.form.get("username")
    password = request.form.get("password")

    db_username, db_password, _, _, _ = db_read_query(
        "select * from users where username = ?",
        params=(username,),
    )

    if not db_username or db_password != password:
        flash("Invalid username or password.", "error")
        return redirect(url_for("index"))

    return render_template("profile.html")


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
def profile():
    return "Profile"


if __name__ == "__main__":
    app.run(FLASK_DEBUG)
