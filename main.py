from flask import Flask, redirect, render_template, url_for
import sqlite3

app = Flask(__name__)



@app.route("/")
def index():
    return render_template("index.html")

@app.route("/szentiras")
def szentiras():
    return render_template("szentiras.html")

@app.route("/teremtestortenet")
def teremtes_tortenet():
    return render_template("teremtes.html")

@app.route("/zarandokhely")
def zarandokhely():
    return render_template("zarandokhely.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)