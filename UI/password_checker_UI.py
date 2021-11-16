from PyQt5 import QtCore, QtWidgets


class Ui_password_checker(object):
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
        self.text_edt1 = QtWidgets.QLineEdit(password_check)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                           QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.text_edt.sizePolicy().hasHeightForWidth())
        self.text_edt.setSizePolicy(sizePolicy)
        self.text_edt.setEchoMode(QtWidgets.QLineEdit.Password)
        self.text_edt.setMinimumSize(QtCore.QSize(250, 30))
        self.text_edt.setMaximumSize(QtCore.QSize(250, 30))
        self.text_edt.setObjectName("text_edt")
        self.lbl1 = QtWidgets.QLabel(password_check)
        self.lbl1.setText("Повторите пароль")
        self.lbl1.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl1.setObjectName("lbl")
        self.text_edt1.setSizePolicy(sizePolicy)
        self.text_edt1.setEchoMode(QtWidgets.QLineEdit.Password)
        self.text_edt1.setMinimumSize(QtCore.QSize(250, 30))
        self.text_edt1.setMaximumSize(QtCore.QSize(250, 30))
        self.text_edt1.setObjectName("text_edt")
        self.verticalLayout.addWidget(self.text_edt)
        self.verticalLayout.addWidget(self.lbl1)
        self.verticalLayout.addWidget(self.text_edt1)
        self.check_btn = QtWidgets.QPushButton(password_check)
        self.check_btn.setObjectName("check_btn")
        self.verticalLayout.addWidget(self.check_btn)
        self.text_edt1.hide()
        self.lbl1.hide()
        self.retranslateUi(password_check)
        QtCore.QMetaObject.connectSlotsByName(password_check)

    def retranslateUi(self, password_check):
        _translate = QtCore.QCoreApplication.translate
        password_check.setWindowTitle(
            _translate("password_check", "Вход"))
        self.check_btn.setText(_translate("password_check", "Далее"))
