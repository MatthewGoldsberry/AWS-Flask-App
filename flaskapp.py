"""Flask app implementation."""

import sqlite3

from flask import Flask, render_template, request

app = Flask(__name__)

# sqlite setup


@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return f"Login attempted for: {username} with password: {password}"

if __name__ == "__main__":
    app.run(debug=True)