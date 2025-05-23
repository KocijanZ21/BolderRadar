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

    def dobi_parkirisca_sektor(self, sektor:str) -> List[Parkirisca]:
        self.cur.execute("""
            SELECT p.* FROM parkirisca p
            JOIN sektor_parkirisce sp ON p.id = sp.parkirisce_id
            JOIN sektorji s ON s.id = sp.sektor_id
            WHERE s.ime = %s;
             """, (sektor,))
        s_parkirisca = [Parkirisca.from_dict(p) for p in self.cur.fetchall()]
        return s_parkirisca
    
    def dobi_parkirisca_bolder(self, bolder:str) -> List[Parkirisca]:
        self.cur.execute("""
            SELECT p.* FROM parkirisca p
            JOIN bolder_parkirisce bp ON p.id = bp.parkirisce_id
            JOIN bolderji b ON b.id = bp.bolder_id
            WHERE b.ime = %s;
             """, (bolder,))
        b_parkirisca = [Parkirisca.from_dict(p) for p in self.cur.fetchall()]
        return b_parkirisca
    
    def dobi_smeri_bolder(self, bolder:str) -> List[Smeri]:
        self.cur.execute("""
            SELECT s.* FROM smeri s
            JOIN bolderji b ON s.bolder_id = b.id
            WHERE b.ime = %s;
             """, (bolder,))
        b_smeri = [Smeri.from_dict(s) for s in self.cur.fetchall()]
        return b_smeri
    

    def dobi_uporabnika(self, email:str) -> Uporabniki:
        self.cur.execute("""
            SELECT id, ime, email, geslo, datum_registracije
            FROM Uporabniki
            WHERE email = %s
             """, (email,))
        
        b = Uporabniki.from_dict(self.cur.fetchone())
        return b

    def dobi_bolder_id(self, id:int) -> Bolderji:
        self.cur.execute("""
            SELECT id, ime, lat, lng, opis, sektor_id, datum_dodajanja
            FROM bolderji
            WHERE id = %s
             """, (id,))
        b = Bolderji.from_dict(self.cur.fetchone())
        return b
        
    def dobi_sektor_ime(self, ime:str) -> Sektorji:
        self.cur.execute("""
            SELECT id, ime, pokrajina, lat, lng, opis
            FROM sektorji
            WHERE ime = %s
             """, (ime,))
        sektor_podatki = self.cur.fetchone()  # Fetch result
    
        if sektor_podatki is None:
            return None  # Če sektor ne obstaja, vrni None
        s = Sektorji.from_dict(sektor_podatki)
        return s
    
    def dobi_sektor_id(self, id:int) -> Sektorji:
        self.cur.execute("""
            SELECT id, ime, pokrajina, lat, lng, opis
            FROM sektorji
            WHERE id = %s
             """, (id,))
        sektor_podatki = self.cur.fetchone()
        if sektor_podatki is None:
            return None
        s = Sektorji.from_dict(sektor_podatki)
        return s
    
    def dobi_parkirisce(self, id:int) -> Parkirisca:
        self.cur.execute("""
            SELECT id, ime, lat, lng, opis
            FROM parkirisca
            WHERE id = %s
             """, (id,))
        p = Parkirisca.from_dict(self.cur.fetchone())
        return p
    
    def dodaj_uporabnika(self, uporabnik: Uporabniki):
        self.cur.execute("""
            INSERT into uporabniki(ime, email, geslo, datum_registracije)
            VALUES (%s, %s, %s, %s)
            """, (uporabnik.ime, uporabnik.email, uporabnik.geslo, uporabnik.datum_reg))
        self.conn.commit()
    
    
    def dodaj_sektor(self, sektor: Sektorji):
        self.cur.execute("""
            INSERT into sektorji(ime, pokrajina, lat, lng, opis)
            VALUES (%s, %s, %s, %s, %s)
            """, (sektor.ime, sektor.pokrajina, sektor.lat, sektor.lng, sektor.opis))
        self.conn.commit()
    
    def dodaj_parkirisce(self, parkirisce: Parkirisca):
        self.cur.execute("""
            INSERT into parkirisca(ime, lat, lng, opis)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """, (parkirisce.ime, parkirisce.lat, parkirisce.lng, parkirisce.opis))
        parkirisce_id = self.cur.fetchone()[0]
        self.conn.commit()
        return parkirisce_id  # Vrnemo ID parkirišča, ki smo ga dodali
    
    def dodaj_bolder(self, ime, lat, lng, opis, sektor_ime, datum_dod): 
        
        # Preverimo, ali sektor že obstaja, če ne, ga dodamo
        self.cur.execute("SELECT id FROM sektorji WHERE ime = %s;", (sektor_ime,))
        sektor = self.cur.fetchone()
        sektor_id = sektor[0]  # ID sektorja
        
        # Zdaj lahko dodamo bolder s pridobljenim sektor_id in parkirisce_id
        self.cur.execute("""
            INSERT INTO bolderji (ime, lat, lng, opis, sektor_id, datum_dodajanja)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
            """, (ime, lat, lng, opis, sektor_id, datum_dod))

        self.conn.commit()


    def dodaj_smer(self, ime, tezavnost, opis, bolder_id):
        self.cur.execute("""
            INSERT into smeri(ime, tezavnost, opis, bolder_id)
            VALUES (%s, %s, %s, %s)
            """, (ime, tezavnost, opis, bolder_id))
        self.conn.commit()

    def odstrani_bolder(self, id):
        self.cur.execute("""
            DELETE from smeri
            WHERE bolder_id = %s
            """, (id,))
        self.cur.execute("""
            DELETE from bolder_parkirisce
            WHERE bolder_id = %s
            """, (id,))
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
            DELETE from bolder_parkirisce
            WHERE parkirisce_id = %s
            """, (id,))
        self.cur.execute("""
            DELETE from sektor_parkirisce
            WHERE parkirisce_id = %s
            """, (id,))
        self.cur.execute("""
            DELETE from parkirisca
            WHERE id = %s
            """, (id,))
        self.conn.commit()
    
    def povezi_bolder_in_parkirisce(self, bolder_id: int, park_id: int):
        self.cur.execute("""
            INSERT INTO bolder_parkirisce (bolder_id, parkirisce_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (bolder_id, park_id))
        self.conn.commit()
    
    def povezi_sektor_in_parkirisce(self, sektor_id, parkirisce_id):
        self.cur.execute("""
            INSERT INTO sektor_parkirisce (sektor_id, parkirisce_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (sektor_id, parkirisce_id))
        self.conn.commit()
    
    def dobi_sektorje_park(self, parkirisce_id):
        self.cur.execute("""
            SELECT s.* FROM sektorji s
            JOIN sektor_parkirisce sp ON s.id = sp.sektor_id
            WHERE sp.parkirisce_id = %s;
             """, (parkirisce_id,))
        sektorji = [Sektorji.from_dict(s) for s in self.cur.fetchall()]
        return sektorji
    
    def dobi_bolderje_park(self, parkirisce_id):
        self.cur.execute("""
            SELECT b.* FROM bolderji b
            JOIN bolder_parkirisce bp ON b.id = bp.bolder_id
            WHERE bp.parkirisce_id = %s;
             """, (parkirisce_id,))
        bolderji = [Bolderji.from_dict(b) for b in self.cur.fetchall()]
        return bolderji
    
    def odstrani_sektor(self, id):
        # 1. Najdi vse bolder_id-je iz tega sektorja
        self.cur.execute("""
            SELECT id FROM bolderji
            WHERE sektor_id = %s
            """, (id,))
        bolder_ids = [row[0] for row in self.cur.fetchall()]
        # 2. Izbriši iz bolder_parkirisce vse povezave z njimi
        if bolder_ids:  # samo če jih je
            self.cur.execute("""
                DELETE FROM bolder_parkirisce
                WHERE bolder_id = ANY(%s)
                """, (bolder_ids,))
        # 3. Izbriši vse bolderje iz sektorja
        self.cur.execute("""
            DELETE FROM bolderji
            WHERE sektor_id = %s
            """, (id,))
        # 4. Izbriši vse povezave sektor-parkirišče
        self.cur.execute("""
            DELETE FROM sektor_parkirisce
            WHERE sektor_id = %s
            """, (id,))
        # 5. Izbriši sam sektor
        self.cur.execute("""
            DELETE from sektorji
            WHERE id = %s
            """, (id,))
        self.conn.commit()
    
    def odstrani_povezavo_b_p(self, bolder_id, park_id):
        self.cur.execute("""
            DELETE from bolder_parkirisce
            WHERE bolder_id = %s AND parkirisce_id = %s
            """, (bolder_id, park_id))
        self.conn.commit()
    
    def odstrani_povezavo_s_p(self, sektor_id, park_id):
        self.cur.execute("""
            DELETE from sektor_parkirisce
            WHERE sektor_id = %s AND parkirisce_id = %s
            """, (sektor_id, park_id))
        self.conn.commit()

