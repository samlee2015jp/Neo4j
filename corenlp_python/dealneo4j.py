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

    def create_relation(self, entity1, entity2, property1_name, property2_name, relation):
        with self.driver.session() as session:
            # entity, property name and relation
            print("entity1: ", entity1)
            print("entity2: ", entity2)
            print("property1_name: ", property1_name)
            print("property2_name: ", property2_name)
            print("relation: ", relation)

            # entity1
            entityResult1 = None
            if entity1 != '':
                entityResult1 = self._find_entity(
                    self, entity1)
            else:
                entityResult1 = ''
            print("entityResult1: ", entityResult1)

            # entity2
            entityResult2 = None
            if entity2 != '':
                entityResult2 = self._find_entity(
                    self, entity2)
            else:
                entityResult2 = ''
            print("entityResult2: ", entityResult2)

            # propertyResult1
            propertyResult1 = None
            if property1_name != '':
                propertyResult1 = self._find_entity_property(
                    self, entity1, property1_name)
            else:
                propertyResult1 = ''
            print("propertyResult1: ", propertyResult1)

            # propertyResult2
            propertyResult2 = None
            if property2_name != '':
                propertyResult2 = self._find_entity_property(
                    self, entity2, property2_name)

            else:
                propertyResult2 = ''
            print("propertyResult2: ", propertyResult2)

            # relationResult
            relationResult = None
            if ((relation != 'ROOT') and (relation != '')):
                relationResult = self._find_relation(
                    self, entity1, entity2, property1_name, property2_name, relation)
            else:
                relationResult = ''
            print("relationResult: ", relationResult)

            # Write transactions allow the driver to handle retries and transient errors
            if (entityResult1 != None) and (entityResult2 == None) and (propertyResult1 != None) and (propertyResult2 == None) and (relationResult != None):
                createPropertyResult2 = session.write_transaction(
                    self._create_and_return_entity_property, entity2, property2_name)
                print('created property2: ' + createPropertyResult2[0])

            # creating property2 and relation
            elif (propertyResult1 != None) and (propertyResult2 == None) and (relationResult == None):
                createrRelationPropertyResult2 = session.write_transaction(
                    self._create_and_return_relation_property2, property1_name, property2_name, relation)
                print('created property2 and relation: ' +
                      createrRelationPropertyResult2[0])

            # creating property1 and relation
            elif (propertyResult1 == None) and (propertyResult2 != None) and (relationResult == None):
                createrRelationPropertyResult1 = session.write_transaction(
                    self._create_and_return_relation_property1, property1_name, property2_name, relation)
                print('created property1 and relation: ' +
                      createrRelationPropertyResult1[0])

            # creating property1, property2 and relation
            elif (propertyResult1 == None) and (propertyResult2 == None) and (relationResult == None):
                createrRelationPropertyResult12 = session.write_transaction(
                    self._create_and_return_relation_properties, property1_name, property2_name, relation)
                print('created property1, property2 and relation: ' +
                      createrRelationPropertyResult12[0])

            # creating relation
            elif (propertyResult1 != None) and (propertyResult2 != None) and (relationResult == None):
                createrRelationResult = session.write_transaction(
                    self._create_and_return_relation, property1_name, property2_name, relation)
                print('created relation: ' +
                      createrRelationResult[0])

            # creating relation
            elif (propertyResult1 != None) and (propertyResult2 != None) and (relationResult != None) and (propertyResult1 != '') and (propertyResult2 != '') and (relationResult != ''):
                createrRelationPropertyResult = session.write_transaction(
                    self._set_and_return_relation_property, property1_name, property2_name, relation)
                print('set size property of relation: ' +
                      str(createrRelationPropertyResult[0]))

            # doing nothing
            else:
                print('Doing nothing.')

            # when it doesnot exist entity1
            print('--------------------------------The end of creating each property or relation.--------------------------------')

    @staticmethod
    def _set_and_return_relation_property(tx, property1_name, property2_name, relation):
        query = (
            "MATCH(n: Entity{name: $property1_name})-[r: " +
            relation + "] -> (m: Entity{name: $property2_name} )"
            "SET r.size=CASE WHEN r.size IS NULL THEN 2 ELSE r.size + 1 END "
            "RETURN r.size AS size"
        )
        result = tx.run(query, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["size"] for record in result]

    @staticmethod
    def _create_and_return_relation(tx, property1_name, property2_name, relation):
        query = (
            "MATCH (n:Entity {name: $property1_name}), (m:Entity {name: $property2_name}) "
            "CREATE (n)-[r:" + relation + "]->(m) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_properties(tx, property1_name, property2_name, relation):
        query = (
            "CREATE (n: Entity{name: $property1_name})-[r:" + relation +
            "] -> (m: Entity{name: $property2_name}) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_property1(tx, property1_name, property2_name, relation):
        query = (
            "MATCH (m: Entity{name: $property2_name}) "
            "CREATE (n: Entity{name: $property1_name})-[r:" + relation +
            "] -> (m) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_property2(tx, property1_name, property2_name, relation):
        query = (
            "MATCH (n: Entity{name: $property1_name}) "
            "CREATE (n)-[r:" + relation +
            "] -> (m: Entity{name: $property2_name}) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_entity_property(tx, entity, property_name):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (e:" + entity + " {name: $property_name}) "
            "RETURN e.name AS name"
        )
        result = tx.run(query, entity=entity, property_name=property_name)
        return [record["name"] for record in result]

    @staticmethod
    def _find_entity(self, entity):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_entity, entity)
            for record in result:
                print("Found entity name: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_entity(tx, entity):
        query = (
            "MATCH (e:" + entity + ") "
            "RETURN e.name AS name"
        )
        result = tx.run(query, entity=entity)
        return [record["name"] for record in result]

    @staticmethod
    def _find_entity_property(self, entity, property_name):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_entity_property, entity, property_name)
            for record in result:
                print("Found entity and property name: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_entity_property(tx, entity, property_name):
        query = (
            "MATCH (e:" + entity + ") "
            "WHERE e.name = $property_name "
            "RETURN e.name AS name"
        )
        result = tx.run(query, entity=entity, property_name=property_name)
        return [record["name"] for record in result]

    @staticmethod
    def _find_relation(self, entity1, entity2, property1_name, property2_name, relation):
        with self.driver.session() as session:
            result = session.read_transaction(
                self._find_and_return_relation, entity1=entity1, entity2=entity2, property1_name=property1_name, property2_name=property2_name, relation=relation)
            for record in result:
                print("Found property name: {record}".format(record=record))
                return record

    @staticmethod
    def _find_and_return_relation(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "MATCH (n:" + entity1 + " {name:$property1_name})-[r:" +
            relation + "]->(m:" + entity2 + "{name:$property2_name}) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
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
    sentence = "Sam go to aist in Tokyo everyday."
    # sentence = 'I go to aist in Tokyo everyday. I go to school every weekday. Everyone plays game at home, where I donot play.'
    # sentence = 'I go to aist in Tokyo everyday.'
    nlp = NLP(sentence)
    print("ner: ", nlp.get_ner())
    # print("tokenize: ", nlp.get_tokenize())
    # print("annotate: ", nlp.get_annotate())
    # print("pos_tag: ", nlp.get_pos_tag())
    # print("sentence: ", nlp.sentence)
    # print("parse: ", nlp.get_parse())
    print("dependency_parse: ", nlp.get_dependency_parse())
    ner = nlp.get_ner()
    dependencies = nlp.get_dependency_parse()

    # the count of dependency
    dependencyCount = 0

    # the count of root
    rootCount = 0

    # the count of dependency root
    dependencyRootCount = 0

    # get the dependencies
    for x, y, z in dependencies:
        # properties
        property1 = ''
        property2 = ''
        entity1 = ''
        entity2 = ''
        print(x)
        print(dependencyCount)
        # the first sentence
        if (x == 'ROOT') and (rootCount == 0):
            if y != 0:
                entity1 = ner[y-1][1]
                property1 = ner[y-1][0]
                print(entity1)
                print(property1)

            if z != 0:
                entity2 = ner[z-1][1]
                property2 = ner[z-1][0]
                print(entity2)
                print(property2)

            # create relation
            myneo4j.create_relation(entity1, entity2, property1, property2, x.replace(':', ''))

            # increase the count of root
            rootCount += 1

        elif (x != 'ROOT') and (rootCount == 1):
            if y != 0:
                entity1 = ner[y-1][1]
                property1 = ner[y-1][0]
                print(entity1)
                print(property1)

            if z != 0:
                entity2 = ner[z-1][1]
                property2 = ner[z-1][0]
                print(entity2)
                print(property2)

            # create relation
            myneo4j.create_relation(entity1, entity2, property1, property2, x.replace(':', ''))

        elif (x == 'ROOT') and (rootCount > 0):
            if y != 0:
                entity1 = ner[y-1][1]
                property1 = ner[y-1+dependencyCount][0]
                print(entity1)
                print(property1)

            if z != 0:
                entity2 = ner[z-1][1]
                property2 = ner[z-1+dependencyCount][0]
                print(entity2)
                print(property2)

            # create relation
            myneo4j.create_relation(entity1, entity2, property1, property2, x.replace(':', ''))

            # increase the count of root
            rootCount += 1
            # decrease dependency count
            dependencyRootCount = dependencyCount

        elif (x != 'ROOT') and (rootCount > 1):
            if y != 0:
                entity1 = ner[y-1][1]
                property1 = ner[y-1+dependencyRootCount][0]
                print(entity1)
                print(property1)

            if z != 0:
                entity2 = ner[z-1][1]
                property2 = ner[z-1+dependencyRootCount][0]
                print(entity2)
                print(property2)

            # create relation
            myneo4j.create_relation(entity1, entity2, property1, property2, x.replace(':', ''))

        else:
            print(dependencyCount)

        # increase dependency count
        dependencyCount += 1

    myneo4j.close()
