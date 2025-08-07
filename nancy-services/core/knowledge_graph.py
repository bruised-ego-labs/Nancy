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

class GraphBrain:
    """
    Handles interactions with the Graph Brain (Neo4j) - the project knowledge graph.
    Captures the complete story of project decisions, relationships, and evolution.
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
    
    # ============================================================================
    # ENHANCED PROJECT STORY CAPABILITIES
    # Capturing decisions, meetings, features, and project evolution
    # ============================================================================
    
    def add_decision_node(self, decision_name: str, decision_maker: str, context: str = None, era: str = None):
        """
        Add a decision node with the person who made it and optional context.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_decision_node, decision_name, decision_maker, context, era)
            print(f"Added Decision '{decision_name}' by {decision_maker} to GraphBrain.")
    
    @staticmethod
    def _create_decision_node(tx, decision_name, decision_maker, context, era):
        # Create decision node
        query = "MERGE (d:Decision {name: $decision_name})"
        if context:
            query += " SET d.context = $context"
        if era:
            query += " SET d.era = $era"
        tx.run(query, decision_name=decision_name, context=context, era=era)
        
        # Link to decision maker
        tx.run("""
            MERGE (p:Person {name: $decision_maker})
            MERGE (d:Decision {name: $decision_name})
            MERGE (p)-[:MADE]->(d)
        """, decision_maker=decision_maker, decision_name=decision_name)
    
    def add_meeting_node(self, meeting_name: str, attendees: list, decisions_made: list = None, era: str = None):
        """
        Add a meeting node with attendees and any decisions that resulted.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_meeting_node, meeting_name, attendees, decisions_made, era)
            print(f"Added Meeting '{meeting_name}' with {len(attendees)} attendees to GraphBrain.")
    
    @staticmethod
    def _create_meeting_node(tx, meeting_name, attendees, decisions_made, era):
        # Create meeting node
        query = "MERGE (m:Meeting {name: $meeting_name})"
        if era:
            query += " SET m.era = $era"
        tx.run(query, meeting_name=meeting_name, era=era)
        
        # Link attendees
        for attendee in attendees:
            tx.run("""
                MERGE (p:Person {name: $attendee})
                MERGE (m:Meeting {name: $meeting_name})
                MERGE (p)-[:ATTENDED]->(m)
            """, attendee=attendee, meeting_name=meeting_name)
        
        # Link decisions made in meeting
        if decisions_made:
            for decision in decisions_made:
                tx.run("""
                    MERGE (m:Meeting {name: $meeting_name})
                    MERGE (d:Decision {name: $decision})
                    MERGE (m)-[:RESULTED_IN]->(d)
                """, meeting_name=meeting_name, decision=decision)
    
    def add_feature_node(self, feature_name: str, owner: str = None, influenced_by_decisions: list = None, era: str = None):
        """
        Add a feature node and link it to decisions that influenced it.
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_feature_node, feature_name, owner, influenced_by_decisions, era)
            print(f"Added Feature '{feature_name}' to GraphBrain.")
    
    @staticmethod
    def _create_feature_node(tx, feature_name, owner, influenced_by_decisions, era):
        # Create feature node
        query = "MERGE (f:Feature {name: $feature_name})"
        if era:
            query += " SET f.era = $era"
        tx.run(query, feature_name=feature_name, era=era)
        
        # Link to owner
        if owner:
            tx.run("""
                MERGE (p:Person {name: $owner})
                MERGE (f:Feature {name: $feature_name})
                MERGE (p)-[:OWNS]->(f)
            """, owner=owner, feature_name=feature_name)
        
        # Link to influencing decisions
        if influenced_by_decisions:
            for decision in influenced_by_decisions:
                tx.run("""
                    MERGE (d:Decision {name: $decision})
                    MERGE (f:Feature {name: $feature_name})
                    MERGE (d)-[:LED_TO]->(f)
                """, decision=decision, feature_name=feature_name)
    
    def add_era_node(self, era_name: str, description: str = None, start_date: str = None, end_date: str = None):
        """
        Add a project era/phase node (e.g., "Initial Research", "Q3 2025", "MVP Development").
        """
        with self.driver.session() as session:
            session.write_transaction(self._create_era_node, era_name, description, start_date, end_date)
            print(f"Added Era '{era_name}' to GraphBrain.")
    
    @staticmethod
    def _create_era_node(tx, era_name, description, start_date, end_date):
        query = "MERGE (e:Era {name: $era_name})"
        if description:
            query += " SET e.description = $description"
        if start_date:
            query += " SET e.start_date = $start_date"
        if end_date:
            query += " SET e.end_date = $end_date"
        tx.run(query, era_name=era_name, description=description, start_date=start_date, end_date=end_date)
    
    def link_document_to_era(self, filename: str, era_name: str):
        """
        Link a document to the era when it was created.
        """
        with self.driver.session() as session:
            session.write_transaction(self._link_document_era, filename, era_name)
            print(f"Linked document {filename} to era {era_name}.")
    
    @staticmethod
    def _link_document_era(tx, filename, era_name):
        tx.run("""
            MERGE (d:Document {filename: $filename})
            MERGE (e:Era {name: $era_name})
            MERGE (d)-[:CREATED_IN]->(e)
        """, filename=filename, era_name=era_name)
    
    def find_decision_provenance(self, feature_or_topic: str) -> list[dict]:
        """
        Trace back to find what decisions led to a feature or influenced work on a topic.
        This answers "Why did we build this feature this way?"
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_decision_provenance, feature_or_topic)
    
    @staticmethod
    def _find_decision_provenance(tx, feature_or_topic):
        query = """
            // Find decisions that led to features
            MATCH (d:Decision)-[:LED_TO]->(f:Feature)
            WHERE f.name CONTAINS $topic
            MATCH (p:Person)-[:MADE]->(d)
            OPTIONAL MATCH (m:Meeting)-[:RESULTED_IN]->(d)
            OPTIONAL MATCH (doc:Document)-[:INFLUENCED_BY]->(d)
            RETURN 'feature' as type,
                   f.name as target,
                   d.name as decision,
                   p.name as decision_maker,
                   d.context as decision_context,
                   d.era as era,
                   m.name as meeting,
                   collect(DISTINCT doc.filename) as influencing_documents
            
            UNION
            
            // Find decisions that influenced documents about the topic
            MATCH (d:Decision)<-[:INFLUENCED_BY]-(doc:Document)
            WHERE doc.filename CONTAINS $topic
            MATCH (p:Person)-[:MADE]->(d)
            OPTIONAL MATCH (m:Meeting)-[:RESULTED_IN]->(d)
            RETURN 'document' as type,
                   doc.filename as target,
                   d.name as decision,
                   p.name as decision_maker,
                   d.context as decision_context,
                   d.era as era,
                   m.name as meeting,
                   [] as influencing_documents
            
            ORDER BY era, decision_maker
        """
        
        result = tx.run(query, topic=feature_or_topic)
        return [record.data() for record in result]
    
    def find_knowledge_expert(self, topic: str) -> list[dict]:
        """
        Find who are the real experts on a topic by analyzing their connections
        to decisions, documents, and features related to that topic.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_knowledge_expert, topic)
    
    @staticmethod
    def _find_knowledge_expert(tx, topic):
        query = """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[:AUTHORED]->(doc:Document)
            WHERE doc.filename CONTAINS $topic
            OPTIONAL MATCH (p)-[:MADE]->(d:Decision)
            WHERE d.name CONTAINS $topic OR d.context CONTAINS $topic
            OPTIONAL MATCH (p)-[:OWNS]->(f:Feature)
            WHERE f.name CONTAINS $topic
            
            WITH p, 
                 count(DISTINCT doc) as documents_authored,
                 count(DISTINCT d) as decisions_made,
                 count(DISTINCT f) as features_owned,
                 (count(DISTINCT doc) + count(DISTINCT d) * 2 + count(DISTINCT f) * 3) as expertise_score
            
            WHERE expertise_score > 0
            
            RETURN p.name as expert,
                   documents_authored,
                   decisions_made,
                   features_owned,
                   expertise_score
            ORDER BY expertise_score DESC
            LIMIT 10
        """
        
        result = tx.run(query, topic=topic)
        return [record.data() for record in result]
    
    def find_impact_analysis(self, document_name: str) -> list[dict]:
        """
        Find what would be affected if we changed a specific document.
        Answers "What will this change affect?"
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_impact_analysis, document_name)
    
    @staticmethod
    def _find_impact_analysis(tx, document_name):
        query = """
            MATCH (doc:Document {filename: $document_name})
            
            // Find decisions influenced by this document
            OPTIONAL MATCH (doc)-[:INFLUENCED_BY]->(d:Decision)
            OPTIONAL MATCH (d)-[:LED_TO]->(f:Feature)
            OPTIONAL MATCH (f)<-[:OWNS]-(owner:Person)
            
            // Find documents that reference this one
            OPTIONAL MATCH (doc)<-[:REFERENCES|DEPENDS_ON]-(other_doc:Document)
            OPTIONAL MATCH (other_doc)<-[:AUTHORED]-(author:Person)
            
            RETURN 'decision_impact' as impact_type,
                   d.name as affected_item,
                   f.name as downstream_feature,
                   owner.name as stakeholder,
                   'Decision maker' as stakeholder_role
            WHERE d IS NOT NULL
            
            UNION
            
            MATCH (doc:Document {filename: $document_name})
            OPTIONAL MATCH (doc)<-[:REFERENCES|DEPENDS_ON]-(other_doc:Document)
            OPTIONAL MATCH (other_doc)<-[:AUTHORED]-(author:Person)
            
            RETURN 'document_impact' as impact_type,
                   other_doc.filename as affected_item,
                   null as downstream_feature,
                   author.name as stakeholder,
                   'Document author' as stakeholder_role
            WHERE other_doc IS NOT NULL
            
            ORDER BY impact_type, affected_item
        """
        
        result = tx.run(query, document_name=document_name)
        return [record.data() for record in result]
    
    def find_project_timeline(self, era_name: str = None) -> list[dict]:
        """
        Get a timeline view of project evolution showing decisions, meetings, and documents by era.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_project_timeline, era_name)
    
    @staticmethod
    def _find_project_timeline(tx, era_name):
        if era_name:
            query = """
                MATCH (e:Era {name: $era_name})
                OPTIONAL MATCH (doc:Document)-[:CREATED_IN]->(e)
                OPTIONAL MATCH (doc)<-[:AUTHORED]-(author:Person)
                OPTIONAL MATCH (d:Decision {era: $era_name})
                OPTIONAL MATCH (d)<-[:MADE]-(decision_maker:Person)
                OPTIONAL MATCH (m:Meeting {era: $era_name})
                
                RETURN e.name as era,
                       e.description as era_description,
                       collect(DISTINCT {document: doc.filename, author: author.name}) as documents,
                       collect(DISTINCT {decision: d.name, maker: decision_maker.name, context: d.context}) as decisions,
                       collect(DISTINCT m.name) as meetings
                ORDER BY e.start_date
            """
            result = tx.run(query, era_name=era_name)
        else:
            query = """
                MATCH (e:Era)
                OPTIONAL MATCH (doc:Document)-[:CREATED_IN]->(e)
                OPTIONAL MATCH (doc)<-[:AUTHORED]-(author:Person)
                OPTIONAL MATCH (d:Decision {era: e.name})
                OPTIONAL MATCH (d)<-[:MADE]-(decision_maker:Person)
                OPTIONAL MATCH (m:Meeting {era: e.name})
                
                RETURN e.name as era,
                       e.description as era_description,
                       collect(DISTINCT {document: doc.filename, author: author.name}) as documents,
                       collect(DISTINCT {decision: d.name, maker: decision_maker.name, context: d.context}) as decisions,
                       collect(DISTINCT m.name) as meetings
                ORDER BY e.start_date, e.name
            """
            result = tx.run(query)
        
        return [record.data() for record in result]
    
    def find_knowledge_silos(self) -> list[dict]:
        """
        Identify potential knowledge silos - people who are the only ones connected to certain topics.
        """
        with self.driver.session() as session:
            return session.read_transaction(self._find_knowledge_silos)
    
    @staticmethod
    def _find_knowledge_silos(tx):
        query = """
            // Find concepts/topics that only one person is connected to
            MATCH (concept)
            WHERE concept:Feature OR concept:Decision OR 
                  (concept:Document AND concept.filename =~ '.*(?i)(spec |design |architecture ).*')
            
            MATCH (concept)<-[r]-(p:Person)
            
            WITH concept, count(DISTINCT p) as person_count, collect(DISTINCT p.name) as connected_people
            WHERE person_count = 1
            
            RETURN labels(concept)[0] as concept_type,
                   concept.name as concept_name,
                   connected_people[0] as sole_expert,
                   'Potential knowledge silo' as risk_level
            
            ORDER BY concept_type, concept_name
        """
        
        result = tx.run(query)
        return [record.data() for record in result]
    
    def get_authored_documents(self, author_name: str) -> list[dict]:
        """
        Get documents authored by a specific person (for IntelligentQueryOrchestrator).
        """
        with self.driver.session() as session:
            return session.read_transaction(self._get_authored_documents, author_name)
    
    @staticmethod
    def _get_authored_documents(tx, author_name):
        query = """
            MATCH (p:Person {name: $author_name})-[:AUTHORED]->(d:Document)
            RETURN d.filename as document, d.file_type as file_type
            ORDER BY d.filename
        """
        result = tx.run(query, author_name=author_name)
        return [record.data() for record in result]
    
    def explore_relationships(self, entity_name: str) -> list[dict]:
        """
        Explore relationships for a specific entity (for IntelligentQueryOrchestrator).
        """
        with self.driver.session() as session:
            return session.read_transaction(self._explore_relationships, entity_name)
    
    @staticmethod
    def _explore_relationships(tx, entity_name):
        query = """
            MATCH (entity)
            WHERE entity.name = $entity_name
            MATCH (entity)-[r]-(related)
            RETURN entity.name as source,
                   type(r) as relationship,
                   related.name as target,
                   labels(related)[0] as target_type,
                   r.context as context
            LIMIT 20
        """
        result = tx.run(query, entity_name=entity_name)
        return [record.data() for record in result]
    
    def get_cross_references(self) -> list[dict]:
        """
        Get documents that reference each other (for IntelligentQueryOrchestrator).
        """
        with self.driver.session() as session:
            return session.read_transaction(self._get_cross_references)
    
    @staticmethod
    def _get_cross_references(tx):
        query = """
            MATCH (d1:Document)-[r:REFERENCES]->(d2:Document)
            RETURN d1.filename as source,
                   d2.filename as target,
                   r.context as context
            ORDER BY d1.filename, d2.filename
        """
        result = tx.run(query)
        return [record.data() for record in result]
