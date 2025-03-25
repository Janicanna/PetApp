CREATE TABLE IF NOT EXISTS animal_actions (
    animal_id INTEGER,
    action_name TEXT,
    FOREIGN KEY (animal_id) REFERENCES animals(id)
);

INSERT INTO animal_actions (animal_id, action_name) VALUES
-- Koira (id = 1)
(1, 'ruokailu'), (1, 'ulkoilu'), (1, 'kakat'), (1, 'koulutus'),

-- Kissa (id = 2)
(2, 'ruokailu'), (2, 'ulkoilu'), (2, 'koulutus'),

-- Kala (id = 3)
(3, 'ruokailu'),

-- Jyrsijä (id = 4)
(4, 'ruokailu'), (4, 'koulutus'),

-- Kani (id = 5)
(5, 'ruokailu'), (5, 'ulkoilu');
