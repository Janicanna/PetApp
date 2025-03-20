import sqlite3
from flask import Flask, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    pets = []  # Oletusarvo: jos käyttäjä ei ole kirjautunut sisään, ei näytetä lemmikkejä

    if "username" in session:
        username = session["username"]
        user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

        if user_query:
            user_id = user_query[0][0]

            # Haetaan kirjautuneen käyttäjän lemmikit
            pets = db.query("""
                SELECT p.id, p.pet_name, b.breed_name, p.description
                FROM pets p
                JOIN breeds b ON p.breed_id = b.id
                WHERE p.user_id = ?
                ORDER BY p.pet_name
            """, [user_id])

    return render_template("index.html", pets=pets)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/new_pet", methods=["GET", "POST"])
def new_pet():
    # Jos avataan sivu GET-metodilla, näytetään eläinlajit
    if request.method == "GET":
        animal_types = db.get_animal_types()
        return render_template("new_pet.html", animal_types=animal_types)

    # POST-pyyntö → Käyttäjä valinnut eläimen lajin
    animal_id = request.form.get("animal_id")

    # Jos lajia ei valittu, palataan samaan sivuun
    if not animal_id:
        animal_types = db.get_animal_types()
        return render_template("new_pet.html", animal_types=animal_types)

    # Haetaan valitun eläimen rodut ja näytetään toinen lomake
    breeds = db.get_breeds_by_animal(animal_id)
    animal_types = db.get_animal_types()
    return render_template("new_pet.html",
                           animal_types=animal_types,
                           breeds=breeds,
                           selected_animal_id=animal_id)

@app.route("/save_pet", methods=["POST"])
def save_pet():
    if "username" not in session:
        return redirect("/login")

    # Haetaan kirjautuneen käyttäjän ID
    username = session["username"]
    user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

    if not user_query:
        return "Virhe: Käyttäjää ei löytynyt"

    user_id = user_query[0][0]  # Tallennetaan käyttäjän ID

    # Haetaan lomakkeesta tiedot
    animal_id = request.form.get("animal_id")
    breed_id = request.form.get("breed_id")
    pet_name = request.form.get("title")
    description = request.form.get("description")

    if not animal_id or not breed_id or not pet_name:
        return "VIRHE: Kaikki kentät (laji, rotu, nimi) eivät ole täytettyjä"

    # Tallennetaan tietokantaan ja lisätään `user_id`
    sql = """INSERT INTO pets (user_id, animal_id, breed_id, pet_name, description)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, animal_id, breed_id, pet_name, description])

    # Palataan etusivulle
    return redirect("/")

@app.route("/pet/<int:pet_id>/edit", methods=["GET"])
def edit_pet(pet_id):
    if "username" not in session:
        return redirect("/login")  # Varmistetaan, että käyttäjä on kirjautunut

    username = session["username"]
    user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

    if not user_query:
        return "Virhe: Käyttäjää ei löytynyt"

    user_id = user_query[0][0]

    # Tarkistetaan, onko lemmikki tämän käyttäjän omistuksessa
    pet_query = db.query("SELECT * FROM pets WHERE id = ? AND user_id = ?", [pet_id, user_id])

    if not pet_query:
        return "Virhe: Sinulla ei ole oikeuksia muokata tätä lemmikkiä."

    pet = pet_query[0]
    return render_template("edit_pet.html", pet=pet)

@app.route("/pet/<int:pet_id>/update", methods=["POST"])
def update_pet(pet_id):
    if "username" not in session:
        return redirect("/login")  # Varmistetaan, että käyttäjä on kirjautunut

    username = session["username"]
    user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

    if not user_query:
        return "Virhe: Käyttäjää ei löytynyt"

    user_id = user_query[0][0]

    # Varmistetaan, että käyttäjä omistaa lemmikin
    pet_query = db.query("SELECT * FROM pets WHERE id = ? AND user_id = ?", [pet_id, user_id])

    if not pet_query:
        return "Virhe: Sinulla ei ole oikeuksia muokata tätä lemmikkiä."

    # Haetaan lomakkeen tiedot
    new_name = request.form.get("pet_name")
    new_description = request.form.get("description")

    if not new_name:
        return "Virhe: Lemmikin nimi ei voi olla tyhjä."

    # Päivitetään tietokantaan
    db.execute("UPDATE pets SET pet_name = ?, description = ? WHERE id = ?", [new_name, new_description, pet_id])

    return redirect(f"/pet/{pet_id}")  # Ohjataan takaisin lemmikin tarkastelusivulle

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return render_template("register.html", error="VIRHE: Salasanat eivät ole samat")

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("register.html", error="VIRHE: Tunnus on jo varattu")

    #  Kirjataan käyttäjä automaattisesti sisään
    session["username"] = username

    #  Ohjataan käyttäjä etusivulle
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

     # Tarkistetaan, löytyykö käyttäjä tietokannasta
    sql = "SELECT password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    # Jos käyttäjää ei löydy, näytetään virheilmoitus
    if not result:
        return render_template("login.html", error="VIRHE: Käyttäjätunnus tai salasana on väärin.")

    password_hash = result[0][0]

    # Jos salasana on väärin, näytetään virheilmoitus
    if not check_password_hash(password_hash, password):
        return render_template("login.html", error="VIRHE: Käyttäjätunnus tai salasana on väärin.")

    # Jos käyttäjätunnus ja salasana ovat oikein, kirjaudutaan sisään
    session["username"] = username
    return redirect("/")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/pet/<int:pet_id>")
def show_pet(pet_id):
    # # Haetaan yksittäisen lemmikin tiedot
    sql_pet = """
        SELECT p.id, p.pet_name, p.description,
               b.breed_name, a.name AS animal_name
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
        JOIN animals a ON p.animal_id = a.id
        WHERE p.id=?
    """
    pet_info = db.query(sql_pet, [pet_id])
    if not pet_info:
        return "Virhe: Lemmikkiä ei löytynyt"
    pet_info = pet_info[0]

    # # Haetaan tämän päivän merkinnät (ruokailu, ulkoilu, kakat, pissat, koulutus)
    sql_logs = """
      SELECT action_name, COUNT(*) AS cnt, MAX(timestamp) AS latest_time
      FROM pet_logs
      WHERE pet_id=? AND DATE(timestamp) = DATE('now')
      GROUP BY action_name
    """
    logs = db.query(sql_logs, [pet_id])

    # # Kerätään (action_name → lukumäärä) sanakirjaan
    daily_counts = {}
    for row in logs:
        daily_counts[row["action_name"]] = {
            "cnt": row["cnt"],
            "latest": row["latest_time"][11:16] if row["latest_time"] else "–"
        }

    # # Palautetaan pet.html, jossa näytetään lemmikin tiedot ja päivittäiset merkinnät
    return render_template("pet.html", pet=pet_info, daily_counts=daily_counts)

@app.route("/pet/<int:pet_id>/action", methods=["POST"])
def add_pet_action(pet_id):
    # # Lisätään pet_logs-tauluun rivi action_name = (ruokailu tms.)
    action_name = request.form.get("action_name")
    # Haetaan nykyinen Helsingin aika (UTC+2 talvella, UTC+3 kesällä)
    helsinki_time = datetime.now(timezone.utc) + timedelta(hours=2)

    # Muodostetaan aikaleima muodossa "YYYY-MM-DD HH:MM:SS"
    formatted_time = helsinki_time.strftime("%Y-%m-%d %H:%M:%S")

    # Tallennetaan tietokantaan Suomen ajan mukaisena
    sql_insert = "INSERT INTO pet_logs (pet_id, action_name, timestamp) VALUES (?, ?, ?)"
    db.execute(sql_insert, [pet_id, action_name, formatted_time])

    # # Ohjataan takaisin lemmikin sivulle
    return redirect(f"/pet/{pet_id}")

@app.route("/confirm_delete_pet/<int:pet_id>")
def confirm_delete_pet(pet_id):
    # Haetaan lemmikin tiedot, jotta ne voidaan näyttää vahvistussivulla
    pet_query = db.query("SELECT id, pet_name FROM pets WHERE id = ?", [pet_id])

    if not pet_query:
        return "Virhe: Lemmikkiä ei löytynyt."

    pet = pet_query[0]
    return render_template("confirm_delete_pet.html", pet=pet)

@app.route("/delete_pet/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    if "username" not in session:
        return redirect("/login")  # Varmistetaan, että käyttäjä on kirjautunut

    username = session["username"]
    user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

    if not user_query:
        return "Virhe: Käyttäjää ei löytynyt."

    user_id = user_query[0][0]

    # Tarkistetaan, onko käyttäjä lemmikin omistaja
    pet_query = db.query("SELECT id FROM pets WHERE id = ? AND user_id = ?", [pet_id, user_id])

    if not pet_query:
        return "Virhe: Sinulla ei ole oikeuksia poistaa tätä lemmikkiä."

    # Poistetaan ensin lemmikin päiväkirjamerkinnät, jotta tietokanta ei anna virhettä
    db.execute("DELETE FROM pet_logs WHERE pet_id=?", [pet_id])

    # Poistetaan varsinainen lemmikki
    db.execute("DELETE FROM pets WHERE id=?", [pet_id])

    # Ohjataan etusivulle poiston jälkeen
    return redirect("/")



