import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import Data.auth_public as auth
import datetime
import os

from Data.models import Uporabniki, Parkirisca, Sektorji, Bolderji, Smeri
from typing import List

# Preberemo port za bazo iz okoljskih spremenljivk
DB_PORT = os.environ.get('POSTGRES_PORT', 5432)

## V tej datoteki bomo implementirali razred Repo, ki bo vseboval metode za delo z bazo.

class Repo:
    def __init__(self):
        # Ko ustvarimo novo instanco definiramo objekt za povezavo in cursor
        self.conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password, port=DB_PORT)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def dobi_uporabnike(self) -> List[Uporabniki]:
        self.cur.execute("""
            SELECT * FROM Uporabniki
            Order by datum_reg desc
        """)
        uporabniki = [Uporabniki.from_dict(u) for u in self.cur.fetchall()]
        return uporabniki

    def dobi_bolderje(self) -> List[Bolderji]:
        self.cur.execute("""
            SELECT * FROM Bolderji
            Order by id         
        """)
        bolderji = [Bolderji.from_dict(b) for b in self.cur.fetchall()]
        return bolderji
    
    def dobi_bolderje_sektor(self, sektor:str) -> List[Bolderji]:
        self.cur.execute("""
            SELECT b.* FROM bolderji b
            JOIN sektorji s ON b.sektor_id = s.id
            WHERE s.ime = %s;
             """, (sektor,))
        s_bolderji = [Bolderji.from_dict(b) for b in self.cur.fetchall()]
        return s_bolderji
        
    
    def dobi_sektorje(self) -> List[Sektorji]:
        self.cur.execute("""
            SELECT * FROM Sektorji
            Order by id         
        """)
        sektorji = [Sektorji.from_dict(s) for s in self.cur.fetchall()]
        return sektorji
    
    def dobi_sektorje_pokrajina(self, pokrajina:str) -> List[Sektorji]:
        self.cur.execute("""
            SELECT * FROM Sektorji
            WHERE pokrajina = %s
             """, (pokrajina,))
        p_sektorji = [Sektorji.from_dict(s) for s in self.cur.fetchall()]
        return p_sektorji

    def dobi_parkirisca(self) -> List[Parkirisca]:
        self.cur.execute("""
            SELECT * FROM Parkirisca
            Order by id         
        """)
        parkirisca = [Parkirisca.from_dict(p) for p in self.cur.fetchall()]
        return parkirisca
    
    def dobi_parkirisca_sektor(self, sektor:str) -> List[Parkirisca]:
        self.cur.execute("""
            SELECT p.* FROM parkirisca p
            JOIN sektorji s ON p.sektor_id = s.id
            WHERE s.ime = %s;
             """, (sektor,))
        s_parkirisca = [Parkirisca.from_dict(p) for p in self.cur.fetchall()]
        return s_parkirisca
    
    def dobi_smeri(self) -> List[Smeri]:
        self.cur.execute("""
            SELECT * FROM Smeri
            Order by id         
        """)
        smeri = [Smeri.from_dict(s) for s in self.cur.fetchall()]
        return smeri
    
    def dobi_smeri_bolder(self, bolder:str) -> List[Smeri]:
        self.cur.execute("""
            SELECT s.* FROM smeri s
            JOIN bolderji b ON s.bolder_id = b.id
            WHERE b.ime = %s;
             """, (bolder,))
        return self.cur.fetchall()
    

    def dobi_uporabnika(self, email:str) -> Uporabniki:
        self.cur.execute("""
            SELECT id, ime, email, geslo, datum_registracije
            FROM Uporabniki
            WHERE email = %s
             """, (email,))
        
        b = Uporabniki.from_dict(self.cur.fetchone())
        print('repo uporabnik', b)
        return b

    def dobi_bolder(self, ime:str) -> Bolderji:
        self.cur.execute("""
            SELECT id, ime, lat, lng, opis, sektor, parkirisce, datum_dod
            FROM Bolderji
            WHERE ime = %s
             """, (ime,))
        b = Bolderji.from_dict(self.cur.fetchone())
        return b
        
    def dobi_sektor(self, ime:str) -> Sektorji:
        self.cur.execute("""
            SELECT id, ime, lat, lng, opis, parkirisce
            FROM Sektorji
            WHERE ime = %s
             """, (ime,))
        s = Sektorji.from_dict(self.cur.fetchone())
        return s
    
    def dobi_parkirisce(self, ime:str) -> Parkirisca:
        self.cur.execute("""
            SELECT id, ime, lat, lng, opis
            FROM Parkirisca
            WHERE ime = %s
             """, (ime,))
        p = Parkirisca.from_dict(self.cur.fetchone())
        return p
    
    def dobi_smer(self, ime:str) -> Smeri:
        self.cur.execute("""
            SELECT id, ime, tezavnost, opis, bolder
            FROM Smeri
            WHERE ime = %s
             """, (ime,))
        s = Smeri.from_dict(self.cur.fetchone())
        return s
    
    def dodaj_uporabnika(self, uporabnik: Uporabniki):
        self.cur.execute("""
            INSERT into uporabniki(ime, email, geslo, datum_registracije)
            VALUES (%s, %s, %s, %s)
            """, (uporabnik.ime, uporabnik.email, uporabnik.geslo, uporabnik.datum_reg))
        self.conn.commit()
    
    
    def dodaj_sektor(self, sektor: Sektorji):
        self.cur.execute("""
            INSERT into sektor(ime, lat, lng, opis, parkirisce_id)
            VALUES (%s, %s, %s, %s, %s)
            """, (sektor.ime, sektor.lat, sektor.lng, sektor.opis, sektor.parkirisce))
        self.conn.commit()
    
    def dodaj_parkirisce(self, parkirisce: Parkirisca):
        self.cur.execute("""
            INSERT into bolder(ime, lat, lng, opis)
            VALUES (%s, %s, %s, %s)
            """, (parkirisce.ime, parkirisce.lat, parkirisce.lng, parkirisce.opis))
        self.conn.commit()
    
    def dodaj_bolder(self, ime, lat, lng, opis, sektor_ime, parkirisce_ime, datum_dod): 
        # Doda nov bolder, pri čemer poskrbi, da sektor in parkirišče obstajata.
        
        # Preverimo, ali parkirišče že obstaja, če ne, ga dodamo
        self.cur.execute("SELECT id FROM parkirisca WHERE ime = %s;", (parkirisce_ime,))
        parkirisce = self.cur.fetchone()

        if not parkirisce:
            novo_parkirisce = Parkirisca(ime=parkirisce_ime, lat=lat, lng=lng, opis="Samodejno dodano")
            self.dodaj_parkirisce(novo_parkirisce)
            self.cur.execute("SELECT id FROM parkirisca WHERE ime = %s;", (parkirisce_ime,))
            parkirisce = self.cur.fetchone()

        parkirisce_id = parkirisce["id"]

        # Preverimo, ali sektor že obstaja, če ne, ga dodamo
        self.cur.execute("SELECT id FROM sektorji WHERE ime = %s;", (sektor_ime,))
        sektor = self.cur.fetchone()

        if not sektor:
            nov_sektor = Sektorji(ime=sektor_ime, lat=lat, lng=lng, opis="Samodejno dodano", parkirisce=parkirisce_id)
            self.dodaj_sektor(nov_sektor)
            self.cur.execute("SELECT id FROM sektorji WHERE ime = %s;", (sektor_ime,))
            sektor = self.cur.fetchone()

        sektor_id = sektor["id"]

        # Zdaj lahko dodamo bolder s pridobljenim sektor_id in parkirisce_id
        self.cur.execute("""
            INSERT INTO bolderji (ime, opis, sektor_id, parkirisce_id, lat, lng)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (ime, opis, sektor_id, parkirisce_id, lat, lng))

        self.conn.commit()

        return self.cur.fetchone()["id"]  # Vrne ID novega bolderja


    def dodaj_smer(self, ime, tezavnost, opis, bolder_ime):
# Preverimo, ali sektor že obstaja, če ne, ga dodamo
        self.cur.execute("SELECT id FROM sektorji WHERE ime = %s;", (bolder_ime,))
        bolder = self.cur.fetchone()

        bolder_id = bolder["id"]

        self.cur.execute("""
            INSERT into smer(ime, tezavnost, opis, bolder_id)
            VALUES (%s, %s, %s, %s)
            """, (ime, tezavnost, opis, bolder_id))
        self.conn.commit()

    def odstrani_bolder(self, id):
        self.cur.execute("""
            DELETE from bolderji
            WHERE id = %s
        """, (id,))
        self.conn.commit()
    
    def odstrani_smer(self, id):
        self.cur.execute("""
            DELETE from smeri
            WHERE id = %s
        """, (id,))
        self.conn.commit()
    
    def odstrani_parkirisce(self, id):
        self.cur.execute("""
            DELETE from parkirisca
            WHERE id = %s
        """, (id,))
        self.conn.commit()

