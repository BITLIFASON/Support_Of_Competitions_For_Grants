from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import sys

#       !!! проблема с Нет !!! в фильтрации

# загрузка форм и окон из ui файлов
MainForm, MainWindow = uic.loadUiType("MainWindow.ui")  # главное окно
ProjViewForm, ProjViewWindow = uic.loadUiType("ProjViewWindow.ui")  # окно показа проектов
ProjSortForm, ProjSortWindow = uic.loadUiType("ProjSortWindow.ui") # окно сортировки проектов
ProjFilterForm, ProjFilterWindow = uic.loadUiType("ProjFilterWindow.ui") # окно фильтрации проектов
KonkViewForm, KonkViewWindow = uic.loadUiType("KonkViewWindow.ui")  # окно показа конкурсов
VuzViewForm, VuzViewWindow = uic.loadUiType("VuzViewWindow.ui")  # окно показа вузов
HelpViewForm, HelpViewWindow = uic.loadUiType("HelpViewWindow.ui")  # окно показа справки
HelpProgViewForm, HelpProgViewWindow = uic.loadUiType("HelpProgViewWindow.ui")  # окно показа справки по программе


# инициализация имени базы данных
db_name = 'bd.sqlite'

# инициализация фильтра
query_sql_filter_save = None

def check_active_window():
    # проверяет какое окно открыто и возвращает его номер
    for i, window in enumerate(window_list):
        if window.isActiveWindow():
            return i


def open_proj_window():
    # открывает окно показа таблицы конкурсов
    window_list[check_active_window()].close()
    proj_view_window.show()
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM gr_proj")
    table_model.setQuery(query)
    proj_view_form.tableView.setSortingEnabled(True)
    proj_view_form.tableView.setModel(table_model)


def proj_select_check():
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM gr_proj")
    table_model.setQuery(query)
    rows = sorted(set(index.row() for index in proj_view_form.tableView.selectionModel().selectedRows()))
    for row in rows:
        print('Row %d is selected' % row)
        print(table_model.data(table_model.index(row, 1)))


def open_proj_sort_window():
    # открывает окно показа таблицы конкурсов
    window_list[check_active_window()].close()
    proj_sort_window.show()
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM gr_proj")
    table_model.setQuery(query)
    proj_sort_form.tableView.setSortingEnabled(True)
    proj_sort_form.tableView.setModel(table_model)


def proj_sort():
    # сортирует таблицу конкурсов
    combo_cond_sort_g1 = proj_sort_form.combo_box_order_g1.currentText()
    combo_cond_sort_codkon = proj_sort_form.combo_box_order_codkon.currentText()
    table_model = QSqlTableModel()
    cond_sort_g1 = "ASC" if combo_cond_sort_g1 == "По возрастанию" else "DESC"
    cond_sort_codkon = "ASC" if combo_cond_sort_codkon == "По возрастанию" else "DESC"
    query_sort = QSqlQuery(f"SELECT * FROM gr_proj ORDER BY g1 {cond_sort_g1}, codkon {cond_sort_codkon}")
    table_model.setQuery(query_sort)
    proj_sort_form.tableView.setSortingEnabled(True)
    proj_sort_form.tableView.setModel(table_model)


def open_proj_filter_window():
    # открывает окно показа таблицы конкурсов
    window_list[check_active_window()].close()
    proj_filter_window.show()
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM gr_proj")
    table_model.setQuery(query)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    query = QSqlQuery("SELECT codkon FROM gr_konk")
    set_codkon, set_region, set_oblname, set_city, set_z2 = set(), set(), set(), set(), set()
    while query.next():
        set_codkon.add(str(query.value(0)))
    proj_filter_form.combo_box_filter_codkon.addItems(sorted(list(set_codkon)))
    query = QSqlQuery("""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city,proj.z2 AS z2
                         FROM gr_proj as proj
                         INNER JOIN vuz ON proj.codvuz == vuz.codvuz""")
    while query.next():
        set_region.add(str(query.value(0)))
        set_oblname.add(str(query.value(1)))
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))
    table_model
    proj_filter_form.combo_box_filter_region.addItems(sorted(list(set_region)))
    proj_filter_form.combo_box_filter_oblname.addItems(sorted(list(set_oblname)))
    proj_filter_form.combo_box_filter_city.addItems(sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(sorted(list(set_z2)))


def proj_filter_codkon():
    # фильтрует по коду конкурса
    #       !!! проблема с Нет !!!
    table_model = QSqlTableModel()
    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()
    cond_filter = f"codkon == \"{combo_box_filter_codkon}\""
    query_sql_filter = QSqlQuery(f"""SELECT * FROM gr_proj WHERE {cond_filter}""")
    table_model.setQuery(query_sql_filter)
    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city, proj.z2 AS z2
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    set_region, set_oblname, set_city, set_z2 = set(), set(), set(), set()
    query = QSqlQuery(query_sql_filter)
    while query.next():
        set_region.add(str(query.value(0)))
        set_oblname.add(str(query.value(1)))
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()
    proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))
    proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))
    proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_region():
    # фильтрует по региону конкурса
    table_model = QSqlTableModel()
    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()
    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()
    cond_filter = f"proj.codkon == \"{combo_box_filter_codkon}\" AND vuz.region == \"{combo_box_filter_region}\""
    query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    table_model.setQuery(query_sql_filter)
    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city,proj.z2 AS z2
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    set_oblname, set_city, set_z2 = set(), set(), set()
    query = QSqlQuery(query_sql_filter)
    while query.next():
        set_oblname.add(str(query.value(1)))
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()
    proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))
    proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_oblname():
    # фильтрует по субъекту РФ конкурса
    table_model = QSqlTableModel()
    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()
    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()
    combo_box_filter_oblname = proj_filter_form.combo_box_filter_oblname.currentText()
    cond_filter = f"proj.codkon == \"{combo_box_filter_codkon}\" " \
                  f"AND vuz.region == \"{combo_box_filter_region}\" " \
                  f"AND vuz.oblname == \"{combo_box_filter_oblname}\""
    query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    table_model.setQuery(query_sql_filter)
    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city,proj.z2 AS z2
                                        FROM gr_proj as proj
                                        INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                        WHERE {cond_filter}""")
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    set_city, set_z2 = set(), set()
    query = QSqlQuery(query_sql_filter)
    while query.next():
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()
    proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_city():
    # фильтрует по городу конкурса
    table_model = QSqlTableModel()
    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()
    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()
    combo_box_filter_oblname = proj_filter_form.combo_box_filter_oblname.currentText()
    combo_box_filter_city = proj_filter_form.combo_box_filter_city.currentText()
    cond_filter = f"proj.codkon == \"{combo_box_filter_codkon}\" " \
                  f"AND vuz.region == \"{combo_box_filter_region}\" " \
                  f"AND vuz.oblname == \"{combo_box_filter_oblname}\"" \
                  f"AND vuz.city == \"{combo_box_filter_city}\""
    query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                         FROM gr_proj as proj
                                         INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                         WHERE {cond_filter}""")
    table_model.setQuery(query_sql_filter)
    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city,proj.z2 AS z2
                                            FROM gr_proj as proj
                                            INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                            WHERE {cond_filter}""")
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    set_z2 = set()
    query = QSqlQuery(query_sql_filter)
    while query.next():
        set_z2.add(str(query.value(3)))
    proj_filter_form.combo_box_filter_z2.clear()
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_z2():
    # фильтрует по вузу конкурса
    table_model = QSqlTableModel()
    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()
    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()
    combo_box_filter_oblname = proj_filter_form.combo_box_filter_oblname.currentText()
    combo_box_filter_city = proj_filter_form.combo_box_filter_city.currentText()
    combo_box_filter_z2 = proj_filter_form.combo_box_filter_z2.currentText()
    cond_filter = f"proj.codkon == \"{combo_box_filter_codkon}\" " \
                  f"AND vuz.region == \"{combo_box_filter_region}\" " \
                  f"AND vuz.oblname == \"{combo_box_filter_oblname}\"" \
                  f"AND vuz.city == \"{combo_box_filter_city}\"" \
                  f"AND vuz.z2 == \"{combo_box_filter_z2}\""
    query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                             FROM gr_proj as proj
                                             INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                             WHERE {cond_filter}""")
    table_model.setQuery(query_sql_filter)
    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city,proj.z2 AS z2
                                                FROM gr_proj as proj
                                                INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                                WHERE {cond_filter}""")
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)


def proj_filter_save():
    combo_box_filter_codkon = ("proj.codkon", proj_filter_form.combo_box_filter_codkon.currentText())
    combo_box_filter_region = ("vuz.region", proj_filter_form.combo_box_filter_region.currentText())
    combo_box_filter_oblname = ("vuz.oblname", proj_filter_form.combo_box_filter_oblname.currentText())
    combo_box_filter_city = ("vuz.city", proj_filter_form.combo_box_filter_city.currentText())
    combo_box_filter_z2 = ("vuz.z2",proj_filter_form.combo_box_filter_z2.currentText())
    combo_box_filter_list = [combo_box_filter_codkon, combo_box_filter_region, combo_box_filter_oblname, combo_box_filter_city, combo_box_filter_z2]
    global query_sql_filter_save
    query_sql_filter_save = ""
    flag = True
    for combo_box_filter in combo_box_filter_list:
        if combo_box_filter[1] != "Нет":
            if query_sql_filter_save != "":
                query_sql_filter_save += " AND "
            if combo_box_filter[0] != "vuz.z2":
                query_sql_filter_save += f"{combo_box_filter[0]} == \"{combo_box_filter[1]}\""
            else:
                query_sql_filter_save += f"{combo_box_filter[0]} == \"{combo_box_filter[1]}\""
            flag = False
    if flag:
        query_sql_filter_save = ""


def proj_filter_check():
    print(query_sql_filter_save)


def open_konk_window():
    # открывает окно показа таблицы конкурсов
    window_list[check_active_window()].close()
    konk_view_window.show()
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM gr_konk")
    table_model.setQuery(query)
    konk_view_form.tableView.setSortingEnabled(True)
    konk_view_form.tableView.setModel(table_model)


def open_vuz_window():
    # открывает окно показа таблицы вузов
    window_list[check_active_window()].close()
    vuz_view_window.show()
    table_model = QSqlTableModel()
    query = QSqlQuery("SELECT * FROM vuz")
    table_model.setQuery(query)
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


# инициализация окна показа таблицы проектов
proj_view_window = ProjViewWindow()
proj_view_form = ProjViewForm()
proj_view_form.setupUi(proj_view_window)
proj_view_form.push_button_sort.clicked.connect(open_proj_sort_window)
proj_view_form.push_button_filter.clicked.connect(open_proj_filter_window)
proj_view_form.pushButton.clicked.connect(proj_select_check)

# инициализация окна сортировки таблицы проектов
proj_sort_window = ProjSortWindow()
proj_sort_form = ProjSortForm()
proj_sort_form.setupUi(proj_sort_window)
proj_sort_form.push_button_sort.clicked.connect(proj_sort)


# инициализация окна фильтрации таблицы проектов
proj_filter_window = ProjFilterWindow()
proj_filter_form = ProjFilterForm()
proj_filter_form.setupUi(proj_filter_window)
proj_filter_form.push_button_set_codkon.clicked.connect(proj_filter_codkon)
proj_filter_form.push_button_set_region.clicked.connect(proj_filter_region)
proj_filter_form.push_button_set_oblname.clicked.connect(proj_filter_oblname)
proj_filter_form.push_button_set_city.clicked.connect(proj_filter_city)
proj_filter_form.push_button_set_z2.clicked.connect(proj_filter_z2)
proj_filter_form.push_button_filter_save.clicked.connect(proj_filter_save)
proj_filter_form.push_button_filter_check.clicked.connect(proj_filter_check)


# инициализация окна показа справки
help_view_window = HelpViewWindow()
help_view_form = HelpViewForm()
help_view_form.setupUi(help_view_window)


# инициализация окна показа справки по программе
help_prog_view_window = HelpProgViewWindow()
help_prog_view_form = HelpProgViewForm()
help_prog_view_form.setupUi(help_prog_view_window)


# список всех окон приложения
window_list = [main_window, konk_view_window, vuz_view_window, proj_view_window,  help_view_window, help_prog_view_window, proj_sort_window, proj_filter_window]


# привязка функций показа таблиц ко кнопкам панели в главном окне
main_form.panel_data_konk.triggered.connect(open_konk_window)
main_form.panel_data_vuz.triggered.connect(open_vuz_window)
main_form.panel_data_proj.triggered.connect(open_proj_window)
main_form.panel_help_view.triggered.connect(open_help_view_window)
main_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
main_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы конкурсов
konk_view_form.panel_data_konk.triggered.connect(open_konk_window)
konk_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
konk_view_form.panel_data_proj.triggered.connect(open_proj_window)
konk_view_form.panel_help_view.triggered.connect(open_help_view_window)
konk_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
konk_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы вузов
vuz_view_form.panel_data_konk.triggered.connect(open_konk_window)
vuz_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
vuz_view_form.panel_data_proj.triggered.connect(open_proj_window)
vuz_view_form.panel_help_view.triggered.connect(open_help_view_window)
vuz_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
vuz_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы проектов
proj_view_form.panel_data_konk.triggered.connect(open_konk_window)
proj_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_view_form.panel_data_proj.triggered.connect(open_proj_window)
proj_view_form.panel_help_view.triggered.connect(open_help_view_window)
proj_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне сортировки таблицы проектов
proj_sort_form.panel_data_konk.triggered.connect(open_konk_window)
proj_sort_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_sort_form.panel_data_proj.triggered.connect(open_proj_window)
proj_sort_form.panel_help_view.triggered.connect(open_help_view_window)
proj_sort_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_sort_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне фильтрации таблицы проектов
proj_filter_form.panel_data_konk.triggered.connect(open_konk_window)
proj_filter_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_filter_form.panel_data_proj.triggered.connect(open_proj_window)
proj_filter_form.panel_help_view.triggered.connect(open_help_view_window)
proj_filter_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_filter_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа помощи
help_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_view_form.panel_data_proj.triggered.connect(open_proj_window)
help_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа помощи по программе
help_prog_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_prog_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_prog_view_form.panel_data_proj.triggered.connect(open_proj_window)
help_prog_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_prog_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_prog_view_form.panel_exit_action.triggered.connect(close_prog)


main_window.show()
app.exec()
