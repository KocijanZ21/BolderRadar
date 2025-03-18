from Presentation.bottleext import get, post, run, request, template, redirect, static_file, url, response, template_user

from Services.bolder_service import BolderjiService
import os
service = BolderjiService()

# privzete nastavitve
SERVER_PORT = os.environ.get('BOTTLE_PORT', 8080)
RELOADER = os.environ.get('BOTTLE_RELOADER', True)

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='Presentation/static')


@get('/')
def index():
    """
    Domača stran s plovili.
    """   
  
    bolderji = service.dobi_bolderje()  
        
    return template('osnova.html', bolderji = bolderji)


if __name__ == "__main__":
    run(host='localhost', port=SERVER_PORT, reloader=RELOADER, debug=True)