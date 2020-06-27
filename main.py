import sqlite3
from flask import Flask, request, render_template, make_response, url_for, redirect, session
from random import randint
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '936ec63693b47733017578f9a19c6695f72836a3'

users = dict()


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password


class DbUsers:
    @staticmethod
    def create_user(login, password):
        with sqlite3.connect(r'E:\Tutorial\Python\flask_test\test.db') as conn:
            cursor = conn.cursor()
            # cursor.execute('create table users (name text, age integer)')
            # for i in range(10000):
            cursor.execute(f'insert into blackjack (login, password) values ("{login}", "{password}")')

    @staticmethod
    def read_user(login: str) -> User:
        with sqlite3.connect(r'E:\Tutorial\Python\flask_test\test.db') as conn:
            cursor = conn.cursor()
            cursor.execute('select * from blackjack')
            users = cursor.fetchall()
            for user in users:
                if user[0] == login:
                    return User(user[0], user[1])

    @staticmethod
    def change_password(login, new_password):
        with sqlite3.connect(r'E:\Tutorial\Python\flask_test\test.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f'update blackjack set password = "{new_password}" where login = "{login}"')

    @staticmethod
    def change_login(new_login):
        old_login = session['login']
        with sqlite3.connect(r'E:\Tutorial\Python\flask_test\test.db') as conn:
            cursor = conn.cursor()
            cursor.execute(f'update blackjack set login = "{new_login}" where login = "{old_login}"')
        session['login'] = new_login


class CsvUsers:
    @staticmethod
    def create_user(login, password):
        user = [login, password]
        with open(r'users.csv', 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(user)

    @staticmethod
    def read_user(login):
        try:
            with open(r'users.csv', 'r', newline='') as file:
                reader = csv.reader(file, delimiter=';')
                for user in reader:
                    if len(user) > 0 and user[0] == login:
                        return User(user[0], user[1])
        except FileNotFoundError:
            pass

    @staticmethod
    def read_users() -> list:

        with open(r'users.csv', 'r', newline='') as file:
            reader = csv.reader(file, delimiter=';')
            return list(reader)
            # new_users = []
            # for user in reader:
            #     if user[0] == login:
            #         user[1] == new_password
            #     new_users.append(user)

    @staticmethod
    def write_users(users):
        with open(r'users.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows(users)

    @staticmethod
    def change_password(login, new_password):
        users = CsvUsers.read_users()
        for user in users:
            if user[0] == login:
                user[1] = new_password
                break
        CsvUsers.write_users(users)

    @staticmethod
    def change_login(new_login):
        old_login = session['login']
        users = CsvUsers.read_users()
        for user in users:
            if user[0] == old_login:
                user[0] = new_login
                session['login'] = new_login
                break
        CsvUsers.write_users(users)


# users2 = DbUsers()


users2 = CsvUsers()


@app.route('/game/')
def game():
    if 'login' not in session:
        return redirect(url_for('login'))
    if session['login'] == 'tom':
        users.clear()
    return render_template('blackjack.html')


@app.route('/game/', methods=['post'])
def game_post():
    name = session['login']  # request.cookies.get('login')
    users[name] = users.get(name, 0) + randint(1, 11)
    return render_template('blackjack.html', count=users[name])


@app.route('/login/', methods=['get', 'post'])
def login():
    if request.method == 'POST':
        # res = make_response('')
        user_login = request.form.get('login')
        user_password = request.form.get('pas')
        user = users2.read_user(user_login)
        if not user:
            return render_template('login_game.html', fail='Такого пользователя нет')
        # elif user.password != user_password:
        #     return render_template('login_game.html', fail='Вы ввели неверный пароль')
        if user.login == user_login and user.password == str(user_password):
            session['login'] = user_login
            session['password'] = user_password
            # if user[2] == 'admin':
            #     session['adm'] = '1'
            return redirect(url_for('game'))
    return render_template('login_game.html')

    # res.set_cookie('login', user_login, 60 * 60)
    # res.headers['location'] = url_for('game')
    # return res, 302
    # session['login'] = request.form.get('login')
    # return redirect(url_for('game'))


@app.route('/register/')
def register():
    return render_template('register.html')


@app.route('/register/', methods=['post'])
def register_post():
    log = request.form.get('log')
    pas = request.form.get('pass')
    if users2.read_user(log):
        return render_template('register.html', fail='Такой пользователь уже зарегистрирован.')
    users2.create_user(log, pas)
    return redirect(url_for('login'))


# @app.route('/')
# def f_get():
#     if request.remote_addr == '192.168.100.7':
#
#         count_Ant = 0
#         return render_template('blackjack.html', count=count_Ant)
#     elif request.remote_addr == '192.168.100.9':
#         count_And = 0
#         return render_template('blackjack.html', count=count_And)
#     else:
#         return 'ВЫ НЕ ИЗ НАШЕЙ ДЕРЕВНИ.'


@app.route('/result/', methods=['get', 'post'])
def result():
    return render_template('result.html', users=users)


@app.route('/changepassword/')
def changepassword_get():
    return render_template('changepassword.html')


@app.route('/changepassword/', methods=['post'])
def changepassword_post():
    login = session['login']
    old_password = session['password']
    old_password_form = request.form.get('oldpassword')
    new_password = request.form.get('newpassword')
    if old_password != old_password_form:
        return render_template('changepassword.html', fail='Вы ввели неверный старый пароль')
    elif old_password == new_password:
        return render_template('changepassword.html', fail='Старый и новый пароли равны')
    users2.change_password(login, new_password)
    return redirect(url_for('login'))


@app.route('/changelogin/')
def changelogin_get():
    return render_template('changelogin.html')


@app.route('/changelogin/')
def changelogin_post():
    old_login = session['login']
    new_login = request.form.get('newlogin')
    # if old_login == new_login:
    #     return render_template('changelogin.html', fail='Старый и новый логины равны')
    if users2.read_user(new_login):
        return render_template('changelogin.html', fail='Такой логин уже используется')
    users2.change_login(new_login)
    return redirect(url_for('login'))


# @app.route('/', methods=['post'])
# def f_post():
#     warning = ''
#     global count_Ant, count_And
#     if request.remote_addr == '192.168.100.7':
#         count_Ant += randint(2, 11)
#         if count_Ant > 21:
#             warning = '; Перебор'
#         elif count_Ant == 21:
#             warning = '; BlackJack'
#         return render_template('blackjack.html', count=count_Ant, warning=warning)
#
#     elif request.remote_addr == '192.168.100.9':
#         count_And += randint(2, 11)
#         if count_And > 21:
#             warning = '; Перебор'
#         elif count_And == 21:
#             warning = '; BlackJack'
#         return render_template('blackjack.html', count=count_And, warning=warning)


if __name__ == '__main__':
    app.run(host='192.168.100.9', port=80, debug=True)

# if request.method == 'POST':
#
#     request.cookies.get('test')
#     res = make_response("")
#     res.set_cookie("font", request.form.get('font'), 60 * 60 * 24 * 15)
#     #res.headers['Set-Cookie'] = f'font={request.form.get("font")}; Expires=Thu, 04-Jun-2020 21:22:55 GMT; Max-Age=120; Path=/'
#     res.headers['location'] = url_for('article')
#     res.headers['fuck'] = 'Fuck you'
#     return res, 302
#
# return render_template('article.html')
