import db
from flask import session

def get_user_id():
    #Palauttaa kirjautuneen käyttäjän ID:n
    if "username" not in session:
        return None
    user_query = db.query("SELECT id FROM users WHERE username = ?", [session["username"]])
    return user_query[0][0] if user_query else None

def get_user_pets():
    #Palauttaa kirjautuneen käyttäjän lemmikit
    user_id = get_user_id()
    if not user_id:
        return []
    return db.query("""
        SELECT p.id, p.pet_name, b.breed_name, p.description
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
        WHERE p.user_id = ?
        ORDER BY p.pet_name
    """, [user_id])

def get_pet_by_id(pet_id):
    # Palauttaa yksittäisen lemmikin tiedot, mukaan lukien user_id
    pet = db.query("""
        SELECT p.id, p.pet_name, p.description, p.animal_id,
               b.breed_name, a.name AS animal_name,
               p.user_id, u.username AS owner_username
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
        JOIN animals a ON p.animal_id = a.id
        JOIN users u ON p.user_id = u.id
        WHERE p.id=?
    """, [pet_id])
    return pet[0] if pet else None

def save_pet(animal_id, breed_id, pet_name, description):
    #Tallentaa uuden lemmikin tietokantaan
    user_id = get_user_id()
    if not user_id:
        return False
    sql = """INSERT INTO pets (user_id, animal_id, breed_id, pet_name, description)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, animal_id, breed_id, pet_name, description])
    return True

def update_pet(pet_id, pet_name, description):
    #Päivittää olemassa olevan lemmikin tiedot
    user_id = get_user_id()
    if not user_id:
        return False
    db.execute("UPDATE pets SET pet_name = ?, description = ? WHERE id = ? AND user_id = ?", 
               [pet_name, description, pet_id, user_id])
    return True

def delete_pet(pet_id):
    #Poistaa lemmikin ja sen merkinnät
    user_id = get_user_id()
    if not user_id:
        return False
    db.execute("DELETE FROM pet_logs WHERE pet_id=?", [pet_id])
    db.execute("DELETE FROM pets WHERE id=? AND user_id=?", [pet_id, user_id])
    return True

def find_pets(query):
    like_term = f"%{query}%"
    sql = """
        SELECT p.id, p.pet_name, b.breed_name
        FROM pets p
        JOIN breeds b ON p.breed_id = b.id
        JOIN animals a ON p.animal_id = a.id
        WHERE p.pet_name LIKE ?
           OR b.breed_name LIKE ?
           OR a.name LIKE ?
           OR p.description LIKE ?
    """
    return db.query(sql, [like_term, like_term, like_term, like_term])

def get_allowed_actions(animal_id):
    sql = "SELECT action_name FROM animal_actions WHERE animal_id = ?"
    result = db.query(sql, [animal_id])
    return [row["action_name"] for row in result]
