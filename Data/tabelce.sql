-- Active: 1713445777319@@baza.fmf.uni-lj.si@5432@sem2024_zivak@public

CREATE TABLE uporabniki (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    geslo TEXT NOT NULL,
    datum_registracije TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sektorji (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(255) UNIQUE NOT NULL,
    pokrajina VARCHAR(100) NOT NULL CHECK (pokrajina IN (
        'Gorenjska', 'Štajerska', 'Prekmurje', 'Koroška', 'Notranjska', 'Primorska', 'Dolenjska'
    )),
    lat DECIMAL(9,6) NOT NULL,
    lng DECIMAL(9,6) NOT NULL,
    opis TEXT
);

CREATE TABLE bolderji (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(255) NOT NULL,
    lat DECIMAL(9,6) NOT NULL,
    lng DECIMAL(9,6) NOT NULL,
    opis TEXT NOT NULL,
    sektor_id INT REFERENCES sektorji(id) ON DELETE CASCADE NOT NULL,
    datum_dodajanja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parkirisca (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(255) NOT NULL,
    lat DECIMAL(9,6) NOT NULL,
    lng DECIMAL(9,6) NOT NULL,
    opis TEXT
);

CREATE TABLE smeri (
    id SERIAL PRIMARY KEY,
    ime VARCHAR(50) NOT NULL,
    tezavnost VARCHAR(5) NOT NULL CHECK (tezavnost IN (
        '3', '4a', '4b', '4c', '5a', '5b', '5c', 
        '6a', '6a+', '6b', '6b+', '6c', '6c+',
        '7a', '7a+', '7b', '7b+', '7c', '7c+',
        '8a', '8a+', '8b', '8b+', '8c', '8c+', '9a', '9a+'
    )),
    opis TEXT NOT NULL,
    bolder_id INT REFERENCES bolderji(id)
)


CREATE TABLE bolder_parkirisce (
    bolder_id INT REFERENCES Bolderji(id) ON DELETE CASCADE,
    parkirisce_id INT REFERENCES Parkirisca(id) ON DELETE CASCADE,
    PRIMARY KEY (bolder_id, parkirisce_id)
);

CREATE TABLE sektor_parkirisce (
    sektor_id INT REFERENCES sektorji(id) ON DELETE CASCADE,
    parkirisce_id INT REFERENCES parkirisca(id) ON DELETE CASCADE,
    PRIMARY KEY (sektor_id, parkirisce_id)
);

SELECT 
    b.ime AS bolder_ime,
    p.ime AS parkirisce_ime
FROM Bolder_Parkirisce bp
JOIN Bolderji b ON bp.bolder_id = b.id
JOIN Parkirisca p ON bp.parkirisce_id = p.id;

SELECT 
    s.ime AS sektor_ime,
    p.ime AS parkirisce_ime
FROM sektor_parkirisce sp
JOIN sektorji s ON sp.sektor_id = s.id
JOIN parkirisca p ON sp.parkirisce_id = p.id;



##################################################################

DROP TABLE uporabniki

DROP TABLE bolder_parkirisce

DROP VIEW bolderji_z_imeni_sektorjev

DROP VIEW smeri_z_imeni_bolderjev

DROP TABLE sektor_Parkirisce 

DROP TABLE parkirisca

DROP TABLE smeri

DROP TABLE bolderji

DROP TABLE sektorji


##################################################################

# PRIMERI

INSERT INTO bolderji (ime, lat, lng, opis, sektor_id) 
VALUES ('Plezalni Raj', 46.0511, 14.5051, 'Odličen balvan z več težavnostmi', 1);

INSERT INTO bolderji (ime, lat, lng, opis, sektor_id) 
VALUES ('Tricky Boulder', 46.0511, 14.5051, 'Zelo tehničen problem', 3);
INSERT INTO bolderji (ime, lat, lng, opis, sektor_id) 
VALUES ('Moj Prvi Boulder', 46.0532, 14.5085, 'Kratek, a težek problem', 1);

CREATE VIEW bolderji_z_imeni_sektorjev AS
SELECT 
    bolderji.id AS bolder_id,
    bolderji.ime AS ime_bolderja,
    bolderji.lat,
    bolderji.lng,
    bolderji.opis,
    sektorji.ime AS ime_sektorja
FROM bolderji
JOIN sektorji ON bolderji.sektor_id = sektorji.id;

INSERT INTO Parkirisca (ime, lat, lng, opis) 
VALUES ('Parkirišče pri gozdu', 46.0520, 14.5040, 'Prostor za max 3 avtomobile'),
       ('Veliko parkirišče', 46.0505, 14.5060, 'Prostora kolikor želiš');

INSERT INTO Bolder_Parkirisce (bolder_id, parkirisce_id) 
VALUES (1, 1), (1, 2);
SELECT p.ime, p.lat, p.lng
FROM Parkirisca p
JOIN Bolder_Parkirisce bp ON p.id = bp.parkirisce_id
WHERE bp.bolder_id = 1;

INSERT INTO sektorji (ime, pokrajina, lat, lng, opis) 
VALUES ('Sektor A', 'Gorenjska', 46.0525, 14.5075, 'Sončna stena z veliko oprimki');
INSERT INTO Sektorji (ime, pokrajina, lat, lng, opis) 
VALUES ('Sektor B', 'Primorska', 46.0530, 14.5080, 'Senca cel dan');

INSERT INTO Sektorji (ime, pokrajina, lat, lng, opis) 
VALUES ('Jedina', 'Primorska', 46.5439, 14.1987, 'Ta sektor mora bit unik');

INSERT INTO sektor_parkirisce (sektor_id, parkirisce_id) 
VALUES (1, 1), (1, 2);

SELECT p.ime, p.lat, p.lng
FROM parkirisca p
JOIN sektor_Parkirisce sp ON p.id = sp.parkirisce_id
WHERE sp.sektor_id = 1;

INSERT INTO smeri (ime, tezavnost, opis, bolder_id)
VALUES ('Pikapolonica', '4a', 'Išči šalce', 1)

CREATE VIEW smeri_z_imeni_bolderjev AS
SELECT 
    smeri.id AS smer_id,
    smeri.ime AS ime_smeri,
    smeri.tezavnost,
    smeri.opis,
    bolderji.ime AS ime_bolderja
FROM smeri
JOIN bolderji ON smeri.bolder_id = bolderji.id;



