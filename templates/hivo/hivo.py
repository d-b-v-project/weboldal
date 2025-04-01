from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash, session
import hashlib
import psycopg2
import key
from datetime import datetime
now = datetime.now()


def init_db():
    conn = psycopg2.connect(
                    database=key.db_name,
                    host=key.host,
                    user=key.user_name,
                    password=key.pass_word,
                    port=key.port)
    return conn

hivo = Blueprint('hivo', __name__, template_folder='templates')
SECRET_KEY = 'development'



@hivo.route("/login_page")
def login_page():
    return render_template("hivo/login.html")


@hivo.route("/login", methods=["POST"])
def login():
    con = init_db()
    cur = con.cursor()
    username_in_html = request.form['username']
    if len(username_in_html) > 16:
        flash("A maximális hosszúság 16 karakter")
    logged_in_username = username_in_html
    password_in_html = request.form['password']
    password_hash = hashlib.sha256(password_in_html.encode("UTF-8")).hexdigest()
    username_in_html_felesleggel = f"('{username_in_html}',)"
    password_hash_felesleggel = f"('{password_in_html}',)"
    # Hitelesítés az előre megadott adatokkal
    
    
    
    
    cur.execute(f"SELECT name, password FROM public.hivok WHERE name = '{username_in_html}'")
    login_in_db = cur.fetchall()
    
    if len(login_in_db) == 0:
        flash("Helytelen felhasználónév vagy jelszó.", "error")  
        return redirect(url_for("hivo.login_page"))
    if login_in_db[0][1] != password_hash:
        flash("Helytelen felhasználónév vagy jelszó.", "error")
        return redirect(url_for("hivo.login_page"))
    session["hivo"] = username_in_html
    print("Bejelentkezettt")
    flash("Sikeres bejelentkezés!", "success")
    ip = request.remote_addr
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    logged_in_user = session["hivo"]

    try:
        user = session["hivo"]
    except:
        return redirect(url_for("index"))
    return redirect(url_for("hivo.dashboard"))

@hivo.route("/dashboard")
def dashboard():
    if "hivo" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    con = init_db()
    cur = con.cursor()
    cur.execute(f"SELECT in_one FROM messages")
    in_one = cur.fetchall()
    
    return render_template("hivo/dashboard.html", in_one=in_one)



@hivo.route("/send_message", methods=["POST"])
def send_message():
    con = init_db()
    cur = con.cursor()
    message_in_html = request.form["message"]
    user = session["hivo"]
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    
    if message_in_html == "":
        flash("Nem lehet üresen beküldeni.")
        return redirect(url_for("hivo.dashboard"))
    elif message_in_html == " " or message_in_html == "  " or message_in_html == "   " or message_in_html == "    ":
        flash("Nem lehet üresen beküldeni.")
        return redirect(url_for("hivo.dashboard"))
        
    url_reszek = ["https://", "http://", ".eu", ".hu", ".net", ".com", ".de", ".en"]
    for tiltott_url in url_reszek:
        if tiltott_url in message_in_html:
            flash("Nem lehet linket küldeni.")
            return redirect(url_for("hivo.dashboard"))
    in_one = f"{user}: {message_in_html} | {date}"
    cur.execute(f"INSERT INTO messages (name, message, date, in_one) values ('{user}', '{message_in_html}', '{date}', '{in_one}')")
    con.commit()
    ip = request.remote_addr
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    #logged_in_user = session["user"]
    return redirect(url_for("hivo.dashboard"))