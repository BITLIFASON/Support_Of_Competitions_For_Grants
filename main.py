from PyQt6 import uic
from PyQt6.QtWidgets import QApplication
from PyQt6.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
import sys, copy
import sqlite3
from functools import partial
import itertools as it


# загрузка форм и окон из ui файлов
MainForm, MainWindow = uic.loadUiType("MainWindow.ui")  # главное окно
ProjViewForm, ProjViewWindow = uic.loadUiType("ProjViewWindow.ui")  # окно показа проектов
ProjSortForm, ProjSortWindow = uic.loadUiType("ProjSortWindow.ui") # окно сортировки проектов
ProjFilterForm, ProjFilterWindow = uic.loadUiType("ProjFilterWindow.ui") # окно фильтрации проектов
KonkViewForm, KonkViewWindow = uic.loadUiType("KonkViewWindow.ui")  # окно показа конкурсов
VuzViewForm, VuzViewWindow = uic.loadUiType("VuzViewWindow.ui")  # окно показа вузов
HelpViewForm, HelpViewWindow = uic.loadUiType("HelpViewWindow.ui")  # окно показа справки
HelpProgViewForm, HelpProgViewWindow = uic.loadUiType("HelpProgViewWindow.ui")  # окно показа справки по программе
DeleteWindowForm, DeleteWindow = uic.loadUiType("DeleteWindow.ui") # окно с подтверждением удаления строок
AddRowWindowForm, AddRowWindowWindow = uic.loadUiType("AddRowWindow.ui") # окно с добавлением строк
ErrorAddRowForm , ErrorAddRowWindow = uic.loadUiType("Error_row_add.ui") # окно с указанием ошибки добавлекния строки
ChangeForm , ChangeWindow = uic.loadUiType("ChangeWindow.ui") # окно с редактированием строк
AnalysisForm , AnalysisWindow = uic.loadUiType("AnalysisWindow.ui") # окно с редактированием строк


# инициализация имени базы данных
db_name = 'bd.sqlite'


# инициализация фильтра
query_sql_filter_temp = {}
query_sql_filter_save = {}

query_sql_sort_save = {}


def check_active_window():
    # проверяет какое окно открыто и возвращает его номер

    for i, window in enumerate(window_list):
        if window.isActiveWindow():
            return i


def open_proj_window():
    # открывает окно показа таблицы конкурсов

    global query_sql_filter_save

    window_list[check_active_window()].close()
    proj_view_window.showMaximized()

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))
    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                 proj.g1 AS "Код НИР",
                                 proj.g8 AS "Руководитель НИР",
                                 proj.g7 AS "Код по ГРНТИ",
                                 proj.z2 AS "Наименование вуза",
                                 proj.g5 AS "Плановый объем",
                                 proj.g6 AS "Наименование НИР",
                                 proj.g2 AS "Фактический объем гранта",
                                 proj.g21 as"Поквартальное финансирование",
                                 proj.g22 as"Поквартальное финансирование",
                                 proj.g23 as"Поквартальное финансирование",
                                 proj.g24 as"Поквартальное финансирование",
                                 proj.g9 as "Должность руководителя",
                                 proj.g10 as"Учёное звание руководителя",
                                 proj.g11 as"Учёная степень руководителя"
                          FROM gr_proj AS proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                          {cond_filter if query_sql_filter_save != {} else ""}
                          {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query)

    proj_view_form.tableView.setModel(table_model)
    proj_view_form.tableView.setSortingEnabled(True)
    proj_view_form.tableView.resizeColumnsToContents()

    while table_model.canFetchMore():
        table_model.fetchMore()
    proj_view_form.tableView.setFocus()
    proj_view_form.tableView.selectRow(380)


def add_row():
    add_view_window.showMaximized()
    proj_view_window.close()
    # заполняем какие коды уже заняты
    g1=set()
    query = QSqlQuery("SELECT * FROM gr_proj")
    while query.next():
        g1.add(str(query.value(0)))
    result = sorted([int(item) for item in g1])
    result1 =[str(item) for item in result]

    add_view_form.comboBox_cod_nir.addItems(result1)
    #заполняем код конкурса
    query = QSqlQuery("SELECT k2 , codkon FROM gr_konk")
    name_kon=set()
    while query.next():
        name_kon.add(str(query.value(1))+'-'+str(query.value(0)))
    name_kon=list(name_kon)
    add_view_form.comboBox_cod_kon.addItems(sorted(name_kon, key=lambda x:x[:3]))
    # заполняем код вуза и наименование вуза
    name_vuza=set()
    kod_vuza=set()
    query = QSqlQuery("SELECT * FROM vuz")
    while query.next():
        name_vuza.add(str(query.value(3))+ '-' + str(query.value(0)))
    name_vuza=list(name_vuza)
    add_view_form.comboBox_cod_vuz.addItems(sorted(name_vuza, key=lambda x: x[:3]))
    add_view_form.pushButton_back.clicked.connect(return_back)
    add_view_form.pushButton_add_row.clicked.connect(partial(read_data_add_row, result1))


def read_data_add_row(result1):
    # Чтение с лейблов и боксов
    table_model = QSqlTableModel()
    proj_view_form.tableView.setModel(table_model)
    data_g1 = add_view_form.lineEdit_g1.text()
    data_g7 = add_view_form.lineEdit_g7.text()
    data_g5 = add_view_form.lineEdit_g5.text()
    data_g2 = add_view_form.lineEdit_g2.text()
    data_g21 = add_view_form.lineEdit_g21.text()
    data_g22 = add_view_form.lineEdit_g22.text()
    data_g23 = add_view_form.lineEdit_g23.text()
    data_g24 = add_view_form.lineEdit_g24.text()
    data_g6 = add_view_form.lineEdit_g6.text()
    data_g8 = add_view_form.lineEdit_g8.text()
    data_g9 = add_view_form.lineEdit_g9.text()
    data_g10 = add_view_form.lineEdit_g10.text()
    data_g11 = add_view_form.lineEdit_g11.text()
    data_cod_kon = add_view_form.comboBox_cod_kon.currentText()
    data_cod_vuza = add_view_form.comboBox_cod_vuz.currentText()
    j=0
    add_error_text=str()
    #Провекра вводимых данных
    # Проверка g1
    simbol="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+,-./:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    if (any((c in data_g1) for c in simbol) or data_g1==''):
        j=j+1
        add_error_text=add_error_text+str('Вы ввели неверное значение g1- '+str(data_g1)+' - А ожидался код нира не из списка примечаний')

    else:
        if int(data_g1) in list(map(int, result1)):
            j = j + 1
            add_error_text = add_error_text + str(
                'Вы ввели неверное значение g1- ' + str(data_g1) + ' - А ожидался код нира не из списка примечаний')

    stroka = [(data_g1), data_cod_kon, (data_cod_vuza),  data_g7, data_g5, (data_g2),
              (data_g21), data_g22,
              (data_g23), (data_g24), data_g6, data_g8, data_g9, data_g10, data_g11]
    # проверка ввода g7
    simbol1="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+-/:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    if (any((c in data_g7) for c in simbol1)):
        j=j+1
        add_error_text=add_error_text+str('Вы ввели неверное значение g7- '+data_g7+' - А ожидалось ,например, - 50.09,50.10')
    # Провекра ввода g-g24
    simbol2="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+-/.,:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    data_g5_g24=[data_g5, data_g2,
              data_g21, data_g22,
              data_g23, data_g24]
    data_g5_g24_str = ['g5', 'g2',
                   'g21', 'g22',
                   'g23', 'g24']
    for i in range(len(data_g5_g24)):
        if (any((c in data_g5_g24[i]) for c in simbol1)):
            j=j+1
            add_error_text=add_error_text+str('\nВы ввели неверное значение '+(data_g5_g24_str[i])+' - '+str(data_g5_g24[i])+ ' - А ожидалось целочисленное значение')

    #
    # проверка g6_g11
    data_g6_g11=[data_g6, data_g8, data_g9, data_g10, data_g11]
    data_g6_g11_str = ['g6', 'g8', 'g9', 'g10', 'g11']
    simbol2 = """1234567890!\/"#$%&'()*+-/:;<=>?@[]^_`{|}~"""
    for i in range(len(data_g6_g11)):
        if (any((c in data_g6_g11[i]) for c in simbol2)):
            j=j+1
            add_error_text = add_error_text + str(
                '\nВы ввели неверное значение ' + (data_g6_g11_str[i]) + ' - ' + str(
                    data_g6_g11[i]) + ' - А ожидалось текствое значение')

    #Вывод на экран то что значения были введены неверно
    if j>0:
        error_add_row_form.textBrowser.setText(add_error_text)
        error_add_row_window.showMaximized()
    # Добавление элементов с таблицу
    else:
        cod_vuza=int([''.join(x) for _, x in it.groupby(data_cod_vuza, key=lambda c: c=='-')][2])
        name_vuza_add=[''.join(x) for _, x in it.groupby(data_cod_vuza, key=lambda c: c=='-')][0]
        value=[int(data_g1),data_cod_kon[0:2],cod_vuza,name_vuza_add,data_g7,data_g5,data_g2,data_g21,data_g22,data_g23,data_g24,data_g6,data_g8,data_g9,data_g10,data_g11]
        # print(value)
        # for i in range(len(value)):
        #     if value[i]=='':
        #         value[i]=None
        # print(value)
        # for i in range(5,11):
        #     if value[i]!=None:
        #         value[i]=int(value[i])
        # print(value)

        print(value)
        for i in range(5, 11):
            if value[i] != '':
                value[i] = int(value[i])
        print(value)

        # conn=sqlite3.connect(db_name)
        # cur=conn.cursor()
        # cur.execute('''INSERT INTO gr_proj(g1,codkon,codvuz,z2,g7,g5,g2,g21,g22,g23,g24,g6,g8,g9,g10,g11) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);''',value).fetchall()

        # conn.commit()
        # cur.close()
        # conn.close()
        query = QSqlQuery()
        insert_sql = '''INSERT INTO gr_proj(g1,codkon,codvuz,z2,g7,g5,g2,g21,g22,g23,g24,g6,g8,g9,g10,g11)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
        query.prepare(insert_sql)
        for v in value:
            query.addBindValue(v)
        if input() == '1':
            query.exec()
        else:
            pass
        print('inserted')


        add_view_window.close()
        proj_view_window.showMaximized()
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


def return_back():
    add_view_window.close()
    proj_view_window.showMaximized()


def proj_select_check():

    def pb_no():
        delete_proj_window.close()
        proj_view_window.showMaximized()

    def pb_yes():
        query = QSqlQuery(f"DELETE FROM gr_proj WHERE g1=={curr_index.sibling(curr_index.row(), 1).data()}")
        table_model.setQuery(query)
        query = QSqlQuery("SELECT * FROM gr_proj")
        table_model.setQuery(query)
        delete_proj_window.close()
        proj_view_window.showMaximized()
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
        proj_view_form.tableView.resizeColumnsToContents()


    table_model = QSqlTableModel()
    global  curr_index
    curr_index = proj_view_form.tableView.currentIndex()
    print(curr_index.sibling(curr_index.row(), 1).data())  # 1 - индекс нужного столбца
    if curr_index.sibling(curr_index.row(), 1).data()!=None:
        proj_view_window.close()
        delete_proj_window.showMaximized()
        query = QSqlQuery(f"""SELECT codkon AS "Код конкурса",
                         g1 AS "Код НИР",
                         g8 AS "Руководитель НИР",
                         g6 AS "Наименование НИР",
                         g7 AS "Код по ГРНТИ",
                         z2 AS "Наименование вуза" ,
                         g5 AS "Плановый объем",
                         g2 AS "Фактический объем гранта"
                         FROM gr_proj WHERE g1=={curr_index.sibling(curr_index.row(), 1).data()}""")

        table_model.setQuery(query)
        delete_proj_form.tableView_delete_row.setModel(table_model)

        delete_proj_form.pushButton_yes.clicked.connect(pb_yes)
        delete_proj_form.pushButton_no.clicked.connect(pb_no)

    else:
        print('Ничего не выбрано')
    delete_proj_form.tableView_delete_row.resizeColumnsToContents()


def read_data_add_row1(spis):
    table_model = QSqlTableModel()
    proj_view_form.tableView.setModel(table_model)
    data_g1 = change_form.lineEdit_g1.text()
    data_g7 = change_form.lineEdit_g7.text()
    data_g5 = change_form.lineEdit_g5.text()
    data_g2 = change_form.lineEdit_g2.text()
    data_g21 = change_form.lineEdit_g21.text()
    data_g22 = change_form.lineEdit_g22.text()
    data_g23 = change_form.lineEdit_g23.text()
    data_g24 = change_form.lineEdit_g24.text()
    data_g6 = change_form.lineEdit_g6.text()
    data_g8 = change_form.lineEdit_g8.text()
    data_g9 = change_form.lineEdit_g9.text()
    data_g10 = change_form.lineEdit_g10.text()
    data_g11 = change_form.lineEdit_g11.text()
    data_cod_kon = change_form.comboBox_cod_kon.currentText()
    data_cod_vuza = change_form.comboBox_cod_vuz.currentText()
    #
    j=0
    add_error_text=str()
    #Провекра вводимых данных
    # Проверка g1
    simbol="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+,-./:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    if (any((c in data_g1) for c in simbol) or data_g1==''):
        j=j+1
        add_error_text=add_error_text+str('Вы ввели неверное значение g1- '+str(data_g1)+' - А ожидался код нира не из списка примечаний')

    stroka = [(data_g1), data_cod_kon, (data_cod_vuza),  data_g7, data_g5, (data_g2),
              (data_g21), data_g22,
              (data_g23), (data_g24), data_g6, data_g8, data_g9, data_g10, data_g11]
    # проверка ввода g7
    simbol1="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+-/:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    if (any((c in data_g7) for c in simbol1)):
        j=j+1
        add_error_text=add_error_text+str('Вы ввели неверное значение g7- '+data_g7+' - А ожидалось ,например, - 50.09,50.10')
    # Провекра ввода g-g24
    simbol2="""abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\/"#$%&'()*+-/.,:;<=>?@[]^_`{|}~абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ """
    data_g5_g24=[data_g5, data_g2,
              data_g21, data_g22,
              data_g23, data_g24]
    data_g5_g24_str = ['g5', 'g2',
                   'g21', 'g22',
                   'g23', 'g24']
    for i in range(len(data_g5_g24)):
        if (any((c in data_g5_g24[i]) for c in simbol1)):
            j=j+1
            add_error_text=add_error_text+str('\nВы ввели неверное значение '+(data_g5_g24_str[i])+' - '+str(data_g5_g24[i])+ ' - А ожидалось целочисленное значение')

    # проверка g6_g11
    data_g6_g11=[data_g6, data_g8, data_g9, data_g10, data_g11]
    data_g6_g11_str = ['g6', 'g8', 'g9', 'g10', 'g11']
    simbol2 = """1234567890!\/"#$%&'()*+-/:;<=>?@[]^_`{|}~"""
    for i in range(len(data_g6_g11)):
        if (any((c in data_g6_g11[i]) for c in simbol2)):
            j=j+1
            add_error_text = add_error_text + str(
                '\nВы ввели неверное значение ' + (data_g6_g11_str[i]) + ' - ' + str(
                    data_g6_g11[i]) + ' - А ожидалось текствое значение')

    #Вывод на экран то что значения были введены неверно
    if j>0:
        error_add_row_form.textBrowser.setText(add_error_text)
        error_add_row_window.showMaximized()

    else:
        cod_vuza = int([''.join(x) for _, x in it.groupby(data_cod_vuza, key=lambda c: c == '-')][2])
        name_vuza_add = [''.join(x) for _, x in it.groupby(data_cod_vuza, key=lambda c: c == '-')][0]
        value = [int(data_g1), data_cod_kon[0:2], cod_vuza, name_vuza_add, data_g7, data_g5, data_g2, data_g21,
                 data_g22, data_g23, data_g24, data_g6, data_g8, data_g9, data_g10, data_g11]
        print('Вводимое польз',value)
        print('взяли из бд',spis[1])

        for i in range(len(spis[1])):
            if (spis[1][i]!=value[i] ):
                if value[i]!='':
                    spis[1][i]=value[i]
        print('то что вводим в бд',spis[1])
        print('индекс',spis[2])
        spis2=spis[1]
        conn=sqlite3.connect(db_name)
        cur=conn.cursor()
        cur.execute(f'''UPDATE gr_proj SET codkon={spis2[1]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET codvuz={spis2[2]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET z2=? WHERE g1={spis[2]} ''', (spis2[3],))
        cur.execute(f'''UPDATE gr_proj SET g7=? WHERE g1={spis[2]} ''', (spis2[4],))
        cur.execute(f'''UPDATE gr_proj SET g5={spis2[5]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g2={spis2[6]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g21={spis2[7]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g22={spis2[8]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g23={spis2[9]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g24={spis2[10]} WHERE g1={spis[2]} ''')
        cur.execute(f'''UPDATE gr_proj SET g6=? WHERE g1={spis[2]} ''', (spis2[11],))
        cur.execute(f'''UPDATE gr_proj SET g8=? WHERE g1={spis[2]} ''', (spis2[12],))
        cur.execute(f'''UPDATE gr_proj SET g9=? WHERE g1={spis[2]} ''', (spis2[13],))
        cur.execute(f'''UPDATE gr_proj SET g10=? WHERE g1={spis[2]} ''', (spis2[14],))
        cur.execute(f'''UPDATE gr_proj SET g11=? WHERE g1={spis[2]} ''', (spis2[15],))
        cur.execute(f'''UPDATE gr_proj SET g1={spis2[0]} WHERE g1={spis[2]} ''')
        conn.commit()
        cur.close()
        conn.close()
        change_window.close()
        proj_view_window.showMaximized()
        table_model = QSqlTableModel()

        query = QSqlQuery(f"""SELECT codkon AS "Код конкурса",
                              g1 AS "Код НИР",
                              g8 AS "Руководитель НИР",
                              g7 AS "Код по ГРНТИ",
                              z2 AS "Наименование вуза",
                              g5 AS "Плановый объем",
                              g6 AS "Наименование НИР",
                              g2 AS "Фактический объем гранта",
                              g21 as"Поквартальное финансирование",
                              g22 as"Поквартальное финансирование",
                              g23 as"Поквартальное финансирование",
                              g24 as"Поквартальное финансирование",
                              g9 as "Должность руководителя",
                              g10 as"Учёное звание руководителя",
                              g11 as"Учёная степень руководителя"
                              FROM gr_proj""")


        table_model.setQuery(query)

        proj_view_form.tableView.setModel(table_model)
        proj_view_form.tableView.setSortingEnabled(True)
        proj_view_form.tableView.resizeColumnsToContents()


def change():
    # заполняем комбобоксы
    g1 = set()
    query = QSqlQuery("SELECT * FROM gr_proj")
    while query.next():
        g1.add(str(query.value(0)))
    result = sorted([int(item) for item in g1])
    result1 = [str(item) for item in result]

    change_form.comboBox_cod_nir.addItems(result1)
    # заполняем код конкурса
    query = QSqlQuery("SELECT k2 , codkon FROM gr_konk")
    name_kon = set()
    while query.next():
        name_kon.add(str(query.value(1)) + '-' + str(query.value(0)))
    name_kon = list(name_kon)
    change_form.comboBox_cod_kon.addItems(sorted(name_kon, key=lambda x: x[:3]))
    # заполняем код вуза и наименование вуза
    name_vuza = set()
    kod_vuza = set()
    query = QSqlQuery("SELECT * FROM vuz")
    while query.next():
        name_vuza.add(str(query.value(3)) + '-' + str(query.value(0)))
    name_vuza = list(name_vuza)
    change_form.comboBox_cod_vuz.addItems(sorted(name_vuza, key=lambda x: x[:3]))

    table_model = QSqlTableModel()
    global curr_index
    curr_index = proj_view_form.tableView.currentIndex()
    print(curr_index.sibling(curr_index.row(), 1).data())  # 1 - индекс нужного столбца
    conn=sqlite3.connect(db_name)
    cur=conn.cursor()
    if curr_index.sibling(curr_index.row(), 1).data() != None:
        cur.execute(f'''SELECT * FROM gr_proj WHERE g1=={curr_index.sibling(curr_index.row(), 1).data()}''')
        res = list(cur.fetchone())
        change_window.showMaximized()
        query = QSqlQuery(f"""SELECT codkon AS "Код конкурса",
                              g1 AS "Код НИР",
                              g8 AS "Руководитель НИР",
                              g7 AS "Код по ГРНТИ",
                              z2 AS "Наименование вуза",
                              g5 AS "Плановый объем",
                              g6 AS "Наименование НИР",
                              g2 AS "Фактический объем гранта",
                              g21 as"Поквартальное финансирование",
                              g22 as"Поквартальное финансирование",
                              g23 as"Поквартальное финансирование",
                              g24 as"Поквартальное финансирование",
                              g9 as "Должность руководителя",
                              g10 as"Учёное звание руководителя",
                              g11 as"Учёная степень руководителя"
                              FROM gr_proj WHERE g1=={curr_index.sibling(curr_index.row(), 1).data()}""")

        table_model.setQuery(query)
        change_form.tableView_change.setModel(table_model)
        change_form.tableView_change.resizeColumnsToContents()
        ind=curr_index.sibling(curr_index.row(), 1).data()
        spis=[result1,res , ind]
        change_form.pushButton_change.clicked.connect(partial(read_data_add_row1,spis))
    else:
        print('ничего не выбрано')


def open_proj_sort_window():
    # открывает окно показа таблицы конкурсов

    global query_sql_sort_save
    global query_sql_filter_save

    window_list[check_active_window()].close()
    proj_sort_window.showMaximized()

    table_model = QSqlTableModel()

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                 proj.g1 AS "Код НИР",
                                 proj.g8 AS "Руководитель НИР",
                                 proj.g7 AS "Код по ГРНТИ",
                                 proj.z2 AS "Наименование вуза",
                                 proj.g5 AS "Плановый объем",
                                 proj.g6 AS "Наименование НИР",
                                 proj.g2 AS "Фактический объем гранта",
                                 proj.g21 as"Поквартальное финансирование",
                                 proj.g22 as"Поквартальное финансирование",
                                 proj.g23 as"Поквартальное финансирование",
                                 proj.g24 as"Поквартальное финансирование",
                                 proj.g9 as "Должность руководителя",
                                 proj.g10 as"Учёное звание руководителя",
                                 proj.g11 as"Учёная степень руководителя"
                          FROM gr_proj AS proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                          {cond_filter if query_sql_filter_save != {} else ""}
                          {cond_sort if query_sql_sort_save != {} else ""}""")


    table_model.setQuery(query)
    proj_sort_form.tableView.setSortingEnabled(True)
    proj_sort_form.tableView.setModel(table_model)
    proj_sort_form.tableView.resizeColumnsToContents()


def proj_sort_save():
    # сохраняет сортировку таблицы проектов

    global query_sql_sort_save
    global query_sql_filter_save

    combo_cond_sort_g1 = proj_sort_form.combo_box_order_g1.currentText()
    combo_cond_sort_codkon = proj_sort_form.combo_box_order_codkon.currentText()

    table_model = QSqlTableModel()

    cond_sort_g1 = "ASC" if combo_cond_sort_g1 == "По возрастанию" else "DESC"
    cond_sort_codkon = "ASC" if combo_cond_sort_codkon == "По возрастанию" else "DESC"

    query_sql_sort_save = {'proj.g1': cond_sort_g1, 'proj.codkon': cond_sort_codkon}

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                 proj.g1 AS "Код НИР",
                                 proj.g8 AS "Руководитель НИР",
                                 proj.g7 AS "Код по ГРНТИ",
                                 proj.z2 AS "Наименование вуза",
                                 proj.g5 AS "Плановый объем",
                                 proj.g6 AS "Наименование НИР",
                                 proj.g2 AS "Фактический объем гранта",
                                 proj.g21 as"Поквартальное финансирование",
                                 proj.g22 as"Поквартальное финансирование",
                                 proj.g23 as"Поквартальное финансирование",
                                 proj.g24 as"Поквартальное финансирование",
                                 proj.g9 as "Должность руководителя",
                                 proj.g10 as"Учёное звание руководителя",
                                 proj.g11 as"Учёная степень руководителя"
                          FROM gr_proj AS proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                          {cond_filter if query_sql_filter_save != {} else ""}
                          {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query)
    proj_sort_form.tableView.setSortingEnabled(True)
    proj_sort_form.tableView.setModel(table_model)
    proj_sort_form.tableView.resizeColumnsToContents()


def proj_sort_reset():
    # удаляет сортировку таблицы проектов

    global query_sql_sort_save
    global query_sql_filter_save

    table_model = QSqlTableModel()

    query_sql_sort_save = {}

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                     proj.g1 AS "Код НИР",
                                     proj.g8 AS "Руководитель НИР",
                                     proj.g7 AS "Код по ГРНТИ",
                                     proj.z2 AS "Наименование вуза",
                                     proj.g5 AS "Плановый объем",
                                     proj.g6 AS "Наименование НИР",
                                     proj.g2 AS "Фактический объем гранта",
                                     proj.g21 as"Поквартальное финансирование",
                                     proj.g22 as"Поквартальное финансирование",
                                     proj.g23 as"Поквартальное финансирование",
                                     proj.g24 as"Поквартальное финансирование",
                                     proj.g9 as "Должность руководителя",
                                     proj.g10 as"Учёное звание руководителя",
                                     proj.g11 as"Учёная степень руководителя"
                          FROM gr_proj AS proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                          {cond_filter if query_sql_filter_save != {} else ""}
                          {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query)
    proj_sort_form.tableView.setSortingEnabled(True)
    proj_sort_form.tableView.setModel(table_model)
    proj_sort_form.tableView.resizeColumnsToContents()


def open_proj_filter_window():
    # открывает окно фильтрации таблицы проектов

    global query_sql_sort_save
    global query_sql_filter_save
    global query_sql_filter_temp

    window_list[check_active_window()].close()
    proj_filter_window.showMaximized()

    table_model = QSqlTableModel()

    if query_sql_filter_save == {}:
        query_sql_filter_temp = {}

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                         proj.g1 AS "Код НИР",
                                         proj.g8 AS "Руководитель НИР",
                                         proj.g7 AS "Код по ГРНТИ",
                                         proj.z2 AS "Наименование вуза",
                                         proj.g5 AS "Плановый объем",
                                         proj.g6 AS "Наименование НИР",
                                         proj.g2 AS "Фактический объем гранта",
                                         proj.g21 as"Поквартальное финансирование",
                                         proj.g22 as"Поквартальное финансирование",
                                         proj.g23 as"Поквартальное финансирование",
                                         proj.g24 as"Поквартальное финансирование",
                                         proj.g9 as "Должность руководителя",
                                         proj.g10 as"Учёное звание руководителя",
                                         proj.g11 as"Учёная степень руководителя"
                          FROM gr_proj AS proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                          {cond_filter if query_sql_filter_save != {} else ""}
                          {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query = QSqlQuery(f"""SELECT konk.codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city, vuz.z2 AS z2
                          FROM gr_konk AS konk
                          LEFT JOIN gr_proj AS proj ON proj.codkon = konk.codkon
                          LEFT JOIN vuz ON proj.codvuz = vuz.codvuz
    					  {cond_filter if query_sql_filter_save != {} else ""}""")

    set_codkon, set_region, set_oblname, set_city, set_z2 = set(), set(), set(), set(), set()

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_region.add(str(query.value(1)))
        set_oblname.add(str(query.value(2)))
        set_city.add(str(query.value(3)))
        set_z2.add(str(query.value(4)))

    if '' in set_region and '' in set_oblname and '' in set_city and '' in set_z2:
        set_region.remove('')
        set_oblname.remove('')
        set_city.remove('')
        set_z2.remove('')

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()

    proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))
    proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))
    proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))
    proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))

    if 'proj.codkon' in query_sql_filter_save:
        proj_filter_form.combo_box_filter_codkon.setCurrentIndex((["Нет"] + sorted(list(set_codkon))).index(query_sql_filter_save['proj.codkon']))

    if 'vuz.region' in query_sql_filter_save:
        proj_filter_form.combo_box_filter_region.setCurrentIndex((["Нет"] + sorted(list(set_region))).index(query_sql_filter_save['vuz.region']))

    if 'vuz.oblname' in query_sql_filter_save:
        proj_filter_form.combo_box_filter_oblname.setCurrentIndex((["Нет"] + sorted(list(set_oblname))).index(query_sql_filter_save['vuz.oblname']))

    if 'vuz.city' in query_sql_filter_save:
        proj_filter_form.combo_box_filter_city.setCurrentIndex((["Нет"] + sorted(list(set_city))).index(query_sql_filter_save['vuz.city']))

    if 'vuz.z2' in query_sql_filter_save:
        proj_filter_form.combo_box_filter_z2.setCurrentIndex((["Нет"] + sorted(list(set_z2))).index(query_sql_filter_save['vuz.z2']))


def proj_filter_codkon():
    # фильтрует по коду конкурса

    global query_sql_sort_save
    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_codkon = proj_filter_form.combo_box_filter_codkon.currentText()

    if combo_box_filter_codkon == "Нет" and 'proj.codkon' in query_sql_filter_temp:
        del query_sql_filter_temp['proj.codkon']
    elif combo_box_filter_codkon == "Нет":
        pass
    else:
        query_sql_filter_temp['proj.codkon'] = combo_box_filter_codkon

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query_sql_filter)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query_sql_filter = QSqlQuery(f"""SELECT vuz.region AS region, vuz.oblname AS oblname, vuz.city as city, vuz.z2 AS z2
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}""")

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

    global query_sql_sort_save
    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_region = proj_filter_form.combo_box_filter_region.currentText()

    if combo_box_filter_region == "Нет" and 'vuz.region' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.region']
    elif combo_box_filter_region == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.region'] = combo_box_filter_region

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query_sql_filter)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.oblname AS oblname, vuz.city as city, vuz.z2 AS z2
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}""")

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

    global query_sql_sort_save
    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_oblname = proj_filter_form.combo_box_filter_oblname.currentText()

    if combo_box_filter_oblname == "Нет" and 'vuz.oblname' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.oblname']
    elif combo_box_filter_oblname == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.oblname'] = combo_box_filter_oblname

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query_sql_filter)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.city as city, vuz.z2 AS z2
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}""")

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

    global query_sql_sort_save
    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_city = proj_filter_form.combo_box_filter_city.currentText()

    if combo_box_filter_city == "Нет" and 'vuz.city' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.city']
    elif combo_box_filter_city == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.city'] = combo_box_filter_city

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query_sql_filter)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.z2 AS z2
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}""")

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

    global query_sql_sort_save
    global query_sql_filter_temp

    table_model = QSqlTableModel()

    combo_box_filter_z2 = proj_filter_form.combo_box_filter_z2.currentText()

    if combo_box_filter_z2 == "Нет" and 'vuz.z2' in query_sql_filter_temp:
        del query_sql_filter_temp['vuz.z2']
    elif combo_box_filter_z2 == "Нет":
        pass
    else:
        query_sql_filter_temp['vuz.z2'] = combo_box_filter_z2

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query_sql_filter)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query_sql_filter = QSqlQuery(f"""SELECT proj.codkon AS codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz == vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}""")

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

    global query_sql_sort_save
    global query_sql_filter_save
    global query_sql_filter_temp

    query_sql_filter_temp = {}
    query_sql_filter_save = {}

    table_model = QSqlTableModel()

    cond_sort = 'ORDER BY' + ' ' + ', '.join(f"{field} {value}" for field, value in zip(query_sql_sort_save.keys(), query_sql_sort_save.values()))
    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT proj.codkon AS "Код конкурса",
                                            proj.g1 AS "Код НИР",
                                            proj.g8 AS "Руководитель НИР",
                                            proj.g7 AS "Код по ГРНТИ",
                                            proj.z2 AS "Наименование вуза",
                                            proj.g5 AS "Плановый объем",
                                            proj.g6 AS "Наименование НИР",
                                            proj.g2 AS "Фактический объем гранта",
                                            proj.g21 as"Поквартальное финансирование",
                                            proj.g22 as"Поквартальное финансирование",
                                            proj.g23 as"Поквартальное финансирование",
                                            proj.g24 as"Поквартальное финансирование",
                                            proj.g9 as "Должность руководителя",
                                            proj.g10 as"Учёное звание руководителя",
                                            proj.g11 as"Учёная степень руководителя"
                                     FROM gr_proj as proj INNER JOIN vuz ON proj.codvuz = vuz.codvuz
                                     {cond_filter if query_sql_filter_temp != {} else ""}
                                     {cond_sort if query_sql_sort_save != {} else ""}""")

    table_model.setQuery(query)
    proj_filter_form.tableView.setSortingEnabled(True)
    proj_filter_form.tableView.setModel(table_model)
    proj_filter_form.tableView.resizeColumnsToContents()

    query = QSqlQuery(f"""SELECT konk.codkon, vuz.region AS region, vuz.oblname AS oblname, vuz.city AS city, vuz.z2 AS z2
                          FROM gr_konk AS konk
                          LEFT JOIN gr_proj AS proj ON proj.codkon = konk.codkon
                          LEFT JOIN vuz ON proj.codvuz = vuz.codvuz
    					  {cond_filter if query_sql_filter_save != {} else ""}""")

    set_codkon, set_region, set_oblname, set_city, set_z2 = set(), set(), set(), set(), set()

    while query.next():
        set_codkon.add(str(query.value(0)))
        set_region.add(str(query.value(1)))
        set_oblname.add(str(query.value(2)))
        set_city.add(str(query.value(3)))
        set_z2.add(str(query.value(4)))

    if '' in set_region and '' in set_oblname and '' in set_city and '' in set_z2:
        set_region.remove('')
        set_oblname.remove('')
        set_city.remove('')
        set_z2.remove('')

    proj_filter_form.combo_box_filter_codkon.clear()
    proj_filter_form.combo_box_filter_region.clear()
    proj_filter_form.combo_box_filter_oblname.clear()
    proj_filter_form.combo_box_filter_city.clear()
    proj_filter_form.combo_box_filter_z2.clear()

    proj_filter_form.combo_box_filter_codkon.addItems(["Нет"] + sorted(list(set_codkon)))
    proj_filter_form.combo_box_filter_region.addItems(["Нет"] + sorted(list(set_region)))
    proj_filter_form.combo_box_filter_oblname.addItems(["Нет"] + sorted(list(set_oblname)))
    proj_filter_form.combo_box_filter_city.addItems(["Нет"] + sorted(list(set_city)))
    proj_filter_form.combo_box_filter_z2.addItems(["Нет"] + sorted(list(set_z2)))


def proj_filter_check():
    print('temp',query_sql_filter_temp)
    print('save',query_sql_filter_save)


def open_konk_window():
    # открывает окно показа таблицы конкурсов

    global query_sql_filter_save

    if check_active_window() is not None:
        window_list[check_active_window()].close()
    konk_view_window.showMaximized()

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT konk.k2 AS "Название конкурса", 
                                 konk.codkon AS "Код конкурса",
                                 ifnull(SUM(proj.g5), 0) AS "Плановый объём",
    			                 ifnull(SUM(proj.g2), 0) AS "Фактический объём", 
    			                 ifnull(SUM(proj.g21), 0) AS "Финанисирование в 1 квартале", 
    			                 ifnull(SUM(proj.g22), 0) AS "Финанисирование во 2 квартале", 
    			                 ifnull(SUM(proj.g23), 0) AS "Финанисирование в 3 квартале", 
    			                 ifnull(SUM(proj.g24), 0) AS "Финанисирование в 4 квартале", 
                                 COUNT(proj.codkon) AS "Количество НИР"
                          FROM gr_konk AS konk
                          LEFT JOIN gr_proj AS proj ON proj.codkon = konk.codkon
                          LEFT JOIN vuz ON proj.codvuz = vuz.codvuz
						  {cond_filter if query_sql_filter_save != {} else ""}
						  GROUP BY konk.codkon""")

    table_model.setQuery(query)
    konk_view_form.tableView.setSortingEnabled(True)
    konk_view_form.tableView.setModel(table_model)
    konk_view_form.tableView.resizeColumnsToContents()


def open_vuz_window():
    # открывает окно показа таблицы вузов

    global query_sql_filter_save

    window_list[check_active_window()].close()
    vuz_view_window.showMaximized()

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""SELECT DISTINCT vuz.codvuz AS "Код вуза",
                                 vuz.z1 AS "Наименование вуза",
                                 vuz.z1full AS "Полное юридическое наимнование вуза",
                                 vuz.z2 AS "Сокращённое наименование вуза",
                                 vuz.region AS "Федеральный округ",
                                 vuz.city AS "Город",
                                 vuz.status AS "Статус",
                                 vuz.obl AS "Код субъекта РФ",
                                 vuz.oblname AS "Субъект РФ",
                                 vuz.gr_ved AS "???",
                                 vuz.prof AS "Проф???"
						  FROM vuz LEFT JOIN gr_proj AS proj ON vuz.codvuz = proj.codvuz
						  {cond_filter if query_sql_filter_save != {} else ""}""")

    table_model.setQuery(query)
    vuz_view_form.tableView.setSortingEnabled(True)
    vuz_view_form.tableView.setModel(table_model)
    vuz_view_form.tableView.resizeColumnsToContents()


def open_analysis_vuz_window():
    # открывает окно анализа по вузам

    global query_sql_filter_save

    window_list[check_active_window()].close()
    analysis_window.showMaximized()
    analysis_window.setWindowTitle('Сопровождение конкурсов на соискание грантов — анализ по вузам')

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""WITH temp_cte AS(
                            SELECT vuz.z2 AS z2_cte,
                            COUNT(proj.g1) AS g1_cte,
                            ifnull(SUM(proj.g5), 0) AS g5_cte,
                            COUNT(DISTINCT proj.codkon) AS codkon_cte
                            FROM vuz LEFT JOIN gr_proj AS proj ON vuz.codvuz = proj.codvuz
                            {cond_filter if query_sql_filter_save != {} else ""}
                            GROUP BY proj.codvuz)
                         SELECT z2_cte AS "Наименование вуза",
                                g1_cte AS "Количество НИР",
                                g5_cte AS "Плановый объём",
                                codkon_cte AS "Количество конкурсов в которых учавствует вуз"
                         FROM temp_cte
                         UNION ALL
                         SELECT NULL, NULL, NULL, NULL
                         UNION ALL
                         SELECT 'Итого',
                         		ifnull(SUM(g1_cte), 0),
                         		NULL,
                         		ifnull(SUM(codkon_cte), 0)
                         FROM temp_cte""")

    table_model.setQuery(query)
    analysis_form.tableView.setSortingEnabled(True)
    analysis_form.tableView.setModel(table_model)
    analysis_form.tableView.resizeColumnsToContents()


def open_analysis_konk_window():
    # открывает окно анализа по конкурсам

    global query_sql_filter_save

    window_list[check_active_window()].close()
    analysis_window.showMaximized()
    analysis_window.setWindowTitle('Сопровождение конкурсов на соискание грантов — анализ по конкурсам')

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""WITH temp_cte AS(
                            SELECT konk.k2 AS k2_cte,
                            COUNT(proj.g1) AS g1_cte,
                            ifnull(SUM(proj.g5), 0) AS g5_cte,
                            COUNT(DISTINCT proj.codvuz) AS codvuz_cte
                            FROM gr_konk AS konk
                            LEFT JOIN gr_proj AS proj ON proj.codkon = konk.codkon
                            LEFT JOIN vuz ON proj.codvuz = vuz.codvuz
                            {cond_filter if query_sql_filter_save != {} else ""}
                            GROUP BY konk.codkon)
                         SELECT k2_cte AS "Название конкурса",
                                g1_cte AS "Количество НИР",
                                g5_cte AS "Плановый объём",
                                codvuz_cte AS "Количество вузов которые учавствуют в конкурсе"
                         FROM temp_cte
                         UNION ALL
                         SELECT NULL, NULL, NULL, NULL
                         UNION ALL
                         SELECT 'Итого',
                         		ifnull(SUM(g1_cte), 0),
                         		NULL,
                         		ifnull(SUM(codvuz_cte), 0)
                         FROM temp_cte""")

    table_model.setQuery(query)
    analysis_form.tableView.setSortingEnabled(True)
    analysis_form.tableView.setModel(table_model)
    analysis_form.tableView.resizeColumnsToContents()


def open_analysis_subj_window():
    # открывает окно анализа по субъектам РФ

    global query_sql_filter_save

    window_list[check_active_window()].close()
    analysis_window.showMaximized()
    analysis_window.setWindowTitle('Сопровождение конкурсов на соискание грантов — анализ по субъектам РФ')

    table_model = QSqlTableModel()

    cond_filter = 'WHERE' + ' ' + ' AND '.join(f"{field} == \"{value}\"" for field, value in zip(query_sql_filter_temp.keys(), query_sql_filter_temp.values()))

    query = QSqlQuery(f"""WITH temp_cte AS(
                            SELECT vuz.oblname AS oblname_cte,
                            COUNT(proj.g1) AS g1_cte,
                            ifnull(SUM(proj.g5), 0) AS g5_cte,
							COUNT(DISTINCT vuz.codvuz) AS codvuz_cte,
                            COUNT(DISTINCT proj.codkon) AS codkon_cte
                            FROM vuz LEFT JOIN gr_proj AS proj ON vuz.codvuz = proj.codvuz
                            {cond_filter if query_sql_filter_save != {} else ""}
                            GROUP BY vuz.oblname)
                         SELECT oblname_cte AS "Субъект федерации",
                                g1_cte AS "Количество НИР",
                                g5_cte AS "Плановый объём",
								codvuz_cte AS "Количество вузов в субъекте",
                                codkon_cte AS "Количество конкурсов в субъекте"
                         FROM temp_cte
                         UNION ALL
                         SELECT NULL, NULL, NULL, NULL, NULL
                         UNION ALL
                         SELECT 'Итого',
                         		ifnull(SUM(g1_cte), 0),
                         		NULL,
								ifnull(SUM(codvuz_cte), 0),
                         		ifnull(SUM(codkon_cte), 0)
                         FROM temp_cte""")

    table_model.setQuery(query)
    analysis_form.tableView.setSortingEnabled(True)
    analysis_form.tableView.setModel(table_model)
    analysis_form.tableView.resizeColumnsToContents()

def open_help_view_window():
    # открывает окно показа справки

    window_list[check_active_window()].close()
    help_view_window.showMaximized()


def open_help_prog_view_window():
    # открывает окно показа справки по программе

    window_list[check_active_window()].close()
    help_prog_view_window.showMaximized()


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
proj_view_form.pushButton_add_row.clicked.connect(add_row)


# инициализация окна сортировки таблицы проектов
proj_sort_window = ProjSortWindow()
proj_sort_form = ProjSortForm()
proj_sort_form.setupUi(proj_sort_window)
proj_sort_form.push_button_sort_save.clicked.connect(proj_sort_save)
proj_sort_form.push_button_sort_reset.clicked.connect(proj_sort_reset)


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


# инициализация окна добавления строки
add_view_window = AddRowWindowWindow()
add_view_form= AddRowWindowForm()
add_view_form.setupUi(add_view_window)


error_add_row_window=ErrorAddRowWindow()
error_add_row_form=ErrorAddRowForm()
error_add_row_form.setupUi(error_add_row_window)


# инициализация окна показа справки по программе
help_prog_view_window = HelpProgViewWindow()
help_prog_view_form = HelpProgViewForm()
help_prog_view_form.setupUi(help_prog_view_window)


# инициализация редактирования строк
change_window=ChangeWindow()
change_form=ChangeForm()
change_form.setupUi(change_window)
proj_view_form.pushButton_change.clicked.connect(change)


# инициализация окна удаления
delete_proj_window=DeleteWindow()
delete_proj_form=DeleteWindowForm()
delete_proj_form.setupUi(delete_proj_window)


# инициализация окна анализа
analysis_window=AnalysisWindow()
analysis_form=AnalysisForm()
analysis_form.setupUi(analysis_window)


# список всех окон приложения
window_list = [main_window, konk_view_window, vuz_view_window, proj_view_window,  help_view_window, help_prog_view_window, proj_sort_window, proj_filter_window,
               error_add_row_window, add_view_window, change_window, delete_proj_window, analysis_window]


# привязка функций показа таблиц ко кнопкам панели в главном окне
main_form.panel_data_konk.triggered.connect(open_konk_window)
main_form.panel_data_vuz.triggered.connect(open_vuz_window)
main_form.panel_data_proj.triggered.connect(open_proj_window)
main_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
main_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
main_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
main_form.panel_help_view.triggered.connect(open_help_view_window)
main_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
main_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы конкурсов
konk_view_form.panel_data_konk.triggered.connect(open_konk_window)
konk_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
konk_view_form.panel_data_proj.triggered.connect(open_proj_window)
konk_view_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
konk_view_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
konk_view_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
konk_view_form.panel_help_view.triggered.connect(open_help_view_window)
konk_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
konk_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы вузов
vuz_view_form.panel_data_konk.triggered.connect(open_konk_window)
vuz_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
vuz_view_form.panel_data_proj.triggered.connect(open_proj_window)
vuz_view_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
vuz_view_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
vuz_view_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
vuz_view_form.panel_help_view.triggered.connect(open_help_view_window)
vuz_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
vuz_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа таблицы проектов
proj_view_form.panel_data_konk.triggered.connect(open_konk_window)
proj_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_view_form.panel_data_proj.triggered.connect(open_proj_window)
proj_view_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
proj_view_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
proj_view_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
proj_view_form.panel_help_view.triggered.connect(open_help_view_window)
proj_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне сортировки таблицы проектов
proj_sort_form.panel_data_konk.triggered.connect(open_konk_window)
proj_sort_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_sort_form.panel_data_proj.triggered.connect(open_proj_window)
proj_sort_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
proj_sort_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
proj_sort_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
proj_sort_form.panel_help_view.triggered.connect(open_help_view_window)
proj_sort_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_sort_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне фильтрации таблицы проектов
proj_filter_form.panel_data_konk.triggered.connect(open_konk_window)
proj_filter_form.panel_data_vuz.triggered.connect(open_vuz_window)
proj_filter_form.panel_data_proj.triggered.connect(open_proj_window)
proj_filter_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
proj_filter_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
proj_filter_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
proj_filter_form.panel_help_view.triggered.connect(open_help_view_window)
proj_filter_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
proj_filter_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне анализа
analysis_form.panel_data_konk.triggered.connect(open_konk_window)
analysis_form.panel_data_vuz.triggered.connect(open_vuz_window)
analysis_form.panel_data_proj.triggered.connect(open_proj_window)
analysis_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
analysis_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
analysis_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
analysis_form.panel_help_view.triggered.connect(open_help_view_window)
analysis_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
analysis_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа помощи
help_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_view_form.panel_data_proj.triggered.connect(open_proj_window)
help_view_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
help_view_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
help_view_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
help_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_view_form.panel_exit_action.triggered.connect(close_prog)


# привязка функций показа таблиц ко кнопкам панели в окне показа помощи по программе
help_prog_view_form.panel_data_konk.triggered.connect(open_konk_window)
help_prog_view_form.panel_data_vuz.triggered.connect(open_vuz_window)
help_prog_view_form.panel_data_proj.triggered.connect(open_proj_window)
help_prog_view_form.panel_analysis_vuz.triggered.connect(open_analysis_vuz_window)
help_prog_view_form.panel_analysis_konk.triggered.connect(open_analysis_konk_window)
help_prog_view_form.panel_analysis_subj.triggered.connect(open_analysis_subj_window)
help_prog_view_form.panel_help_view.triggered.connect(open_help_view_window)
help_prog_view_form.panel_help_prog.triggered.connect(open_help_prog_view_window)
help_prog_view_form.panel_exit_action.triggered.connect(close_prog)


open_konk_window()
app.exec()
