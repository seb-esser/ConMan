import uuid

from data_structures.Teams.Member import Member
from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class DeliveryTeam:
    def __init__(self, name, id=None, uuid_str=None):
        if id is None:
            self.id = -1
        else:
            self.id = id

        self.name = name
        self.members = []
        if uuid_str is None:
            self.uuid = uuid.uuid4().hex
        else:
            self.uuid = uuid_str

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
            team = cls(name=row[0], id=row[1], uuid_str=row[2])
            team.members = [x for x in members if x.team_id == row[1]]
            teams.append(team)

        return teams

    def to_db(self):
        sql = "INSERT INTO deliveryTeam (name, UUID) VALUES ('{}', '{}')".format(self.name, self.uuid)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

