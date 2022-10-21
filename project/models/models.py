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
    home_team = db.relationship('MatchesDB', backref='home_team', foreign_keys="[MatchesDB.home_team_id]")
    away_team = db.relationship('MatchesDB', backref='away_team', foreign_keys="[MatchesDB.away_team_id]")


class Match_statusDB(db.Model):
    match_status_id = db.Column(db.Integer, primary_key=True)
    match_status_name = db.Column(db.String)

class Match_recordsDB(db.Model):
    match_record_id = db.Column(db.Integer, primary_key=True)
    match_string_identificator = db.Column(db.String, db.ForeignKey('matchesDB.match_string_identificator'))
    match_minute = db.Column(db.Integer)
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)

class MatchesDB(db.Model):
    match_id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.String)
    league_country = db.Column(db.String)
    league_name = db.Column(db.String)
    match_string_identificator = db.Column(db.String)
    match_date = db.Column(db.Date, default=datetime.utcnow)
    # match_status = db.Column(db.Integer, db.ForeignKey('match_statusDB.match_status_id'))
    match_status_name = db.Column(db.String)
    match_minute = db.Column(db.Integer)
    home_team_id = db.Column(db.Integer, db.ForeignKey('teamsDB.team_id'))
    away_team_id = db.Column(db.Integer, db.ForeignKey('teamsDB.team_id'))
    match_home_team_name = db.Column(db.String)
    match_away_team_name = db.Column(db.String)
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
