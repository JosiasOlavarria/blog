#!/usr/bin/env python3
from flask import jsonify, request, Flask
import mysql.connector
from mysql.connector import Error, InternalError, ProgrammingError, InterfaceError, IntegrityError, DatabaseError
import time
from datetime import datetime
import bcrypt
from consults import create_user
app = Flask(__name__)
confDB = {'user': 'root', 'host': 'localhost', 'password': 'ace9029', 'database': 'blog', 'charset': 'utf8mb4', 'collation': 'utf8mb4_unicode_ci'}


def getConnection():
    try:
        conn = mysql.connector.connect(**confDB)
        if conn.is_connected():
            time.sleep(1)
            print("> exito en la conexion a la base de datos")
            return conn
    except InterfaceError as err:
        print(f"> la conexion la base de datos ha sido interrumpida: {str(err)}")
    except DatabaseError as err:
        print(f' error: {str(err)}')
    except Error as err:
        print(f"> error en la conexion a la base de datos: {str(err)}")
    except Exception as err:
        print(f'\n> error: {str(err)}')
    print('\n> no se pudo establecer la conexion a la base de datos')
    return None


# Log in
@app.route('/api/version1/log-in', methods=['POST'])
def LogIn():
    try:
        conn = getConnection()
        if conn is None:
            print('\n> database error')
            return jsonify({'error': 'error en la conexion a la base de datos'}), 500
        if conn:
            cursor = conn.cursor(dictionary=True)
            data = request.json
            username = data.get("username")
            password = data.get("password")
            cursor.execute("SELECT userId, username, password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if user is None:
                return jsonify({"error": "> el usuario ingresado no existe, debes registarte"}), 400
            if 'username' not in data or 'password' not in data:
                return jsonify({'error': 'el nombre de usuario o la contraseña esta vacia'}), 400
            if user['username'] == username and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                userId = user['userId']
                nameuser = user['username']
                return jsonify({'succes': 'inicio de sesion exitoso', 'sesionData': [userId, nameuser]}), 200
            else:
                return jsonify({"error": "> nombre de usuario o contraseña incorrecta"}), 401
    except ProgrammingError as err:
        print(f"> error en la sintaxis de la consulta sql: {str(err)}")
    except IntegrityError as err:
        print(f"> error en la integridad de los datos sql: {str(err)}")
    except Exception as err:
        print(f'\n> error: {str(err)}')
        return jsonify({'error': 'error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# sign up | create user
@app.route('/api/version1/sign-up', methods=['POST', 'GET'])
def SignUp():
    try:
        conn = getConnection()
        if conn is None:
            return jsonify({'error': 'error en la conexion a la base de datos'}), 500
        if conn:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET':
                confirm_username = request.args.get('username')
                cursor.execute('SELECT username FROM users WHERE username=%s', (confirm_username,))
                match = cursor.fetchone()
                if match is not None:
                    return jsonify({'error': 'este nombre ya esta en uso'}), 409
                else:
                    return jsonify({'succes': 'succes'}), 200
            if request.method == 'POST':
                data = request.json
                fullname = data.get('fullname')
                birthdate = data.get('birthdate')
                gmail = data.get('gmail')
                username = data.get('username')
                password = data.get('password')
                salt = bcrypt.gensalt()
                formatingdate = datetime.strptime(birthdate, '%y-%m-%d')
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
                cursor.execute(create_user, (fullname, formatingdate, gmail, username, hashed_password))
                conn.commit()
                print('\n> nuevo usuario creado')
                return jsonify({'succes': 'usuario registrado con exito'}), 201
    except ProgrammingError as e:
        print(f"> error en la sintaxis del la consulta sql: {str(e)}")
        return jsonify({'error': '> error en la consulta a la base de datos'}), 500
    except Exception as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': 'error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# CRUD user
# read user
@app.route('/api/version1/readData/<int:userId>', methods=['GET'])
def readData(userId):
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT username, fullname,  birthdate, gmail FROM users WHERE userId = %s", (userId,))
            dataUser = cursor.fetchone()
    except ProgrammingError as err:
        print(f"> error en la sintaxis sql: {err}")
    else:
        return jsonify(dataUser), 200
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# Update data
@app.route('/api/version1/update-user', methods=['GET', 'PUT'])
def updateDataUser():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET' and request.args.get('actualPassword'):
                confirmP = request.args.data('actualPassword')
                userId = request.args.data('userId')
                cursor.execute('SELECT password FROM users WHERE userId = %s', (userId,))
                actualP = cursor.fetchone()
                if bcrypt.checkpw(confirmP.encode('utf-8'), actualP.encode('utf-8')):
                    return 200
                else:
                    return jsonify({'error': 'las contraseñas no coinciden'}), 400
            if request.method == 'GET' and request.args.get('newUsername'):
                confirmU = request.args.get('newUsername')
                cursor.execute('SELECT username FROM users WHERE username = %s', (confirmU,))
                match = cursor.fetchone()
                if match is not None:
                    return jsonify({'error': 'nombre de usuario en uso, intenta con otro'}), 409
                return 200
            if request.method == 'PUT':
                data = request.json
                if 'newPassword' in data:
                    newPassword = data.get('newPassword')
                    userId = data.get('userId')
                    salt = bcrypt.gensalt()
                    hashedpassword = bcrypt.hashpw(newPassword.encode('utf-8'), salt)
                    cursor.execute('UPDATE users SET password = %s WHERE userId = %s', (hashedpassword, userId))
                    conn.commit()
                    return jsonify({'succes': 'contraseña actualizada'}), 200
            if request.method == 'PUT':
                data = request.json
                if 'newUsername' in data:
                    newUsername = data.get('newUsername')
                    userId = data.get('userId')
                    cursor.execute('UPDATE users SET username = %s WHERE userId = %s', (newUsername, userId))
                    conn.commit()
                    return jsonify({'succes': 'nombre de usuario actualizado'}), 200
    except ProgrammingError as err:
        print(f"> error en la sintaixs de la consulta sql: {err}")
    except InternalError:
        return jsonify({'error': 'error interno en el servidor'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# delete
@app.route('/api/version1/delete-user/', methods=['DELETE', 'GET'])
def deleteUser():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET' and request.args.get('password'):
                confirmP = request.args.get('password')
                userId = request.args.get('userId')
                cursor.execute('SELECT password FROM users WHERE userId = %s', (userId,))
                actualP = cursor.fetchone()
                if bcrypt.checkpw(confirmP.endcode('utf-8'), actualP.encode('utf-8')):
                    return 200
                else:
                    return 400
            if request.method == 'DELETE':
                data = request.json
                userId = data.get('userId')
                cursor.execute('DELETE FROM users WHERE userId = %s', (userId,))
                conn.commit()
                return 200
    except InternalError:
        return jsonify({'error': 'error interno del servidor'}), 500
    except ProgrammingError:
        print('\n> error en la sintaxis de la consulta sql')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# all posts from all users
@app.route('/api/version1/posts/show-all-posts-users', methods=['GET'])
def showAllPosts():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT users.username, posts.title, posts.content FROM users INNER JOIN posts ON users.userId = posts.userId')  # [{username, title, content}]
            allPosts = cursor.fetchall()
            if not allPosts:
                return jsonify({'empty': 'aun no hay publicaciones'}), 400
            return jsonify(allPosts), 200
    except InternalError:
        return jsonify({'error': 'error interno en la conexion al servidor'}), 500
    except ProgrammingError:
        return jsonify({'error': '> error en la sintaxis de la consulta sql'}), 400
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# read all posts user
@app.route('/api/version1/posts/read-all-posts-user', methods=['GET'])
def readAllPostUser():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            all = request.args.get('all')
            one = request.args.get('byone')
            if all:
                userId = request.args.get('userId')
                cursor.execute('SELECT posts.title, posts.content FROM users INNER JOIN posts ON users.userId = posts.userId WHERE users.userId = %s', (userId,))
                allposts = cursor.fetchall()  # array of dicts
                if not allposts:
                    return jsonify({'error': 'no hay publicaciones aun'}), 400
                return jsonify({'succes': 'tus publicaciones', 'data': allposts}), 200
            if one:
                inpt = request.args.get('search')
                userId = request.args.get('userId')
                cursor.execute('SELECT title, content FROM posts WHERE MATCH(content) AGAINST(%s) AND userId = %s', (inpt, userId))
                post = cursor.fetchone()
                if not post:
                    return jsonify({'error': 'no hay coincidencias'}), 400
                return jsonify({'data': post}), 200
            return jsonify({'error': 'error inesperado'}), 500
    except ProgrammingError:
        print('\n> error en la consulta sql')
        return jsonify({'error': 'error en la consulta a la base de datos'}), 500
    except InternalError:
        print('\n> error en el servidor')
        return jsonify({'error': 'error interno en el servidor'}), 500
    except Exception as e:
        print(f'> error :{str(e)}')
        return jsonify({'error': 'error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# create post
@app.route('/api/version1/posts/create-post-user', methods=['POST'])
def createPost():
    try:
        conn = getConnection()
        if conn:
            cursor = c.cursor(dictionary=True)
            data = request.json
            userId = data.get('userId')
            title = data.get('title')
            content = data.get('content')
            if 'content' in data and data['content'] and 'title' in data and data['title']:
                cursor.execute('INSERT INTO posts(userId, title, content) VALUES(%s,%s,%s)', (userId, title, content))
                conn.commit()
                print(f'\n> publicacion creada\n> titulo: {title}\n> publicacion: {content}')
                return jsonify({'succes': 'exito en la creacion de la publicacion'}), 201
            else:
                return jsonify({'error': '> error en la creacion, faltan datos'}), 400
    except ProgrammingError as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': '> error en la consulta a la base de datos'}), 500
    except InternalError as e:
        print(f'error: {str(e)}')
        return jsonify({'error': 'error interno del servidor'}), 500
    except Exception as e:
        print(f'> error inesperado: {str(e)}')
        return jsonify({'error': 'error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# update post
# SELECT * FROM tabla WHERE MATCH(columna) AGAINST(input);
@app.route('/api/version1/posts/update-post-user', methods=['GET', 'PUT'])
def updatePost():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET':
                userId = request.args.get('userId')
                oldC = request.args.get('oldC')
                cursor.execute('SELECT content FROM posts WHERE MATCH(content) AGAINST(%s)', (oldC,))
                match = cursor.fetchone()
                if not match:
                    return jsonify({'error': 'no hay coincidencias'}), 400
                elif match:
                    return jsonify({'succes': 'exito', 'data': match}), 200
            if request.method == 'PUT':
                data = request.json
                userId = data.get('userId')
                newT = data.get('newT')
                newC = data.get('newC')
                oldC = data.get('oldC')
                if not newT['newT']:
                    if newC['newC']:
                        cursor.execute('UPDATE posts SET content = %s WHERE content = %s AND userId = %s', (newC, oldC, userId ))
                        conn.commit()
                        return jsonify({'succes': 'tu publicacion ha sido actualizada'}), 200
                elif newT['newT']:
                    cursor.execute('UPDATE posts SET title = %s, content = %s WHERE title = %s AND content = %s AND userId = %s', (newT, newC, userId))
                    conn.commit()
                    return jsonify({'succes': 'tu publicacion ha sido actiualizada'}), 200
    except ProgrammingError:
        print('\n> error en la consulta sql')
        return jsonify({'error': 'error en la consulta a la base de datos'}), 500
    except InternalError as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': 'error interno del servidor'}), 500
    except Exception as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': '> error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


# delete post
@app.route('/api/version1/posts/delete-post-user', methods=['DELETE', 'GET'])
def deletePost():
    try:
        conn = getConnection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            if request.method == 'GET':
                content = request.args.get('sp')
                cursor.execute('SELECT content FROM posts WHERE MATCH(content) AGAINST(%s)', (content,))
                match = cursor.fetchone()
                if match:
                    return jsonify(match), 200
                elif not match:
                    return jsonify({'error': 'no hay coincidencias, busca de nuevo'}), 400
            if request.method == 'DELETE':
                data = request.json
                userId = data.get('userId')
                content = data.get('content')
                cursor.execute('DELETE FROM posts WHERE usersId = %s AND content',  (userId, content))
                conn.commit()
                return jsonify({'succes': 'publicacionn eliminada'})
    except ProgrammingError as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': '> error en la consulta a la base de datos'}), 500
    except InternalError as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': 'error interno del servidor'}), 500
    except Exception as e:
        print(f'\n> error: {str(e)}')
        return jsonify({'error': '> error inesperado'}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
