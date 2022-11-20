from PyQt6 import uic
#from PyQt6.QtCore import Qt..
from PyQt6.QtWidgets import QApplication, QHeaderView
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import sys, copy

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
query_sql_filter_temp = {}
query_sql_filter_save = ""

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

    query = QSqlQuery("""SELECT codkon AS "Код конкурса",
                         g1 AS "Код НИР",
                         g8 AS "Руководитель НИР",
                         g6 AS "Наименование НИР",
                         g7 AS "Код по ГРНТИ",
                         z2 AS "Наименование вуза" ,
                         g5 AS "Плановый объем",
                         g2 AS "Фактический объем гранта"
                         FROM gr_proj""")

    table_model.setQuery(query)
    
    proj_view_form.tableView.setModel(table_model)
    proj_view_form.tableView.setSortingEnabled(True)
    proj_view_form.tableView.resizeColumnsToContents()



def proj_select_check():
    curr_index = proj_view_form.tableView.currentIndex()
    print(curr_index.sibling(curr_index.row(), 1).data()) # 1 - индекс нужного столбца


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
    # открывает окно фильтрации таблицы конкурсов

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

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    query = QSqlQuery("""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city, vuz.z2 AS z2
                         FROM gr_proj as proj
                         INNER JOIN vuz ON proj.codvuz == vuz.codvuz""")

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


def proj_filter_codkon():
    # фильтрует по коду конкурса
    # надо сделать более динамическим и других

    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()

    if combo_box_filter_codkon == "Нет" and 'proj.codkon' in query_sql_filter_temp:
        del query_sql_filter_temp['proj.codkon']
    elif combo_box_filter_codkon == "Нет":
        pass
    else:
        query_sql_filter_temp['proj.codkon'] = combo_box_filter_codkon

    cond_filter = ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    if len(query_sql_filter_temp) != 0:
        query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    else:
        query_sql_filter = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query_sql_filter)

    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city as city, vuz.z2 AS z2
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    set_region = set()
    set_oblname = set()
    set_city = set()
    set_z2 = set()

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

    if len(set_region) == 1 and 'vuz.region' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_region.addItems(list(set_region))
    else:
        proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))

    if len(set_oblname) == 1 and 'vuz.oblname' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_oblname.addItems(list(set_oblname))
    else:
        proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))

    if len(set_city) == 1 and 'vuz.city' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_city.addItems(list(set_city))
    else:
        proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))

    if len(set_z2) == 1 and 'vuz.z2' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_z2.addItems(list(set_z2))
    else:
        proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_region():
    # фильтрует по региону конкурса

    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()

    if combo_box_filter_region == "Нет" and 'vuz.region' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.region']
    elif combo_box_filter_region == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.region'] = combo_box_filter_region

    cond_filter = ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    if len(query_sql_filter_temp) != 0:
        query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    else:
        query_sql_filter = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query_sql_filter)

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.oblname AS oblname, vuz.city as city, vuz.z2 AS z2
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    set_codkon = set()
    set_oblname = set()
    set_city = set()
    set_z2 = set()

    query = QSqlQuery(query_sql_filter)

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_oblname.add(str(query.value(1)))
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()

    if len(set_codkon) == 1 and 'proj.codkon' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_codkon.addItems(list(set_codkon))
    else:
        proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    if len(set_oblname) == 1 and 'vuz.oblname' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_oblname.addItems(list(set_oblname))
    else:
        proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))

    if len(set_city) == 1 and 'vuz.city' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_city.addItems(list(set_city))
    else:
        proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))

    if len(set_z2) == 1 and 'vuz.z2' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_z2.addItems(list(set_z2))
    else:
        proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_oblname():
    # фильтрует по субъекту РФ конкурса

    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_oblname = proj_filter_form.combo_box_filter_oblname.currentText()

    if combo_box_filter_oblname == "Нет" and 'vuz.oblname' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.oblname']
    elif combo_box_filter_oblname == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.oblname'] = combo_box_filter_oblname

    cond_filter = ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    if len(query_sql_filter_temp) != 0:
        query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    else:
        query_sql_filter = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query_sql_filter)

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.city as city, vuz.z2 AS z2
                                      FROM gr_proj as proj
                                      INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                      WHERE {cond_filter}""")

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    set_codkon = set()
    set_region = set()
    set_city = set()
    set_z2 = set()

    query = QSqlQuery(query_sql_filter)

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_region.add(str(query.value(1)))
        set_city.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()

    if len(set_codkon) == 1 and 'proj.codkon' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_codkon.addItems(list(set_codkon))
    else:
        proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    if len(set_region) == 1 and 'vuz.region' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_region.addItems(list(set_region))
    else:
        proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))

    if len(set_city) == 1 and 'vuz.city' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_city.addItems(list(set_city))
    else:
        proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))

    if len(set_z2) == 1 and 'vuz.z2' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_z2.addItems(list(set_z2))
    else:
        proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_city():
    # фильтрует по городу конкурса

    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_city = proj_filter_form.combo_box_filter_city.currentText()

    if combo_box_filter_city == "Нет" and 'vuz.city' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.city']
    elif combo_box_filter_city == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.city'] = combo_box_filter_city

    cond_filter = ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    if len(query_sql_filter_temp) != 0:
        query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    else:
        query_sql_filter = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query_sql_filter)

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.z2 AS z2
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    set_codkon = set()
    set_region = set()
    set_oblname = set()
    set_z2 = set()

    query = QSqlQuery(query_sql_filter)

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_region.add(str(query.value(1)))
        set_oblname.add(str(query.value(2)))
        set_z2.add(str(query.value(3)))

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_z2.clear()

    if len(set_codkon) == 1 and 'proj.codkon' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_codkon.addItems(list(set_codkon))
    else:
        proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    if len(set_region) == 1 and 'vuz.region' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_region.addItems(list(set_region))
    else:
        proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))

    if len(set_oblname) == 1 and 'vuz.oblname' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_oblname.addItems(list(set_oblname))
    else:
        proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))

    if len(set_z2) == 1 and 'vuz.z2' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_z2.addItems(list(set_z2))
    else:
        proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_z2():
    # фильтрует по вузу конкурса

    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_z2 = proj_filter_form.combo_box_filter_z2.currentText()

    if combo_box_filter_z2 == "Нет" and 'vuz.z2' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.z2']
    elif combo_box_filter_z2 == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.z2'] = combo_box_filter_z2

    cond_filter = ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    if len(query_sql_filter_temp) != 0:
        query_sql_filter = QSqlQuery(f"""SELECT proj.*
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")
    else:
        query_sql_filter = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query_sql_filter)

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city
                                     FROM gr_proj as proj
                                     INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     WHERE {cond_filter}""")

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    set_codkon = set()
    set_region = set()
    set_oblname = set()
    set_city = set()

    query = QSqlQuery(query_sql_filter)

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_region.add(str(query.value(1)))
        set_oblname.add(str(query.value(2)))
        set_city.add(str(query.value(3)))

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()

    if len(set_codkon) == 1 and 'proj.codkon' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_codkon.addItems(list(set_codkon))
    else:
        proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    if len(set_region) == 1 and 'vuz.region' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_region.addItems(list(set_region))
    else:
        proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))

    if len(set_oblname) == 1 and 'vuz.oblname' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_oblname.addItems(list(set_oblname))
    else:
        proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))

    if len(set_city) == 1 and 'vuz.city' in query_sql_filter_temp:
        proj_filter_form.combo_box_filter_city.addItems(list(set_city))
    else:
        proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))


def proj_filter_save():
    # сохранение фильтра

    global query_sql_filter_save
    global query_sql_filter_temp

    query_sql_filter_save = copy.deepcopy(query_sql_filter_temp)


def proj_filter_reset():
    # удаление фильтра

    global query_sql_filter_save
    global query_sql_filter_temp

    query_sql_filter_temp = {}
    query_sql_filter_save = {}

    table_model = QSqlTableModel()

    query = QSqlQuery("SELECT * FROM gr_proj")

    table_model.setQuery(query)

    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)

    query = QSqlQuery("SELECT codkon FROM gr_konk")

    set_codkon, set_region, set_oblname, set_city, set_z2 = set(), set(), set(), set(), set()

    while query.next():
        set_codkon.add(str(query.value(0)))

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))

    query = QSqlQuery("""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city, vuz.z2 AS z2
                         FROM gr_proj as proj
                         INNER JOIN vuz ON proj.codvuz == vuz.codvuz""")

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


def proj_filter_check():
    print('temp',query_sql_filter_temp)
    print('save',query_sql_filter_save)


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
proj_view_form.push_button_select_check.clicked.connect(proj_select_check)

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
proj_filter_form.push_button_filter_reset.clicked.connect(proj_filter_reset)


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
