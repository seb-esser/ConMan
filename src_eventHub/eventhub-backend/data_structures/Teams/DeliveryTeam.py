
from data_structures.Teams.Member import Member
from functions.sqlite_middleware.SQliteConnector import SQliteConnector

import uuid


class DeliveryTeam:
    def __init__(self, name, id=None, uuid=None):
        if id is None:
            self.id = -1
        else:
            self.id = id

        self.name = name
        self.members = []
        if uuid is None:
            self.uuid = uuid.uuid4().hex
        else:
            self.uuid = uuid

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
            team = cls(name=row[0], id=row[1], uuid=row[2])
            team.members = [x for x in members if x.team_id == row[1]]
            teams.append(team)

        return teams

    def to_db(self):
        sql = "INSERT INTO deliveryTeam (name, UUID) VALUES ('{}', '{}')".format(self.name, self.uuid)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

