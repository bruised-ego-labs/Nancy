"""
Nancy Core Configuration Manager
Handles loading, validation, and management of Nancy Core configuration.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class BrainBackend(str, Enum):
    # Vector backends
    CHROMADB = "chromadb"
    WEAVIATE = "weaviate"
    PINECONE = "pinecone"
    QDRANT = "qdrant"
    FAISS = "faiss"
    
    # Analytical backends
    DUCKDB = "duckdb"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    CLICKHOUSE = "clickhouse"
    
    # Graph backends
    NEO4J = "neo4j"
    ARANGODB = "arangodb"
    TIGERGRAPH = "tigergraph"
    NEPTUNE = "neptune"


class OrchestrationMode(str, Enum):
    FOUR_BRAIN = "four_brain"
    SIMPLIFIED = "simplified"
    CUSTOM = "custom"


class RoutingStrategy(str, Enum):
    LANGCHAIN_ROUTER = "langchain_router"
    CUSTOM = "custom"
    RULE_BASED = "rule_based"


class NancyCoreConfig(BaseModel):
    """Core Nancy configuration section."""
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    instance_name: str = Field(..., pattern=r"^[a-zA-Z0-9_-]+$")
    description: Optional[str] = None


class OrchestrationConfig(BaseModel):
    """Orchestration configuration section."""
    mode: OrchestrationMode = OrchestrationMode.FOUR_BRAIN
    multi_step_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    routing_strategy: RoutingStrategy = RoutingStrategy.LANGCHAIN_ROUTER
    max_query_complexity: int = Field(default=5, ge=1, le=10)
    enable_query_caching: bool = True


class ConnectionConfig(BaseModel):
    """Base connection configuration."""
    pass


class ChromaDBConnection(ConnectionConfig):
    """ChromaDB connection configuration."""
    host: str = "localhost"
    port: int = Field(default=8001, ge=1, le=65535)
    ssl: bool = False
    collection_name: str = "nancy_vectors"


class DuckDBConnection(ConnectionConfig):
    """DuckDB connection configuration."""
    database_path: str
    read_only: bool = False
    memory_limit: str = "1GB"


class Neo4jConnection(ConnectionConfig):
    """Neo4j connection configuration."""
    uri: str
    username: str = "neo4j"
    password: str
    database: str = "neo4j"
    max_connection_lifetime_seconds: int = 3600


class GoogleAIConnection(ConnectionConfig):
    """Google AI connection configuration."""
    api_key_env: str = "GEMINI_API_KEY"
    model: str = "gemini-1.5-flash"
    base_url: Optional[str] = None


class VectorBrainConfig(BaseModel):
    """Vector brain configuration."""
    backend: BrainBackend
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = Field(default=512, ge=100, le=2000)
    chunk_overlap: int = Field(default=50, ge=0, le=200)
    connection: Dict[str, Any]
    
    @validator('backend')
    def validate_vector_backend(cls, v):
        valid_backends = [BrainBackend.CHROMADB, BrainBackend.WEAVIATE, BrainBackend.PINECONE, BrainBackend.QDRANT, BrainBackend.FAISS]
        if v not in valid_backends:
            raise ValueError(f"Invalid vector backend: {v}")
        return v


class AnalyticalBrainConfig(BaseModel):
    """Analytical brain configuration."""
    backend: BrainBackend
    connection: Dict[str, Any]
    query_timeout_seconds: int = Field(default=30, ge=1, le=300)
    
    @validator('backend')
    def validate_analytical_backend(cls, v):
        valid_backends = [BrainBackend.DUCKDB, BrainBackend.POSTGRESQL, BrainBackend.SQLITE, BrainBackend.CLICKHOUSE]
        if v not in valid_backends:
            raise ValueError(f"Invalid analytical backend: {v}")
        return v


class GraphBrainConfig(BaseModel):
    """Graph brain configuration."""
    backend: BrainBackend
    schema_mode: str = Field(default="foundational", pattern="^(foundational|custom|flexible)$")
    connection: Dict[str, Any]
    max_relationship_depth: int = Field(default=5, ge=1, le=10)
    
    @validator('backend')
    def validate_graph_backend(cls, v):
        valid_backends = [BrainBackend.NEO4J, BrainBackend.ARANGODB, BrainBackend.TIGERGRAPH, BrainBackend.NEPTUNE]
        if v not in valid_backends:
            raise ValueError(f"Invalid graph backend: {v}")
        return v


class LinguisticBrainConfig(BaseModel):
    """Linguistic brain configuration."""
    primary_llm: str
    fallback_llm: Optional[str] = None
    connection: Dict[str, Any]
    temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=100, le=8192)


class BrainsConfig(BaseModel):
    """All brain configurations."""
    vector: VectorBrainConfig
    analytical: AnalyticalBrainConfig
    graph: GraphBrainConfig
    linguistic: LinguisticBrainConfig


class MCPServerConfig(BaseModel):
    """MCP server configuration."""
    name: str = Field(..., pattern=r"^nancy-[a-zA-Z0-9_-]+$")
    executable: str
    args: list = Field(default_factory=list)
    auto_start: bool = True
    capabilities: list = Field(default_factory=list)
    supported_extensions: Optional[List[str]] = Field(default_factory=list)
    environment: Dict[str, str] = Field(default_factory=dict)
    health_check_interval_seconds: int = Field(default=60, ge=10, le=300)


class MCPServersConfig(BaseModel):
    """MCP servers configuration."""
    enabled_servers: List[MCPServerConfig]
    auto_discovery: bool = False
    server_timeout_seconds: int = Field(default=30, ge=5, le=300)


class SecurityConfig(BaseModel):
    """Security configuration."""
    authentication: Dict[str, Any] = Field(default_factory=dict)
    mcp_security: Dict[str, Any] = Field(default_factory=dict)


class PerformanceConfig(BaseModel):
    """Performance configuration."""
    query_timeout_seconds: int = Field(default=30, ge=5, le=300)
    max_concurrent_queries: int = Field(default=10, ge=1, le=100)
    cache_enabled: bool = True
    cache_ttl_minutes: int = Field(default=60, ge=1, le=1440)
    memory_limit_mb: int = Field(default=2048, ge=512, le=16384)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARN|ERROR|CRITICAL)$")
    structured: bool = True
    include_performance_metrics: bool = True
    log_queries: bool = False
    retention_days: int = Field(default=30, ge=1, le=365)


class NancyConfiguration(BaseModel):
    """Complete Nancy configuration."""
    nancy_core: NancyCoreConfig
    orchestration: OrchestrationConfig
    brains: BrainsConfig
    mcp_servers: MCPServersConfig
    security: Optional[SecurityConfig] = None
    performance: Optional[PerformanceConfig] = None
    logging: Optional[LoggingConfig] = None


class ConfigurationManager:
    """
    Manages Nancy Core configuration loading, validation, and access.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, will search for default locations.
        """
        self.config_path = config_path
        self.config: Optional[NancyConfiguration] = None
        self._environment_overrides = {}
        
    def load_config(self, config_path: Optional[str] = None) -> NancyConfiguration:
        """
        Load and validate configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Validated configuration object
            
        Raises:
            FileNotFoundError: If config file not found
            ValueError: If configuration is invalid
        """
        if config_path:
            self.config_path = config_path
        
        # Find config file
        config_file = self._find_config_file()
        if not config_file:
            raise FileNotFoundError("No Nancy configuration file found")
        
        # Load config data
        config_data = self._load_config_file(config_file)
        
        # Apply environment overrides
        config_data = self._apply_environment_overrides(config_data)
        
        # Validate and create configuration object
        try:
            self.config = NancyConfiguration(**config_data)
            logger.info(f"Loaded Nancy configuration from {config_file}")
            return self.config
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
    
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in default locations."""
        if self.config_path and os.path.exists(self.config_path):
            return self.config_path
        
        # Search in order of preference
        search_paths = [
            "nancy-config.yaml",
            "nancy-config.yml",
            "./config/nancy-config.yaml",
            "./config/nancy-config.yml",
            os.path.expanduser("~/.nancy/config.yaml"),
            "/etc/nancy/config.yaml"
        ]
        
        # Check for environment-specific configs
        env = os.getenv("NANCY_ENV", "development")
        env_configs = [
            f"nancy-config-{env}.yaml",
            f"nancy-config-{env}.yml",
            f"./config/nancy-config-{env}.yaml"
        ]
        
        # Prioritize environment-specific configs
        for path in env_configs + search_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _load_config_file(self, config_file: str) -> Dict[str, Any]:
        """Load configuration data from file."""
        try:
            with open(config_file, 'r') as f:
                if config_file.endswith('.json'):
                    return json.load(f)
                else:
                    return yaml.safe_load(f)
        except Exception as e:
            raise ValueError(f"Failed to load config file {config_file}: {e}")
    
    def _apply_environment_overrides(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        # Handle ${VAR} and ${VAR:-default} substitutions
        def substitute_env_vars(obj):
            if isinstance(obj, dict):
                return {k: substitute_env_vars(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [substitute_env_vars(item) for item in obj]
            elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
                var_expr = obj[2:-1]  # Remove ${ and }
                if ':-' in var_expr:
                    var_name, default_value = var_expr.split(':-', 1)
                    return os.getenv(var_name, default_value)
                else:
                    env_value = os.getenv(var_expr)
                    if env_value is None:
                        raise ValueError(f"Required environment variable {var_expr} not found")
                    return env_value
            else:
                return obj
        
        return substitute_env_vars(config_data)
    
    def get_config(self) -> NancyConfiguration:
        """Get current configuration."""
        if not self.config:
            raise ValueError("Configuration not loaded. Call load_config() first.")
        return self.config
    
    def get_brain_config(self, brain_type: str) -> Union[VectorBrainConfig, AnalyticalBrainConfig, GraphBrainConfig, LinguisticBrainConfig]:
        """Get configuration for specific brain type."""
        config = self.get_config()
        
        if brain_type == "vector":
            return config.brains.vector
        elif brain_type == "analytical":
            return config.brains.analytical
        elif brain_type == "graph":
            return config.brains.graph
        elif brain_type == "linguistic":
            return config.brains.linguistic
        else:
            raise ValueError(f"Unknown brain type: {brain_type}")
    
    def get_mcp_servers(self) -> List[MCPServerConfig]:
        """Get MCP server configurations."""
        return self.get_config().mcp_servers.enabled_servers
    
    def get_orchestration_config(self) -> OrchestrationConfig:
        """Get orchestration configuration."""
        return self.get_config().orchestration
    
    def is_development_mode(self) -> bool:
        """Check if running in development mode."""
        env = os.getenv("NANCY_ENV", "development")
        return env == "development"
    
    def is_production_mode(self) -> bool:
        """Check if running in production mode."""
        env = os.getenv("NANCY_ENV", "development")
        return env == "production"
    
    def create_default_config(self, output_path: str = "nancy-config.yaml"):
        """
        Create a default configuration file for development.
        
        Args:
            output_path: Path where to save the config file
        """
        default_config = {
            "nancy_core": {
                "version": "2.0.0",
                "instance_name": "nancy-dev",
                "description": "Development Nancy Core instance"
            },
            "orchestration": {
                "mode": "four_brain",
                "multi_step_threshold": 0.7,
                "routing_strategy": "langchain_router",
                "enable_query_caching": True
            },
            "brains": {
                "vector": {
                    "backend": "chromadb",
                    "embedding_model": "BAAI/bge-small-en-v1.5",
                    "chunk_size": 512,
                    "chunk_overlap": 50,
                    "connection": {
                        "host": "localhost",
                        "port": 8001,
                        "collection_name": "nancy_dev_vectors"
                    }
                },
                "analytical": {
                    "backend": "duckdb",
                    "connection": {
                        "database_path": "./data/dev_nancy.duckdb",
                        "memory_limit": "1GB"
                    }
                },
                "graph": {
                    "backend": "neo4j",
                    "schema_mode": "foundational",
                    "connection": {
                        "uri": "bolt://localhost:7687",
                        "username": "neo4j",
                        "password": "password",
                        "database": "nancy_dev"
                    }
                },
                "linguistic": {
                    "primary_llm": "gemma_3n_e4b_it",
                    "fallback_llm": "local_gemma",
                    "connection": {
                        "api_key_env": "GEMINI_API_KEY",
                        "model": "gemini-1.5-flash"
                    },
                    "temperature": 0.1,
                    "max_tokens": 2048
                }
            },
            "mcp_servers": {
                "enabled_servers": [],
                "auto_discovery": False,
                "server_timeout_seconds": 30
            },
            "security": {
                "authentication": {"enabled": False},
                "mcp_security": {
                    "sandbox_mode": True,
                    "allowed_file_extensions": [".xlsx", ".csv", ".md", ".py", ".js", ".json", ".pdf", ".txt"],
                    "max_file_size_mb": 50
                }
            },
            "performance": {
                "query_timeout_seconds": 30,
                "max_concurrent_queries": 5,
                "cache_enabled": True,
                "cache_ttl_minutes": 30
            },
            "logging": {
                "level": "DEBUG",
                "structured": True,
                "include_performance_metrics": True,
                "log_queries": True
            }
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, indent=2)
        
        logger.info(f"Created default configuration file: {output_path}")


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_config(config_path: Optional[str] = None) -> NancyConfiguration:
    """Load Nancy configuration."""
    return get_config_manager().load_config(config_path)


def get_config() -> NancyConfiguration:
    """Get current Nancy configuration."""
    return get_config_manager().get_config()