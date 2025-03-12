from flask import Flask, redirect, render_template, url_for, request, blueprints, flash, abort, session
from flask_mail import Message, Mail
import sqlite3
import psycopg2
from templates.admin.admin import admin_pg
from templates.hivo.hivo import hivo
import hash_gen
import random
import smtplib
import key
import requests

try:
    from key import db_name, user_name, pass_word, host
except:
    print('Csinálj a "key.py"  file-ba "db_name", "user_name","pass_word", "host", "port" változót a megfelelő értékekkel')
    exit()


SECRET_KEY = 'development'

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.register_blueprint(admin_pg, url_prefix="/admin")
app.register_blueprint(hivo, url_prefix="/hivo")

app.config['MAIL_SERVER'] = key.mail_server
app.config['MAIL_PORT'] = key.mail_port
#app.config['MAIL_USERNAME'] = key.mail_username
#app.config['MAIL_PASSWORD'] = key.mail_password
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False



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

@app.route("/imatkozas")
def szentiras():
    return render_template("imatkozas.html")

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
    return render_template("hivove_valas_lap.html", site_key=key.site_key)


mail = Mail(app)
@app.route("/hivove_valas_submit", methods=["POST"])
def hivove_valas_submit():
    con = init_db()
    cur = con.cursor()
    try:
        osztaly = int(request.form['class'])
        os = request.form['os']
        name_in_html = request.form["name"]
        email_in_html = request.form["email"]
        password_in_html = request.form["password"]
    except:
        flash("Minden mezőt tölts ki!")
        return redirect(url_for("hivovevalas"))
    
    cur.execute("SELECT name, email FROM public.hivok")
    hivo_name_email = cur.fetchall()
    
    
    try:
        name_in_db = hivo_name_email[0][0]
        email_in_db = hivo_name_email[0][1]
        if name_in_html == name_in_db:
            flash("Létezik ilyen felhasználónévvel ember!")
            return redirect(url_for("hivovevalas"))
    except:
        pass
    
    
    
    
    verification_code = random.randint(111111, 999999)

    message = Message(
        subject="E-mail ellenőrzés",
        recipients=[email_in_html],
        sender=("Olyan ügyes és okos vagyok", "dani@oregpreshaz.eu")
    )
    message.body = f"Ellenőrző kód: {verification_code}"
    mail.send(message)
    
    
    password_hash = hash_gen.convert(password_in_html)
    cur.execute(f"INSERT INTO pre_hivok (name, email, password, os, class, email_code) VALUES ('{name_in_html}', '{email_in_html}', '{password_hash}', '{os}', '{osztaly}', '{verification_code}')")
    con.commit()
    
    
    secret_response = request.form["g-recaptcha-response"]
    
    verify_response = requests.post(url=f"{key.verify_url}?secret={key.secret_key}&response={secret_response}").json()
    
    if verify_response['success'] == False:
        abort(401)
    
    session["pre_hivo"] = name_in_html
    print(f"{osztaly}, {os}, {name_in_html}, {email_in_html}, {password_in_html}:{password_hash}")
    return redirect(url_for("email_verification_page"))

@app.route("/email_verification_page")
def email_verification_page():
    print(session["pre_hivo"])
    return render_template("email_ver.html")

@app.route("/email_verification", methods=["POST"])
def email_verification():
    con = init_db()
    cur = con.cursor()
    
    code_in_html = request.form["code_html"]
    
    print(session["pre_hivo"])
    
    cur.execute(f"SELECT name, email, password, os, class, email_code FROM public.pre_hivok")
    minden = cur.fetchall()
    
    
    cur.execute(f"SELECT name, email_code FROM public.pre_hivok WHERE name='{session["pre_hivo"]}'")
    code_in_db = cur.fetchall()[0][1]
    
    if code_in_db != code_in_html:
        flash("A kód nem megfelelő")
        return redirect(url_for("email_verification_page"))
    
    cur.execute(f"DELETE FROM public.pre_hivok WHERE email_code='{code_in_html}';")
    con.commit()
    cur.execute(f"INSERT INTO hivok (name, email, password, os, class, email_code) VALUES ('{minden[0][0]}', '{minden[0][1]}', '{minden[0][2]}', '{minden[0][3]}', '{minden[0][4]}', '{minden[0][5]}')")
    con.commit()
    
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
