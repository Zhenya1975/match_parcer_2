from flask import Blueprint, render_template, redirect, url_for, abort, request, jsonify, flash
from models.models import SportDB, LeagueDB, TeamsDB, Match_statusDB, Basketball_matchesDB
from selenium import webdriver
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


@home.route('/')
def home_view():
    return render_template('home.html')


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
    for match_table in driver.find_elements("xpath", table_type_1):
        id = match_table.get_attribute("id")
        match_date_xpath_txt = "//div[@class='calendar__datepicker ']"

        home_team_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__participant event__participant--home fontExtraBold']"
        home_team_final_score_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__score event__score--home']"

        away_team_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__participant event__participant--away']"
        away_team_final_score_xpath_txt = "// *[ @ id = '" + id + "']/div[@class='event__score event__score--away']"

        try:
            match_date = driver.find_element("xpath", match_date_xpath_txt).text
            date_val = match_date[0:1]
            month_val = (match_date[3:4])
            dt_str = date_val + '/' + month_val + '/' + '/2022'
            dt_obj = datetime.strptime(dt_str, '%d/%m/%Y')

            home_team = driver.find_element("xpath", home_team_xpath_txt).text
            home_team_final_score = driver.find_element("xpath", home_team_final_score_xpath_txt).text
            away_team = driver.find_element("xpath", away_team_xpath_txt).text
            away_team_final_score = driver.find_element("xpath", away_team_final_score_xpath_txt).text

            # пробуем получить из базы запись с матчем, в котором есть сегодняшнее число и две команды
            existing_match_data = Basketball_matchesDB.query.filter_by()

            print(match_date, home_team, home_team_final_score, away_team, away_team_final_score)
        except:
            pass




    return "test"
