from flask import Blueprint, render_template, redirect, url_for, abort, request, jsonify, flash
from models.models import SportDB, LeagueDB, TeamsDB, Match_statusDB, MatchesDB
from selenium import webdriver
from sqlalchemy import desc, asc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
from datetime import datetime

from extensions import extensions
# from sqlalchemy import desc, asc, func
# from sqlalchemy import and_, or_
# from flask_socketio import SocketIO, emit
# from datetime import datetime

db = extensions.db
# db.create_all()
# db.session.commit()
home = Blueprint('home', __name__, template_folder='templates')

socketio = extensions.socketio

def check_league(driver, country, league_name, sport_id, league_name_el):
    # проверяем есть ли эта лига в базе
    league_data = LeagueDB.query.filter_by(league_country=country, league_name=league_name).first()
    if league_data:
        print("Данные о лиге уже есть в базе. Страна: ", country, ". Лига: ", league_name)
    else:
        # создаем новую лигу
        print("Данных о лиге в нет в базе")
        new_league = LeagueDB(
            league_country=country,
            league_name=league_name,
            sport_id=sport_id
        )
        db.session.add(new_league)
        db.session.commit()
        league_data = LeagueDB.query.order_by(desc(LeagueDB.league_id)).first()
        league_id = league_data.league_id
        print("Лига : ", league_data.league_name, " была создана")
        # переходим в каталог команд
        league_name_el.click()
        driver.implicitly_wait(3)
        driver.find_element("xpath", "//a[@class='tabs__tab standings_table']").click()

        # получаем список команд
        teams = driver.find_elements("xpath", "//a[@class='tableCellParticipant__name']")
        for team in teams:
            team_name = team.text
            # проверяем есть ли уже запись о команде
            team_data = TeamsDB.query.filter_by(league_id=league_id, team_name=team_name).first()
            if team_data:
                pass
            else:
                new_team_record = TeamsDB(
                    league_id=league_id,
                    team_name=team_name
                )
                db.session.add(new_team_record)
                db.session.commit()
                last_created_team = TeamsDB.query.order_by(desc(TeamsDB.team_id)).first()
                print("Команда : ", last_created_team.team_name, " была создана")
        # возвращаемся обратно
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(3)
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(10)
        # print('Enter your name:')
        # x = input()
        tabs = driver.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
        for tab in tabs:
            tab_name = tab.text
            if tab_name.lower() == "завершенные":
                tab.click()




    return league_data

def update_league_and_team_data(driver, country, league_name, sport_id, status):

        # переходим в список команд для заполнения
        driver.find_element("xpath", "//span[@class='event__title--name']").click()
        driver.implicitly_wait(10)
        driver.find_element("xpath", "//a[@class='tabs__tab standings_table']").click()

        # получаем список команд
        teams = driver.find_elements("xpath", "//a[@class='tableCellParticipant__name']")
        for team in teams:
            team_name = team.text
            # проверяем есть ли уже запись о команде
            team_data = TeamsDB.query.filter_by(league_id=league_id, team_name=team_name).first()
            if team_data:
                pass
            else:
                new_team_record = TeamsDB(
                    league_id=league_id,
                    team_name=team_name
                )
                db.session.add(new_team_record)
                db.session.commit()
                last_created_team = TeamsDB.query.order_by(desc(TeamsDB.team_id)).first()
                print("Команда : ", last_created_team.team_name, " была создана")
        # возвращаемся обратно
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(3)
        driver.execute_script("window.history.go(-1)")
        driver.implicitly_wait(10)
        # print('Enter your name:')
        # x = input()
        tabs = driver.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
        for tab in tabs:
            tab_name = tab.text
            if tab_name.lower() == status:
                tab.click()




@home.route('/')
def home_view():
    data = {'active_tab_pass': 'live_matches'}
    # if int(active_tab_name) == 0:
    #     data = {'active_tab_pass': 'live_matches'}
    # if int(active_tab_name) == 1:
    #     data = {'active_tab_pass': 'settings'}

    return render_template('home.html', data=data)

@home.route('/parse_finished')
def parse_finished():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://www.flashscorekz.com/basketball/")
    # driver.get("https://www.flashscorekz.com/hockey/")
    sport_id = 1
    status = "завершенные"
    top_header_data = {}
    driver.implicitly_wait(10)
    # жмем на кнопку принять куки.
    try:
        driver.find_element("id", 'onetrust-accept-btn-handler').click()
    except Exception as e:
        print("accept_all_button exception ", e)
    tabs = driver.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
    for tab in tabs:
        tab_name = tab.text
        if tab_name.lower() == "завершенные":
            tab.click()
            driver.implicitly_wait(10)

    # получаем хедеры
    try:
        top_headers_list = driver.find_elements("xpath", "//div[@class='event__header top']")
        event_header_list = driver.find_elements("xpath", "//div[@class='event__header']")
        header_list = top_headers_list + event_header_list
        # top_headers_list = driver.find_elements("xpath", "//div[@class='event__titleBox']")
        for header in header_list:
            # проверяем есть ли у топ хедера сохраненная лига и команды
            country_name = header.find_element(By.CLASS_NAME, "event__title--type")
            league_name_el = header.find_element(By.CLASS_NAME, "event__title--name")
            country = country_name.text.lower()
            league_name = league_name_el.text

            # проверяем есть ли эта лига в базе
            league_data = LeagueDB.query.filter_by(league_country=country, league_name=league_name).first()
            if league_data:
                print(f"Данные о лиге уже есть в базе. Страна: ", country, ". Лига: ", league_name)
            else:
                # создаем новую лигу
                print(f"Данных о лиге {league_name} нет в базе")
                new_league = LeagueDB(
                    league_country=country,
                    league_name=league_name,
                    sport_id=sport_id
                )
                db.session.add(new_league)
                db.session.commit()
                league_data = LeagueDB.query.order_by(desc(LeagueDB.league_id)).first()
                league_id = league_data.league_id
                print("Лига : ", league_data.league_name, " была создана")
                # переходим в каталог команд
                # вот этот переход наверное нужно сделать в другом драйвере
                # input("должен открыться")
                driver_2 = webdriver.Chrome("/usr/local/bin/chromedriver")
                driver_2.get("https://www.flashscorekz.com/basketball/")
                driver_2.implicitly_wait(10)
                # жмем на кнопку принять куки.
                try:
                    driver_2.find_element("id", 'onetrust-accept-btn-handler').click()
                except Exception as e:
                    print("accept_all_button exception ", e)
                tabs = driver_2.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
                for tab in tabs:
                    tab_name = tab.text
                    if tab_name.lower() == "завершенные":
                        tab.click()
                        driver.implicitly_wait(10)
                        #  здесь мы должны оказаться во вкладке Завершенные
                        # В драйвере 2 итерируемся по блокам и ищем тот, где есть наша лига, которую нужно заполнить командами
                        top_headers_list = driver_2.find_elements("xpath", "//div[@class='event__header top']")
                        event_header_list = driver_2.find_elements("xpath", "//div[@class='event__header']")
                        header_list_2 = top_headers_list + event_header_list
                        # top_headers_list = driver.find_elements("xpath", "//div[@class='event__titleBox']")
                        for header_2 in header_list_2:
                            # проверяем есть ли у топ хедера сохраненная лига и команды
                            country_name = header_2.find_element(By.CLASS_NAME, "event__title--type")
                            league_name_el_driver_2 = header_2.find_element(By.CLASS_NAME, "event__title--name")
                            country_driver_2 = country_name.text.lower()
                            league_name_driver_2 = league_name_el.text
                            print("country_driver_2: ", country_driver_2, ", league_name_driver_2: ", league_name_driver_2)
                            if country_driver_2 == country and league_name_driver_2 == league_name:
                                league_name_el_driver_2 .click()
                                driver_2.implicitly_wait(3)
                                driver_2.find_element("xpath", "//a[@class='tabs__tab standings_table']").click()
                                driver_2.implicitly_wait(10)
                                # получаем список команд
                                teams = driver_2.find_elements("xpath", "//a[@class='tableCellParticipant__name']")
                                print(f"Во втором драйвере получаем список команд: {country_driver_2} {league_name_driver_2}")
                                for team in teams:
                                    team_name = team.text
                                    # проверяем есть ли уже запись о команде
                                    team_data = TeamsDB.query.filter_by(league_id=league_id, team_name=team_name).first()
                                    if team_data:
                                        pass
                                    else:
                                        new_team_record = TeamsDB(
                                            league_id=league_id,
                                            team_name=team_name
                                        )
                                        db.session.add(new_team_record)
                                        db.session.commit()
                                        # last_created_team = TeamsDB.query.order_by(desc(TeamsDB.team_id)).first()
                                print("Команды в лиге : ", league_data.league_name, " созданы")
                                # driver_2.quit()

        return redirect(url_for('home.home_view'))

    except Exception as e:
        print("Ошибка при попытке получения хедеров в завершенных: ", e)
        return redirect(url_for('home.home_view'))




@home.route('/parse_live')
def parse_live():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://www.flashscorekz.com/basketball/")
    # driver.get("https://www.flashscorekz.com/hockey/")
    sport_id = 1

    # получаем активную вкладку с названием спорта
    # ищем родителя в меню

    # запускаeм цикл по минутам
    for i in range(1000):
        menu_parent = driver.find_element("xpath", "//div[@class='menuTop__items']")
        # получаем детей
        menu_childs = menu_parent.find_elements("xpath", ".//*")
        sport_name = ""
        for menu_child in menu_childs:
            menu_child_class = menu_child.get_attribute("class")
            if menu_child_class and "active" in menu_child_class:
                sport_name = menu_child.text.lower()

        driver.implicitly_wait(10)
        # жмем на кнопку принять куки.
        try:
            driver.find_element("id", 'onetrust-accept-btn-handler').click()
        except Exception as e:
            print("accept_all_button exception ", e)
        tabs = driver.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
        for tab in tabs:
            tab_name = tab.text
            if tab_name.lower() == "live":
                tab.click()
                driver.implicitly_wait(10)
                #  находим родителя sportName basketball
                sport_block_class_name = "sportName basketball"
                sport_block_xpath = "//div[@class='" + sport_block_class_name + "']"
                sport_block_parent_element = driver.find_element("xpath", sport_block_xpath)
                # находим всех его первых потомков
                sport_block_elements = sport_block_parent_element.find_elements("xpath", "./*")

                live_match_data = {} #  сюда записываем данные матчей.

                # ключом этого дикта должен быть идентификатор матча. А все его данные должны уже прицепом прибавляться.

                # live_match_data['sport_name'] = sport_name
                current_league_name = ""
                current_country_name = ""
                #  итерируемся по детям блока с соревнованиями
                for sport_block_element in sport_block_elements:
                    child_class_name = sport_block_element.get_attribute("class")
                    if child_class_name and "event__header" in child_class_name:
                        # создаем дикт с данными лиги
                        league_match_data = {}
                        # Получаем наименование страны лиги
                        country_name_element = sport_block_element.find_element(By.CLASS_NAME, "event__title--type")
                        country_name = country_name_element.text.lower()
                        current_country_name = country_name
                        # получаем наименование лиги
                        league_name_element = sport_block_element.find_element(By.CLASS_NAME, "event__title--name")
                        league_name = league_name_element.text
                        current_league_name = league_name
                        league_identificator = country_name + ": " + league_name
                        # league_match_data["league_identificator"] = league_identificator
                        # league_match_data["league_country"] = country_name
                        # league_match_data["league_name"] = league_name
                        # league_match_data["Sport"] = sport_name

                    if "twoLine" in child_class_name:
                        # находим все элементы внутри таблицы

                        table_elements = sport_block_element.find_elements("xpath", ".//*")
                        match_identificator = ""
                        home_team_name = ""
                        away_team_name = ""
                        for table_element in table_elements:
                            table_element_class = table_element.get_attribute("class")
                            if table_element_class and "event__participant--home" in table_element_class:
                                home_team_name = table_element.text
                            if table_element_class and "event__participant--away" in table_element_class:
                                away_team_name = table_element.text

                        match_identificator = current_league_name + "__" + home_team_name + "___" + away_team_name
                        # проверяем есть ли в базе запись с этим матчем
                        match_data = MatchesDB.query.filter_by(match_string_identificator = match_identificator).first()
                        if match_data:
                            pass
                        else:
                            new_match_record = MatchesDB(
                                sport_name = sport_name,
                                league_country = current_country_name,
                                league_name = current_league_name,
                                match_string_identificator = match_identificator,
                                match_date = datetime.today(),
                            )
                            try:
                                db.session.add(new_match_record)
                                db.session.commit()
                            except Exception as e:
                                print("Ошибка при создании записи о новом матче: ", e)

                        # получаем содержимое таблицы с матчем
                        table_childs = sport_block_element.find_elements("xpath", ".//*")
                        match_status = ""
                        current_minute = 0
                        home_team_name = ""
                        away_team_name = ""
                        home_team_score = 0
                        away_team_score = 0
                        first_quarter_home_score = 0
                        first_quarter_away_score = 0
                        second_quarter_home_score = 0
                        second_quarter_away_score = 0


                        for table_element in table_childs:
                            table_element_class = table_element.get_attribute("class")
                            if table_element_class and "stage--block" in table_element_class:
                                stage_data_text = table_element.text.splitlines()
                                match_status = stage_data_text[0]
                                try:
                                    current_minute = int(stage_data_text[1].strip())
                                except:
                                    pass
                            if table_element_class and "event__participant--home" in table_element_class:
                                home_team_name = table_element.text

                            if table_element_class and "event__participant--away" in table_element_class:
                                away_team_name = table_element.text

                            if table_element_class and "event__score--home" in table_element_class:
                                home_team_score = int(table_element.text)

                            if table_element_class and "event__score--away" in table_element_class:
                                away_team_score = int(table_element.text)

                            if table_element_class and "event__part--home event__part--1" in table_element_class:
                                first_quarter_home_score = int(table_element.text)

                            if table_element_class and "event__part--away event__part--1" in table_element_class:
                                first_quarter_away_score = int(table_element.text)

                            if table_element_class and "event__part--home event__part--2" in table_element_class:
                                second_quarter_home_score = int(table_element.text)

                            if table_element_class and "event__part--away event__part--2" in table_element_class:
                                second_quarter_away_score = int(table_element.text)

                            if table_element_class and "event__part--home event__part--3" in table_element_class:
                                third_quarter_home_score = int(table_element.text)

                            if table_element_class and "event__part--away event__part--3" in table_element_class:
                                third_quarter_away_score = int(table_element.text)

                            if table_element_class and "event__part--home event__part--4" in table_element_class:
                                fourth_quarter_home_score = int(table_element.text)

                            if table_element_class and "event__part--away event__part--4" in table_element_class:
                                fourth_quarter_away_score = int(table_element.text)

                        # обновляем запись о матче данными, собранными из таблицы

                        match_data_record = MatchesDB.query.filter_by(match_string_identificator=match_identificator).first()
                        if match_data_record:
                            match_data_record.match_status_name = match_status
                            match_data_record.match_minute = current_minute
                            match_data_record.match_home_team_name = home_team_name
                            match_data_record.match_away_team_name = away_team_name
                            match_data_record.home_team_final_score = home_team_score
                            match_data_record.away_team_final_score = away_team_score
                            match_data_record.first_quarter_home_score = first_quarter_home_score

                            db.session.commit()
                            # print("Таблица обновилась")
                        else:
                            print(f"запись с идентификатором {match_identificator} не найдена")

        time.sleep(60)
        driver.refresh()
        driver.implicitly_wait(10)

    return redirect(url_for('home.home_view'))

@home.route('/live_mathes_page_load_ajaxfile', methods=["POST", "GET"])
def live_mathes_page_load_ajaxfile():
    if request.method == 'POST':
        # получаем данные о текущих матчах
        # по кнопке live мы получаем запуск скрипта, который парсит страницу с соревнованиями
        # данные складываются в базу
        # из базы их нужо вытаскивать
        live_matches_data = MatchesDB.query.all()
        # получаем список спортов
        # sport_list = db.session.query.distinct(MatchesDB.sport_name)
        sport_list = db.session.query(MatchesDB.sport_name).distinct().all()
        sports_list = []
        for sport in sport_list:
            sports_list.append(sport.sport_name)

        # competition_id = int(request.form['competition_id'])
        # current_user_data = UserDB.query.first()
        #
        # # первый попавшийся раунд в данном соревновании
        # any_round_in_comp = RoundsDB.query.filter_by(competition_id=competition_id).first()
        # round_id = any_round_in_comp.round_id
        # user_selected_round_id = current_user_data.user_saved_round_id
        # if user_selected_round_id !=0:
        #     round_id = user_selected_round_id
        #
        # candidates_data = FightcandidateDB.query.filter_by(round_id=round_id).first()
        # backlog_data = BacklogDB.query.filter_by(round_id=round_id).all()
        # fights_data = FightsDB.query.filter_by(round_number=round_id).all()


        return jsonify({'htmlresponse': render_template('live_matches.html', live_matches_data=live_matches_data)})




@home.route('/test', methods=["POST", "GET"])
def test():
    return render_template("test.html")

@home.route('/parse_league', methods=["POST", "GET"])
def parse_league():
    if request.method == 'POST':
        link = request.form.get('link')
        driver = webdriver.Chrome("/usr/local/bin/chromedriver")
        # web_page = "https://www.flashscorekz.com/basketball/argentina/liga-a/standings/"
        # web_page = "https://www.flashscorekz.com/basketball/europe/champions-league/standings/"
        web_page = link
        driver.get(web_page)
        driver.implicitly_wait(10)
        # жмем на кнопку принять куки.
        try:
            driver.find_element("id", 'onetrust-accept-btn-handler').click()
        except Exception as e:
            print("accept_all_button exception ", e)
        # получаем страну из бредкрамба
        breadcrumb__link = driver.find_elements("xpath", "//a[@class='breadcrumb__link']")
        country = breadcrumb__link[1].text.lower()

        # получаем наименование лиги
        heading_name = driver.find_element("xpath", "//div[@class='heading__name']")
        league_name = heading_name.text
        sport_name = request.form.get('sport')
        sport_data = SportDB.query.filter_by(sport_name=sport_name).first()
        if sport_data:
            pass
        else:
            new_sport = SportDB(
                sport_name = sport_name
            )
            db.session.add(new_sport)
            db.session.commit()
            sport_data = SportDB.query.order_by(desc(SportDB.sport_id)).first()
            print("Спорт : ", sport_data.sport_name, " был создан")
        sport_id = sport_data.sport_id

        # Проверяем есть ли запись в базе с это страной и лигой
        league_data = LeagueDB.query.filter_by(league_country = country, league_name = league_name, sport_id=sport_id).first()
        if league_data:
            pass
        else:
            new_league = LeagueDB(
                league_country=country,
                league_name=league_name,
                sport_id=sport_id
            )
            db.session.add(new_league)
            db.session.commit()
            league_data = LeagueDB.query.order_by(desc(LeagueDB.league_id)).first()
            print("Лига: ", league_data.league_country, " ", league_data.league_name, " была создан")

            # получаем id лиги

        league_id = league_data.league_id

        # получаем список команд
        teams = driver.find_elements("xpath", "//a[@class='tableCellParticipant__name']")
        for team in teams:
            team_name = team.text
            # проверяем есть ли уже запись о команде
            team_data = TeamsDB.query.filter_by(league_id = league_id, team_name=team_name).first()
            if team_data:
                pass
            else:
                new_team_record = TeamsDB(
                    league_id=league_id,
                    team_name=team_name
                )
                db.session.add(new_team_record)
                db.session.commit()
                last_created_team = TeamsDB.query.order_by(desc(TeamsDB.team_id)).first()
                print("Команда : ", last_created_team.team_name, " была создана")

        driver.quit()

        return "парсинг команд"



@home.route('/competition_site')
def competition_site():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    driver.get("https://www.flashscorekz.com/basketball/")

    driver.implicitly_wait(10)
    # жмем на кнопку принять куки.
    try:
        driver.find_element("id", 'onetrust-accept-btn-handler').click()
    except Exception as e:
        print("accept_all_button exception ", e)
    tabs = driver.find_elements("xpath", "//div[@class='filters__text filters__text--default']")
    for tab in tabs:
        tab_name = tab.text
        if tab_name.lower() == "завершенные":
            tab.click()


    driver.implicitly_wait(10)



    table_type_1 = "//div[@class='event__match event__match--twoLine']"
    table_type_2 = "//div[@class='event__match event__match--last event__match--twoLine']"
    table_type_list = [table_type_1, table_type_2]
    for table_type in table_type_list:
        for match_table in driver.find_elements("xpath", table_type):
            id = match_table.get_attribute("id")
            match_date_xpath_txt = "//div[@class='calendar__datepicker ']"

            home_team_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__participant event__participant--home fontExtraBold']"
            home_team_final_score_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__score event__score--home']"

            away_team_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__participant event__participant--away']"
            away_team_final_score_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__score event__score--away']"

            try:
                match_date = driver.find_element("xpath", match_date_xpath_txt).text
                date_val = match_date[0:2]
                month_val = (match_date[3:5])
                dt_str = date_val + '/' + month_val + '/2022'
                dt_obj = datetime.strptime(dt_str, '%d/%m/%Y')

                home_team = driver.find_element("xpath", home_team_xpath_txt).text
                home_team_data = TeamsDB.query.filter_by(team_name=home_team).first()

                home_team_id=0
                if home_team_data:
                    home_team_id = home_team_data.team_id

                home_team_final_score = driver.find_element("xpath", home_team_final_score_xpath_txt).text
                away_team = driver.find_element("xpath", away_team_xpath_txt).text
                away_team_data = TeamsDB.query.filter_by(team_name=away_team).first()
                away_team_id = 0
                if away_team_data:
                    away_team_id = away_team_data.team_id
                away_team_final_score = driver.find_element("xpath", away_team_final_score_xpath_txt).text

                # пробуем получить из базы запись с матчем, в котором есть сегодняшнее число и две команды
                dt_obj = dt_obj.date()
                existing_match_data = Basketball_matchesDB.query.filter_by(match_date=dt_obj, home_team_id=home_team_id, away_team_id=away_team_id).first()
                print("existing_match_data: ", existing_match_data)
                if existing_match_data:
                    print("Данные о матче есть")
                else:
                    if home_team_id != 0 and away_team_id != 0:
                        new_match = Basketball_matchesDB(
                            match_date = dt_obj,
                            home_team_id = home_team_id,
                            away_team_id = away_team_id
                        )
                        db.session.add(new_match)
                        db.session.commit()
                        last_created_match = Basketball_matchesDB.query.order_by(desc(Basketball_matchesDB.match_id)).first()


                        print("Матч c: ", last_created_match.home_team.team_name, " был создан")

                print(match_date, home_team, home_team_final_score, away_team, away_team_final_score)
            except Exception as e:
                pass
                # print("не удалось получить таблицу. ", e)




    return "test"
