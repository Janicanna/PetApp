import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import pets
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = config.secret_key

# Etusivu, näyttää kirjautuneen käyttäjän lemmikit
@app.route("/")
def index():
    pets_list = pets.get_user_pets() if "username" in session else []
    return render_template("index.html", pets=pets_list)

# Käyttäjän rekisteröinti
@app.route("/register")
def register():
    return render_template("register.html")

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

    session["username"] = username  # Kirjataan käyttäjä sisään automaattisesti
    return redirect("/")

# Käyttäjän kirjautuminen
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])

    if not result or not check_password_hash(result[0][0], password):
        return render_template("login.html", error="VIRHE: Käyttäjätunnus tai salasana on väärin.")

    session["username"] = username
    return redirect("/")

# Uloskirjautuminen
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

# Lemmikin lisääminen
@app.route("/new_pet", methods=["GET", "POST"])
def new_pet():
    if request.method == "GET":
        # Käyttäjä avaa lomakkeen ensimmäisen vaiheen (eläintyypin valinta)
        animal_types = db.get_animal_types()
        return render_template("new_pet.html", animal_types=animal_types)

    # Käyttäjä valitsi eläintyypin
    animal_id = request.form.get("animal_id")

    if not animal_id:
        return "Virhe: Valitse ensin eläimen laji."

    # Haetaan valitulle eläimelle sopivat rodut
    breeds = db.get_breeds_by_animal(animal_id)
    animal_types = db.get_animal_types()

    return render_template("new_pet.html", animal_types=animal_types, breeds=breeds, selected_animal_id=animal_id)

@app.route("/save_pet", methods=["POST"])
def save_pet():
    if "username" not in session:
        return redirect("/login")

    # Haetaan käyttäjän ID
    username = session["username"]
    user_query = db.query("SELECT id FROM users WHERE username = ?", [username])

    if not user_query:
        abort(403)

    user_id = user_query[0][0]

    # Haetaan lomakkeesta tiedot
    animal_id = request.form.get("animal_id")
    breed_id = request.form.get("breed_id")
    pet_name = request.form.get("title")
    description = request.form.get("description")

    if not animal_id or not breed_id or not pet_name:
        return "Virhe: Kaikki kentät on täytettävä."

    # Tallennetaan tietokantaan
    sql = """INSERT INTO pets (user_id, animal_id, breed_id, pet_name, description)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, animal_id, breed_id, pet_name, description])

    return redirect("/")

# Lemmikin tarkastelu
@app.route("/pet/<int:pet_id>")
def show_pet(pet_id):
    pet_info = pets.get_pet_by_id(pet_id)
    if not pet_info:
        abort(404)

    # 1. Selvitetään onko käyttäjä kirjautunut
    username = session.get("username")
    is_owner = False
    if username:
        user_id_result = db.query("SELECT id FROM users WHERE username = ?", [username])
        if user_id_result:
            user_id = user_id_result[0][0]
            owner_check = db.query("SELECT id FROM pets WHERE id = ? AND user_id = ?", [pet_id, user_id])
            is_owner = bool(owner_check)

    # 2. Haetaan päivän lokitiedot
    sql_logs = """
      SELECT action_name, COUNT(*) AS cnt, MAX(timestamp) AS latest_time
      FROM pet_logs
      WHERE pet_id=? AND DATE(timestamp) = DATE('now')
      GROUP BY action_name
    """
    logs = db.query(sql_logs, [pet_id])
    daily_counts = {}
    for row in logs:
        daily_counts[row["action_name"]] = {
            "cnt": row["cnt"],
            "latest": row["latest_time"][11:16] if row["latest_time"] else "–"
        }

    # 3. Haetaan eläimen sallitut toiminnot
    animal_id = pet_info["animal_id"]
    actions_query = db.query("SELECT action_name FROM animal_actions WHERE animal_id = ?", [animal_id])
    allowed_actions = [row["action_name"] for row in actions_query]

    return render_template("pet.html", pet=pet_info, is_owner=is_owner,
                           daily_counts=daily_counts, allowed_actions=allowed_actions)
    
# Lemmikin muokkaaminen
@app.route("/pet/<int:pet_id>/edit", methods=["GET"])
def edit_pet(pet_id):
    if "username" not in session:
        return redirect("/login")

    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]
    if pet["user_id"] != user_id:
        abort(403)

    return render_template("edit_pet.html", pet=pet)

@app.route("/pet/<int:pet_id>/update", methods=["POST"])
def update_pet(pet_id):
    new_name = request.form.get("pet_name")
    new_description = request.form.get("description")

    if not pets.update_pet(pet_id, new_name, new_description):
        abort(403)

    return redirect(f"/pet/{pet_id}")

# Lemmikin poistaminen
@app.route("/delete_pet/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    if "username" not in session:
        return redirect("/login")

    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]
    if pet["user_id"] != user_id:
        abort(403)

    db.execute("DELETE FROM pet_logs WHERE pet_id = ?", [pet_id])
    db.execute("DELETE FROM pets WHERE id = ?", [pet_id])

    return redirect("/")

#Vahvista poisto
@app.route("/confirm_delete_pet/<int:pet_id>")
def confirm_delete_pet(pet_id):
    if "username" not in session:
        return redirect("/login")

    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]
    if pet["user_id"] != user_id:
        abort(403)

    return render_template("confirm_delete_pet.html", pet=pet)

# Lemmikin päivän merkintöjen lisääminen (ruokailu, ulkoilu jne.)
@app.route("/pet/<int:pet_id>/action", methods=["POST"])
def add_pet_action(pet_id):
    action_name = request.form.get("action_name")
    helsinki_time = datetime.now(timezone.utc) + timedelta(hours=2)
    formatted_time = helsinki_time.strftime("%Y-%m-%d %H:%M:%S")

    sql_insert = "INSERT INTO pet_logs (pet_id, action_name, timestamp) VALUES (?, ?, ?)"
    db.execute(sql_insert, [pet_id, action_name, formatted_time])

    return redirect(f"/pet/{pet_id}")

# Lemmikin haku
@app.route("/find_pet")
def find_pet():
    query = request.args.get("query", "")
    if query:
        results = pets.find_pets(query) 
    else:
        results = []                   
    return render_template("find_pet.html", query=query, results=results)


