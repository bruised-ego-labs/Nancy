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

    def get_documents_by_author(self, author_name: str) -> list[str]:
        """
        Finds all documents authored by a given person.
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._find_documents_by_author, author_name)
            return result

    @staticmethod
    def _find_documents_by_author(tx, author_name):
        query = (
            "MATCH (p:Person {name: $author_name})-[:AUTHORED]->(d:Document) "
            "RETURN d.filename"
        )
        result = tx.run(query, author_name=author_name)
        return [record["d.filename"] for record in result]

    def add_relationship(self, source_node_label: str, source_node_name: str, relationship_type: str, target_node_label: str, target_node_name: str, context: str = None):
        """
        Creates a generic relationship between two nodes with optional context.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_relationship, source_node_label, source_node_name, relationship_type, target_node_label, target_node_name, context)
            print(f"Linked {source_node_name} -[:{relationship_type}]-> {target_node_name} in Neo4j.")

    @staticmethod
    def _create_relationship(tx, source_node_label, source_node_name, relationship_type, target_node_label, target_node_name, context):
        if context:
            query = (
                f"MERGE (a:{source_node_label} {{name: $source_name}}) "
                f"MERGE (b:{target_node_label} {{name: $target_name}}) "
                f"MERGE (a)-[r:{relationship_type}]->(b) "
                f"SET r.context = $context"
            )
            tx.run(query, source_name=source_node_name, target_name=target_node_name, context=context)
        else:
            query = (
                f"MERGE (a:{source_node_label} {{name: $source_name}}) "
                f"MERGE (b:{target_node_label} {{name: $target_name}}) "
                f"MERGE (a)-[:{relationship_type}]->(b)"
            )
            tx.run(query, source_name=source_node_name, target_name=target_node_name)
    
    def find_related_documents(self, document_filename: str, relationship_types: list = None, max_depth: int = 2) -> list[dict]:
        """
        Find documents related to a given document through various relationship types.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_related_documents, document_filename, relationship_types, max_depth)
    
    @staticmethod
    def _find_related_documents(tx, document_filename, relationship_types, max_depth):
        if relationship_types:
            rel_filter = "|".join(relationship_types)
            query = f"""
                MATCH (d1:Document {{filename: $filename}})
                MATCH (d1)-[r:{rel_filter}*1..{max_depth}]-(d2:Document)
                WHERE d1 <> d2
                RETURN DISTINCT d2.filename as filename, 
                       type(r[0]) as relationship_type,
                       r[0].context as context,
                       length(r) as path_length
                ORDER BY path_length, d2.filename
            """
        else:
            query = f"""
                MATCH (d1:Document {{filename: $filename}})
                MATCH (d1)-[r*1..{max_depth}]-(d2:Document)
                WHERE d1 <> d2
                RETURN DISTINCT d2.filename as filename,
                       type(r[0]) as relationship_type,
                       r[0].context as context,
                       length(r) as path_length
                ORDER BY path_length, d2.filename
            """
        
        result = tx.run(query, filename=document_filename)
        return [record.data() for record in result]
    
    def find_cross_team_influences(self, author1: str, author2: str) -> list[dict]:
        """
        Find how one team member's work influenced another's work.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_cross_team_influences, author1, author2)
    
    @staticmethod
    def _find_cross_team_influences(tx, author1, author2):
        query = """
            MATCH (p1:Person {name: $author1})-[:AUTHORED]->(d1:Document)
            MATCH (p2:Person {name: $author2})-[:AUTHORED]->(d2:Document)
            MATCH (d1)-[r]-(d2)
            RETURN d1.filename as source_doc,
                   d2.filename as target_doc,
                   type(r) as relationship_type,
                   r.context as context
            ORDER BY d1.filename, d2.filename
        """
        
        result = tx.run(query, author1=author1, author2=author2)
        return [record.data() for record in result]
    
    def find_documents_that_reference_topic(self, topic: str) -> list[dict]:
        """
        Find documents that reference or mention a specific topic/concept.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_documents_referencing_topic, topic)
    
    @staticmethod
    def _find_documents_referencing_topic(tx, topic):
        query = """
            MATCH (concept {name: $topic})<-[r:REFERENCES|MENTIONS|AFFECTS|INFLUENCES]-(d:Document)
            RETURN d.filename as filename,
                   type(r) as relationship_type,
                   r.context as context
            ORDER BY d.filename
            
            UNION
            
            MATCH (d:Document)-[r:REFERENCES|MENTIONS|AFFECTS|INFLUENCES]->(concept {name: $topic})
            RETURN d.filename as filename,
                   type(r) as relationship_type,
                   r.context as context
            ORDER BY d.filename
        """
        
        result = tx.run(query, topic=topic)
        return [record.data() for record in result]
    
    def get_author_collaboration_network(self, author: str = None) -> list[dict]:
        """
        Get the collaboration network - who works with whom through document relationships.
        """
        with self.driver.session() as session:
            if author:
                return session.read_transaction(self._get_author_collaborations, author)
            else:
                return session.read_transaction(self._get_all_collaborations)
    
    @staticmethod
    def _get_author_collaborations(tx, author):
        query = """
            MATCH (p1:Person {name: $author})-[:AUTHORED]->(d1:Document)
            MATCH (d1)-[r]-(d2:Document)<-[:AUTHORED]-(p2:Person)
            WHERE p1 <> p2
            RETURN p1.name as author1,
                   p2.name as author2,
                   type(r) as relationship_type,
                   count(*) as interaction_count
            ORDER BY interaction_count DESC, author2
        """
        
        result = tx.run(query, author=author)
        return [record.data() for record in result]
    
    @staticmethod
    def _get_all_collaborations(tx):
        query = """
            MATCH (p1:Person)-[:AUTHORED]->(d1:Document)
            MATCH (d1)-[r]-(d2:Document)<-[:AUTHORED]-(p2:Person)
            WHERE p1.name < p2.name  // Avoid duplicates
            RETURN p1.name as author1,
                   p2.name as author2,
                   type(r) as relationship_type,
                   count(*) as interaction_count
            ORDER BY interaction_count DESC
        """
        
        result = tx.run(query)
        return [record.data() for record in result]
    
    def find_decision_impact_chain(self, decision_maker: str, topic: str) -> list[dict]:
        """
        Find how a decision maker's choices impacted other work on a topic.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_decision_impact_chain, decision_maker, topic)
    
    @staticmethod
    def _find_decision_impact_chain(tx, decision_maker, topic):
        query = """
            MATCH (p:Person {name: $decision_maker})-[:AUTHORED]->(d1:Document)
            MATCH (d1)-[:AFFECTS|INFLUENCES|CONSTRAINS*1..3]->(d2:Document)
            WHERE d1.filename CONTAINS $topic OR d2.filename CONTAINS $topic
            MATCH (d2)<-[:AUTHORED]-(p2:Person)
            RETURN d1.filename as decision_document,
                   d2.filename as affected_document,
                   p2.name as affected_author,
                   length(path) as impact_distance
            ORDER BY impact_distance, affected_author
        """
        
        result = tx.run(query, decision_maker=decision_maker, topic=topic)
        return [record.data() for record in result]
    
    def add_concept_node(self, concept_name: str, concept_type: str = "Concept"):
        """
        Add a concept node to the graph (for topics, technologies, constraints, etc.)
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_concept_node, concept_name, concept_type)
            print(f"Added {concept_type} node for {concept_name} to Neo4j.")
    
    @staticmethod
    def _create_concept_node(tx, concept_name, concept_type):
        query = f"MERGE (c:{concept_type} {{name: $name}})"
        tx.run(query, name=concept_name)
    
    def get_knowledge_graph_statistics(self) -> dict:
        """
        Get statistics about the knowledge graph structure.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._get_graph_statistics)
    
    @staticmethod
    def _get_graph_statistics(tx):
        stats = {}
        
        # Node counts by label
        node_counts = tx.run("""
            CALL db.labels() YIELD label
            CALL apoc.cypher.run('MATCH (n:' + label + ') RETURN count(n) as count', {}) YIELD value
            RETURN label, value.count as count
        """).data()
        
        if not node_counts:  # Fallback if APOC is not available
            node_counts = [
                {"label": "Person", "count": tx.run("MATCH (p:Person) RETURN count(p) as count").single()["count"]},
                {"label": "Document", "count": tx.run("MATCH (d:Document) RETURN count(d) as count").single()["count"]},
                {"label": "Concept", "count": tx.run("MATCH (c:Concept) RETURN count(c) as count").single()["count"]}
            ]
        
        stats['node_counts'] = {item['label']: item['count'] for item in node_counts}
        
        # Relationship counts
        rel_counts = tx.run("""
            MATCH ()-[r]->()
            RETURN type(r) as relationship_type, count(r) as count
            ORDER BY count DESC
        """).data()
        
        stats['relationship_counts'] = {item['relationship_type']: item['count'] for item in rel_counts}
        
        # Most connected documents
        connected_docs = tx.run("""
            MATCH (d:Document)
            OPTIONAL MATCH (d)-[r]-()
            RETURN d.filename as filename, count(r) as connection_count
            ORDER BY connection_count DESC
            LIMIT 10
        """).data()
        
        stats['most_connected_documents'] = connected_docs
        
        return stats
