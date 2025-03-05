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

@admin_pg.route("/szoveg_szerkesztes_page")
def szoveg_szerkesztes():
    con = init_db()
    cur = con.cursor()
    
    cur.execute("SELECT teremtes FROM public.szovegek;")
    teremtes = cur.fetchall()
    cur.execute("SELECT fo_oldal FROM public.szovegek;")
    fo_oldal = cur.fetchall()
    cur.execute("SELECT miatyank FROM public.szovegek;")
    miatyank = cur.fetchall()
    return render_template("/admin/edit_texts.html", teremtes=teremtes, miatyank=miatyank, fo_oldal=fo_oldal)

@admin_pg.route("edit_teremtes", methods=["POST"])
def edit_teremtes():
    if "user" not in session:
        flash("Először jelentkezz be!", "error")
        return redirect(url_for("index"))
    con = init_db()
    cur = con.cursor()
    teremtes_in_html = request.form["teremtes"]
    
    ins = cur.execute(f"INSERT OR REPLACE INTO public.szovegek (teremtes, fo_oldal, miatyank) VALUES ({teremtes_in_html}, 'E vallás A mi istenünk Englert Ervin Brunórol szól. ezen a weboldalon meg lehet találni minden dolgok ami a vallásunkhoz köthető. És ha támogatod a vallásunk adód 1%val (csak is Englert bankkártyát fogadunk el) akkor hozzá férhetsz olyan dolgokhoz amiről csak a fő papjaink tudnak. Na de mihez is férsz hozzá ezen az oldalon: Elmeséljük neked a teremtés történetét. Meg hallgathatod a 10 parancsolatot. Meg tanulhatod hogy a Windows miért rossz. Meg ismerheted a mi istenünk életetét hogy a 7 hét napjában mit csinál. Meg tekintheted az Ervin Galleryt(TM) Játszhatsz A mi Istenünk Játékával és végül de nem utolsó sorban megtanulhatod a miatyánkat (ervin`s version) Na de mihez is férsz hozzá ha támogatsz minket: ez titok hiszen ahoz hogy ezt meg tudd támogatnod kell minket :)', 'Mi atyánk a linux istene szenteltessék meg az ubuntut jöjjön el a distro-d és legyen meg a te akaratod amint az órán úgy a gépen is. Mindennapi fejezetvizsgánkat add meg nékünk ma és bocsásd meg a windows-t miképpen mi is megbocsáltunk a microsoftnak, és ne kényszeríts minket az egyesekre, mert tiéd a laptop, a root jog és az utolsó szó mindörökké ámen');")
    con.commit()
    
admin_pg.route("/insert_eredeti_teremtes")
def insert_eredeti_teremtes():
    con = init_db()
    cur = con.cursor()
    ins = cur.execute(f"""INSERT OR REPLACE INTO public.szovegek
                      (teremtes, fo_oldal, miatyank) VALUES 
                      ('Mielőtt még lett volna Microsoft, Linux vagy Apple, Ervin, a mi istenünk, már létezett. Egy gyönyörű pillanatban kitalálta, hogy megteremti a Linuxot. Ervin így szólt: "Legyen Ubuntu!" És a világ engedelmesen feltelepítette az Ubuntut. Ervin látta, hogy amit teremtett, az jó. Lett tehát az első nap.

A második napon Ervin megteremtette a Pythont. Ervin így szólt: "Legyen egy nyelv, amelyet minden értelmes lény hall és beszél!" És létrejött a Python. Lett tehát a második nap.

A harmadik napon Ervin megteremtette a felhasználói felületet. Ervin így szólt: "Legyen egy vizuálisan kezelhető terület, amelyet még a bolond ember is tud kezelni!" És létrejött a vizuális tér. Ervin látta, hogy amit teremtett, az szép és jó. Lett tehát a harmadik nap.

A negyedik napon Ervin megteremtette a Thonny-t. Ervin így szólt: "Legyen egy tér, ahol a nyelvet lehet beszélni és olvasni!" És létrejött a Thonny. Lett tehát a negyedik nap.

Az ötödik napon Ervin megteremtette a felhasználókat. Ervin így szólt: "Legyenek élőlények, akik használják ezt a gyönyörű rendszert!" És lám, létrejöttek az élőlények változó IQ-szinttel. Lett tehát az ötödik nap.

A hatodik napon Ervin megteremtette az első technikusokat. Ervin így szólt: "Legyenek emberek, akik olyan képességekkel rendelkeznek, hogy uralják ezt a világot!" És létrejött az első admin, neve: "root". Lett tehát a hatodik nap.

A hetedik napon Ervin megpihent a foteljében és megszentelte ezt a napot. Látta azonban, hogy root nem boldogul egyedül, ezért teremtette neki "sudo"-t. Nem sokkal később Bill Gates megkísértette sudo-t, hogy Microsoft-fejlesztő legyen. Bill Gates így szólt: "Ha mellém állsz, erősebb lehetsz, mint Ervin!" Kit valamiért nem tudott ellenállni Bill Gates kísértésének, és Microsoft-fejlesztő lett. Később sudo, root-ot is átalakította Microsoft-fejlesztővé.

Ervin ezt látván így szólt: "Ti átkozottak! Nem mondtam meg, hogy a Microsoft nem jó? Mivel ezt tettétek, kitiltalak titeket az Ubuntu kertjéből! Ami pedig téged illet, Bill Gates, a Windows örökre átkozott és gyenge lesz. Büntetésedül a te szemed szenvedni fog a Windows 11-től!', 'E vallás A mi istenünk Englert Ervin Brunórol szól. ezen a weboldalon meg lehet találni minden dolgok ami a vallásunkhoz köthető. És ha támogatod a vallásunk adód 1%val (csak is Englert bankkártyát fogadunk el) akkor hozzá férhetsz olyan dolgokhoz amiről csak a fő papjaink tudnak. Na de mihez is férsz hozzá ezen az oldalon: Elmeséljük neked a teremtés történetét. Meg hallgathatod a 10 parancsolatot. Meg tanulhatod hogy a Windows miért rossz. Meg ismerheted a mi istenünk életetét hogy a 7 hét napjában mit csinál. Meg tekintheted az Ervin Galleryt(TM) Játszhatsz A mi Istenünk Játékával és végül de nem utolsó sorban megtanulhatod a miatyánkat (ervin`s version) Na de mihez is férsz hozzá ha támogatsz minket: ez titok hiszen ahoz hogy ezt meg tudd támogatnod kell minket :)', 'Mi atyánk a linux istene szenteltessék meg az ubuntut jöjjön el a distro-d és legyen meg a te akaratod amint az órán úgy a gépen is. Mindennapi fejezetvizsgánkat add meg nékünk ma és bocsásd meg a windows-t miképpen mi is megbocsáltunk a microsoftnak, és ne kényszeríts minket az egyesekre, mert tiéd a laptop, a root jog és az utolsó szó mindörökké ámen');""")
    con.commit()
    return redirect(url_for("edit_teremtes"))