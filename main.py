import sys, sqleet, string, random
from typing import List
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainForm(QtWidgets.QWidget):
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
        cur = self.con.cursor()
        l = len(cur.execute("SELECT * FROM passwords").fetchall())
        self.table.insertRow(self.table.rowCount())
        # создаём пустую строку с '' в каждой ячейке
        cur.execute(
            "INSERT INTO passwords(id, name, login, password) VALUES (" + str(
                l + 1) + ", '', '', '');")
        self.con.commit()
        self.update()

    def delete_row(self):
        rows = list(set([i.row() for i in self.table.selectedItems()]))
        ids = [str(i + 1) for i in rows]
        valid = QtWidgets.QMessageBox.question(
            self, '', 'Может не надо?',
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
        cur = self.con.cursor()
        res = cur.execute("SELECT * FROM passwords").fetchall()
        self.table.setRowCount(len(res))
        for i, elem in enumerate(res):
            for j, val in enumerate(elem[1:]):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(
                    str(val)))
        # пометка "слабых" паролей
        for i in range(len(res)):
            if self.table.item(i, 2).text() != '':
                if not check_password(self.table.item(i, 2).text()):
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
                self.table.item(row, col).setText(generate_password())

    def get_key(self, keyy):
        # ф-ия для получения ключа доступа к бд из окна ввода пароля
        self.key = keyy
        try:
            self.con = sqleet.connect(
                'PasswordManager/db.sqlite3', key=self.key)
        except sqleet.AuthenticationError:
            sys.exit(app.exec_())

    def base_updater(self, item):
        # ф-ия для обновления данных в бд в соответствии с изменёнными данными
        # таблицы
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
            cur.execute(
                "UPDATE passwords SET password = " + "'" + txt + "'" + "WHERE "
                                                                       "id ="
                + str(row + 1))
        self.con.commit()
        self.originalBG = self.table.item(0, 0).background()
        if col == 2:
            if check_password(txt) or txt == '':
                self.table.item(row, 2).setToolTip('')
                self.table.item(row, 2).setBackground(self.originalBG)
            else:
                self.table.item(row, 2).setBackground(
                    QtGui.QColor(255, 255, 153))
                self.table.item(row, 2).setToolTip('Unsafe password')

    def setupUi(self, MainForm):
        MainForm.setObjectName("MainForm")
        MainForm.resize(994, 518)
        MainForm.setMinimumSize(QtCore.QSize(994, 300))
        self.mainLayout = QtWidgets.QVBoxLayout(MainForm)
        self.mainLayout.setContentsMargins(0, -1, 0, -1)
        self.mainLayout.setSpacing(7)
        self.mainLayout.setObjectName("mainLayout")
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.layout.setHorizontalSpacing(20)
        self.layout.setVerticalSpacing(7)
        self.layout.setObjectName("layout")
        self.del_btn = QtWidgets.QPushButton(MainForm)
        self.del_btn.setObjectName("del_btn")
        self.layout.addWidget(self.del_btn, 1, 1, 1, 1)
        self.save_btn = QtWidgets.QPushButton(MainForm)
        self.save_btn.setObjectName("save_btn")
        self.layout.addWidget(self.save_btn, 1, 2, 1, 1)
        self.new_btn = QtWidgets.QPushButton(MainForm)
        self.new_btn.setObjectName("new_btn")
        self.layout.addWidget(self.new_btn, 1, 0, 1, 1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        self.table = QtWidgets.QTableWidget(MainForm)
        self.table.setMinimumSize(QtCore.QSize(950, 200))
        self.table.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.table.setObjectName("tableWidget")
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        self.table.horizontalHeader().setCascadingSectionResizes(False)
        self.table.horizontalHeader().setDefaultSectionSize(310)
        self.table.horizontalHeader().setSortIndicatorShown(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setSortIndicatorShown(False)
        self.table.verticalHeader().setStretchLastSection(False)
        self.layout.addWidget(self.table, 0, 0, 1, 3)
        self.mainLayout.addLayout(self.layout)

        self.retranslateUi(MainForm)
        QtCore.QMetaObject.connectSlotsByName(MainForm)

    def retranslateUi(self, MainForm):
        _translate = QtCore.QCoreApplication.translate
        MainForm.setWindowTitle(_translate("MainForm", "Password Manager 2000"))
        self.del_btn.setText(_translate("MainForm", "Delete"))
        self.save_btn.setText(_translate("MainForm", "Save"))
        self.new_btn.setText(_translate("MainForm", "New Password"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("MainForm", "Name"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("MainForm", "Login"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("MainForm", "Password"))


class Ui_password_check(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # проверка, что пользователь уже заходил
        try:
            _ = open('PasswordManager/db.sqlite3')
        except IOError:
            self.lbl.setText('Come up with password')
        else:
            self.lbl.setText('Enter the password')
        self.check_btn.clicked.connect(self.check_password)

    def check_password(self):
        key = self.text_edt.text()
        try:
            _ = open('PasswordManager/db.sqlite3')
        except IOError:
            if key != '':
                MyApp2.show()
                self.hide()
                con = sqleet.connect(
                    'PasswordManager/db.sqlite3', key=key)
                cur = con.cursor()
                cur.execute("CREATE TABLE IF NOT EXISTS passwords(id INTEGER,"
                            "name TEXT, login TEXT, password TEXT);")
                con.commit()
                Ui_MainForm.get_key(Ui_MainForm, key)
            else:
                self.lbl.setText('Enter normal password')
        else:
            try:
                _ = sqleet.connect(
                    'PasswordManager/db.sqlite3', key=key)
            except Exception:
                self.lbl.setText('Incorrect password')
            else:
                MyApp2.show()
                self.close()
                Ui_MainForm.get_key(Ui_MainForm, key)
                MyApp2.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.check_password()

    def setupUi(self, password_check):
        password_check.setObjectName("password_check")
        password_check.resize(278, 120)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            password_check.sizePolicy().hasHeightForWidth())
        password_check.setSizePolicy(sizePolicy)
        password_check.setMaximumSize(QtCore.QSize(278, 120))
        password_check.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.verticalLayout = QtWidgets.QVBoxLayout(password_check)
        self.verticalLayout.setContentsMargins(-1, 7, -1, 10)
        self.verticalLayout.setSpacing(7)
        self.verticalLayout.setObjectName("verticalLayout")
        self.lbl = QtWidgets.QLabel(password_check)
        self.lbl.setText("")
        self.lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        self.text_edt = QtWidgets.QLineEdit(password_check)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.text_edt.sizePolicy().hasHeightForWidth())
        self.text_edt.setSizePolicy(sizePolicy)
        self.text_edt.setMinimumSize(QtCore.QSize(250, 30))
        self.text_edt.setMaximumSize(QtCore.QSize(250, 30))
        self.text_edt.setObjectName("text_edt")
        self.verticalLayout.addWidget(self.text_edt)
        self.check_btn = QtWidgets.QPushButton(password_check)
        self.check_btn.setObjectName("check_btn")
        self.verticalLayout.addWidget(self.check_btn)

        self.retranslateUi(password_check)
        QtCore.QMetaObject.connectSlotsByName(password_check)

    def retranslateUi(self, password_check):
        _translate = QtCore.QCoreApplication.translate
        password_check.setWindowTitle(
            _translate("password_check", "Enter"))
        self.check_btn.setText(_translate("password_check", "OK"))


def generate_password():
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
    while not check_password(res):
        res = generate_random_string(16, string.ascii_uppercase,
                                     string.ascii_lowercase,
                                     string.digits, "_-")
    return res


def check_password(pswrd):
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
    Myapp = Ui_password_check()
    MyApp2 = Ui_MainForm()
    Myapp.show()
    sys.exit(app.exec_())
