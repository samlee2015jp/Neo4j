from nlp import NLP

from neo4j import GraphDatabase


class DealNeo4j:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def remove_relations_nodes(self):
        with self.driver.session() as session:
            session.write_transaction(self._remove_relations_nodes)

    def create_relation(self, entity1, entity2, property1_name, property2_name, relation):
        with self.driver.session() as session:

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
            if (propertyResult1 != None) and (propertyResult2 == None) and (relationResult != None):
                createPropertyResult2 = session.write_transaction(
                    self._create_and_return_entity_property, entity2, property2_name)
                print('created property2: ' + createPropertyResult2[0])

            # creating property2 and relation
            elif (propertyResult1 != None) and (propertyResult2 == None) and (relationResult == None):
                createrRelationPropertyResult2 = session.write_transaction(
                    self._create_and_return_relation_property2, entity1, entity2, property1_name, property2_name, relation)
                print('created property2 and relation: ' + 
                      createrRelationPropertyResult2[0])

            # creating property1 and relation
            elif (propertyResult1 == None) and (propertyResult2 != None) and (relationResult == None):
                createrRelationPropertyResult1 = session.write_transaction(
                    self._create_and_return_relation_property1, entity1, entity2, property1_name, property2_name, relation)
                print('created property1 and relation: ' + 
                      createrRelationPropertyResult1[0])

            # creating property1, property2 and relation
            elif (propertyResult1 == None) and (propertyResult2 == None) and (relationResult == None):
                createrRelationPropertyResult12 = session.write_transaction(
                    self._create_and_return_relation_properties, entity1, entity2, property1_name, property2_name, relation)
                print('created property1, property2 and relation: ' + 
                      createrRelationPropertyResult12[0])

            # creating relation
            elif (propertyResult1 != None) and (propertyResult2 != None) and (relationResult == None):
                createrRelationResult = session.write_transaction(
                    self._create_and_return_relation, entity1, entity2, property1_name, property2_name, relation)
                print('created relation: ' + 
                      createrRelationResult[0])

            # creating relation
            elif (propertyResult1 != None) and (propertyResult2 != None) and (relationResult != None) and (propertyResult1 != '') and (propertyResult2 != '') and (relationResult != ''):
                createrRelationPropertyResult = session.write_transaction(
                    self._set_and_return_relation_property, entity1, entity2, property1_name, property2_name, relation)
                print('set size property of relation: ' + 
                      str(createrRelationPropertyResult[0]))

            # doing nothing
            else:
                print('Doing nothing.')

            # when it doesnot exist entity1
            print('--------------------------------The end of creating each property or relation.--------------------------------')

    @staticmethod
    def _set_and_return_relation_property(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "MATCH(n: " + entity1 + "{name: $property1_name})-[r: " + 
            relation + "] -> (m: " + entity2 + "{name: $property2_name} )"
            "SET r.size=CASE WHEN r.size IS NULL THEN 2 ELSE r.size + 1 END "
            "RETURN r.size AS size"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["size"] for record in result]

    @staticmethod
    def _create_and_return_relation(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "MATCH (n: " + entity1 + " {name: $property1_name}), (m:" + entity2 + " {name: $property2_name}) "
            "CREATE (n)-[r:" + relation + "]->(m) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_properties(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "CREATE (n: " + entity1 + "{name: $property1_name})-[r:" + relation + 
            "] -> (m: " + entity2 + "{name: $property2_name}) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_property1(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "MATCH (m: " + entity2 + "{name: $property2_name}) "
            "CREATE (n: " + entity1 + "{name: $property1_name})-[r:" + relation + 
            "] -> (m) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _create_and_return_relation_property2(tx, entity1, entity2, property1_name, property2_name, relation):
        query = (
            "MATCH (n: " + entity1 + "{name: $property1_name}) "
            "CREATE (n)-[r:" + relation + 
            "] -> (m: " + entity2 + "{name: $property2_name}) "
            "RETURN type(r) AS relation"
        )
        result = tx.run(query, entity1=entity1, entity2=entity2, property1_name=property1_name,
                        property2_name=property2_name, relation=relation)
        return [record["relation"] for record in result]

    @staticmethod
    def _remove_relations_nodes(tx):

        query = (
            "MATCH (n)-[r]->(m) DELETE r,n,m "
        )
        result = tx.run(query)
        return result

    @staticmethod
    def _create_and_return_entity_property(tx, entity, property_name):

        # To learn more about the Cypher syntax.
        # see http://neo4j.com/docs/cypher-manual/current/

        # The Reference Card is also a good resource for keywords,
        # see https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "CREATE (e: " + entity + " {name: $property_name}) "
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
            "MATCH (e: " + entity + ") "
            "RETURN e AS name"
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
            "MATCH (e: " + entity + ") "
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
            "MATCH (n: " + entity1 + " {name:$property1_name})-[r:" + 
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
    # sentence = "Aist is one of departments in National Institute of Advanced Industrial Science amd Technology which is a organization like WTO."
    sentence = "Liu, Li who comes from Changsha and other people go to aist in Tokyo Japan every weekday since Oct 15th 2020, and we come from different countries and areas. \
        aist is one of departments in National Institute of Advanced Industrial Science and Technology which is a organization like WTO. Li who comes from Changsha Hunan province."
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
    # the count of dependency root
    dependencyRootCount = 0
    # the count of root
    rootCount = 0

    # remove all relation and nodes
    myneo4j.remove_relations_nodes()
    print('All the relations and nodes have been removed.')

    myDepen = []

    # get the dependencies
    for x, y, z in dependencies:
        # properties
        property1 = ''
        property2 = ''
        entity1 = ''
        entity2 = ''
        relation = ''
        print('-------------------------------------------------------------------------dependency_parse:[0]: ' + x)
        print('-------------------------------------------------------------------------dependency_parse:[1]: ' + str(y))
        print('-------------------------------------------------------------------------dependency_parse:[2]: ' + str(z))
        print('-------------------------------------------------------------------------dependencyCount: ' + str(dependencyCount))

        if (dependencyCount == 0) and (rootCount == 0) and (x == 'ROOT'):
            print('Nothing')
        elif (dependencyCount > 0) and (rootCount == 0) and (x == 'ROOT'):
            rootCount += 1
            dependencyRootCount = dependencyCount
            z += dependencyRootCount
        elif (dependencyCount > 0) and (rootCount > 0) and (x == 'ROOT'):
            rootCount += 1
            dependencyRootCount = dependencyCount
            z += dependencyRootCount
        elif (dependencyCount > 0) and  (rootCount > 0) and (x != 'ROOT'):
            y += dependencyRootCount
            z += dependencyRootCount
            
        print('******************************************************************************************* x: ' + x)
        print('******************************************************************************************* y: ' + str(y))
        print('******************************************************************************************* z: ' + str(z))
        print('-------------------------------------------------------------------------dependencyCount: ' + str(dependencyCount))

        if y != 0:
                entity1 = ner[y - 1][1]
                property1 = ner[y - 1][0]

        if z != 0:
                entity2 = ner[z - 1][1]
                property2 = ner[z - 1][0]
        relation = x.replace(':', '')
                
        # entity, property name and relation
        print("***********************************************************************************************************************************************")
        print("entity1: ", entity1)
        print("entity2: ", entity2)
        print("property1: ", property1)
        print("property2: ", property2)
        print("relation: ", relation)
        print("***********************************************************************************************************************************************")

        # create relation
        myneo4j.create_relation(entity1, entity2, property1, property2, relation)

        # increase dependency
        dependencyCount += 1

    myneo4j.close()
