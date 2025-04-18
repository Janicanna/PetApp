import sqlite3
from flask import Flask, redirect, render_template, request, session, abort
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import pets
from datetime import datetime, timezone, timedelta
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = config.secret_key

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.context_processor
def inject_user_id():
    user_id = None
    if "username" in session:
        result = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
        if result:
            user_id = result[0][0]
    return dict(session_user_id=user_id)

# Etusivu, näyttää kirjautuneen käyttäjän lemmikit
@app.route("/")
def index():
    if "username" in session:
        user_pets = pets.get_user_pets()
        all_pets = db.query("""
            SELECT p.id, p.pet_name, b.breed_name, a.name AS animal_name, p.user_id, u.username AS owner_username
            FROM pets p
            JOIN breeds b ON p.breed_id = b.id
            JOIN animals a ON p.animal_id = a.id
            JOIN users u ON p.user_id = u.id
            ORDER BY a.name, p.pet_name
        """)
        grouped_pets = {}
        for pet in all_pets:
            animal = pet["animal_name"]
            grouped_pets.setdefault(animal, []).append(pet)
        # Voit välittää omat lemmikkisi muuttujana "pets" jos haluat:
        return render_template("index.html", pets=user_pets, grouped_pets=grouped_pets)
    else:
        return render_template("index.html", pets=None, grouped_pets=None)

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
        return render_template("register.html", error="VIRHE: Salasanat eivät ole samat", username=username)

    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return render_template("register.html", error="VIRHE: Tunnus on jo varattu", username=username)

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
        # Palautetaan käyttäjänimi takaisin, jos virhe
        return render_template("login.html", error="VIRHE: Käyttäjätunnus tai salasana on väärin.", username=username)
    
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

    # Haetaan ja siistitään lomakkeen tiedot
    animal_id = request.form.get("animal_id", "").strip()
    breed_id = request.form.get("breed_id", "").strip()
    pet_name = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()

    if not animal_id or not breed_id or not pet_name:
        return "Virhe: Kaikki kentät on täytettävä."

    if len(pet_name) > 50 or len(description) > 400:
        abort(403)

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
    session_user_id = None

    if username:
        user_id_result = db.query("SELECT id FROM users WHERE username = ?", [username])
        if user_id_result:
            session_user_id = user_id_result[0][0]
            owner_check = db.query("SELECT id FROM pets WHERE id = ? AND user_id = ?", [pet_id, session_user_id])
            is_owner = bool(owner_check)

    # 2. Haetaan päivän lokitiedot (määrät + viimeisin aika)
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

    # 4. Haetaan kommentit
    comments = pets.get_comments_for_pet(pet_id)

    # 5. Haetaan kuvat
    images = pets.get_images_for_pet(pet_id)

    return render_template("pet.html",
                        pet=pet_info,
                        is_owner=is_owner,
                        session_user_id=session_user_id,
                        daily_counts=daily_counts,
                        allowed_actions=allowed_actions,
                        comments=comments,
                        images=images)


# Lemmikin muokkaaminen
@app.route("/pet/<int:pet_id>/edit", methods=["GET", "POST"])
def edit_pet(pet_id):
    if "username" not in session:
        return redirect("/login")

    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]
    if pet["user_id"] != user_id:
        abort(403)

    animal_types = db.get_animal_types()
    selected_animal_id = request.form.get("animal_id") or pet["animal_id"]
    breeds = db.get_breeds_by_animal(selected_animal_id)
    selected_breed_id = request.form.get("breed_id") or pet["breed_id"]

    return render_template("edit_pet.html", pet=pet,
                           animal_types=animal_types,
                           selected_animal_id=int(selected_animal_id),
                           selected_breed_id=int(selected_breed_id),
                           breeds=breeds)

@app.route("/pet/<int:pet_id>/update", methods=["POST"])
def update_pet(pet_id):
    if "username" not in session:
        return redirect("/login")

    username = session["username"]
    user_id = db.query("SELECT id FROM users WHERE username = ?", [username])[0][0]

    pet = pets.get_pet_by_id(pet_id)
    if not pet or pet["user_id"] != user_id:
        abort(403)

    new_name = request.form.get("pet_name")
    new_description = request.form.get("description")
    new_animal_id = request.form.get("animal_id")
    new_breed_id = request.form.get("breed_id")

    if not all([new_name, new_animal_id, new_breed_id]):
        return "Virhe: Kaikki kentät on täytettävä."

    db.execute("""
        UPDATE pets
        SET pet_name = ?, description = ?, animal_id = ?, breed_id = ?
        WHERE id = ? AND user_id = ?
    """, [new_name, new_description, new_animal_id, new_breed_id, pet_id, user_id])

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

    # Poista kaikki viitteet ennen pääpoistoa
    db.execute("DELETE FROM pet_logs WHERE pet_id = ?", [pet_id])
    db.execute("DELETE FROM comments WHERE pet_id = ?", [pet_id])
    db.execute("DELETE FROM images WHERE pet_id = ?", [pet_id])
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

# Käyttäjän profiili
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    user = db.query("SELECT username FROM users WHERE id = ?", [user_id])
    if not user:
        abort(404)

    username = user[0][0]
    pets_list = db.query("""
        SELECT p.id, p.pet_name, b.breed_name
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
        WHERE p.user_id = ?
        ORDER BY p.pet_name
    """, [user_id])

    return render_template("user_profile.html", username=username, pets=pets_list)

@app.route("/pet/<int:pet_id>/comment", methods=["POST"])
def add_comment(pet_id):
    if "username" not in session:
        return redirect("/login")

    content = request.form.get("comment")
    if not content or len(content.strip()) == 0:
        return "Virhe: Tyhjää kommenttia ei voida lähettää."

    # Hae käyttäjän ID
    user_id_query = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    if not user_id_query:
        abort(403)

    user_id = user_id_query[0][0]

    sql = "INSERT INTO comments (pet_id, user_id, content) VALUES (?, ?, ?)"
    db.execute(sql, [pet_id, user_id, content])

    return redirect(f"/pet/{pet_id}")

@app.route("/comment/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    if "username" not in session:
        return redirect("/login")

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]

    # Haetaan kommentin tiedot
    comment_info = db.query("SELECT pet_id, user_id FROM comments WHERE id = ?", [comment_id])
    if not comment_info:
        abort(404)

    pet_id = comment_info[0]["pet_id"]
    comment_owner_id = comment_info[0]["user_id"]

    pet_info = db.query("SELECT user_id FROM pets WHERE id = ?", [pet_id])
    is_pet_owner = pet_info and pet_info[0]["user_id"] == user_id

    if user_id == comment_owner_id or is_pet_owner:
        db.execute("DELETE FROM comments WHERE id = ?", [comment_id])
    else:
        abort(403)

    return redirect(f"/pet/{pet_id}")

#Kuvan lähetysreitti
@app.route("/pet/<int:pet_id>/upload_image", methods=["POST"])
def upload_image(pet_id):
    if "username" not in session:
        return redirect("/login")

    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)

    user_id = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])[0][0]
    if pet["user_id"] != user_id:
        abort(403)

    file = request.files.get("image")
    if not file or file.filename == "":
        return "Virhe: Tiedosto puuttuu"

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    db.save_image(pet_id, filename)
    return redirect(f"/pet/{pet_id}")

#Poista lisätty kuva
@app.route("/pet/<int:pet_id>/delete_image/<int:image_id>", methods=["POST"])
def delete_image(pet_id, image_id):
    if "username" not in session:
        return redirect("/login")
    
    pet = pets.get_pet_by_id(pet_id)
    if not pet:
        abort(404)
    
    # Hae kirjautuneen käyttäjän ID
    user_id_result = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    if not user_id_result:
        abort(403)
    user_id = user_id_result[0][0]

    if pet["user_id"] != user_id:
        abort(403)
    
    # Tarkista, että kuva kuuluu tähän lemmikkiin
    image = db.query("SELECT id FROM images WHERE id = ? AND pet_id = ?", [image_id, pet_id])
    if not image:
        abort(404)
    
    db.execute("DELETE FROM images WHERE id = ?", [image_id])
    
    return redirect(f"/pet/{pet_id}")

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

