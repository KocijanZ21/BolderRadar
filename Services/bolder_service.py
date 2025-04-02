from Data.repository import Repo
from Data.models import *
from typing import List
from datetime import date


# V tej datoteki bomo definirali razred za obdelavo in delo z bolderji

class BolderjiService:
    def __init__(self) -> None:
        self.repo = Repo()

    def dobi_bolderje(self) -> List[Bolderji]:
        return self.repo.dobi_bolderje()

    def dobi_bolderje_sektor(self, sektor:str) -> List[Bolderji]:
        return self.repo.dobi_bolderje_sektor(sektor)
    
    def dobi_sektorje_pokrajina(self, pokrajina:str) -> List[Sektorji]:
        return self.repo.dobi_sektorje_pokrajina(pokrajina)
    
    def dobi_parkirisca_sektor(self, sektor:str) -> List[Parkirisca]:
        return self.repo.dobi_parkirisca_sektor(sektor)
    
    def dobi_smeri_bolder(self, bolder:str) -> List[Smeri]:
        return self.repo.dobi_smeri_bolder(bolder)

    def dobi_sektor(self, ime:str) -> List[Sektorji]:
        sektor = self.repo.dobi_sektor
        return sektor
    
    def dobi_bolder(self, ime:str) -> List[Bolderji]:
        bolder = self.repo.dobi_bolder(ime)
        return bolder
    
    def dobi_smer(self, ime:str) -> List[Smeri]:
        smer = self.repo.dobi_smer(ime)
        return smer

    def dobi_parkirisce(self, ime:str) -> List[Parkirisca]:
        park = self.repo.dobi_parkirisce(ime)
        return park

    def dodaj_bolder(self, b_ime, b_lat, b_lng, b_opis, b_sektor):
        b = Bolderji(
            ime=b_ime,
            lat=b_lat,
            lng=b_lng,
            opis=b_opis,
            sektor_ime=b_sektor,
            datum_dod= datetime.today()
        )
        self.repo.dodaj_bolder(b) # a dela? Če ne v to vrstico naštej vsakega posebej
    
    def dodaj_sektor(self, s_ime, s_pokrajina, s_lat, s_lng, s_opis):
            s = Sektorji(
                ime=s_ime,
                pokrajina=s_pokrajina,
                lat=s_lat,
                lng=s_lng,
                opis=s_opis
            )
            self.repo.dodaj_sektor(s)

    def dodaj_smer(self, ime, tezavnost, opis, bolder_ime):
        self.repo.dodaj_smer(ime, tezavnost, opis, bolder_ime)

    def odstrani_bolder(self, id):
        self.repo.odstrani_bolder(id)

    def odstrani_smer(self, id):
        self.repo.odstrani_smer











