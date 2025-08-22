"""
Nancy Knowledge Packet Schema Validation
Implements JSON schema validation for standardized Nancy Knowledge Packets.
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib


KNOWLEDGE_PACKET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://schemas.nancy.ai/knowledge-packet/v1.0",
    "title": "Nancy Knowledge Packet Schema",
    "description": "Standardized data format for submitting content to Nancy Core from MCP servers",
    "type": "object",
    "required": [
        "packet_version",
        "packet_id", 
        "timestamp",
        "source",
        "metadata",
        "content"
    ],
    "properties": {
        "packet_version": {
            "type": "string",
            "pattern": "^\\d+\\.\\d+$",
            "description": "Schema version for this packet"
        },
        "packet_id": {
            "type": "string",
            "pattern": "^[a-f0-9]{64}$",
            "description": "SHA256 hash serving as unique identifier"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp when packet was created"
        },
        "source": {
            "type": "object",
            "required": ["mcp_server", "server_version", "original_location", "content_type"],
            "properties": {
                "mcp_server": {"type": "string"},
                "server_version": {
                    "type": "string", 
                    "pattern": "^\\d+\\.\\d+\\.\\d+$"
                },
                "original_location": {"type": "string"},
                "content_type": {
                    "type": "string",
                    "enum": ["spreadsheet", "document", "codebase", "email", "chat", "api_docs", "presentation", "image", "video", "audio", "database", "custom"]
                },
                "extraction_method": {"type": "string"}
            }
        },
        "metadata": {
            "type": "object",
            "required": ["title"],
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "contributors": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "created_at": {"type": "string", "format": "date-time"},
                "modified_at": {"type": "string", "format": "date-time"},
                "file_size": {"type": "integer", "minimum": 0},
                "content_hash": {
                    "type": "string",
                    "pattern": "^[a-f0-9]{64}$"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "department": {"type": "string"},
                "project": {"type": "string"},
                "classification": {
                    "type": "string",
                    "enum": ["public", "internal", "confidential", "restricted"]
                },
                "language": {
                    "type": "string",
                    "pattern": "^[a-z]{2}(-[A-Z]{2})?$"
                }
            }
        },
        "content": {
            "type": "object",
            "properties": {
                "vector_data": {
                    "type": "object",
                    "properties": {
                        "chunks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["chunk_id", "text"],
                                "properties": {
                                    "chunk_id": {"type": "string"},
                                    "text": {"type": "string"},
                                    "chunk_metadata": {"type": "object"}
                                }
                            }
                        },
                        "embedding_model": {"type": "string"},
                        "chunk_strategy": {
                            "type": "string",
                            "enum": ["fixed_size", "semantic_paragraphs", "sentence_boundary", "document_structure", "code_functions", "custom"]
                        },
                        "chunk_size": {"type": "integer", "minimum": 50, "maximum": 8192},
                        "chunk_overlap": {"type": "integer", "minimum": 0, "maximum": 500}
                    }
                },
                "analytical_data": {
                    "type": "object",
                    "properties": {
                        "structured_fields": {"type": "object"},
                        "table_data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["table_name", "columns", "rows"],
                                "properties": {
                                    "table_name": {"type": "string"},
                                    "columns": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "rows": {
                                        "type": "array",
                                        "items": {"type": "array"}
                                    },
                                    "column_types": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": ["string", "integer", "float", "boolean", "date", "datetime"]
                                        }
                                    }
                                }
                            }
                        },
                        "time_series": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["timestamp", "value"],
                                "properties": {
                                    "timestamp": {"type": "string", "format": "date-time"},
                                    "value": {"type": "number"},
                                    "metric": {"type": "string"},
                                    "unit": {"type": "string"}
                                }
                            }
                        },
                        "statistics": {"type": "object"}
                    }
                },
                "graph_data": {
                    "type": "object",
                    "properties": {
                        "entities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "name"],
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": ["Person", "Document", "TechnicalConcept", "System", "Component", "Decision", "Meeting", "Project", "Team", "Role", "Process", "Constraint", "Risk", "Action"]
                                    },
                                    "name": {"type": "string"},
                                    "properties": {"type": "object"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                                }
                            }
                        },
                        "relationships": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["source", "relationship", "target"],
                                "properties": {
                                    "source": {
                                        "type": "object",
                                        "required": ["type", "name"],
                                        "properties": {
                                            "type": {"type": "string"},
                                            "name": {"type": "string"}
                                        }
                                    },
                                    "relationship": {
                                        "type": "string",
                                        "enum": [
                                            "HAS_EXPERTISE", "HAS_ROLE", "MEMBER_OF", "MADE", "ATTENDED",
                                            "PART_OF", "INTERFACES_WITH", "CONSTRAINED_BY", "AFFECTS", 
                                            "VALIDATED_BY", "PRODUCED", "MITIGATED_BY", "RESULTED_IN",
                                            "AUTHORED", "MENTIONS", "REFERENCES", "DISCUSSES", "DEPENDS_ON"
                                        ]
                                    },
                                    "target": {
                                        "type": "object",
                                        "required": ["type", "name"],
                                        "properties": {
                                            "type": {"type": "string"},
                                            "name": {"type": "string"}
                                        }
                                    },
                                    "properties": {"type": "object"},
                                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                                }
                            }
                        },
                        "context": {"type": "object"}
                    }
                }
            }
        },
        "processing_hints": {
            "type": "object",
            "properties": {
                "priority_brain": {
                    "type": "string",
                    "enum": ["vector", "analytical", "graph", "auto"]
                },
                "semantic_weight": {"type": "number", "minimum": 0, "maximum": 1},
                "relationship_importance": {"type": "number", "minimum": 0, "maximum": 1},
                "requires_expert_routing": {"type": "boolean"},
                "content_classification": {
                    "type": "string",
                    "enum": ["technical", "financial", "strategic", "operational", "compliance", "research", "mixed"]
                },
                "update_frequency": {
                    "type": "string",
                    "enum": ["static", "daily", "weekly", "monthly", "real_time"]
                },
                "indexing_priority": {
                    "type": "string",
                    "enum": ["high", "medium", "low"]
                }
            }
        },
        "quality_metrics": {
            "type": "object",
            "properties": {
                "extraction_confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "content_completeness": {"type": "number", "minimum": 0, "maximum": 1},
                "relationship_accuracy": {"type": "number", "minimum": 0, "maximum": 1},
                "text_quality_score": {"type": "number", "minimum": 0, "maximum": 1},
                "metadata_richness": {"type": "number", "minimum": 0, "maximum": 1},
                "processing_errors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "error_type": {"type": "string"},
                            "error_message": {"type": "string"},
                            "severity": {"type": "string", "enum": ["low", "medium", "high"]},
                            "component": {"type": "string", "enum": ["vector_extraction", "analytical_extraction", "graph_extraction", "metadata_extraction"]}
                        }
                    }
                }
            }
        },
        "versioning": {
            "type": "object",
            "properties": {
                "packet_version": {"type": "integer", "minimum": 1},
                "previous_packet_id": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
                "change_summary": {"type": "string"},
                "data_lineage": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source_system": {"type": "string"},
                            "transformation": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    }
}


class NancyKnowledgePacket:
    """
    Represents a validated Nancy Knowledge Packet with helper methods.
    """
    
    def __init__(self, packet_data: Dict[str, Any]):
        """Initialize with validated packet data."""
        self.data = packet_data
        self._validate()
    
    def _validate(self):
        """Validate packet against schema."""
        try:
            jsonschema.validate(self.data, KNOWLEDGE_PACKET_SCHEMA)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Invalid Knowledge Packet: {e.message}")
    
    @classmethod
    def create(cls, 
               mcp_server: str,
               server_version: str,
               original_location: str,
               content_type: str,
               title: str,
               content: Dict[str, Any],
               author: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None,
               processing_hints: Optional[Dict[str, Any]] = None,
               quality_metrics: Optional[Dict[str, Any]] = None) -> 'NancyKnowledgePacket':
        """
        Create a new Knowledge Packet with required fields.
        """
        # Generate packet ID from content
        content_str = json.dumps(content, sort_keys=True)
        packet_id = hashlib.sha256(content_str.encode()).hexdigest()
        
        # Build packet data
        packet_data = {
            "packet_version": "1.0",
            "packet_id": packet_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": {
                "mcp_server": mcp_server,
                "server_version": server_version,
                "original_location": original_location,
                "content_type": content_type
            },
            "metadata": {
                "title": title,
                **(metadata or {})
            },
            "content": content
        }
        
        # Add optional author
        if author:
            packet_data["metadata"]["author"] = author
        
        # Add optional fields
        if processing_hints:
            packet_data["processing_hints"] = processing_hints
        
        if quality_metrics:
            packet_data["quality_metrics"] = quality_metrics
        
        return cls(packet_data)
    
    @property
    def packet_id(self) -> str:
        return self.data["packet_id"]
    
    @property
    def source(self) -> Dict[str, Any]:
        return self.data["source"]
    
    @property
    def metadata(self) -> Dict[str, Any]:
        return self.data["metadata"]
    
    @property
    def content(self) -> Dict[str, Any]:
        return self.data["content"]
    
    @property
    def processing_hints(self) -> Optional[Dict[str, Any]]:
        return self.data.get("processing_hints")
    
    @property
    def quality_metrics(self) -> Optional[Dict[str, Any]]:
        return self.data.get("quality_metrics")
    
    def has_vector_data(self) -> bool:
        """Check if packet contains vector data."""
        return "vector_data" in self.content and bool(self.content["vector_data"])
    
    def has_analytical_data(self) -> bool:
        """Check if packet contains analytical data."""
        return "analytical_data" in self.content and bool(self.content["analytical_data"])
    
    def has_graph_data(self) -> bool:
        """Check if packet contains graph data."""
        return "graph_data" in self.content and bool(self.content["graph_data"])
    
    def get_priority_brain(self) -> str:
        """Get the suggested priority brain for routing."""
        hints = self.processing_hints
        if hints and "priority_brain" in hints:
            return hints["priority_brain"]
        
        # Auto-detect based on content
        if self.has_graph_data() and self.has_analytical_data():
            return "graph"
        elif self.has_analytical_data():
            return "analytical"
        elif self.has_vector_data():
            return "vector"
        else:
            return "auto"
    
    def to_dict(self) -> Dict[str, Any]:
        """Return packet as dictionary."""
        return self.data
    
    def to_json(self) -> str:
        """Return packet as JSON string."""
        return json.dumps(self.data, indent=2)


class KnowledgePacketValidator:
    """
    Validates and processes Nancy Knowledge Packets.
    """
    
    def __init__(self):
        self.schema = KNOWLEDGE_PACKET_SCHEMA
    
    def validate(self, packet_data: Dict[str, Any]) -> bool:
        """
        Validate packet data against schema.
        
        Args:
            packet_data: Dictionary containing packet data
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If packet is invalid
        """
        try:
            jsonschema.validate(packet_data, self.schema)
            return True
        except jsonschema.ValidationError as e:
            raise ValueError(f"Knowledge Packet validation failed: {e.message}")
    
    def validate_packet(self, packet: NancyKnowledgePacket) -> bool:
        """Validate a NancyKnowledgePacket instance."""
        return self.validate(packet.to_dict())
    
    def get_validation_errors(self, packet_data: Dict[str, Any]) -> List[str]:
        """
        Get list of validation errors without raising exception.
        
        Args:
            packet_data: Dictionary containing packet data
            
        Returns:
            List of validation error messages
        """
        errors = []
        validator = jsonschema.Draft7Validator(self.schema)
        
        for error in validator.iter_errors(packet_data):
            errors.append(f"{error.json_path}: {error.message}")
        
        return errors