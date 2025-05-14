from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response
from functools import wraps
import json

from Services.auth_service import AuthService
from Services.bolder_service import BolderjiService
import os

auth = AuthService()
service = BolderjiService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)


def cookie_required(f):
    """
    Dekorator, ki zahteva veljaven piškotek. Če piškotka ni, uporabnika preusmeri na stran za prijavo.
    """
    @wraps(f)
    def decorated( *args, **kwargs):
        cookie = request.get_cookie("uporabnik")
        if cookie:
            return f(*args, **kwargs)
        return template("login.html",uporabnik=None, napaka="Potrebna je prijava!")
        
    return decorated

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='Presentation/static')

def uporabnik_klic():
    """
    Funkcija, ki pridobi uporabniško ime iz piškotkov.
    """
    raw = request.get_cookie("uporabnik")
    uporabnik = None
    if raw:
        try:
            uporabnik = raw.encode('latin1').decode('utf-8')
        except UnicodeEncodeError:
            uporabnik = raw
    return uporabnik

@get('/')
def index():
    """
    Domača stran z mapo sektorjev.
    """   

    sektorji = [{
    "id": s.id, "ime": s.ime, "pokrajina": s.pokrajina, "lat": s.lat, "lng": s.lng, "opis": s.opis
    } for s in service.dobi_sektorje()]
    sektorji_json = json.dumps(sektorji)  # Seriliziraj seznam sektorjev v JSON

    email = request.get_cookie('email')
    uporabnik = uporabnik_klic()

    return template('index', uporabnik=uporabnik, email=email, request=request, sektorji=sektorji_json)


@get('/aboutus')
def about_us():
    uporabnik = uporabnik_klic()
    return template('about_us.html', request=request, uporabnik=uporabnik)


@get('/prijava')
def prijava_get():
    return template('login.html', uporabnik=None, napaka=None)

@post('/prijava')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku.
    Drugače sporoči, da je prijava neuspešna.
    """
    email = request.forms.getunicode('email')
    password = request.forms.getunicode('password')
    
    prijava = auth.prijavi_uporabnika(email, password)
    if prijava:
        response.set_cookie("email", email, path="/")   
        response.set_cookie("uporabnik", prijava.ime, path="/")
        uporabnik=prijava.ime
        redirect(url('index', uporabnik=uporabnik))

    else:
        return template("login.html", uporabnik=None, napaka="Neuspešna prijava. Napačno geslo ali email naslov.")

@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku.
    """
    
    response.delete_cookie("uporabnik")
    response.delete_cookie("email")
    
    redirect(url('index', uporabnik = None))

@get('/registracija')
def registracija_get():
    return template('register.html', uporabnik=None, napaka=None)

@post('/registracija')
def registracija_post():
    """
    Registracija uporabnika. Dodajanje uporabnika v tabelo uporabniki.
    """
    ime =  request.forms.getunicode('ime')  # Prepozna šumnike
    email = request.forms.getunicode('email')
    password = request.forms.getunicode('password')

    # Preveri, če uporabniško ime že obstaja
    if auth.obstaja_uporabnik(email):
        return template('registracija.html', napaka="Profil s tem email naslovom že obstaja.")

    auth.dodaj_uporabnika(ime, email, password)

    redirect(url('prijava_get'))

@get('/dodaj_bolder')
def dodaj_bolder_get():
    uporabnik = uporabnik_klic()
    return template('submit_boulder_form.html', uporabnik=uporabnik, request=request, sektor_msg=None)

@post('/dodaj_bolder') 
def dodaj_bolder_post():
    """
    Dodajanje bolderja v tabelo bolderji.
    """
    ime = request.forms.getunicode('b_ime')
    lat = request.forms.getunicode('b_lat')
    lng = request.forms.getunicode('b_lng')
    opis = request.forms.getunicode('b_opis')
    sektor = request.forms.getunicode('sektor')

    if service.dobi_sektor_ime(sektor) is None:
        uporabnik = uporabnik_klic()
        return template('submit_boulder_form.html', uporabnik=uporabnik, sektor_msg="Ta sektor še ne obstaja.", request=request)
    s_id = service.dobi_sektor_ime(sektor).id
    service.dodaj_bolder(ime, lat, lng, opis, sektor)
    redirect(url('sektor_info', id=s_id))


@post('/dodaj_sektor')
def dodaj_sektor():
    ime = request.forms.getunicode('s_ime')
    pokrajina = request.forms.getunicode('pokrajina')
    lat = request.forms.getunicode('s_lat')
    lng = request.forms.getunicode('s_lng')
    opis = request.forms.getunicode('s_opis')
    service.dodaj_sektor(ime, pokrajina, lat, lng, opis)
    uporabnik = uporabnik_klic()
    return template('submit_boulder_form.html', uporabnik=uporabnik, sektor_msg="Sektor uspešno dodan!", request=request)

@post('/dodaj_smer')
def dodaj_smer():
    ime = request.forms.getunicode('ime')
    tezavnost = request.forms.getunicode('tezavnost')
    opis = request.forms.getunicode('opis')
    bolder_id = request.forms.getunicode('bolder_id')
    service.dodaj_smer(ime, tezavnost, opis, bolder_id)
    
    # 🔁 Preusmeri nazaj na bolder_info s tem id-jem
    redirect(f'/bolder_info?id={bolder_id}')

@get('/sektor_info')
def sektor_info():
    uporabnik = uporabnik_klic()
    sektor_id = request.query.id
    sektor = service.dobi_sektor_id(sektor_id)
    bolderji=service.dobi_bolderje_sektor(sektor.ime)
    parkirisca=service.dobi_parkirisca_sektor(sektor.ime)
    return template('sector_info.html', uporabnik=uporabnik, request=request, sektor=sektor, bolderji=bolderji, parkirisca=parkirisca)

@get('/bolder_info')
def bolder_info():
    uporabnik = uporabnik_klic()
    bolder_id = request.query.id
    bolder = service.dobi_bolder_id(bolder_id)
    smeri=service.dobi_smeri_bolder(bolder.ime)
    sektor=service.dobi_sektor_id(bolder.sektor_id)
    parkirisca=service.dobi_parkirisca_bolder(bolder.ime)
    parkirisca_sektorja = service.dobi_parkirisca_sektor(sektor.ime)

    parkirisca_id = [p.id for p in parkirisca]
    filtrirana_p = [p for p in parkirisca_sektorja if p.id not in parkirisca_id]

    return template('boulder_info.html', uporabnik=uporabnik, request=request, bolder=bolder, sektor=sektor, smeri=smeri, parkirisca=parkirisca, parkirisca_sektorja=filtrirana_p)

@get('/park_info')   # very much not okej, ampak maš na nečem za delat
def parkirisce_info():
    uporabnik = uporabnik_klic()
    parkirisce_id = request.query.id
    parkirisce = service.dobi_parkirisce(parkirisce_id)
    sektorji=service.dobi_sektorje_park(parkirisce_id)
    bolderji = service.dobi_bolderje_park(parkirisce_id)
    vsi_sektorji = service.dobi_sektorje()

    sektorji_id = [s.id for s in sektorji]
    filtrirani_s = [s for s in vsi_sektorji if s.id not in sektorji_id]

    bolderji_gledena_s = []
    for sektor in sektorji:
        boldi = service.dobi_bolderje_sektor(sektor.ime)
        bolderji_gledena_s += boldi
    
    bolderji_id = [b.id for b in bolderji]
    filtrirani_b = [b for b in bolderji_gledena_s if b.id not in bolderji_id]
    
    return template('park_info.html', uporabnik=uporabnik, request=request, parkirisce=parkirisce, sektorji=sektorji, bolderji=bolderji, vsi_sektorji=filtrirani_s, bolderji_gledena_s=filtrirani_b)

@post('/dodaj_povezavo_b_parkirisce')
def dodaj_povezavo_b_parkirisce():
    bolder_id = request.forms.getunicode('bolder_id')
    park_id = request.forms.getunicode('park_id')

    # Doda povezavo med bolderjem in parkiriščem
    service.povezi_bolder_in_parkirisce(bolder_id, park_id)

    # Preusmeri nazaj na boulder_info z ustreznim ID-jem
    redirect(f"/bolder_info?id={bolder_id}")

@post('/dodaj_parkirisce_s')
def dodaj_parkirisce_s():
    ime = request.forms.getunicode('ime')
    lat = request.forms.getunicode('lat')
    lng = request.forms.getunicode('lng')
    opis = request.forms.getunicode('opis')

    # Bolder ID iz hidden inputa
    sektor_id = request.forms.getunicode('sektor_id')

    # 1. Dodamo parkirišče v tabelo parkirisca
    parkirisce_id = service.dodaj_parkirisce(ime, lat, lng, opis)
    # 2. Dodamo povezavo parkirišče <-> sektor
    service.povezi_sektor_in_parkirisce(sektor_id, parkirisce_id)
    # Preusmeri nazaj na boulder_info z ustreznim ID-jem
    redirect(f"/sektor_info?id={sektor_id}")
    

@post('/dodaj_parkirisce_b')
def dodaj_parkirisce_b():
    ime = request.forms.getunicode('ime')
    lat = request.forms.getunicode('lat')
    lng = request.forms.getunicode('lng')
    opis = request.forms.getunicode('opis')

    # Bolder ID iz hidden inputa
    bolder_id = request.forms.getunicode('bolder_id')

    # Dobimo bolder in njegov sektor
    bolder = service.dobi_bolder_id(bolder_id)
    sektor_id = bolder.sektor_id

    # 1. Dodamo parkirišče v tabelo parkirisca
    parkirisce_id = service.dodaj_parkirisce(ime, lat, lng, opis)

    # 2. Dodamo povezavo parkirišče <-> bolder
    service.povezi_bolder_in_parkirisce(bolder_id, parkirisce_id)

    # 3. Dodamo povezavo parkirišče <-> sektor
    service.povezi_sektor_in_parkirisce(sektor_id, parkirisce_id)

    # Preusmeri nazaj na boulder_info z ustreznim ID-jem
    redirect(f"/bolder_info?id={bolder_id}")

@post("/dodaj_povezavo_s_parkirisce")
def dodaj_povezavo_s_parkirisce():
    sektor_id = request.forms.getunicode('sektor_id')
    park_id = request.forms.getunicode('parkirisce_id')

    # Doda povezavo med sektorjem in parkiriščem
    service.povezi_sektor_in_parkirisce(sektor_id, park_id)

    # Preusmeri nazaj na sektor_info z ustreznim ID-jem
    redirect(f"/park_info?id={park_id}")

@get('/pokrajine')
def pokrajine():
    uporabnik = uporabnik_klic()
    pokrajine = ['Gorenjska', 'Štajerska', 'Prekmurje', 'Koroška', 'Notranjska', 'Primorska', 'Dolenjska']
    izbrana_p = request.query.pokrajina

    if izbrana_p and izbrana_p != "vse":
        sektorji = service.dobi_sektorje_pokrajina(izbrana_p)
    else:
        sektorji = service.dobi_sektorje()
    return template('pokrajine.html', uporabnik=uporabnik, request=request, sektorji=sektorji, pokrajine=pokrajine, izbrana_p=izbrana_p)

@post('/odstrani_bolder')
def odstrani_bolder():
    bolder_id = request.forms.getunicode('bolder_id')
    sektor_id = service.dobi_bolder_id(bolder_id).sektor_id
    service.odstrani_bolder(bolder_id)
    redirect(f"/sektor_info?id={sektor_id}")


@post('/odstrani_smer')
def odstrani_smer():
    id = request.forms.getunicode('smer_id')
    service.odstrani_smer(id)
    bolder_id = request.forms.getunicode('bolder_id')
    redirect(f"/bolder_info?id={bolder_id}")

@post('/odstrani_parkirisce')
def odstrani_parkirisce():
    park_id = request.forms.getunicode('park_id')
    service.odstrani_parkirisce(park_id)
    redirect(url('index'))

@post('/odstrani_sektor')
def odstrani_sektor():
    sektor_id = request.forms.getunicode('sektor_id')
    service.odstrani_sektor(sektor_id)
    redirect(url('index'))

@post('/odstrani_povezavo_b_p')
def odstrani_povezavo_b_p():
    # Odstranjujemo povezavo iz tabele bolder_parkirisce na strani bolder_info
    bolder_id = request.forms.getunicode('bolder_id')
    park_id = request.forms.getunicode('park_id')
    service.odstrani_povezavo_b_p(bolder_id, park_id)
    redirect(f"/bolder_info?id={bolder_id}")

@post('/odstrani_povezavo_p_b')
def odstrani_povezavo_p_b():
    # Odstranjujemo povezavo iz tabele bolder_parkirisce na strani park_info
    bolder_id = request.forms.getunicode('bolder_id')
    park_id = request.forms.getunicode('park_id')
    service.odstrani_povezavo_b_p(bolder_id, park_id)

    redirect(f"/park_info?id={park_id}")

@post('/odstrani_povezavo_s_p')
def odstrani_povezavo_s_p():
    # Odstranjujemo povezavo iz tabele sektor_parkirisce na strani sektor_info
    sektor_id = request.forms.getunicode('sektor_id')
    park_id = request.forms.getunicode('park_id')
    service.odstrani_povezavo_s_p(sektor_id, park_id)
    redirect(f"/sektor_info?id={sektor_id}")

@post('/odstrani_povezavo_p_s')
def odstrani_povezavo_p_s():
    # Odstranjujemo povezavo iz tabele sektor_parkirisce na strani park_info
    sektor_id = request.forms.getunicode('sektor_id')
    park_id = request.forms.getunicode('parkirisce_id')
    service.odstrani_povezavo_s_p(sektor_id, park_id)
    redirect(f"/park_info?id={park_id}")

if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
