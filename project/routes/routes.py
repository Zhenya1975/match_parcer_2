from flask import Blueprint, render_template, redirect, url_for, abort, request, jsonify, flash
from models.models import SportDB, LeagueDB, TeamsDB, Match_statusDB, Basketball_matchesDB
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
    return render_template('home.html')

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
            parent = driver.find_element("xpath", "//div[@class='sportName basketball']")
            # находим всех его первых потомков
            childs = parent.find_elements("xpath", "./*")
            #  итерируемся по детям
            league_count = 0
            live_match_data = {}
            current_league_identificator = ""
            for child in childs:
                child_class_name = child.get_attribute("class")
                if "event__header" in child_class_name:
                    country_name_element = child.find_element(By.CLASS_NAME, "event__title--type")
                    country_name = country_name_element.text.lower()
                    league_name_element = child.find_element(By.CLASS_NAME, "event__title--name")
                    league_name = league_name_element.text
                    league_identificator = country_name + ": " + league_name
                    current_league_identificator = league_identificator
                if "twoLine" in child_class_name:
                    # находим все элементы внутри таблицы
                    # нужно получить уникальный идентификатор данной игры.
                    # сумма названий команд даст уникальность
                    table_childs = child.find_elements("xpath", ".//*")
                    game_identificator = ""
                    home_team_name = ""
                    away_team_name = ""
                    for table_element in table_childs:
                        table_element_class = table_element.get_attribute("class")

                        if table_element_class and "event__participant--home" in table_element_class:
                            home_team_name = table_element.text
                        if table_element_class and "event__participant--away" in table_element_class:
                            away_team_name = table_element.text
                        game_identificator = home_team_name + "___" + away_team_name

                    table_data = {}
                    live_match_data[game_identificator] = table_data

                    table_childs = child.find_elements("xpath", ".//*")
                    for table_element in table_childs:
                        table_element_class = table_element.get_attribute("class")
                        if table_element_class and "stage--block" in table_element_class:
                            stage_data_text = table_element.text.splitlines()
                            quarter_name = stage_data_text[0]
                            table_data['quarter_name'] = quarter_name
                            try:
                                current_minute = int(stage_data_text[1].strip())
                                table_data['current_minute'] = current_minute
                            except:
                                pass
                        if table_element_class and "event__participant--home" in table_element_class:
                            home_team_name = table_element.text
                            table_data['home_team_name'] = home_team_name
                        if table_element_class and "event__participant--away" in table_element_class:
                            away_team_name = table_element.text
                            table_data['away_team_name'] = away_team_name

                        if table_element_class and "event__score--home" in table_element_class:
                            home_team_score = int(table_element.text)
                            table_data['home_team_score'] = home_team_score
                        if table_element_class and "event__score--away" in table_element_class:
                            away_team_score = int(table_element.text)
                            table_data['away_team_score'] = away_team_score

                    print(live_match_data)


                    # stage_data_element = child.find_element(By.CLASS_NAME, "event__stage--block")
                    # stage_data_text = stage_data_element.text
                    # home_team_element = child.find_element(By.CLASS_NAME, "event__participant event__participant--home")
                    # home_team_name = home_team_element.text
                    # away_team_element = child.find_element(By.CLASS_NAME, "event__participant event__participant--away")
                    # away_team_name = away_team_element.text
                    # print(stage_data_text, home_team_name, away_team_name)




            # try:
            #     top_headers_list = driver.find_elements("xpath", "//div[@class='event__header top']")
            #     event_header_list = driver.find_elements("xpath", "//div[@class='event__header']")
            #     header_list = top_headers_list + event_header_list
            #     # top_headers_list = driver.find_elements("xpath", "//div[@class='event__titleBox']")
            #     for header in header_list:
            #         # проверяем есть ли у топ хедера сохраненная лига и команды
            #         country_name = header.find_element(By.CLASS_NAME, "event__title--type")
            #         league_name_el = header.find_element(By.CLASS_NAME, "event__title--name")
            #         country = country_name.text.lower()
            #         league_name = league_name_el.text
            #
            #         # проверяем есть ли эта лига в базе
            #         league_data = LeagueDB.query.filter_by(league_country=country, league_name=league_name).first()
            #         if league_data:
            #             print(f"Данные о лиге уже есть в базе. Страна: ", country, ". Лига: ", league_name)
            #         else:
            #             # создаем новую лигу
            #             print(f"Данных о лиге {league_name} нет в базе")

                    # получаем матчи в данной лиге.
                    # для этого получаем таблицы sibling

                    # //div[contains(text(),'(123)')]/parent::div/following-sibling::div
                    # driver.find_element_by_xpath("//div[@class='txt-bx']/following-sibling::p")


            # except Exception as e:
            #     print("Ошибка при парсинге live ", e)


    return redirect(url_for('home.home_view'))



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
