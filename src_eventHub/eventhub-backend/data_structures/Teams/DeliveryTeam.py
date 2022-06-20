from data_structures.Teams.Member import Member
from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class DeliveryTeam:
    def __init__(self, name, id=None):
        if id is None:
            self.id = -1
        else:
            self.id = id

        self.name = name
        self.members = []

    @classmethod
    def from_db(cls):

        members = Member.from_db()

        sql = "SELECT * FROM deliveryTeam"
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

        teams = []

        for row in res:
            team = cls(row[0], row[1])
            team.members = [x for x in members if x.team_id == row[1]]
            teams.append(team)

        return teams

    def to_db(self):
        sql = "INSERT INTO deliveryTeam (name) VALUES ('{}')".format(self.name)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

