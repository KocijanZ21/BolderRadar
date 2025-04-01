from Data.repository import Repo
from Data.models import *
from typing import List
import bcrypt
from datetime import date


class AuthService:
    repo : Repo
    def __init__(self):
         self.repo = Repo()

    def obstaja_uporabnik(self, uporabnik: str) -> bool:
        try:
            user = self.repo.dobi_uporabnika(uporabnik)
            return True
        except:
            return False
        
    def prijavi_uporabnika(self, uporabnik : str, u_geslo: str) -> UporabnikiDto | bool :

        # Najprej dobimo uporabnika iz baze
        try:
            user = self.repo.dobi_uporabnika(uporabnik)
            print('service user', user)
        except:
            return False
        # Preverimo, če je geslo pravilno
        geslo_bytes = u_geslo.encode('utf-8')
        # Ustvarimo hash iz gesla, ki ga je vnesel uporabnik
        succ = bcrypt.checkpw(geslo_bytes, user.geslo.encode('utf-8'))

        if succ:
            return UporabnikiDto(ime=user.ime, email=user.email)
        
        return False

    def dodaj_uporabnika(self, uporabnik: str, u_email:str, geslo: str) -> UporabnikiDto:

        # zgradimo hash za geslo od uporabnika

        # Najprej geslo zakodiramo kot seznam bajtov
        bytes = geslo.encode('utf-8')
  
        # Nato ustvarimo salt
        salt = bcrypt.gensalt()
        
        # In na koncu ustvarimo hash gesla
        password_hash = bcrypt.hashpw(bytes, salt)

        # Sedaj ustvarimo objekt Uporabnik in ga zapišemo bazo

        u = Uporabniki(
            ime=uporabnik,
            email=u_email,
            geslo=password_hash.decode(),
            datum_reg=datetime.today().isoformat()
            )

        self.repo.dodaj_uporabnika(u)
        
        return UporabnikiDto(ime=uporabnik)
