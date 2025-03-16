import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    pets = db.query("""
        SELECT p.pet_name, b.breed_name, p.description
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
    """)
    return render_template("index.html", pets=pets)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/new_item") #uusi julkaisu
def new_item():
    return render_template("new_item.html")

@app.route("/new_pet", methods=["GET", "POST"])
def new_pet():
    if request.method == "GET":
        # 1) Käyttäjä avaa sivun -> Näytetään valittavissa olevat eläinlajit
        animal_types = db.get_animal_types()  # = animals-taulun rivit
        return render_template("new_pet.html", animal_types=animal_types)

    # 2) POST-pyyntö = käyttäjä on valinnut jonkun lajin
    animal_id = request.form.get("animal_id")

    # Jos lajia ei valittu, palataan sivulle
    if not animal_id:
        animal_types = db.get_animal_types()
        return render_template("new_pet.html", animal_types=animal_types)

    # Haetaan rodut valitulle lajille
    breeds = db.get_breeds_by_animal(animal_id)
    animal_types = db.get_animal_types()

    # Näytetään new_pet.html, jossa "breeds" on annettu -> ladataan toinen lomake
    return render_template(
        "new_pet.html",
        animal_types=animal_types,
        breeds=breeds,
        selected_animal_id=animal_id
    )

@app.route("/save_pet", methods=["POST"])
def save_pet():
    # Käyttäjä lähetti lopulliset tiedot
    animal_id = request.form.get("animal_id")
    breed_id = request.form.get("breed_id")
    pet_name = request.form.get("title")
    description = request.form.get("description")

    # Varmistetaan, että kaikki tarvittava on annettu
    if not animal_id or not breed_id or not pet_name:
        return "VIRHE: Kaikki kentät (laji, rotu, nimi) eivät ole täytettyjä"

    # Tallennetaan tietokantaan
    sql = """INSERT INTO pets (animal_id, breed_id, pet_name, description)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [animal_id, breed_id, pet_name, description])

    # Palataan etusivulle
    return redirect("/")


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

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
        
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
    sql = "SELECT password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])[0][0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        return redirect("/")
    else:
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")