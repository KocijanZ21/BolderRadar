import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki
import auth_public as auth
import datetime
import os

from models import Uporabniki, Parkirisca, Sektorji, Bolderji, Smeri
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
            SELECT * FROM uporabniki
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
    
    def dobi_sektorje(self) -> List[Sektorji]:
        self.cur.execute("""
            SELECT * FROM Sektorji
            Order by id         
        """)
        sektorji = [Sektorji.from_dict(s) for s in self.cur.fetchall()]
        return sektorji

    def dobi_parkirisca(self) -> List[Parkirisca]:
        self.cur.execute("""
            SELECT * FROM Parkirisca
            Order by id         
        """)
        parkirisca = [Parkirisca.from_dict(p) for p in self.cur.fetchall()]
        return parkirisca
    
    def dobi_smeri(self) -> List[Smeri]:
        self.cur.execute("""
            SELECT * FROM Smeri
            Order by id         
        """)
        smeri = [Smeri.from_dict(s) for s in self.cur.fetchall()]
        return smeri

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
            SELECT id, ime, tezavnost, opis, sektor
            FROM Smeri
            WHERE ime = %s
             """, (ime,))
        s = Smeri.from_dict(self.cur.fetchone())
        return s
    
    def dodaj_uporabnika(self, uporabnik: Uporabniki):
        self.cur.execute("""
            INSERT into uporabniki(ime, email, geslo, datum_reg)
            VALUES (%s, %s, %s, %s)
            """, (uporabnik.ime,uporabnik.email, uporabnik.geslo, uporabnik.datum_reg))
        self.conn.commit()
    
    def dodaj_bolder(self, bolder: Bolderji):
        self.cur.execute("""
            INSERT into bolder(ime, lat, lng, opis, sektor_id, parkirisce_id, datum_dod)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (bolder.ime, bolder.lat, bolder.lng, bolder.opis, bolder.sektor, bolder.parkirisce, bolder.datum_dod))
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
    
    def dodaj_smer(self, smer: Smeri):
        self.cur.execute("""
            INSERT into smer(ime, tezavnost, opis, sektor_id)
            VALUES (%s, %s, %s, %s)
            """, (smer.ime, smer.tezavnost, smer.opis, smer.sektor_id))
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
    


