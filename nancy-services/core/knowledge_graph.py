from neo4j import GraphDatabase
import os
from typing import Optional


def get_neo4j_driver():
    """
    Returns a Neo4j driver connected to the specified URI.
    """
    uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
    # The default auth is neo4j/password in the docker-compose file
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver

class RelationalBrain:
    """
    Handles interactions with the Relational Brain (Neo4j).
    """
    def __init__(self):
        self.driver = get_neo4j_driver()

    def close(self):
        self.driver.close()

    def add_document_node(self, filename: str, file_type: str):
        """
        Adds a new Document node to the graph.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_document_node, filename, file_type)
            print(f"Added Document node for {filename} to Neo4j.")

    @staticmethod
    def _create_document_node(tx, filename, file_type):
        query = (
            "MERGE (d:Document {filename: $filename}) "
            "ON CREATE SET d.file_type = $file_type"
        )
        tx.run(query, filename=filename, file_type=file_type)

    def query(self, cypher_query: str, params: dict = None):
        """
        Placeholder for querying the graph database.
        """
        with self.driver.session() as session:
            result = session.run(cypher_query, params)
            return [record.data() for record in result]

    def get_author_of_document(self, filename: str) -> Optional[str]:
        """
        Finds the author of a given document.
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._find_author, filename)
            return result[0] if result else None

    @staticmethod
    def _find_author(tx, filename):
        query = (
            "MATCH (p:Person)-[:AUTHORED]->(d:Document {filename: $filename}) "
            "RETURN p.name"
        )
        result = tx.run(query, filename=filename)
        return [record["p.name"] for record in result]

    def add_author_relationship(self, filename: str, author_name: str):
        """
        Creates a Person node for the author (if it doesn't exist)
        and links it to the Document node.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_author_relationship, filename, author_name)
            print(f"Linked author {author_name} to document {filename} in Neo4j.")

    @staticmethod
    def _create_author_relationship(tx, filename, author_name):
        query = (
            "MERGE (p:Person {name: $author_name}) "
            "MERGE (d:Document {filename: $filename}) "
            "MERGE (p)-[:AUTHORED]->(d)"
        )
        tx.run(query, author_name=author_name, filename=filename)
