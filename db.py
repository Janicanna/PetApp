import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    con = get_connection()
    try:
        result = con.execute(sql, params)  # 🔄 Tämä rivi suorittaa SQL-kyselyn
        con.commit()
    except sqlite3.OperationalError as e:
        print("SQLite OperationalError:", e)
    finally:
        con.close() 

def last_insert_id():
    return getattr(g, "last_insert_id", None)    
    
def query(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    con.close()
    return result

def get_animal_types():
    con = get_connection()
    animals = con.execute('SELECT * FROM animals ORDER BY name ASC').fetchall()
    con.close()
    return animals

def get_breeds_by_animal(animal_id):
    con = get_connection()
    breeds = con.execute(
        'SELECT * FROM breeds WHERE animal_id = ? ORDER BY breed_name ASC', (animal_id,)
    ).fetchall()
    con.close()
    return breeds

def save_image(pet_id, filename):
    sql = "INSERT INTO images (pet_id, filename) VALUES (?, ?)"
    execute(sql, [pet_id, filename])

def get_images_for_pet(pet_id):
    sql = "SELECT id, filename FROM images WHERE pet_id = ?"
    return query(sql, [pet_id])


