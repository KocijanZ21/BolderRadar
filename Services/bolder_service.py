from Data.repository import Repo
from Data.models import *
from typing import List
from datetime import date


# V tej datoteki bomo definirali razred za obdelavo in delo z bolderji

class BolderjiService:
    def __init__(self) -> None:
        self.repo = Repo()

    def dobi_bolderje_sektor(self, sektor:str) -> List[Bolderji]:
        return self.repo.dobi_bolderje_sektor(sektor)
    
    def dobi_sektorje(self) -> List[Sektorji]:
        return self.repo.dobi_sektorje()
    
    def dobi_sektorje_pokrajina(self, pokrajina:str) -> List[Sektorji]:
        return self.repo.dobi_sektorje_pokrajina(pokrajina)
    
    def dobi_parkirisca_sektor(self, sektor:str) -> List[Parkirisca]:
        return self.repo.dobi_parkirisca_sektor(sektor)
    
    def dobi_parkirisca_bolder(self, bolder:str) -> List[Parkirisca]:
        return self.repo.dobi_parkirisca_bolder(bolder)
    
    def dobi_smeri_bolder(self, bolder:str) -> List[Smeri]:
        return self.repo.dobi_smeri_bolder(bolder)

    def dobi_sektor_ime(self, ime:str) -> List[Sektorji]:
        sektor = self.repo.dobi_sektor_ime(ime)
        return sektor
    
    def dobi_sektor_id(self, id:int) -> List[Sektorji]:
        sektor = self.repo.dobi_sektor_id(id)
        return sektor
    
    def dobi_bolder_id(self, id:int) -> List[Bolderji]:
        bolder = self.repo.dobi_bolder_id(id)
        return bolder
    
    def dobi_parkirisce(self, id:int) -> List[Parkirisca]:
        park = self.repo.dobi_parkirisce(id)
        return park

    def dodaj_bolder(self, b_ime, b_lat, b_lng, b_opis, b_sektor):
        datum_dod= datetime.today()
        self.repo.dodaj_bolder(b_ime, b_lat, b_lng, b_opis, b_sektor, datum_dod)
    
    def dodaj_sektor(self, s_ime, s_pokrajina, s_lat, s_lng, s_opis):
            s = Sektorji(
                ime=s_ime,
                pokrajina=s_pokrajina,
                lat=s_lat,
                lng=s_lng,
                opis=s_opis
            )
            self.repo.dodaj_sektor(s)

    def dodaj_smer(self, ime, tezavnost, opis, bolder_id):
        self.repo.dodaj_smer(ime, tezavnost, opis, bolder_id)

    def odstrani_bolder(self, id):
        self.repo.odstrani_bolder(id)

    def odstrani_smer(self, id):
        self.repo.odstrani_smer(id)
    
    def odstrani_sektor(self, id):
        self.repo.odstrani_sektor(id)
    
    def odstrani_parkirisce(self, id):
        self.repo.odstrani_parkirisce(id)

    def povezi_bolder_in_parkirisce(self, bolder_id, park_id):
        self.repo.povezi_bolder_in_parkirisce(bolder_id, park_id)
    
    def povezi_sektor_in_parkirisce(self, sektor_id, parkirisce_id):
        self.repo.povezi_sektor_in_parkirisce(sektor_id, parkirisce_id)
    
    def dodaj_parkirisce(self, ime, lat, lng, opis):
        p = Parkirisca(ime=ime, lat=lat, lng=lng, opis=opis)
        id_park = self.repo.dodaj_parkirisce(p)
        return id_park
    
    def dobi_sektorje_park(self, parkirisce_id):
        return self.repo.dobi_sektorje_park(parkirisce_id)
    
    def dobi_bolderje_park(self, parkirisce_id):
        return self.repo.dobi_bolderje_park(parkirisce_id)
    
    def odstrani_povezavo_b_p(self, bolder_id, park_id):
        self.repo.odstrani_povezavo_b_p(bolder_id, park_id)
    
    def odstrani_povezavo_s_p(self, sektor_id, park_id):
        self.repo.odstrani_povezavo_s_p(sektor_id, park_id)











