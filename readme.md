# Название: Python Password Manager

# Автор проекта: Галета Михаил

# Описание: 
Классический менеджер папролей на языке Python, при первом запуске в окне 
проверки пароля ввести пароль для дальнейшего входа, 
после чего попадаем на основную страницу, где и располагаются пароли. Далее в этом окне: кнопка "New"-создать новую запись;
												"Delete"-удалить выделенные записи;
												"Save"-сохранить изменения, хотя изменения
												сохраняются сами)
Пароли в таблице хранятся так же вместе с логинами и названием пароля или сайта, чтобы пользователю было удобнее его запомнить. Любые из
этих данных необязательно записывать. Также в программе реализована генерация нового пароля и проверка каждого из существующих, с пометкой 
лёгкого пароля.


# Описание реализации:
Интерфейс написан с помощью PyQt, для БД используется sqleet, так как в нём можно использовать шифрование, для входа в основную часть
программы используется форма проверки пароля, реализованная в виде QWidget, оснавная часть реализована так же. Для передачи информации
о том, что проверка пароля в начальной форме прошла успешна, в основной части программы есть функция get_key(), которая и загружает в 
таблицу QTable данные из БД. 

# Описание технологий + необходимые для запуска библиотеки:
	пример:
	Для работы проекта необходимы:
	0. main.py - '.py' файл проекта
	1. main.exe - основной файл проекта с реализацией
	2. PasswordManager/db.sqlite3 - зашифрованное бд с данными о паролях итд, создаётся после создания пароля
	3. readme.md - файл который вы читаете
	4. requirements.txt - список необходимых библиотек для работы. Для установки запустите: pip install -r requirements.txt
	5. каталог (папка\директория) в которой будет запускаться проект должен быть доступен для записи