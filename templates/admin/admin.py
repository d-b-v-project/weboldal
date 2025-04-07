from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash, session
import hashlib
import psycopg2
import key
from datetime import datetime
now = datetime.now()
import sqlite3
import hash_gen

DB_FILE = "db/database.db"


def init_db():
    conn = psycopg2.connect(
                    database=key.db_name,
                    host=key.host,
                    user=key.user_name,
                    password=key.pass_word,
                    port=key.port)
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
    con = init_db()
    cur = con.cursor()
    cur.execute(f"SELECT * FROM messages")
    minden = cur.fetchall()
    cur.execute(f"SELECT in_one FROM messages")
    in_one = cur.fetchall()
    
    rendes = {}
    count = 0
    
    
    print(in_one[0][count])
    for message in minden:
        sender = message[0]
        message_text = message[1]
        send_date = message[2]
        rendes[in_one[count][0]] = [sender, message_text, send_date]
        count += 1
    print(rendes)
        
    for in_ones, all in rendes.items():
        print(f"{in_ones} = {all}")
        
    return render_template("admin/dashboard.html", in_one=in_one, user=session["user"], minden=minden, rendes=rendes)

@admin_pg.route("/short_url_page")
def short_url_page():
    conn = init_db()
    cursor = conn.cursor()
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    
    cursor = conn.cursor()
    cursor.execute("SELECT \"full\", short FROM urls")
    data = cursor.fetchall()
    
    url_header = ["Teljes url", "Rövidített"]
    
    
    return render_template("admin/short_url.html", heading=url_header, data=data)

@admin_pg.route("/del_url/<short>")
def del_url(short):
    short_url = short[1:-1]
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM urls WHERE short='{short_url}'")
        data = cursor.fetchall()
    return(redirect(url_for("admin.short_url_page")))

@admin_pg.route("/log_out")
def admin_log_out():
    session.pop("user", None)
    return redirect(url_for("index"))



@admin_pg.route("/hivo_edit_page")
def hivo_edit_page():
    con = init_db()
    cur = con.cursor()
    cur.execute("SELECT name FROM hivok")
    name_in_user_tb = cur.fetchall()
    cur.execute("SELECT name FROM pre_hivok")
    name_in_pre_user_tb = cur.fetchall()
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    return render_template("admin/hivo.html", name_in_user_tb=name_in_user_tb, name_in_pre_user_tb=name_in_pre_user_tb)

@admin_pg.route("/stuck_hivo", methods=["POST", "GET"])
def stuck_hivo():
    con = init_db()
    cur = con.cursor()
    cur.execute("DELETE FROM public.pre_hivok;")
    con.commit()
    return redirect(url_for("admin.hivo_edit_page"))

@admin_pg.route("/del_hivo", methods=["POST", "GET"])
def del_hivo():
    con = init_db()
    cur = con.cursor()
    hivo = request.form["username"]
    if hivo == '0':
        flash("Válassz ki egy felhasználót")
        return redirect(url_for("admin.hivo_edit_page"))
    cur.execute(f"DELETE FROM public.hivok WHERE name='{hivo}';")
    con.commit()
    
    
    return redirect(url_for("admin.hivo_edit_page"))


@admin_pg.route("/del_pre_hivo", methods=["POST", "GET"])
def del_pre_hivo():
    con = init_db()
    cur = con.cursor()
    hivo = request.form["username"]
    if hivo == '0':
        flash("Válassz ki egy felhasználót")
        return redirect(url_for("admin.hivo_edit_page"))
    cur.execute(f"DELETE FROM public.pre_hivok WHERE name='{hivo}';")
    con.commit()
    
    
    return redirect(url_for("admin.hivo_edit_page"))


@admin_pg.route("/change_data")
def change_data():
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))

    
    return render_template("admin/edit_data.html")

@admin_pg.route("/change_name", methods=["post"])
def change_name():
    con = init_db()
    cur = con.cursor()
    
    logged_in_people = session["user"]
    new_name_in_html = request.form["new_name"]
    
    cur.execute(f"UPDATE public.login SET name='{new_name_in_html}' WHERE name='{logged_in_people}';")
    con.commit()
    
    session.pop("user", None)
    return redirect(url_for("index"))


@admin_pg.route("/change_password", methods=["post"])
def change_password():
    con = init_db()
    cur = con.cursor()
    
    logged_in_people = session["user"]
    new_password_in_html = request.form["new_password"]
    old_password_in_html = request.form["old_password"]
    new_password_in_html_hash = hash_gen.convert(new_password_in_html)
    old_password_in_html_hash = hash_gen.convert(old_password_in_html)
    cur.execute(f"SELECT password FROM login WHERE password='{old_password_in_html_hash}'")
    old_form_db = cur.fetchall()
    print(old_form_db)
    
    
    if len(old_form_db) == 0:
        return redirect(url_for("admin.change_data"))
    
    cur.execute(f"UPDATE public.login SET password='{new_password_in_html_hash}' WHERE password='{old_form_db[0][0]}';")
    con.commit()
    
    #return redirect(url_for("admin.change_data"))
    session.pop("user", None)
    return redirect(url_for("index"))








@admin_pg.route("/del_msg/<minden>")
def del_msg(minden):
    con = init_db()
    cur = con.cursor()
    print(minden)
    if minden[0] == "'":
        cur.execute(f"DELETE FROM messages WHERE in_one={minden}")
    else:
        cur.execute(f"DELETE FROM messages WHERE in_one='{minden}'")
    con.commit()
    print(minden)
    return redirect(url_for("admin.dashboard"))



@admin_pg.route("/szoveg_szerkesztes_page")
def szoveg_szerkesztes():
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT * FROM public.szovegek;")
    minden = cur.fetchall()
    teremtes = minden[0][0]
    fo_oldal = minden[0][1]
    miatyank = minden[0][2]
    tiz_parancsolat = minden[0][3]
    keletkezes = minden[0][4]
    
    
    
    return render_template("/admin/edit_texts.html", teremtes=teremtes, miatyank=miatyank, fo_oldal=fo_oldal, tiz_parancsolat=tiz_parancsolat, keletkezes=keletkezes)

@admin_pg.route("/edit_text", methods=["POST"])
def edit_text():
    con = init_db()
    cur = con.cursor()
    teremtes_in_html = request.form["teremtes"]
    fooldal_in_html = request.form["fo_oldal"]
    miatyank_in_html = request.form["miatyank"]
    tiz_parancsolat_in_html = request.form["tiz_parancsolat"]
    keletkezes_in_html = request.form["keletkezes"]
    
    cur.execute(f"UPDATE public.szovegek SET teremtes='{teremtes_in_html}', fo_oldal='{fooldal_in_html}', miatyank='{miatyank_in_html}', tiz_parancsolat='{tiz_parancsolat_in_html}', keletkezes='{keletkezes_in_html}'")
    con.commit()
    
    return redirect(url_for("admin.szoveg_szerkesztes"))

@admin_pg.route("/eredeti")
def eredeti():
    con = init_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM rec_szoveg")
    szovegek = cur.fetchall()
    teremtes = szovegek[0][0]
    fo_oldal = szovegek[0][1]
    miatyank = szovegek[0][2]
    tiz_parancsolat = szovegek[0][3]
    keletkezes = szovegek[0][4]
    
    cur.execute(f"UPDATE public.szovegek SET teremtes='{teremtes}', fo_oldal='{fo_oldal}', miatyank='{miatyank}', tiz_parancsolat='{tiz_parancsolat}', keletkezes='{keletkezes}';")
    con.commit()
    
    return redirect(url_for("admin.szoveg_szerkesztes"))



@admin_pg.route("/send_message", methods=["POST"])
def send_message():
    con = init_db()
    cur = con.cursor()
    message_in_html = request.form["message"]
    user = session["user"]
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    in_one = f"{user}: {message_in_html} | {date}"
    cur.execute(f"INSERT INTO messages (name, message, date, in_one) values ('{user}', '{message_in_html}', '{date}', '{in_one}')")
    con.commit()
    ip = request.remote_addr
    date = now.strftime("%Y.%m.%d, %H:%M:%S")
    #logged_in_user = session["user"]
    return redirect(url_for("admin.dashboard"))


@admin_pg.route("/add_eredeti")
def add_eredeti():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT * FROM szovegek")
    szovegek = cur.fetchall()
    teremtes = szovegek[0][0]
    fo_oldal = szovegek[0][1]
    miatyank = szovegek[0][2]
    tiz_parancsolat = szovegek[0][3]
    keletkezes = szovegek[0][4]
    
    cur.execute(f"UPDATE public.rec_szoveg SET teremtes='{teremtes}', fo_oldal='{fo_oldal}', miatyank='{miatyank}', tiz_parancsolat='{tiz_parancsolat}', keletkezes='{keletkezes}';")
    con.commit()
    
    
    return redirect(url_for("admin.szoveg_szerkesztes"))