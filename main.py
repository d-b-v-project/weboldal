from flask import Flask, redirect, render_template, url_for, request, blueprints
import sqlite3
import psycopg2
from templates.admin.admin import admin_pg

try:
    from key import db_name, user_name, pass_word, host
except:
    print('Csinálj a "key.py"  file-ba "db_name", "user_name","pass_word", "host", "port" változót a megfelelő értékekkel')
    exit()


SECRET_KEY = 'development'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(admin_pg, url_prefix="/admin")


def init_db():
    conn = psycopg2.connect(
                    database=db_name,
                    host=host,
                    user=user_name,
                    password=pass_word,
                    port=5433)
    return conn


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/szentiras")
def szentiras():
    return render_template("szentiras.html")

@app.route("/teremtestortenet")
def teremtes_tortenet():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT teremtes FROM public.szovegek;")
    teremtes_tortenet_szoveg = cur.fetchall()[0][0]
    teremtes_tortenet_sorok = str(teremtes_tortenet_szoveg).split("\n")

    
    
    
    return render_template("teremtes.html", teremtes_tortenet_sorok=teremtes_tortenet_sorok)

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
