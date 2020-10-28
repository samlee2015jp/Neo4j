from nlp import NLP

import logging

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from neo4j.work import result


class DealNeo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_relation(self, property1_name, property2_name, relation):
        with self.driver.session() as session:
            # property name and relation
            print("property1_name: ", property1_name)
            print("property2_name: ", property2_name)
            print("relation: ", relation)

            # propertyResult1
            propertyResult1 = None
            if property1_name != '':
                propertyResult1 = self._find_property(
                    self, property1_name)
            else:
                propertyResult1 = ''
            print("propertyResult1: ", propertyResult1)

            # propertyResult2
            propertyResult2 = None
            if property2_name != '':
                propertyResult2 = self._find_property(
                    self, property2_name)

            else:
                propertyResult2 = ''
            print("propertyResult2: ", propertyResult2)

            # relationResult
            relationResult = None
            if ((relation != 'ROOT') and (relation != '')):
                relationResult = self._find_relation(
                    self, relation)
            else:
                relationResult = ''
            print("relationResult: ", relationResult)

            # Write transactions allow the driver to handle retries and transient errors
            if (propertyResult1 != None) and (propertyResult2 == None) and (relationResult != None):
                createPropertyResult2 = session.write_transaction(
                    self._create_and_return_property, property2_name)
                print('created property2: ' + createPropertyResult2)

            # when it doesnot exist entity1
            print('The end of creating each property or relation.')

    @staticmethod
    def _create_and_return_property(tx, property_name):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (e:Entity {name: $property_name}) "
            "RETURN e.name AS name"
        )
        result = tx.run(query, property_name=property_name)
        return [record["name"] for record in result]

    @staticmethod
    def _find_property(self, property_name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_property, property_name)
            for record in result:
                print("Found property name: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_property(tx, property_name):
        query = (
            "MATCH (p:Entity) "
            "WHERE p.name = $property_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, property_name=property_name)
        return [record["name"] for record in result]

    @staticmethod
    def _find_relation(self, relation):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_property, relation)
            for record in result:
                print("Found property name: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_relation(tx, relation):
        query = (
            "MATCH (n)-[r:$relation]->(m) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, relation=relation)
        return [record["relation"] for record in result]


if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.

    scheme = "bolt"  # connecting to Aura. use the "neo4j+s" URI scheme
    host_name = "localhost"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(
        scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "password"
    myneo4j = DealNeo4j(url, user, password)

    # the sentence
    sentence = 'I go to aist in Tokyo everyday.'
    nlp = NLP(sentence)
    # print("ner: ", nlp.get_ner())
    # print("dependency_parse: ", nlp.get_dependency_parse())
    ner = nlp.get_ner()
    dependencies = nlp.get_dependency_parse()
    for dependency in dependencies:
        # entity
        property1 = ''
        property2 = ''
        if dependency[1] != 0:
            property1 = ner[dependency[1]-1][0]

        if dependency[2] != 0:
            property2 = ner[dependency[2]-1][0]

        # create relation
        myneo4j.create_relation(
            property1, property2, dependency[0].replace(':', ''))

    myneo4j.close()
