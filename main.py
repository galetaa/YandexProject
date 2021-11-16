import sys, sqlite3, string, random
from typing import List
from PyQt5 import QtCore, QtGui, QtWidgets
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
from base64 import b64encode, b64decode
from UI.main_UI import Ui_MainForm
from UI.password_checker_UI import Ui_password_checker


class MainForm(QtWidgets.QWidget, Ui_MainForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.key = ''
        # создаём все события программы
        self.new_btn.clicked.connect(self.new_password)
        self.del_btn.clicked.connect(self.delete_row)
        self.save_btn.clicked.connect(self.update)
        self.table.itemChanged.connect(self.base_updater)
        self.table.cellDoubleClicked.connect(self.paste_safe_password)

    def new_password(self):
        # ф-ия создания новой строки таблицы
        self.con = sqlite3.connect('db/db.sqlite3')
        cur = self.con.cursor()
        l = len(cur.execute("SELECT * FROM passwords").fetchall())
        self.table.insertRow(self.table.rowCount())
        # создаём пустую строку с '' в каждой ячейке, для пароля нужно
        # отправить в бд зашифрованную с помощью ключа пользователя строку ''
        cur.execute(
            "INSERT INTO passwords(id, name, login, password) VALUES (" + str(
                l + 1) + ", '', '', " + "'" + AES_Tool('', self.key).encrypt()
            + "'" + ");")
        self.con.commit()
        self.update()

    def delete_row(self):
        # ф-ия удаления выделенных строк таблицы
        self.con = sqlite3.connect('db/db.sqlite3')
        rows = list(set([i.row() for i in self.table.selectedItems()]))
        ids = [str(i + 1) for i in rows]
        valid = QtWidgets.QMessageBox.question(
            self, '', 'Вы уверены?',
            QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if valid == QtWidgets.QMessageBox.Yes:
            cur = self.con.cursor()
            cur.execute("DELETE FROM passwords WHERE id IN (" + ", ".join(
                '?' * len(ids)) + ")", ids)
            self.con.commit()
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM passwords").fetchall()
        num_db_rows = len(res)
        # заново раздаём id для каждой строки, начиная с 1
        for i in range(1, num_db_rows + 1):
            cur = self.con.cursor()
            cur.execute(
                "UPDATE passwords SET id = " + str(i) + " WHERE id = "
                + str(res[i - 1][0]))
            self.con.commit()
        self.update()

    def update(self):
        # ф-ия для обновления данных таблицы в соответствии с бд
        self.con = sqlite3.connect('db/db.sqlite3')
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM passwords").fetchall()
        self.table.setRowCount(len(res))
        for i, elem in enumerate(res):
            for j, val in enumerate(elem[1:]):
                if j != 2:
                    self.table.setItem(i, j, QtWidgets.QTableWidgetItem(
                        str(val)))
                else:
                    self.table.setItem(i, j, QtWidgets.QTableWidgetItem(
                        AES_Tool(val, self.key).decrypt()))
        # пометка "слабых" паролей
        for i in range(len(res)):
            if self.table.item(i, 2).text() != '':
                if not check_user_password(self.table.item(i, 2).text()):
                    self.table.item(i, 2).setBackground(
                        QtGui.QColor(255, 255, 153))
                    self.table.item(i, 2).setToolTip('Unsafe password')
                else:
                    self.table.item(i, 2).setToolTip('')

    def paste_safe_password(self, row, col):
        # когда пользователь начинает заполнять пароль в пустую ячейку
        # предлагаем вставить туда "безопасный" пароль
        if col == 2 and self.table.item(row, col).text() == '':
            valid = QtWidgets.QMessageBox.question(
                self, '', 'Вставить надёжный пароль?',
                QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if valid == QtWidgets.QMessageBox.Yes:
                self.table.item(row, col).setText(generate_user_password())

    def get_key(self, key_from_check_form):
        # ф-ия для получения ключа доступа к бд из окна ввода пароля
        self.key = key_from_check_form
        if not authorize_check(self.key):
            sys.exit(app.exec_())

    def base_updater(self, item):
        # ф-ия для обновления данных в бд в соответствии с изменёнными данными
        # таблицы
        self.con = sqlite3.connect('db/db.sqlite3')
        row = item.row()
        col = item.column()
        txt = item.text()
        cur = self.con.cursor()
        if col == 0:
            cur.execute(
                "UPDATE passwords SET name = " + "'" + txt + "'" + "WHERE id ="
                + str(row + 1))
        elif col == 1:
            cur.execute(
                "UPDATE passwords SET login = " + "'" + txt + "'" + "WHERE id ="
                + ' ' + str(row + 1))
        else:
            cur.execute("UPDATE passwords SET password = " + "'"
                        + AES_Tool(txt, self.key).encrypt()
                        + "'" + "WHERE id =" + str(row + 1))
        self.con.commit()
        self.originalBG = self.table.item(0, 0).background()
        if col == 2:
            if check_user_password(txt) or txt == '':
                self.table.item(row, 2).setToolTip('')
                self.table.item(row, 2).setBackground(self.originalBG)
            else:
                self.table.item(row, 2).setBackground(
                    QtGui.QColor(255, 255, 153))
                self.table.item(row, 2).setToolTip('Ненадёжный пароль')


class PasswordChecker(QtWidgets.QWidget, Ui_password_checker):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.entered_before = False
        # проверка, что пользователь уже заходил для показа верной информации
        try:
            _ = open('db/db.sqlite3')
        except IOError:
            self.lbl.setText('Придумайте пароль для входа')
            self.lbl1.show()
            self.text_edt1.show()
        else:
            self.lbl.setText('Введите пароль')
            self.entered_before = True
        self.check_btn.clicked.connect(self.check_entered_password)

    def check_entered_password(self):
        # ф-ия проверяющая пароль введённый в QLineEdit, сравнивает со
        # значением которое ввёл пользователь для проверки пароля, а если до
        # этого пользователь не пользовался программой, создаёт бд
        key = self.text_edt.text()
        if key != '':
            if self.entered_before:
                if authorize_check(key):
                    MyApp2.show()
                    self.hide()
                    MainForm.get_key(MainForm, key)
                    MyApp2.update()
                else:
                    self.lbl.setText('Неправильный пароль')
            else:
                if self.text_edt.text() == self.text_edt1.text():
                    MyApp2.show()
                    self.hide()
                    con = sqlite3.connect(
                        'db/db.sqlite3')
                    cur = con.cursor()
                    # создание таблицы в бд, в которой хранятся все данные,
                    # которые далее и будут показываться в QTable
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS passwords(id INTEGER,"
                        "name TEXT, login TEXT, password TEXT);")
                    con.commit()
                    # создание таблицы бд для хранения пароля для будущего
                    # доступа к программе в зашифрованном ввиде
                    cur.execute("CREATE TABLE IF NOT EXISTS enterpassword("
                                "password TEXT);")
                    cur.execute(
                        "INSERT INTO enterpassword(password) VALUES (" + "'" +
                        AES_Tool('password', key).encrypt() + "'" + ");")
                    con.commit()
                else:
                    self.lbl.setText('Пароли должны совпадать')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.check_entered_password()


class AES_Tool:
    # класс для работы с зашифрованными с помощью стандарта шифроваия AES
    # данными в бд
    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (
                self.block_size - len(s) % self.block_size) * chr(
            self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        # ф-ия зашифровки строки
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return b64encode(iv + cipher.encrypt(plain_text.encode())).decode()

    def decrypt(self):
        # ф-ия расшифровки строки
        cipher_text = b64decode(self.data.encode())
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return self.unpad(
            cipher.decrypt(cipher_text[self.block_size:])).decode()


def authorize_check(key):
    # ф-ия проверки правильности введённого пароля, посредством расшифровки
    # сообщения "password" с помощью данного ключа
    cur = sqlite3.connect('db/db.sqlite3').cursor()
    encrypted = cur.execute("SELECT * FROM enterpassword").fetchall()
    if AES_Tool(encrypted[0][0], key).decrypt() == 'password':
        return True
    return False


def generate_user_password():
    # ф-ия для создания надёжного пароля
    def generate_random_string(length: int, *choices: str):
        if not choices:
            choices = (string.ascii_letters,)
        all_choices = "".join(choices)
        result: List[str] = []
        choice_index = 0
        while len(result) < length:
            if choice_index < len(choices):
                symbol = random.choice(choices[choice_index])
                result.append(symbol)
                choice_index += 1
                continue
            symbol = random.choice(all_choices)
            result.append(symbol)
        random.shuffle(result)
        return "".join(result)

    res = generate_random_string(16, string.ascii_uppercase,
                                 string.ascii_lowercase,
                                 string.digits, "_-")
    while not check_user_password(res):
        res = generate_random_string(16, string.ascii_uppercase,
                                     string.ascii_lowercase,
                                     string.digits, "_-")
    return res


def check_user_password(pswrd):
    # ф-ия проверки пароля
    DIGITS = '0123456789'
    KEYBOARD = 'qwertyuiop   asdfghjkl   zxcvbnm   ' \
               'йцукенгшщзхъ   фывапролджэё   ячсмитьбю'
    fl = False
    if len(pswrd) <= 8:
        return
    for i in pswrd:
        if i in DIGITS:
            fl = True
    if not fl:
        return
    if pswrd.islower() or pswrd.isupper():
        return
    if pswrd.isdigit():
        return
    for i in range(len(pswrd)):
        if i != 0 and i != len(pswrd) - 1:
            x = pswrd[i - 1:i + 2]
            if pswrd[i - 1:i + 2].lower() in KEYBOARD:
                return
    return True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    Myapp = PasswordChecker()
    MyApp2 = MainForm()
    Myapp.show()
    sys.exit(app.exec_())
