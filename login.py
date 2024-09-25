import pwinput
import requests
from msg import inputFullName, inputUsername, inputGmail, inputPassword, inputBirthDate
import re
from datetime import datetime


class LogIn():
    # create user method
    def signUp(self):
        BASE_URL = "http://127.0.0.1:5000/api/version1/sign-up"
        data = {'fullname': '', 'birthdate': '', 'username': '', 'password': '', 'gmail': ''}
        try:
            # full name
            while True:
                fullname = input(f"\n{inputFullName}")
                if not fullname:
                    print("\n> esta entrada no puede estar vacia")
                    continue
                if re.match("[A-Za-z ]", fullname):
                    if len(fullname) >= 8:
                        data['fullname'] = fullname
                        break
                    else:
                        print('\n> longitud invalida')
                else:
                    print('\n> tipo de dato invalido')
            # birthdate input
            while True:
                birthdate = input(f"\n{inputBirthDate}")
                if not birthdate:
                    print("\n> esta entrada no puede estar vacia")
                    continue
                try:
                    formatingdate = datetime.strptime(birthdate, "%y-%m-%d")  # formating birthdate
                except ValueError as err:
                    print(f"\n> ingresa tu fecha de nacimiento en el formato solicitado: {err}")
                else:
                    date = formatingdate.strftime('%y-%m-%d')
                    data['birthdate'] = date
                    break
            # user name input
            while True:
                username = input(f"\n{inputUsername}")
                if not username:
                    print("\n> esta entrada no puede estar vacia")
                    continue
                response = requests.get(BASE_URL, params={'username': username})
                if response.status_code == 409:
                    res = response.json()
                    print(f"\n{res['error']}")
                    continue
                elif response.status_code == 200:
                    if re.match("[a-zA-Z._1234567890]", username):
                        if len(username) >= 8 and len(username) <= 99:
                            data['username'] = username
                            break
                        else:
                            print("\n> longitud invalida")
                    else:
                        print("\n> nombre de usuario invalido")
            # password input
            while True:
                password = pwinput.pwinput(f"\n{inputPassword}", mask="*")
                if not password:
                    print("\n> la contraseña no puede estar vacia")
                    continue
                if password.isdigit():
                    print('\n> la contraseña no puede contener solo numeros')
                    continue
                if re.match("[a-zA-Z._1234567890]", password):
                    if len(password) >= 8 and len(password) <= 99:
                        self.confirmPass(password, data)
                        break
                    else:
                        print("\n> la longitud de la contraseña es invalida")
                else:
                    print("\n> el formato de la cadena es incorrecto")
            # gmail input
            while True:
                gmail = input(f"\n{inputGmail}")
                if not gmail:
                    print("\n> gmail no puede estar vacio")
                    continue
                if re.match("[a-zA-Z@gmail.com]", gmail) or re.match("[a-zA-Z@hotmail.com]", gmail) or re.match("[a-zA-Zgmail.cl]", gmail):
                    if len(gmail) >= 20 or len(gmail) <= 30:
                        data['gmail'] = gmail
                        break
                    else:
                        print("\n> longitud invalida")
                else:
                    print("\n> correo electronico invalido")
        except requests.exceptions.ConnectionError:
            print("\n> error en el servidor")
        except requests.exceptions.HTTPError:
            print("\n> error en el protocolo http")
        else:
            response = requests.post(BASE_URL, json=data)
            if response.status_code == 201:
                res = response.json()
                print(f'\n> {res['succes']}')
            if response.status_code == 500:
                res = response.json()
                print(f'\n> {res['error']}')

    # log in method
    def logIn(self):
        BASE_URL = "http://127.0.0.1:5000/api/version1/log-in"
        data = {'username': str, 'password': str}
        try:
            while True:
                username = input("\n> ingresa tu nombre de usuario: ")
                password = pwinput.pwinput("\n> ingresa tu contraseña: ", mask="*")
                data['username'] = username
                data['password'] = password
                response = requests.post(BASE_URL, json=data)
                if response.status_code == 200:
                    res = response.json()
                    print(f"{res['succes']}")
                    d = res['sesionData']  # {id, username}
                    from main import Main
                    main_session = Main(d)
                    main_session.main()
                    break
                if response.status_code == 400:
                    res = response.json()
                    print(f"{res['error']}")
                if response.status_code == 401:
                    res = response.json()
                    print(f"{res['error']}")
        except requests.exceptions.ConnectionError:
            print("\n> error en la conexion del servidor")
        except requests.exceptions.HTTPError:
            print("\n> error en el protocolo http")
        except KeyboardInterrupt:
            print('\n saliendo')

    def confirmPass(self, password, data):
        while True:
            confirmPass = pwinput.pwinput("\n> confirma tu contraseña: ", mask="*")
            if confirmPass == password:
                data['password'] = confirmPass
                break
            print("\n> las contraseñas no coinciden")
