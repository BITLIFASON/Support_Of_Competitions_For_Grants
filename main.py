#Подключение бибилотек
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QLineEdit, QComboBox
from PyQt6.QtSql import *
import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from SecondWindow import Ui_Dialog
from SecondWindow import Ui_Dialog
# задаем путь и имя нашей БД
db_name = 'databases/bd.sqlite'
#Создаем форму и окно для каждого окна
Form, Window = uic.loadUiType("MainWindow.ui")
Form1, Window1 = uic.loadUiType("FirstWindow.ui")
Form2, Window2 = uic.loadUiType("SecondWindow.ui")
Form3, Window3 = uic.loadUiType("ThirdWindow.ui")
Form4, Window4 = uic.loadUiType("ForthWindow.ui")
Form5, Window5 = uic.loadUiType("FifthWindow.ui")

#Функция , которая выводит таблицу с просмотром информации о конкурсах на  соискание  грантов
def on_click_konk_na_soiskanie(self):
    table_model = QSqlTableModel()
    table_model.setTable('gr_konk_1')
    table_model.select()
    form3.tableView2.setSortingEnabled(True)
    form3.tableView2.setModel(table_model)

#Функция , которая выводит таблицу с просмотром информации о НИР выполняемых по грантам
def on_click_konk_na_soiskanie1(self):
    table_model = QSqlTableModel()
    table_model.setTable('nir_po_grantam')
    table_model.select()
    form3.tableView2.setSortingEnabled(True)
    form3.tableView2.setModel(table_model)

#Функция , которая выводит таблицу gr_proj
def on_click_proj():
    table_model = QSqlTableModel()
    table_model.setTable('gr_proj')
    table_model.select()
    form1.tableView1.setSortingEnabled(True)
    form1.tableView1.setModel(table_model)

#Функция , которая выводит таблицу gr_konk
def on_click_konk():
    table_model = QSqlTableModel()
    table_model.setTable('gr_konk')
    table_model.select()
    form1.tableView1.setSortingEnabled(True)
    form1.tableView1.setModel(table_model)

#Функция , которая выводит таблицу vuz
def on_click_vuz():
    table_model = QSqlTableModel()
    table_model.setTable('vuz')
    table_model.select()
    form1.tableView1.setSortingEnabled(True)
    form1.tableView1.setModel(table_model)

#Подключение к нашей БД
def connect_db(db_name):
    con = QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(db_name)
    if not con.open():
        print('не удалось подключиться к базе')
        return False
    return con

#Функция , которая открывает первое окно , в котором мы можем  выводить исходные таблицы
def open_First_Window():
    window.close()
    window1.show()
    form1.pushButton1.clicked.connect(on_click_proj)
    form1.pushButton2.clicked.connect(on_click_konk)
    form1.pushButton3.clicked.connect(on_click_vuz)
# Функция , которая при нажатии на кнопку выводит нас обратно на главное окно
    def returnToMain():
        window1.close()
        window.show()
    form1.pb_first_window_back.clicked.connect(returnToMain)

# Функция , которая открывает второе окно , в котором мы просматриваем доп информацию
def open_Second_Window():
    window.close()
    window2.show()
    form2.pushButton4.clicked.connect(open_Third_Window)
    form2.pushButton4.clicked.connect(on_click_konk_na_soiskanie)
    form2.pushButton8.clicked.connect(open_Third_Window)
    form2.pushButton8.clicked.connect(on_click_konk_na_soiskanie1)
# Функция , которая при нажатии на кнопку возвращает нас на главное окно
    def returnToMain():
        window2.close()
        window.show()
    form2.pushButton6.clicked.connect(returnToMain)

#Функция , которая открывает третье окно , в которое выводится доп информация
def open_Third_Window():
    window2.close()
    window3.show()
#Функция , которая возвращает нас на предыдущее окно
    def returnToLastWindow():
        window3.close()
        window2.show()
    form3.pushButton7.clicked.connect(returnToLastWindow)

#Функция , которая преобразовывает в текст выбранное пользователем окно
def input_data():
    data = form4.comboBox
    text = data.currentText()
    print(text)

#Функция , которая выходит с пятого окна в главное
def to_main_from_5():
    window5.close()
    window.show()

#Функция , которая возвращает к главному окну
def fun_exit():
    window4.close()
    window.show()

#Фукнция , которая открывает четвертое окно , в котором мы выбираем в какую таблицу добавляем строки
def open_Forth_Window():
    window.close()
    window4.show()
    data = form4.comboBox
    text = data.currentText()
    form4.pb_forth_window_choose.clicked.connect(input_data)
    form4.pb_forth_window_choose.clicked.connect(open_Fifth_Window)
    form4.pb_forth_window_exit.clicked.connect(fun_exit)




#Функция , которая открывает пятое окно , в котором мы вводим значение строки , которое добавляем в таблицу
def open_Fifth_Window():
    window4.close()
    window5.show()
    data_k2 = form5.lineEdit_k2
    data_codkon = form5.lineEdit_codkon
    data_k12 = form5.lineEdit_k12
    data_k4 = form5.lineEdit_k4
    data_k41 = form5.lineEdit_k41
    data_k42 = form5.lineEdit_k42
    data_k43 = form5.lineEdit_k43
    data_k44 = form5.lineEdit_k44
    data_npr=form5.lineEdit_npr
#Функция , которая преобразовывает записанные пользователем значеия в текст
    def input_data_gr_kon():
        text_k2=data_k2.text()
        text_codkon=data_codkon.text()
        text_k12=data_k12.text()
        text_k4=data_k4.text()
        text_k41=data_k41.text()
        text_k42=data_k42.text()
        text_k43=data_k43.text()
        text_k44=data_k44.text()
        text_npr=data_npr.text()
        values=[text_k2,text_codkon,int(text_k12),int(text_k4),int(text_k41),int(text_k42),int(text_k43),int(text_k44),int(text_npr)]
        #добавляем в таблицу новую строку и добавляем часть этой строки в доп информацию о соискание грантов
        values1=values[0:2]
        print(values)
        print(values1)
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute('''INSERT INTO gr_konk VALUES(?,?,?,?,?,?,?,?,?)''' , values)
        conn.commit()
        cur = conn.cursor()
        cur.execute('''INSERT INTO gr_konk_1 VALUES(?,?)''', values1)
        conn.commit()


    form5.pb_input.clicked.connect(input_data_gr_kon)
    form5.pb_to_main.clicked.connect(to_main_from_5)

#Функция , которая закрывает главное окно
def close_Main_Window():
    window.close()


if not connect_db(db_name):
    sys.exit(-1)
else:
    print('Connection OK')

app = QApplication([])

#объявляем формы и окна
window = Window()
form = Form()
form.setupUi(window)
form1 = Form1()
window1 = Window1()
form1.setupUi(window1)
form2 = Form2()
window2 = Window2()
form2.setupUi(window2)
form3 = Form3()
window3 = Window3()
form3.setupUi(window3)
form4 = Form4()
window4 = Window4()
form4.setupUi(window4)
form5 = Form5()
window5 = Window5()
form5.setupUi(window5)
#кнопки в главном окна
form.pb_main_window_1.clicked.connect(open_First_Window)
form.pb_main_window_2.clicked.connect(open_Second_Window)
form.pb_main_window_3.clicked.connect(open_Forth_Window)
form.pb_exit.clicked.connect(close_Main_Window)

window.show()
app.exec()