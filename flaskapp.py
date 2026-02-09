"""Flask app implementation."""

import sqlite3

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# sqlite setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute(
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
conn.commit()
conn.close()


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return f"Login attempted for: {username} with password: {password}"

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/registered", methods=["POST"])
def registered():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")
    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)