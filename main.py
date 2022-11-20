from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import *
import sys

Form, Window = uic.loadUiType("./my_dop/MainForm.ui")

db_name = './my_dop/bd.sqlite'

def on_click_proj():
    table_model = QSqlTableModel()
    table_model.setTable('gr_proj')
    table_model.select()
    form.tableView1.setSortingEnabled(True)
    form.tableView1.setModel(table_model)

def on_click_konk():
    table_model = QSqlTableModel()
    table_model.setTable('gr_konk')
    table_model.select()
    form.tableView1.setSortingEnabled(True)
    form.tableView1.setModel(table_model)

def on_click_vuz():
    table_model = QSqlTableModel()
    table_model.setTable('vuz')
    table_model.select()
    form.tableView1.setSortingEnabled(True)
    form.tableView1.setModel(table_model)

def connect_db(db_name):
    con = QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(db_name)
    if not con.open():
        print('не удалось подключиться к базе')
        return False
    return con

if not connect_db(db_name):
    sys.exit(-1)
else:
    print('Connection OK')

app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

form.pushButton1.clicked.connect(on_click_proj)
form.pushButton2.clicked.connect(on_click_konk)
form.pushButton3.clicked.connect(on_click_vuz)

window.show()
app.exec()