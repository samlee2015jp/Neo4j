from stanfordcorenlp import StanfordCoreNLP
import platform

from neo4j import GraphDatabase


class DealNeo4j:

    def __init__(self):
        # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.

        scheme = "bolt"  # connecting to Aura. use the "neo4j+s" URI scheme
        host_name = "localhost"
        port = 7687
        url = "{scheme}://{host_name}:{port}".format(
            scheme=scheme, host_name=host_name, port=port)
        user = "neo4j"
        password = "password"
        self.driver = GraphDatabase.driver(url, auth=(user, password))
        # stanford-corenlp path
        file_path = ''
        if platform.system() == 'Windows':
            file_path = r'D:\samli_202010\CoreNLP\CoreNLP\stanford-corenlp-4.1.0'
        elif platform.system() == 'Darwin':
            file_path = r'/Users/Sam/demo/neo4j/stanford-corenlp-4.1.0'
        else:
            print('This system is Linux.')
        self.nlp = StanfordCoreNLP(file_path)

    def close(self):
        self.nlp.close
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
            "MATCH (n: " + entity1 + " {name: $property1_name}), (m:" +
            entity2 + " {name: $property2_name}) "
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
                print("Found entity and property name: {record}".format(
                    record=record))
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
    myneo4j = DealNeo4j()

    # the sentence
    # sentence = "Aist is one of departments in National Institute of Advanced Industrial Science amd Technology which is a organization like WTO."
    # sentence = "Liu, Li who comes from Changsha and other people go to aist in Tokyo Japan every weekday since Oct 15th 2020, and we come from different countries and areas. \
    #     Aist is one of departments in National Institute of Advanced Industrial Science and Technology which is a organization like WTO. Li who comes from\
    #     Changsha Hunan province is Chinese Engineer. My Github address is https://github.com/samlee2015jp."

#     sentence = "If you're a photographer, keep all the necessary lens, cords, and batteries in the same quadrant of your home or studio. Paints should be kept with brushes, cleaner, and canvas, print supplies should be by the ink, etc. Make broader groups and areas for your supplies to make finding them easier, limiting your search to a much smaller area. Some ideas include:\
# \
# \
# Essential supplies area -- the things you use every day.\
# Inspiration and reference area.\
# Dedicated work area .\
# Infrequent or secondary supplies area, tucked out of the way.;\
# , This doesn't mean cleaning the entire studio, it just means keeping the area immediately around the desk, easel, pottery wheel, etc. clean each night. Discard trash or unnecessary materials and wipe down dirty surfaces. Endeavor to leave the workspace in a way that you can sit down the next day and start working immediately, without having to do any work or tidying.\
# \
# \
# Even if the rest of your studio is a bit disorganized, an organized workspace will help you get down to business every time you want to make art.\
# \
# , As visual people, a lot of artist clutter comes from a desire to keep track of supplies visually instead of tucked out of sight. By using jars, old glasses, vases, and cheap, clear plastic drawers, you can keep things \
# in sight without leaving it strewn about haphazardly. Some ideas, beyond those just mentioned, include:\
# \
# \
# Canvas shoe racks on the back of the door\
# Wine racks with cups in each slot to hold pens/pencils.\
# Plastic restaurant squirt bottles for paint, pigment, etc., Simply string up the wires across a wall or along the ceiling and use them to hold essential papers that you don't want to cut or ruin with tacks or tape. Cheap and easy, this is also a good way to handle papers and ideas you touch regularly or need to pin up and down for inspiration., Shelving is an artist's best friend and is a cheap and easy way to get more room in your studio or art space. Don't be afraid to get up high either, especially for infrequently used supplies. The upper reaches of the room are often the most under-utilized, but provide vital space for all your tools and materials., Turning one wall into a chalkboard gives you a perfect space for ideas, sketches, and planning without requiring extra equipment or space. You can even use it for smaller areas. Paint over jars or storage equipment, allowing you to relabel them with chalk as your needs change.\
# \
# , A lot of disorganization comes when you keep moving the location of things, trying to optimize your space by reorganizing frequently. This usually has the opposite effect, leading to lost items and uncertainty when cleaning, but an afternoon with a label maker can solve everything. Instead of spending all of your mental energy looking for or storing things, you can just follow the labels, freeing your mind to think about art., Once a \
# month, do a purge of your studio. If it isn't essential or part of a project, either throw it out or file it away for later. Artists are constantly making new things, experimenting, and making a mess. This is a good thing, but only if you set aside time to declutter. It may not be fun at the moment, but it is a lot more fun than spending 30 minutes digging through junk to find the right paint or an old sketch.\
# \
# \
# Don't be sentimental here. If you haven't used it in the last six months there is little chance you'll use it in the next six months. Toss it."
    sentence = 'I go to AIST in Tokyo everyday. I go to school every weekday. Everyone plays game at home, where I donot play.'
    # sentence = 'Joe is living in Los Angeles.'
    print("ner: ", myneo4j.nlp.ner(sentence))
    # print("tokenize: ", myneo4j.nlp.tokenize(sentence))
    # print("annotate: ", myneo4j.nlp.annotate(sentence))
    print("pos_tag: ", myneo4j.nlp.pos_tag(sentence))
    # print("sentence: ", myneo4j.nlp.sentence(sentence))
    # print("parse: ", myneo4j.nlp.parse((sentence)))
    print("dependency_parse: ", myneo4j.nlp.dependency_parse(sentence))
    ner = myneo4j.nlp.ner(sentence)
    pos = myneo4j.nlp.pos_tag(sentence)
    dependencies = myneo4j.nlp.dependency_parse(sentence)

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
        print(
            '-------------------------------------------------------------------------dependency_parse:[0]: ' + x)
        print(
            '-------------------------------------------------------------------------dependency_parse:[1]: ' + str(y))
        print(
            '-------------------------------------------------------------------------dependency_parse:[2]: ' + str(z))
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
        elif (dependencyCount > 0) and (rootCount > 0) and (x != 'ROOT'):
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
        myneo4j.create_relation(
            entity1, entity2, property1, property2, relation)

        # increase dependency
        dependencyCount += 1

    myneo4j.close()
