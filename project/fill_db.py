from models.models import SportDB, LeagueDB, TeamsDB, Basketball_matchesDB
from sqlalchemy import desc, asc
from extensions import extensions
from app import app
db = extensions.db
from data_samples import teams_data

def create_sports():
    with app.app_context():
        new_sport = SportDB(
            sport_name = "Хоккей"
        )
        db.session.add(new_sport)
        db.session.commit()
        last_created_sport= SportDB.query.order_by(desc(SportDB.sport_id)).first()

        print("Спорт : ", last_created_sport.sport_name, " был создан")

# create_sports()

def create_league():
    with app.app_context():
        new_league = LeagueDB(
            league_country = "Аргентина",
            league_name = "Лига А",
            sport_id = 1
        )
        db.session.add(new_league)
        db.session.commit()
        last_created_league= LeagueDB.query.order_by(desc(LeagueDB.league_id)).first()

        print("Лига : ", last_created_league.league_name, " была создана")

# create_league()

def fill_teams():
    with app.app_context():
        teams_dict = teams_data.teams
        for key_1, value_1 in teams_dict.items():
            sport_id = key_1
            country_dict = value_1
            for key_2, value_2 in country_dict.items():
                country_name = key_2
                league_dict = value_2
                for key_3, value_3 in league_dict.items():
                    league_id = key_3
                    teams_data_dict = value_3
                    for key_4, value_4 in teams_data_dict.items():
                        team_name = value_4
                        new_team = TeamsDB(
                            team_name = team_name,
                            league_id = league_id
                        )
                        db.session.add(new_team)
                        db.session.commit()
                        last_created_team = TeamsDB.query.order_by(desc(TeamsDB.team_id)).first()

                        print("команда : ", last_created_team.team_name, " была создана")

# fill_teams()
def delete_matches():
    with app.app_context():
        matches_data = Basketball_matchesDB.query.all()
        for match in matches_data:
            db.session.delete(match)
            db.session.commit()

# delete_matches()

def delete_league_record():
    with app.app_context():
        league_data = LeagueDB.query.filter_by(league_country = 'сша', league_name='НХЛ').first()
        db.session.delete(league_data)
        db.session.commit()
# delete_league_record()


def lower_country_name():
    with app.app_context():
        league_data = LeagueDB.query.all()
        for league in league_data:
            country_name = league.league_country
            new_country_name = country_name.lower()
            league.league_country = new_country_name
            db.session.commit()
# lower_country_name()

