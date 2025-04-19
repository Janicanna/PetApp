-- Lisää eläintyypit
INSERT INTO animals (name) VALUES 
('Koira'), 
('Kissa'), 
('Kala'), 
('Jyrsijät'), 
('Kanit'),
('Matelijat'),
('Ötökät');

INSERT INTO breeds (animal_id, breed_name) VALUES 
-- Koirarodut (animal_id = 1)
(1, 'Sekarotuinen'), (1, 'Kultainennoutaja'), (1, 'Dalmatialainen'),
(1, 'Labradorinnoutaja'), (1, 'Saksanpaimenkoira'), (1, 'Rottweiler'),
(1, 'Bulldoggi'), (1, 'Mopsi'), (1, 'Beagle'), (1, 'Bordercollie'), 
(1, 'Siperianhusky'), (1, 'Seiskarinkoira'), (1, 'Landseer'), 
(1, 'Lagotto Romagnolo'), (1, 'Kleinspitz'), (1, 'Karjalankarhukoira'), 
(1, 'Jackrussellinterrieri'), (1, 'Hokkaido'), (1, 'Irlanninsusikoira'),
(1, 'Italianvinttikoira'), (1, 'Eurasier'), (1, 'Dobermanni'), 
(1, 'Chow Chow'), (1, 'Cairnterrieri'), (1, 'Cockerspanieli'), 
(1, 'Collie, pitkäkarvainen'), (1, 'Collie, sileäkarvainen'), 
(1, 'Bullmastiffi'), (1, 'Bichon Frisé'), (1, 'Basenji'), (1, 'Akita'), 
(1, 'Bernhardinkoira'), (1, 'Chihuahua'), (1, 'Espanjanvesikoira'), 
(1, 'Kiinanharjakoira'), (1, 'Lapinporokoira'), (1, 'Mittelspitz'), 
(1, 'Novascotiannoutaja'), (1, 'Parsonrussellinterrieri'), 
(1, 'Pomeranian'), (1, 'Shar Pei'), (1, 'Shiba'), (1, 'Shih Tzu'), 
(1, 'Snautseri'), (1, 'Suomenlapinkoira'), (1, 'Suomenpystykorva'), 
(1, 'Venäjäntoy'), (1, 'Whippet'),

-- Kissarodut (animal_id = 2)
(2, 'Maine Coon'), (2, 'Siamilainen'), (2, 'Persialainen'),
(2, 'Ragdoll'), (2, 'Bengali'), (2, 'Norjalainen metsäkissa'),
(2, 'Scottish Fold'), (2, 'Sfinksikissa'), (2, 'Brittiläinen lyhytkarva'),
(2, 'Venäjänsininen'), (2, 'Abyssinialainen'), (2, 'Burma'), 
(2, 'Cornish Rex'), (2, 'Devon Rex'), (2, 'Egyptin Mau'), 
(2, 'Himalajan kissa'), (2, 'Japanin Bobtail'), (2, 'Korati'), 
(2, 'Manx'), (2, 'Ocicat'), (2, 'Savannah'), (2, 'Selkirk Rex'), 
(2, 'Singapura'), (2, 'Snowshoe'), (2, 'Somali'), (2, 'Sokoke'), 
(2, 'Tonkineesi'), (2, 'Turkkilainen Angora'), (2, 'Turkkilainen Van'), 
(2, 'LaPerm'), (2, 'Cymric'), (2, 'Balinese'), (2, 'Chartreux'), 
(2, 'Korat'), (2, 'Munchkin'), (2, 'Peterbald'), (2, 'Oriental'), 
(2, 'Toyger'), (2, 'Cheetoh'), (2, 'Ojos Azules'), (2, 'Serengeti'), 
(2, 'American Curl'), (2, 'European Shorthair'), (2, 'Exotic Shorthair'),

-- Kalarodut (animal_id = 3)
(3, 'Kultakala'), (3, 'Betta'), (3, 'Neontetra'),
(3, 'Guppy'), (3, 'Kardinaalikala'), (3, 'Pleko'),
(3, 'Lehtikala'), (3, 'Miekkapyrstö'), (3, 'Kirjosampi'), (3, 'Discus'),

-- Jyrsijät (animal_id = 4)
(4, 'Hamsteri'), (4, 'Marsut'), (4, 'Chinchilla'),
(4, 'Rotta'), (4, 'Gerbiili'), (4, 'Degut'),
(4, 'Orava'), (4, 'Hiiri'), (4, 'Fretit'), (4, 'Sugarglider'),

-- Kanit (animal_id = 5)
(5, 'Leijonanharjas'), (5, 'Kääpiöluppa'), (5, 'Belgianjätti'),
(5, 'Hermeliini'), (5, 'Rex'),

-- Matelijat (animal_id = 6)
(6, 'Kuningaspyton'), (6, 'Boa'), (6, 'Gekko'), (6, 'Iguana'),
(6, 'Vesikilpikonna'), (6, 'Maanikilpikonna'), (6, 'Anolis'),

-- Ötökät (animal_id = 7)
(7, 'Hämähäkki'), (7, 'Skorpioni'), (7, 'Torakka'), (7, 'Tuhatjalkainen'),
(7, 'Heinäsirkka'), (7, 'Leppäkerttu');
