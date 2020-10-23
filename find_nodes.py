from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))


def get_friends_of(tx, name):
    friends = []
    result = tx.run("MATCH (a:Person)-[:KNOWS]->(f) "
                    "WHERE a.name = $name "
                    "RETURN f.name AS friend", name=name
                    )
    for record in result:
        friends.append((record["friend"]))
    return friends


with driver.session() as session:
    friends = session.read_transaction(get_friends_of, "Alice")

    for friend in friends:
        print(friend)

driver.close
