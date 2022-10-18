from extensions import extensions
from datetime import datetime, date

db = extensions.db


class SportDB(db.Model):
    sport_id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.String)


class LeagueDB(db.Model):
    league_id = db.Column(db.Integer, primary_key=True)
    league_country = db.Column(db.String)
    league_name = db.Column(db.String)
    sport_id = db.Column(db.Integer, db.ForeignKey('sportDB.sport_id'))


class TeamsDB(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String)
    league_id = db.Column(db.Integer, db.ForeignKey('leagueDB.league_id'))


class Match_statusDB(db.Model):
    match_status_id = db.Column(db.Integer, primary_key=True)
    match_status_name = db.Column(db.String)


class Basketball_matchesDB(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    match_date = db.Column(db.Date, default=datetime.utcnow)
    match_status = db.Column(db.Integer, db.ForeignKey('match_statusDB.match_status_id'))
    home_team_id = db.Column(db.Integer, db.ForeignKey('teamsDB.team_id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teamsDB.team_id'))
    home_team_final_score = db.Column(db.Integer)
    away_team_final_score = db.Column(db.Integer)
    first_quarter_home_score = db.Column(db.Integer)
    first_quarter_away_score = db.Column(db.Integer)
    second_quarter_home_score = db.Column(db.Integer)
    second_quarter_away_score = db.Column(db.Integer)
    third_quarter_home_score = db.Column(db.Integer)
    third_quarter_away_score = db.Column(db.Integer)
    fourth_quarter_home_score = db.Column(db.Integer)
    fourth_quarter_away_score = db.Column(db.Integer)
