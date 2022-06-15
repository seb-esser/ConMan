from functions.sqlite_middleware.SQliteConnector import SQliteConnector


class DeliveryTeam:
    def __init__(self, name):
        self.id = 0
        self.name = name
        self.members = []

    @classmethod
    def from_db(cls):
        sql = "SELECT * FROM member INNER JOIN deliveryTeam ON member.TeamID = deliveryTeam.ID"
        connector = SQliteConnector()
        connector.create_connection()
        res = connector.run_sql_command(sql)
        print(res)
