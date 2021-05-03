from neo4j_middleware import neo4jConnector


class PatchIntegrator(object):
    """ applies an incoming patch on a database """

    def __init__(self, connector: neo4jConnector):
        self.connector = connector

    def apply_patch(self, patch: Patch):
        raise NotImplementError()
