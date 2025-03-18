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
        result = con.execute(sql, params)
        con.commit()
    except sqlite3.OperationalError as e:
        print("SQLite OperationalError:", e)  # Tulostaa virheen, jos tietokanta on lukittu
    finally:
        con.close()  # Sulkee tietokantayhteyden aina

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
