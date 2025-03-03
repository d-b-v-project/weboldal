from flask import Flask, redirect, render_template, url_for, request, blueprints
import sqlite3
from templates.admin.admin import admin_pg



SECRET_KEY = 'development'

app = Flask(__name__)
app.register_blueprint(admin_pg, url_prefix="/admin")



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


#================HÍVŐVÉ VÁLÁS====================
@app.route("/hivovevalas")
def hivovevalas():
    return render_template("hivove_valas_lap.html")

@app.route("/hivove_valas_submit", methods=["POST"])
def hivove_valas_submit():
    option = request.form['class']
    name_in_html = request.form["name"]
    email_in_html = request.form["email"]
    password_in_html = request.form["password"]
    print(option)
    return redirect(url_for("hivovevalas"))



if __name__ == "__main__":
    app.run(debug=True, port=5000)
