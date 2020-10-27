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

    def create_relationship(self, person1_name, person2_name, relation_ship):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_relationship, person1_name, person2_name, relation_ship)
            for record in result:
                print("Created friendship between: {p1}, {p2}".format(
                    p1=record['p1'], p2=record['p2']
                ))

    @staticmethod
    def _create_and_return_relationship(tx, person1_name, person2_name, relation_ship):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (p1:Entity { name: $person1_name }) "
            "CREATE (p2:Entity { name: $person2_name }) "
            "CREATE (p1)-[r:" + relation_ship + "]->(p2) "
            "RETURN p1, p2"
        )
        result = tx.run(query, person1_name=person1_name,
                        person2_name=person2_name, relation_ship=relation_ship)
        try:
            return [{"p1": record["p1"]["name"],
                     "p2": record["p2"]["name"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_person, person_name)
            for record in result:
                print("Found person: {record}".format(record=record))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Entity) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [record["name"] for record in result]


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
    print("ner: ", nlp.get_ner())
    print("dependency_parse: ", nlp.get_dependency_parse())
    ner = nlp.get_ner()
    dependencies = nlp.get_dependency_parse()
    for dependency in dependencies:
        # entity
        entity1 = ''
        entity2 = ''
        if dependency[1] != 0:
            entity1 = ner[dependency[1]-1][0]

        if dependency[2] != 0:
            entity2 = ner[dependency[2]-1][0]

        # create relationship
        myneo4j.create_relationship(
            entity1, entity2, dependency[0].replace(':', ''))

    # app.find_person("Alice")
    myneo4j.close()
