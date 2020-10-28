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
            # entity1
            propertyResult1 = None

            if property1_name != '':
                propertyResult1 = self._find_entity_property(
                    self, property1_name)
                print("entityResult1: ", propertyResult1)

            # entity2
            propertyResult2 = None

            if property2_name != '':
                propertyResult2 = self._find_entity_property(
                    self, property2_name)
                print("entityResult2: ", propertyResult2)

            # relation
            if relation == 'ROOT':
                relation = None
            relationResult = None

            # Write transactions allow the driver to handle retries and transient errors
            if (relationResult == None) and (propertyResult1 == None) and (propertyResult2 != None):
                result = session.write_transaction(
                    self._create_and_return_relation_entity, property1_name, property2_name, relation)
                for record in result:
                    print("Created relation between: {p1}, {p2}, {r}".format(
                        p1=record['p1'], p2=record['p2'], r=record['r']
                    ))

            elif (relationResult == None) and (propertyResult1 != None) and (propertyResult2 == None):
                result = session.write_transaction(
                    self._create_and_return_relation_entity, property2_name, property1_name, relation)
                for record in result:
                    print("Created relation between: {p1}, {p2}, {r}".format(
                        p1=record['p1'], p2=record['p2'], r=record['r']
                    ))

            elif (relationResult == None) and (propertyResult1 != None) and (propertyResult2 != None):
                result = session.write_transaction(
                    self._create_and_return_relation, property1_name, property2_name, relation)
                for record in result:
                    print("Created relation between: {p1}, {p2}, {r}".format(
                        p1=record['p1'], p2=record['p2'], r=record['r']
                    ))

                # when it doesnot exist entity1,entity2 and relation
            elif (propertyResult1 == None) and (propertyResult2 == None) and (relationResult == None):
                result = session.write_transaction(
                    self._create_and_return_relation_entities, property1_name, property2_name, relation)
                for record in result:
                    print("Created relation between: {p1}, {p2}, {r}".format(
                        p1=record['p1'], p2=record['p2'], r=record['r']
                    ))

            # when it doesnot exist entity1

    @staticmethod
    def _create_and_return_relation_entity(tx, entity1_name, entity2_name, relation):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (p1:Entity { name: $entity1_name }) "
            "CREATE (p1)-[r:" + relation + "]->(p2) "
            "RETURN p1, p2, r"
        )
        result = tx.run(query, entity1_name=entity1_name,
                        entity2_name=entity2_name, relation=relation)
        try:
            return [{"p1": record["p1"]["name"],
                     "p2": record["p2"]["name"],
                     "r":record["r"]
                     }
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _create_and_return_relation(tx, entity1_name, entity2_name, relation):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (p1)-[r:" + relation + "]->(p2) "
            "RETURN p1, p2, r"
        )
        result = tx.run(query, entity1_name=entity1_name,
                        entity2_name=entity2_name, relation=relation)
        try:
            return [{"p1": record["p1"]["name"],
                     "p2": record["p2"]["name"],
                     "r":record["r"]
                     }
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _create_and_return_relation_entities(tx, entity1_name, entity2_name, relation):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (p1:Entity { name: $entity1_name }) "
            "CREATE (p2:Entity { name: $entity2_name }) "
            "CREATE (p1)-[r:" + relation + "]->(p2) "
            "RETURN p1, p2, r"
        )
        result = tx.run(query, entity1_name=entity1_name,
                        entity2_name=entity2_name, relation=relation)
        try:
            return [{"p1": record["p1"]["name"],
                     "p2": record["p2"]["name"],
                     "r":record["r"]
                     }
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def _find_entity_property(self, property_name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_entity_property, property_name)
            for record in result:
                print("Found entity: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_entity_property(tx, property_name):
        query = (
            "MATCH (p:Entity) "
            "WHERE p.name = $property_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, property_name=property_name)
        return [record["name"] for record in result]

    @staticmethod
    def _find_relation(self, entity1_name, entity2_name, relation):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_relation, entity1_name=entity1_name, entity2_name=entity2_name, relation=relation)
            for record in result:
                print("Found relation: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_relation(tx, entity1_name, entity2_name, relation):
        query = (
            "MATCH (p:Entity)-[r:" + relation + "]-(s:Entity) "
            "WHERE p.name = $entity1_name and s.name = $entity2_name "
            "RETURN r AS relation"
        )
        result = tx.run(query, entity1_name=entity1_name,
                        entity2_name=entity2_name, relation=relation)
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
