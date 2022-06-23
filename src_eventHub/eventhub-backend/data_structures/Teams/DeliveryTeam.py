import uuid

from data_structures.Teams.Member import Member
from data_structures.Teams.Subscriber import Subscriber
from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class DeliveryTeam(Subscriber):
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

    def get_team_by_id(self, uuid_str):
        sql = "SELECT ID FROM deliveryTeam WHERE deliveryTeam.UUID = '{}'".format(uuid_str)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()
        return res[0][0]

    def delete_team(self, uuid_str):
        sql = "DELETE FROM deliveryTeam WHERE deliveryTeam.UUID = '{}'".format(uuid_str)
        connector = SQliteConnector()
        connector.create_connection()
        connector.run_sql_command(sql)
        connector.close_connection()

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

    @classmethod
    def from_db_by_uuid(cls, uuid_str):
        sql = "SELECT * FROM deliveryTeam WHERE deliveryTeam.UUID == '{}'".format(uuid_str)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

        team = cls(name=res[0][0], id=res[0][1], uuid_str=res[0][2])
        return team

    def to_db(self):
        sql = "INSERT INTO deliveryTeam (name, UUID) VALUES ('{}', '{}') ".format(self.name, self.uuid)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)

        connector.close_connection()
        return res

