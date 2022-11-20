from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel
import sys

# загрузка форм и окон из ui файлов
MainForm, MainWindow = uic.loadUiType("MainWindow.ui")  # главное окно
KonkViewForm, KonkViewWindow = uic.loadUiType("KonkViewWindow.ui")  # окно показа конкурсов
VuzViewForm, VuzViewWindow = uic.loadUiType("VuzViewWindow.ui")  # окно показа вузов
HelpViewForm, HelpViewWindow = uic.loadUiType("HelpViewWindow.ui")  # окно показа справки
HelpProgViewForm, HelpProgViewWindow = uic.loadUiType("HelpProgViewWindow.ui")  # окно показа справки по программе

# инициализация имени базы данных
db_name = 'bd.sqlite'


def check_active_window():
    # проверяет какое окно открыто и возвращает его номер
    for i, window in enumerate(window_list):
        if window.isActiveWindow():
            return i


def open_konk_window():
    # открывает окно показа таблицы конкурсов
    window_list[check_active_window()].close()
    konk_view_window.show()
    table_model = QSqlTableModel()
    table_model.setTable('gr_konk')
    table_model.select()
    konk_view_form.tableView.setSortingEnabled(True)
    konk_view_form.tableView.setModel(table_model)


def open_vuz_window():
    # открывает окно показа таблицы вузов
    window_list[check_active_window()].close()
    vuz_view_window.show()
    table_model = QSqlTableModel()
    table_model.setTable('vuz')
    table_model.select()
    vuz_view_form.tableView.setSortingEnabled(True)
    vuz_view_form.tableView.setModel(table_model)


def open_help_view_window():
    # открывает окно показа справки
    window_list[check_active_window()].close()
    help_view_window.show()


def open_help_prog_view_window():
    # открывает окно показа справки по программе
    window_list[check_active_window()].close()
    help_prog_view_window.show()


def close_prog():
    # закрывает программу
    window_list[check_active_window()].close()


def connect_db():
    # подключает базу данных
    con = QSqlDatabase.addDatabase('QSQLITE')
    con.setDatabaseName(db_name)
    if not con.open():
        print('Не удалось подключиться к базе данных')
        return False
    return con


# проверка подключения к базе данных
if not connect_db():
    sys.exit(-1)
else:
    print('Подключение к базе данных прошло успешно')

app = QApplication([])

# инициализация главного окна
main_window = MainWindow()
main_form = MainForm()
main_form.setupUi(main_window)

# инициализация окна показа таблицы конкурсов
konk_view_window = KonkViewWindow()
konk_view_form = KonkViewForm()
konk_view_form.setupUi(konk_view_window)

# инициализация окна показа таблицы вузов
vuz_view_window = VuzViewWindow()
vuz_view_form = VuzViewForm()
vuz_view_form.setupUi(vuz_view_window)

# инициализация окна показа справки
help_view_window = HelpViewWindow()
help_view_form = HelpViewForm()
help_view_form.setupUi(help_view_window)

# инициализация окна показа справки по программе
help_prog_view_window = HelpProgViewWindow()
help_prog_view_form = HelpProgViewForm()
help_prog_view_form.setupUi(help_prog_view_window)

# список всех окон приложения
window_list = [main_window, konk_view_window, vuz_view_window, help_view_window, help_prog_view_window]

# привязка функций показа таблиц ко кнопкам панели в главном окне
main_form.panel_data_konk.triggered.connect(open_konk_window)
main_form.panel_data_vuz.triggered.connect(open_vuz_window)
main_form.panel_help_view.triggered.connect(open_help_view_window)
main_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
main_form.panel_exit_action.triggered.connect(close_prog)

# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы конкурсов
konk_view_form.panel_data_konk.triggered.connect(open_konk_window)
konk_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
konk_view_form.panel_help_view.triggered.connect(open_help_view_window)
konk_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
konk_view_form.panel_exit_action.triggered.connect(close_prog)

# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы вузов
vuz_view_form.panel_data_konk.triggered.connect(open_konk_window)
vuz_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
vuz_view_form.panel_help_view.triggered.connect(open_help_view_window)
vuz_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
vuz_view_form.panel_exit_action.triggered.connect(close_prog)

# привязка функций показа таблиц ко кнопкам панели в окне показа помощи
help_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_view_form.panel_exit_action.triggered.connect(close_prog)

# привязка функций показа таблиц ко кнопкам панели в окне показа помощи по программе
help_prog_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_prog_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_prog_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_prog_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_prog_view_form.panel_exit_action.triggered.connect(close_prog)

main_window.show()
app.exec()