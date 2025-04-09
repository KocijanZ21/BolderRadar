from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response
from functools import wraps
import json

from Services.auth_service import AuthService
from Services.bolder_service import BolderjiService
import os

auth = AuthService()
service = BolderjiService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8083)
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


@get('/')
def index():
    """
    Domača stran z mapo sektorjev.
    """   

    sektorji = [{
    "id": s.id, "ime": s.ime, "lat": s.lat, "lng": s.lng, "opis": s.opis
    } for s in service.dobi_sektorje()]
    print(sektorji)
    sektorji_json = json.dumps(sektorji)  # Seriliziraj seznam sektorjev v JSON

    email = request.get_cookie('email')
    uporabnik = request.get_cookie("uporabnik")  # Pridobi uporabniško ime iz piškotkov

    # Pomembno: Podaj `request` v template, da bo deloval `request.get_cookie` v Mako
    return template('index', uporabnik=uporabnik, email=email, request=request, sektorji=sektorji_json)


@get('/aboutus')
def about_us():
    uporabnik = request.get_cookie("uporabnik")
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
    email = request.forms.get('email')
    password = request.forms.get('password')
    
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
    
    return template('index.html', uporabnik=None, napaka=None, request=request)

@get('/registracija')
def registracija_get():
    return template('register.html', uporabnik=None, napaka=None)

@post('/registracija')
def registracija_post():
    """
    Registracija uporabnika. Dodajanje uporabnika v tabelo uporabniki.
    """
    ime = request.forms.get('ime').encode('utf-8').decode('utf-8')  # Prepozna šumnike
    email = request.forms.getunicode('email')
    password = request.forms.get('password')

    # Preveri, če uporabniško ime že obstaja
    if auth.obstaja_uporabnik(email):
        return template('registracija.html', napaka="Profil s tem email naslovom že obstaja.")

    auth.dodaj_uporabnika(ime, email, password)

    redirect(url('prijava_get'))

@get('/dodaj_bolder')
def dodaj_bolder_get():
    uporabnik = request.get_cookie("uporabnik")
    return template('submit_boulder_form.html', uporabnik=uporabnik, request=request, sektor_msg=None)

@post('/dodaj_bolder') 
def dodaj_bolder_post():
    """
    Dodajanje bolderja v tabelo bolderji.
    """
    ime = request.forms.get('b_ime')
    lat = request.forms.get('b_lat')
    lng = request.forms.get('b_lng')
    opis = request.forms.get('b_opis')
    sektor = request.forms.get('sektor')

    if service.dobi_sektor(sektor) is None:
        return template('submit_boulder_form.html', uporabnik=request.get_cookie("uporabnik"), sektor_msg="Ta sektor še ne obstaja.", request=request)

    service.dodaj_bolder(ime, lat, lng, opis, sektor)
    print("Bolder dodan!")
    redirect(url('index'))

@post('/dodaj_parkirisce')                          # Not there yet
def dodaj_parkirisce():
    print("Parkirišče dodano!")
    return "Uspešno dodano!"

@post('/dodaj_sektor')
def dodaj_sektor():
    ime = request.forms.getunicode('s_ime')
    pokrajina = request.forms.get('pokrajina')
    lat = request.forms.get('s_lat')
    lng = request.forms.get('s_lng')
    opis = request.forms.get('s_opis')
    service.dodaj_sektor(ime, pokrajina, lat, lng, opis)
    return template('submit_boulder_form.html', uporabnik=request.get_cookie("uporabnik"), sektor_msg="Sektor uspešno dodan!", request=request)

@post('/dodaj_smer')
def dodaj_smer():
    ime = request.forms.get('smer_ime')
    tezavnost = request.forms.get('tezavnost')
    opis = request.forms.get('smer_opis')




if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
