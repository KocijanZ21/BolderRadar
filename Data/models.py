from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from datetime import datetime

# V tej datoteki definiramo vse podatkovne modele, ki jih bomo uporabljali v aplikaciji
# Pazi na vrstni red anotacij razredov!

@dataclass_json
@dataclass

class Uporabniki:
    id : int = field(default=0)  # Za vsako polje povemo tip in privzeto vrednost
    ime : str = field(default="")
    email: str =field(default="")
    geslo: str =field(default="")
    datum_reg: datetime=field(default=datetime.now()) 
    


# Za posamezno entiteto ponavadi ustvarimo tudi tako imenovan
# DTO (database transfer object) objekt. To izhaja predvsem iz tega,
# da v sami aplikaciji ponavadi želimo prikazati podatke drugače kot so v bazi.
# Dodatno bi recimo želeli narediti kakšen join in vzeti podatek oziroma stolpec iz druge tabele


@dataclass_json
@dataclass
class Parkirisca:    
    id : int = field(default=0) 
    ime : str = field(default="")
    lat : float = field(default="")
    lng: float = field(default="") 
    opis : str = field(default="")
 
@dataclass_json
@dataclass
class Sektorji:
    id : int = field(default=0)
    ime : str = field(default="") 
    lat : float = field(default=0)
    lng : float=field(default=0) 
    opis : str=field(default="")
    parkirisce_id : int=field(default=0)


@dataclass_json
@dataclass
class Bolderji:
    id : int = field(default=0) 
    ime : str = field(default="")
    lat : float = field(default="")
    lng: float = field(default="") 
    opis : str = field(default="")
    sektor_id : int=field(default=0)
    parkirisce_id : int=field(default=0)
    datum_dod: datetime = field(default=datetime.now()) 

   
@dataclass_json
@dataclass
class Smeri:
    id : int = field(default=0)
    ime : str = field(default="") 
    tezavnost : str = field(default="")
    opis : str=field(default="")
    bolder_id : int = field(default=0)