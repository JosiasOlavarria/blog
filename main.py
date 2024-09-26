#!/usr/bin/env python3
from msg import menuPerfil, menuMain, menuLogin, crudDatos, crudPosts
import requests
import re
import time
from pwinput import pwinput
import pandas as pd
from tabulate import tabulate


class Main():
    def __init__(self, data):
        self.user = data

    def main(self):
        username = self.user[1]
        print(f'\n> Hola {username}')
        try:
            while True:
                menu = input(menuMain)
                if menu == '1':
                    self.allPosts()
                elif menu == '2':
                    self.myProfile(self.user)
                elif menu == '3':
                    print('saliendo')
                    break
        except KeyboardInterrupt:
            print("\n> saliendo")

    def allPosts(self):
        BASE_URL = 'http://127.0.0.1:5000/api/version1/posts/show-all-posts-users'
        try:
            readall = requests.get(BASE_URL)
            if readall.status_code == 200:
                res = readall.json()
                df = pd.DataFrame(res)
                print(f'\n{tabulate(df, headers='keys', tablefmt='psql')}')
            if readall.status_code == 400:
                res = readall.json()
                print(f'\n> {res['empty']}')
            if readall.status_code == 500:
                res = readall.json()
                print(f"\n> {res['error']}")
        except KeyboardInterrupt:
            print('\n> interrupcion')
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion del servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo http')

    def myProfile(self, user):
        try:
            while True:
                menu = input(f"\n{menuPerfil}")
                if menu == '1':
                    init_posts = PostsProfile(user)
                    init_posts.postProfile()
                elif menu == '2':
                    init_myProfile = DataProfile(user)
                    init_myProfile.data()
                elif menu == '3':
                    break
        except KeyboardInterrupt:
            print(" interrupcion")


class DataProfile():
    def __init__(self, data):
        self.user = data

    def data(self):
        try:
            while True:
                choice = input(f"\n{crudDatos}")
                if choice == '1':
                    self.read_user()
                elif choice == '2':
                    self.update_user()
                elif choice == '3':
                    self.delete_user()
                elif choice == '4':
                    break
                else:
                    raise ValueError()
        except KeyboardInterrupt:
            print("\n> interrupcion del teclado")
        except ValueError:
            print('\n> ingresaste una opcion invalida')

    def read_user(self):
        userId = self.user[0]
        BASE_URL = "http://127.0.0.1:5000/api/version1/readData"
        response = requests.get(f"{BASE_URL}/{userId}")
        # {username, fullname,  birthdate, gmail}
        if response.status_code == 200:
            res = response.json()
            df = pd.DataFrame(res)
            print(f'\n{tabulate(df, headers='keys', tablefmt='psql')}\n')
        else:
            print("\n> los datos no se pudieron visualizar intentalo de nuevo")

    def update_user(self):
        userId = self.user[0]
        BASE_URL = "http://127.0.0.1:5000/api/version1/update-data"
        try:
            choice = input('\n> para editar tu contraseña escribe (contraseña)\n> para editar tu nombre de usuario escribe (nombre de usuario)\n> escribe aqui: ')
            if choice in ['contraseña', 'editar contraseña']:
                while True:
                    confirmPassword = pwinput('\n> ingresa tu contraseña actual: ', mask='*')
                    response = requests.get(BASE_URL, params={'userId': userId, 'actualPassword': confirmPassword})
                    if response.status_code == 200:  # status code ok
                        while True:
                            newPassword = pwinput('\n> ingresa la nueva contraseña', mask='*')
                            if not newPassword:
                                print('\n> la contraseña no puede estar vacia')
                                continue
                            if newPassword.isdigit():
                                print('\n> la contraseña no puede contener solo numeros')
                                continue
                            if re.match('[a-zA-Z._1234567890]', newPassword):
                                if len(newPassword) >= 8:
                                    response = requests.put(BASE_URL, json={'newPassword': newPassword, 'userId': userId})  # solicitud put de la nueva contraseña
                                    if response.status_code == 200:
                                        res = response.json()
                                        print(f'\n> {res['succes']}')
                                        return
                                elif response.status_code == 500:
                                    res = response.json()
                                    print(f'\n> {res['error']}')
                                    return
                            else:
                                print('\n> la contraseña es invalida, prueba con otra')
                    if response.status_code == 400:
                        res = response.json()
                        print(f'\n> {res['error']}')
                    if response.status_code == 500:
                        res = response.json()
                        print(f'\n> {res['error']}')
            if choice in ['nombre de usuario', 'username', 'quiero editar mi nombre de usuario']:
                while True:
                    newUsername = input('\n> ingresa tu nuevo nombre de usuario')
                    if not newUsername:
                        print('\n> el nombre de usuario no puede estar vacio')
                        continue
                    if newUsername.isdigit():
                        print('\n> el nombre de usuario no puede contener solo numeros')
                        continue
                    response = requests.get(BASE_URL, params={'newUsername': newUsername})
                    if response.status_code == 409:  # integrity error
                        res = response.json()
                        print(f'\n> {res['error']}')
                        continue
                    if response.status_code == 200:
                        if re.match('[a-zA-Z._1234567890]', newUsername):
                            if len(newUsername) >= 8:
                                response = requests.put(BASE_URL, json={'userId': userId, 'username': newUsername})
                                if response.status_code == 200:
                                    res = response.json()
                                    print(f'\n> {res['succes']}')
                                    return
                                if response.status_code == 500:
                                    res = response.json()
                                    print(f'\n> {res['error']}')
                                    return
                            else:
                                print('\n> el nombre de usuario es muy corto, intenta con otro')
                        else:
                            print('\n> el nombre de usuario es invalido, intenta combinando caracteres, numeros y mayusculas, ej: Usuario._1234')
                    if response.status_code == 500:
                        res = response.json()
                        print(f'\n> {res['error']}')  # error interno del servidor
                        return
        except KeyboardInterrupt:
            print(" interrupcion")
        except requests.exceptions.ConnectionError:
            print('error en la conexion del servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo http')

    def delete_user(self):
        userId = self.user[0]
        BASE_URL = 'http://127.0.0.1:5000/api/version1/delete-user'
        while True:
            passConfirm = pwinput('\n> si eliminas tu usuario, sera borrada tu cuenta y todos los datos con ella, ingresa tu contraseña para confirmar, de lo contrario presiona ctrl+c', mask='*')
            confirmP = requests.get(BASE_URL, params={'password': passConfirm, 'userId': userId})  # solicitud de confirmacion para contraseña
            if confirmP.status_code == 200:
                print('\n> eliminando usuario')
                time.sleep(1)
                deleteU = requests.delete(BASE_URL, json={'userId': userId})  # solicitud de eliminacion de usuario
                if deleteU.status_code == 200:
                    break
                if deleteU.status_code == 500:
                    res = deleteU.json()
                    print(res['error'])
                    self.delete_user()
            if confirmP.status_code == 400:
                res = confirmP.json()
                print(f'\n> {res['error']}')


class PostsProfile():
    def __init__(self, data):
        self.user = data

    def postProfile(self):
        try:
            while True:
                choice = input(f'\n{crudPosts}')
                if choice == '1':
                    self.readPosts()
                elif choice == '2':
                    self.createPost()
                elif choice == '3':
                    self.updatePost()
                elif choice == '4':
                    self.deletePost()
                elif choice == '5':
                    break
                else:
                    raise ValueError()
        except KeyboardInterrupt:
            print('\n> interrupcion en el teclado')
        except ValueError:
            print('\n> ingresa un dato valido')
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion al servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo mediador')

    def readPosts(self):
        BASE_URL = 'http://127.0.0.1:5000/api/version1/posts/read-all-posts-user'
        userId = self.user[0]
        try:
            while True:
                choice = input('\n> (1) ver todas tus publicaciones\n> (2) buscar una publicacion\n> Entrada: ')
                if choice == '1':
                    allposts = requests.get(BASE_URL, params={'userId': userId, 'all': 'all'})
                    if allposts.status_code == 200:  # ok
                        res = allposts.json()
                        df = pd.DataFrame(res)
                        print(f'\n{tabulate(df, headers='keys', tablefmt='psql')}\n')
                        break
                    if allposts.status_code == 400:  # not ok
                        res = allposts.json()
                        print(f'\n> {res['error']}')
                        break
                    if allposts.status_code == 500:  # not ok
                        res = allposts.json()
                        print(f'\n> {res['error']}')
                        continue
                if choice == '2':
                    while True:
                        search = input('\n> busca tu publicacion: ')
                        byone = requests.get(BASE_URL, params={'userId': userId, 'byone': 'one', 'search': search})
                        if byone.status_code == 200:  # ok
                            res = byone.json()
                            df = pd.DataFrame(res)
                            print(f'\n{tabulate(df, headers='keys', tablefmt='psql')}\n')
                        if byone.status_code == 400:
                            res = byone.json()
                            print(f'\n> {res['error']}')
                            continue
                        if byone.status_code == 500:
                            res = byone.json()
                            print(f'\n> {res['error']}')
                            continue
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion al servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en la comunicacion al servidor')
        except KeyboardInterrupt:
            print(' interrupcion del teclado')

    def createPost(self):
        BASE_URL = 'http://127.0.0.1:5000/api/version1/posts/create-post-user'
        userId = self.user[0]
        data = {'userId': userId, 'title': '', 'content': ''}
        try:
            while True:
                title = input('\n> dale un titulo a tu publicacion: ')
                content = input('\n> escribe tu publicacion: ')
                if not title or not content:
                    print('\n> faltan datos para crear la publicacion')
                data['title'] = title
                data['content'] = content
                response = requests.post(BASE_URL, json=data)
                if response.status_code == 201:  # post creado con exito
                    res = response.json()
                    print(f'\n{res['succes']}')
                    break
                if response.status_code == 500:  # error interno en el servidor
                    res = response.json()
                    print(f'\n{res['error']}')
                if response.status_code == 400:
                    res = response.json()
                    print(f'\n> {res['error']}')
        except KeyboardInterrupt:
            print('\n> interrupcion del teclado')
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion del servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo mediador')

    def updatePost(self):
        BASE_URL = 'http://127.0.0.1:5000/api/version1/posts/update-post-user'
        userId = self.user[0]
        alldata = {'userId': userId, 'newT': '', 'newC': '', 'oldC': ''}
        try:
            while True:
                content = input('\n> busca la publicacion que quieres editar: ')
                search = requests.get(BASE_URL, params={'userId': userId, 'oldC': content})
                if search.status_code == 200:
                    match = search.json()
                    data = match['data']  # [{title}, {content}]
                    df = pd.DataFrame(match)
                    print(f'\n{tabulate(df, header='keys', tablefmt='psql')}\n')
                    choice = input('\n> es tu publicacion?: ')
                    if choice in ['si', 'yes', 'sure', 'es la publicacion que busco', 'ok']:
                        alldata['oldC'] = data['content']
                        newTitle = input('\n> ingresa el titulo de tu nueva publicacion, si quieres editar solo la publicacion presiona enter, de lo contrario, escribe y presiona enter: ')
                        if newTitle:
                            alldata['newT'] = newTitle
                        while True:
                            newContent = input('\n> escribe tu nueva publicacion: ')
                            if not newContent:
                                print('\n> tu publicacion no puede estar vacia')
                                continue
                            alldata['newC'] = newContent
                            push = requests.put(BASE_URL, json=alldata)
                            if push.status_code == 200:
                                res = push.json()
                                print(f'\n> {res['succes']}')
                                break
                            if push.status_code == 500:
                                res = push.json()
                                print(f'\n> {res['error']}, vuelve a escribir la nueva publicacion')
                    elif choice in ['nop', 'no', 'no ok', 'no es la publicacion que busco']:
                        print('\n> busca nuevamente')
                        self.updatePost()
                if search.status_code == 400:
                    res = search.json()
                    print(f'\n> {res['error']}')  # no results
                    continue
                if search.status_code == 500:
                    res = search.json()
                    print(f'\n> {res['error']}, vuelve a buscar la publicacion')  # error interno
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion al servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo mediador')

    def deletePost(self):
        BASE_URL = 'http://127.0.0.1:5000/api/version1/posts/delete-post-user'
        userId = self.user[0]
        data = {'userId': userId, 'content': ''}
        try:
            while True:
                search = input('\n> busca el titulo de la publicacion o la publicacion que quieres eliminar: ')
                if not search:
                    print('\n> tienes que buscar la publicacion')
                    continue
                sp = requests.get(BASE_URL, params={'sp': search})
                if sp.status_code == 200:
                    match = sp.json()
                    while True:
                        choice = input(f'\n> esta es la publicacion que buscas?: {match['content']}: ')
                        if not choice:
                            print('\n> tienes que responder')
                            continue
                        if choice in ['si', 'sip', 'esa es la publicacion']:
                            data['content'] = match['content']
                            delP = requests.delete(BASE_URL, json=data)
                            if delP.status_code == 200:
                                match = delP.json()
                                print(f'\n> {match['succes']}')
                                break
                            if delP.status_code == 500:
                                match = delP.json()
                                print(f'\n> {match['error']}, vuelve a buscar la publicacion que quieres eliminar')
                                return self.deletePost()
                if sp.status_code == 400:
                    match = sp.json()
                    print(f'\n> {match['error']}')  # no results
                    continue
                if sp.status_code == 500:
                    match = sp.json()
                    print(f'\n> {match['error']}, vuelve a buscar la publicacion')
        except KeyboardInterrupt:
            print('\n> interrupcion')
        except requests.exceptions.ConnectionError:
            print('\n> error en la conexion del servidor')
        except requests.exceptions.HTTPError:
            print('\n> error en el protocolo')


if __name__ == '__main__':
    try:
        while True:
            choice = input(f'\n{menuLogin}')
            if choice == '1':
                from login import LogIn
                init_sesion = LogIn()
                init_sesion.logIn()
                break
            elif choice == '2':
                from login import LogIn
                sign_up = LogIn()
                sign_up.signUp()
            else:
                print("\n> escoje entre las opciones")
    except KeyboardInterrupt:
        print("\n> saliendo...")
