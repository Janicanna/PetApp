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
    user_id INTEGER NOT NULL,
    animal_id INTEGER NOT NULL,
    breed_id INTEGER NOT NULL,
    pet_name TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (animal_id) REFERENCES animals(id),
    FOREIGN KEY (breed_id) REFERENCES breeds(id)
);

CREATE TABLE pet_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    action_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pet_id) REFERENCES pets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);


