from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user
from functools import wraps

from Services.auth_service import AuthService
from Services.bolder_service import BolderjiService
import os

auth = AuthService()
service = BolderjiService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8081)
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
    Domača stran z mapo bolderjev.
    """   
    email = request.get_cookie('email')
    uporabnik = request.get_cookie("uporabnik")  # Pridobi uporabniško ime iz piškotkov

    # Pomembno: Podaj `request` v template, da bo deloval `request.get_cookie` v Mako
    return template('index', uporabnik=uporabnik, email=email, request=request)


@get('/aboutus')
def about_us():
    return template('about_us.html', request=request)


@get('/prijava')
def prijava_get():
    return template('login.html', uporabnik=None)

@post('/prijava')
def prijava():
    """
    Prijavi uporabnika v aplikacijo. Če je prijava uspešna, ustvari piškotke o uporabniku.
    Drugače sporoči, da je prijava neuspešna.
    """
    email = request.forms.get('email')
    password = request.forms.get('password')

    if not auth.obstaja_uporabnik(email):
        return template("login.html", napaka="Uporabnik s tem imenom ne obstaja")

    prijava = auth.prijavi_uporabnika(email, password)
    if prijava:
        response.set_cookie("uporabnik", email, path="/")
        bolderji = service.dobi_bolderje()
        
        redirect(url('index', uporabnik=email))

    else:
        return template("prijava.html", uporabnik=None, napaka="Neuspešna prijava. Napačno geslo ali elektronska pošta.")

@get('/odjava')
def odjava():
    """
    Odjavi uporabnika iz aplikacije. Pobriše piškotke o uporabniku.
    """
    
    response.delete_cookie("uporabnik")
    
    return template('index.html', uporabnik=None, napaka=None)

@get('/registracija')
def registracija_get():
    return template('register.html', uporabnik=None)

@post('/registracija')
def registracija_post():
    """
    Registracija uporabnika. Dodajanje uporabnika v tabelo uporabniki.
    """
    ime = request.forms.getunicode('ime')
    email = request.forms.get('email')
    password = request.forms.get('password')

    auth.dodaj_uporabnika(ime, email, password)

    redirect(url('index'))

@get('/dodaj_bolder')
def dodaj_bolder_get():
    return template('dsubmit_bolder_form.html', uporabnik=None)

#@post('/dodaj_bolder')
#def dodaj_bolder_post():
#    """
#    Dodajanje bolderja v tabelo bolderji.
#    """
#    ime = request.forms.getunicode('ime')
#    tezavnost = request.forms.getunicode('tezavnost')
#    opis = request.forms.getunicode('opis')
#    service.dodaj_bolder(ime, tezavnost, opis)
#    redirect(url('index'))





if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)
