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


def new_league(country, league_name, sport_id):
    new_league = LeagueDB(
        league_country=country,
        league_name=league_name,
        sport_id=sport_id
    )
    db.session.add(new_league)
    db.session.commit()
    last_created_league = LeagueDB.query.order_by(desc(LeagueDB.league_id)).first()
    print("Лига : ", last_created_league.league_name, " была создана")
    last_created_league_id = last_created_league.league_id
    return last_created_league_id


@home.route('/')
def home_view():
    return render_template('home.html')


@home.route('/parse_live')
def parse_live():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    # driver.get("https://www.flashscorekz.com/basketball/")
    driver.get("https://www.flashscorekz.com/hockey/")
    sport_id = 2

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
    # получаем страну и лигу
    top_header = driver.find_element("xpath", "//div[@class='event__header top']")
    # получаем страну и лигу из топхедера
    # это будет первое вхождение, если живые матчи есть на странице

    try:
        country_top_header = driver.find_element("xpath", "//span[@class='event__title--type']")
        league_top_header = driver.find_element("xpath", "//span[@class='event__title--name']")

        country_top_header = country_top_header.text.lower()
        league_top_header =league_top_header.text
        # проверяем есть ли эта лига в базе
        league_data = LeagueDB.query.filter_by(league_country=country_top_header, league_name=league_top_header).first()
        if league_data:
            pass
        else:
            # создаем новую лигу
            last_created_league_id = new_league(country_top_header, league_top_header, sport_id)
            league_id = last_created_league_id
            #  и переходим в список команд для заполнения
            driver.find_element("xpath", "//span[@class='event__title--name']").click()
            driver.implicitly_wait(10)
            driver.find_element("xpath", "//a[@class='tabs__tab standings_table']").click()
            # парсим таблицу с командами

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


    except Exception as e:
        print(e)

    # все нижние соседи

    siblings = top_header.find_elements("xpath", "//div[@class='event__header top']/following-sibling::*")
    for block in siblings:
        try:
            class_name = block.get_attribute("class")
            # print("class_name: ", class_name)
        except:
            pass

        try:
            id = block.get_attribute("id")
            # print(id)
        except:
            pass

    return "парсер живых матчей"


@home.route('/parse_league')
def parse_league():
    driver = webdriver.Chrome("/usr/local/bin/chromedriver")
    # web_page = "https://www.flashscorekz.com/basketball/argentina/liga-a/standings/"
    web_page = "https://www.flashscorekz.com/basketball/europe/champions-league/standings/"
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
    sport_id = 1
    # Проверяем есть ли запись в базе с это страной и лигой
    existing_league_data = LeagueDB.query.filter_by(league_country = country, league_name = league_name).first()
    if existing_league_data:
        pass
    else:
        new_league(country, league_name, sport_id)

    # получаем id лиги
    league_data = LeagueDB.query.filter_by(league_country = country, league_name = league_name).first()
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
