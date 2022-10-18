"""init

Revision ID: 91e8b96f7c2f
Revises: 
Create Date: 2022-10-18 16:01:41.549908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91e8b96f7c2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('match_statusDB',
    sa.Column('match_status_id', sa.Integer(), nullable=False),
    sa.Column('match_status_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('match_status_id', name=op.f('pk_match_statusDB'))
    )
    op.create_table('sportDB',
    sa.Column('sport_id', sa.Integer(), nullable=False),
    sa.Column('sport_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('sport_id', name=op.f('pk_sportDB'))
    )
    op.create_table('leagueDB',
    sa.Column('league_id', sa.Integer(), nullable=False),
    sa.Column('league_country', sa.String(), nullable=True),
    sa.Column('league_name', sa.String(), nullable=True),
    sa.Column('sport_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sport_id'], ['sportDB.sport_id'], name=op.f('fk_leagueDB_sport_id_sportDB')),
    sa.PrimaryKeyConstraint('league_id', name=op.f('pk_leagueDB'))
    )
    op.create_table('teamsDB',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('team_name', sa.String(), nullable=True),
    sa.Column('league_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['league_id'], ['leagueDB.league_id'], name=op.f('fk_teamsDB_league_id_leagueDB')),
    sa.PrimaryKeyConstraint('team_id', name=op.f('pk_teamsDB'))
    )
    op.create_table('basketball_matchesDB',
    sa.Column('match_id', sa.Integer(), nullable=False),
    sa.Column('match_date', sa.Date(), nullable=True),
    sa.Column('match_status', sa.Integer(), nullable=True),
    sa.Column('home_team_id', sa.Integer(), nullable=True),
    sa.Column('away_team_id', sa.Integer(), nullable=True),
    sa.Column('home_team_final_score', sa.Integer(), nullable=True),
    sa.Column('away_team_final_score', sa.Integer(), nullable=True),
    sa.Column('first_quarter_home_score', sa.Integer(), nullable=True),
    sa.Column('first_quarter_away_score', sa.Integer(), nullable=True),
    sa.Column('second_quarter_home_score', sa.Integer(), nullable=True),
    sa.Column('second_quarter_away_score', sa.Integer(), nullable=True),
    sa.Column('third_quarter_home_score', sa.Integer(), nullable=True),
    sa.Column('third_quarter_away_score', sa.Integer(), nullable=True),
    sa.Column('fourth_quarter_home_score', sa.Integer(), nullable=True),
    sa.Column('fourth_quarter_away_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['away_team_id'], ['teamsDB.team_id'], name=op.f('fk_basketball_matchesDB_away_team_id_teamsDB')),
    sa.ForeignKeyConstraint(['home_team_id'], ['teamsDB.team_id'], name=op.f('fk_basketball_matchesDB_home_team_id_teamsDB')),
    sa.ForeignKeyConstraint(['match_status'], ['match_statusDB.match_status_id'], name=op.f('fk_basketball_matchesDB_match_status_match_statusDB')),
    sa.PrimaryKeyConstraint('match_id', name=op.f('pk_basketball_matchesDB'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('basketball_matchesDB')
    op.drop_table('teamsDB')
    op.drop_table('leagueDB')
    op.drop_table('sportDB')
    op.drop_table('match_statusDB')
    # ### end Alembic commands ###
