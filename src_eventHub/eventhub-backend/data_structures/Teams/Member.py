import uuid

from data_structures.Teams.Subscriber import Subscriber
from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class Member(Subscriber):

    def __init__(self, first_name: str, last_name: str, id=None, team_id=None, is_admin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.is_admin = is_admin
        if id is None:
            self.user_id = uuid.uuid4().hex
        else:
            self.user_id = id

        if team_id is None:
            self.team_id = -1
        else:
            self.team_id = team_id

    def __eq__(self, other):
        if self.user_id == other.user_id:
            return True
        else:
            return False

    def delete_member(self, uuid_str):
        sql = "DELETE FROM member WHERE member.UUID = '{}'".format(uuid_str)
        connector = SQliteConnector()
        connector.create_connection()
        connector.run_sql_command(sql)
        connector.close_connection()

    @classmethod
    def from_db(cls):
        sql = "SELECT * FROM member"
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

        members = []
        for row in res:
            member = cls(row[0], row[1], row[2], row[3], row[4])
            members.append(member)
        return members

    @classmethod
    def from_db_by_uuid(cls, uuid_str):
        sql = "SELECT * FROM member WHERE member.UUID == '{}'".format(uuid_str)
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        connector.close_connection()

        member = cls(res[0][0], res[0][1], res[0][2], res[0][3], res[0][4])
        return member

    def to_db(self):
        sql = "INSERT INTO member (lastName, firstName, UUID, TeamID, isAdmin) VALUES ('{}', '{}', '{}', {}, {}})"\
            .format(self.last_name, self.first_name, self.user_id, self.team_id, self.is_admin)

        connector = SQliteConnector()
        connector.create_connection()
        connector.run_sql_command(sql)
        connector.close_connection()

