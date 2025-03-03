from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash, session
import hashlib
import psycopg2
from key import *
from datetime import datetime
now = datetime.now()


def init_db():
    conn = psycopg2.connect(
                    database=db_name,
                    host=host,
                    user=user_name,
                    password=pass_word,
                    port=5433)
    return conn

admin_pg = Blueprint('admin', __name__, template_folder='templates')
SECRET_KEY = 'development'


@admin_pg.route("/login_page")
def login_page():
    return render_template("admin/login.html")


@admin_pg.route("/login", methods=["POST"])
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
    
    
    
    
    cur.execute(f"SELECT name, password FROM public.login WHERE name = '{username_in_html}'")
    login_in_db = cur.fetchall()
    print(login_in_db[0][1])
    
    if len(login_in_db) == 0:
        flash("Helytelen felhasználónév vagy jelszó.", "error")  
        return redirect(url_for("admin.login_page"))
    if login_in_db[0][1] != password_hash:
        flash("Helytelen felhasználónév vagy jelszó.", "error")
        return redirect(url_for("admin.login_page"))
    session["user"] = username_in_html
    print("Bejelentkezettt")
    flash("Sikeres bejelentkezés!", "success")
    ip = request.remote_addr
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    logged_in_user = session["user"]

    try:
        user = session["user"]
    except:
        return redirect(url_for("index"))
    return redirect(url_for("admin.dashboard"))
    

@admin_pg.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    
    return render_template("admin/dashboard.html")

@admin_pg.route("/log_out")
def admin_log_out():
    session.pop("user", None)
    return redirect(url_for("index"))