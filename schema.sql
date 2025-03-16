CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE animals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE breeds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER,
    breed_name TEXT NOT NULL,
    FOREIGN KEY (animal_id) REFERENCES animals(id)
);

CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    animal_id INTEGER NOT NULL,
    breed_id INTEGER NOT NULL,
    pet_name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (breed_id) REFERENCES breeds(id)
);
