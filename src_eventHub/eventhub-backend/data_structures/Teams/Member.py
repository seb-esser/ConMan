import uuid

from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class Member:

    def __init__(self, first_name: str, last_name: str, id=None, team_id=None):
        self.first_name = first_name
        self.last_name = last_name
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

    @classmethod
    def from_db(cls):
        sql = "SELECT * FROM member"
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)

        members = []
        for row in res:
            member = cls(row[0], row[1], row[2], row[3])
            members.append(member)
        return members

    def to_db(self):
        sql = "INSERT INTO member (lastName, firstName, UUID, TeamID) VALUES ('{}', '{}', '{}', '{}')"\
            .format(self.last_name, self.first_name, self.user_id, self.team_id)

        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)

