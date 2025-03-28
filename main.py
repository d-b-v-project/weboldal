#!./venv/bin/python
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
from datetime import datetime
import string
import get_urls


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

DB_FILE = "db/database.db"

def init_db():
    conn = psycopg2.connect(
                    database=db_name,
                    host=host,
                    user=user_name,
                    password=pass_word,
                    port=key.port)
    
    return conn

def init_sqlie():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                short TEXT UNIQUE,
                full TEXT
            )
        """)
        conn.commit()


@app.route("/")
def index():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT fo_oldal FROM public.szovegek")
    fo_oldal = cur.fetchall()
    szoveg = fo_oldal[0][0]
    fo_oldal_sorok = str(szoveg).split("\n")
    
    cur.execute("SELECT keletkezes FROM public.szovegek")
    keletkezes = cur.fetchall()[0][0]
    keletkezes_sorok = str(keletkezes).split("\n")
    
    cur.execute("SELECT name FROM hivok")
    hivok = cur.fetchall()
    hivok_szama = int()
    for i in hivok:
        hivok_szama += 1
    
    return render_template("index.html", fo_oldal_sorok=fo_oldal_sorok, hivok_szama=hivok_szama, keletkezes_sorok=keletkezes_sorok)




# Rövid kód generálása
def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Főoldal
@app.route('/linkshorter', methods=['POST', 'GET'])
def short_link():
    tiltott_url = list(get_urls.open_file("main.py")) 
    if request.method == 'POST':
        full_url = request.form['url']
        short_url = request.form['short_url']
        tiltott_url_str = ""
        for url in tiltott_url:
            tiltott_url_str += f"{url}, "
        for url in tiltott_url:
            print(f"{short_url} == {url[1:]}")
            if short_url == url[1:]:
                flash(f"Ez a rövidítés használva van már! Ezeket a neveket nem használhatod: {tiltott_url_str}")
                return redirect(url_for("short_link"))
            
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT short, full FROM urls WHERE short='{short_url}'")
            a = cursor.fetchall()
            if len(a) != 0:
                flash(f"Ez a rövidítés használva van már!")
                return redirect(url_for("short_link"))
        
        if len(short_url) > 16:
            flash("Maximális hossza a rövid url-nek 16 karakter")
            return redirect(url_for("short_link"))
        elif short_url == "":
            flash("Maximális hossza a rövid url-nek 16 karakter")
            return redirect(url_for("short_link"))
        short_code = short_url
        
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO urls (short, full) VALUES ('{short_code}', '{full_url}')")
            conn.commit()
        
        short_url = request.host_url + short_code
        return render_template('linkshort.html', short_url=short_url)
    
    return render_template('linkshort.html')

# Átirányítás rövid URL alapján
@app.route('/<short_code>')
def redirect_url(short_code):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT full FROM urls WHERE short = ?", (short_code,))
        result = cursor.fetchone()
        
        if result:
            return redirect(result[0])
        else:
            return "URL not found", 404





@app.route("/imatkozas")
def szentiras():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT miatyank FROM public.szovegek")
    minden = cur.fetchall()
    
    return render_template("imatkozas.html", minden=minden)

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
old_minute = int()

mail = Mail(app)
@app.route("/hivove_valas_submit", methods=["POST"])
def hivove_valas_submit():
    global old_minute
    con = init_db()
    cur = con.cursor()
    hozzajarult = False
    
    tiltott_nevek = ["ADOLF HITLER", "HITLER", "ENGLERT", "ERVIN"]
    
    
    try:
        osztaly = int(request.form['class'])
        os = request.form['os']
        name_in_html = request.form["name"]
        email_in_html = request.form["email"]
        password_in_html = request.form["password"]
        
    except:
        flash("Minden mezőt tölts ki!")
        return redirect(url_for("hivovevalas"))
    
    for tiltott_nev in tiltott_nevek:
        if tiltott_nev in name_in_html:
            flash("Ez a felhasználónév le van tiltva!")
            return redirect(url_for("hivovevalas"))
    
    try:
        hozzajarulas = request.form["hozzajarulas"]
        hozzajarult = True
    except:
        hozzajarult = False
    
    if hozzajarult == False:
        flash("El kell fogadnon a felhasználási feltételeket!")
        return redirect(url_for("hivovevalas"))
    
    cur.execute("SELECT name, email FROM public.hivok")
    hivo_name_email = cur.fetchall()
    cur.execute(f"SELECT name, password FROM public.hivok WHERE name = '{name_in_html}'")
    login_in_db = cur.fetchall()
    if len(login_in_db) != 0:
        flash("Létezik ilyen felhasználónévvel ember!")
        return redirect(url_for("hivovevalas"))
    
    
    try:
        name_in_db = hivo_name_email[0][0]
        email_in_db = hivo_name_email[0][1]
        if name_in_html == name_in_db:
            flash("Létezik ilyen felhasználónévvel ember!")
            return redirect(url_for("hivovevalas"))
    except:
        pass
    
    
    
    
    verification_code = random.randint(111111, 999999)
    
    password_hash = hash_gen.convert(password_in_html)
    
    cur.execute("SELECT * FROM pre_hivok")
    pre_hivo = cur.fetchall()
    
    
    now = datetime.now()
    if len(pre_hivo) > 20:
        flash("Valaki jelenleg próbál bejelentkezni. Kérem várjon")
        return redirect(url_for("hivovevalas"))
    
    
    
    
    cur.execute(f"SELECT join_time FROM pre_hivok")
    join_times = cur.fetchall()
    
    
        
    
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    cur.execute(f"INSERT INTO pre_hivok (name, email, password, os, class, email_code, join_time) VALUES ('{name_in_html}', '{email_in_html}', '{password_hash}', '{os}', '{osztaly}', '{verification_code}', '{date}')")
    con.commit()

    cur.execute(f"SELECT name, email, password, os, class, email_code FROM public.pre_hivok")
    minden = cur.fetchall()
    
    minden = minden[0]


    message = Message(
        subject="E-mail ellenőrzés",
        recipients=[email_in_html],
        sender=("Email ellenőrzése", "automail@ervinizmus.eu")
    )
    message.body = f"Sikeresen regisztráltál: {minden[0]},\n{minden[0]} {minden[3]} operációs rendszert használ és\n{minden[4]}-dik osztályba jár\n# Ellenőrző kód: {verification_code}"
    
    
    
    mail.send(message)
    
    
    
    
    
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


@app.route("/tiz_parancsolat")
def tiz_parancsolat():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT tiz_parancsolat FROM szovegek")
    tiz_parancsolat = cur.fetchall()[0][0]
    
    parancsolat = str(tiz_parancsolat).split("\n")
    
    
    
    
    return render_template("tiz_parancsolat.html", parancsolat=parancsolat)


@app.route("/email_verification", methods=["POST"])
def email_verification():
    con = init_db()
    cur = con.cursor()
    
    code_in_html = request.form["code_html"]
    
    cur.execute(f"SELECT name, email, password, os, class, email_code FROM public.pre_hivok")
    minden = cur.fetchall()
    
    pre_hivo_sesion = session["pre_hivo"]
    cur.execute(f"SELECT name, email_code FROM public.pre_hivok WHERE name='{pre_hivo_sesion}'")
    code_in_db = cur.fetchall()[0][1]
    
    if code_in_db != code_in_html:
        flash("A kód nem megfelelő")
        return redirect(url_for("email_verification_page"))
    
    cur.execute(f"DELETE FROM public.pre_hivok WHERE email_code='{code_in_html}';")
    con.commit()
    cur.execute(f"INSERT INTO hivok (name, email, password, os, class, email_code) VALUES ('{minden[0][0]}', '{minden[0][1]}', '{minden[0][2]}', '{minden[0][3]}', '{minden[0][4]}', '{minden[0][5]}')")
    con.commit()
    
    return redirect(url_for("index"))

@app.route("/elerhetosegek")
def elerhetosegek():
    return render_template("elerhetosegek.html")

@app.route("/info")
def info():
    return render_template("felh_felt.html")

@app.route("/wikipedia")
def wiki():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT * FROM wikipedia")
    minden_nyers = cur.fetchall()
    minden = minden_nyers[0][0]
    
    modulok = str(minden).split("   ")

    
    wiki_sorok = str(minden).split("\n")
    
    
    
    return render_template("wiki.html", modulok=modulok)






if __name__ == "__main__":
    app.run(debug=True, port=5000)
