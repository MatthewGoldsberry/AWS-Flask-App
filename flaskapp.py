"""Flask app implementation."""

from flask import Flask, redirect, render_template, request, url_for

from helpers import db_write_query

app = Flask(__name__)

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
def index():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
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
    app.run(debug=True)
