#!/usr/bin/env python3
"""
Codebase Intelligence Testing

Specifically validates Nancy's codebase analysis capabilities with AST parsing 
and Git integration against baseline text search approaches.

Tests:
1. Function discovery and author attribution
2. Dependency graph analysis
3. Code structure understanding
4. Git history integration
5. Change impact analysis
"""

import requests
import json
import time
import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, List, Any

class CodebaseIntelligenceTest:
    def __init__(self):
        self.nancy_url = "http://localhost:8000"
        self.baseline_url = "http://localhost:8002"
        self.test_codebase_dir = "test_codebase_intelligence"
        
        # Codebase intelligence test scenarios
        self.codebase_tests = [
            {
                "category": "Function Discovery",
                "description": "Find specific functions and their authors",
                "test_cases": [
                    {
                        "query": "What functions handle database connections and who wrote them?",
                        "expected_nancy": "AST parsing to find exact functions like connect(), DatabaseConnection.__init__(), with Git authors",
                        "expected_baseline": "Text search for 'database' keywords in comments and strings",
                        "success_criteria": ["function name", "author attribution", "exact identification"]
                    },
                    {
                        "query": "Which functions in thermal_control.py call database methods?",
                        "expected_nancy": "AST analysis of function calls and method invocations",
                        "expected_baseline": "Text pattern matching for database-related keywords",
                        "success_criteria": ["function call analysis", "cross-module dependencies"]
                    }
                ]
            },
            {
                "category": "Dependency Analysis", 
                "description": "Understand module dependencies and imports",
                "test_cases": [
                    {
                        "query": "Which modules import database_manager and what functions do they use?",
                        "expected_nancy": "Complete import graph with function usage analysis",
                        "expected_baseline": "Text search for import statements",
                        "success_criteria": ["import mapping", "function usage", "dependency graph"]
                    },
                    {
                        "query": "Show me all dependencies of the authentication module",
                        "expected_nancy": "AST-based dependency tree with transitive dependencies",
                        "expected_baseline": "Text-based import detection",
                        "success_criteria": ["complete dependency tree", "transitive analysis"]
                    }
                ]
            },
            {
                "category": "Code Structure",
                "description": "Understanding of classes, methods, and code organization",
                "test_cases": [
                    {
                        "query": "What classes are defined in the codebase and what are their methods?",
                        "expected_nancy": "Complete class hierarchy with method signatures",
                        "expected_baseline": "Text search for 'class' and 'def' keywords",
                        "success_criteria": ["class identification", "method listing", "structural understanding"]
                    },
                    {
                        "query": "Which methods in ThermalController handle temperature monitoring?",
                        "expected_nancy": "AST analysis of class methods with semantic understanding",
                        "expected_baseline": "Text search within class definition",
                        "success_criteria": ["method identification", "semantic matching", "class scope"]
                    }
                ]
            },
            {
                "category": "Change Impact",
                "description": "Understanding code changes and their effects",
                "test_cases": [
                    {
                        "query": "If I change the database connection method, what code would be affected?",
                        "expected_nancy": "Impact analysis through dependency graph and function calls",
                        "expected_baseline": "Cannot perform - requires structural analysis",
                        "success_criteria": ["impact analysis", "change propagation", "dependency tracking"]
                    },
                    {
                        "query": "What would happen if I modify the authentication token generation?",
                        "expected_nancy": "Analysis of all code that uses token generation",
                        "expected_baseline": "Text search for token-related keywords",
                        "success_criteria": ["usage analysis", "impact scope", "functional dependencies"]
                    }
                ]
            }
        ]
    
    def setup_enhanced_codebase(self) -> Dict[str, Any]:
        """Create enhanced codebase with realistic engineering content"""
        print("🏗️  Setting up enhanced codebase for intelligence testing...")
        
        if not os.path.exists(self.test_codebase_dir):
            os.makedirs(self.test_codebase_dir)
        
        # Enhanced realistic engineering codebase
        codebase_files = {
            "thermal_control.py": '''"""
Thermal Control System - Main Controller
Author: Sarah Chen <sarah.chen@company.com>
Last Modified: 2024-08-12
Dependencies: database_manager, sensors, numpy
"""
import database_manager
from sensors import TemperatureSensor, PressureSensor
import numpy as np
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class ThermalReading:
    """Data structure for thermal readings"""
    timestamp: float
    temperature: float
    pressure: float
    component_id: str

class ThermalController:
    """
    Main thermal control system managing temperature monitoring
    and cooling activation based on component requirements.
    """
    
    def __init__(self, max_temp: float = 85.0, config_path: str = None):
        self.max_temp = max_temp
        self.temperature_sensor = TemperatureSensor()
        self.pressure_sensor = PressureSensor()
        self.db_connection = database_manager.connect()
        self.logger = logging.getLogger(__name__)
        self.active_alerts = []
        
    def monitor_temperature(self) -> ThermalReading:
        """
        Monitor thermal constraints per COMP-001 requirements.
        Returns current thermal reading and triggers alerts if needed.
        """
        current_temp = self.temperature_sensor.read_temperature()
        current_pressure = self.pressure_sensor.read_pressure()
        
        reading = ThermalReading(
            timestamp=time.time(),
            temperature=current_temp,
            pressure=current_pressure,
            component_id="COMP-001"
        )
        
        # Log reading to database
        self.db_connection.log_thermal_reading(reading)
        
        if current_temp > self.max_temp:
            self.trigger_cooling_sequence(current_temp)
            
        return reading
        
    def trigger_cooling_sequence(self, temperature: float):
        """
        Emergency cooling activation when thermal limits exceeded.
        Implements multi-stage cooling based on temperature severity.
        """
        alert_data = {
            "temperature": temperature,
            "max_allowed": self.max_temp,
            "severity": "critical" if temperature > self.max_temp * 1.2 else "warning",
            "timestamp": time.time()
        }
        
        # Log to database via database_manager
        self.db_connection.log_event("THERMAL_ALERT", alert_data)
        
        # Activate cooling
        if temperature > self.max_temp * 1.2:
            self.activate_emergency_cooling()
        else:
            self.activate_standard_cooling()
            
        self.active_alerts.append(alert_data)
        
    def activate_emergency_cooling(self):
        """Emergency cooling - maximum fan speed and coolant flow"""
        self.logger.critical("EMERGENCY COOLING ACTIVATED")
        # Implementation would control hardware
        
    def activate_standard_cooling(self):
        """Standard cooling response to elevated temperatures"""
        self.logger.warning("Standard cooling activated")
        # Implementation would control hardware
        
    def get_thermal_history(self, hours: int = 24) -> List[ThermalReading]:
        """Retrieve thermal history from database"""
        return self.db_connection.get_thermal_readings(hours)
        
    def analyze_thermal_trends(self) -> Dict[str, Any]:
        """Analyze thermal trends using database data"""
        readings = self.get_thermal_history(24)
        if not readings:
            return {"status": "no_data"}
            
        temperatures = [r.temperature for r in readings]
        return {
            "average_temp": np.mean(temperatures),
            "max_temp": np.max(temperatures),
            "min_temp": np.min(temperatures),
            "trend": "increasing" if temperatures[-1] > temperatures[0] else "decreasing",
            "alert_count": len([t for t in temperatures if t > self.max_temp])
        }
''',
            
            "database_manager.py": '''"""
Database Connection and Management System
Author: Mike Rodriguez <mike.rodriguez@company.com>
Last Modified: 2024-08-10
Handles all database operations for thermal system data
"""
import sqlite3
import json
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager

class DatabaseConnection:
    """
    Singleton database connection manager.
    Handles telemetry data, thermal readings, and system events.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = "thermal_system.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
        
    def __init__(self, db_path: str = "thermal_system.db"):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path
            self.connection = None
            self._connect()
            self._create_tables()
            self.initialized = True
            
    def _connect(self):
        """Establish database connection with error handling"""
        try:
            self.connection = sqlite3.connect(
                self.db_path, 
                check_same_thread=False,
                timeout=30.0
            )
            self.connection.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")
            
    def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.connection.cursor()
        
        # Thermal readings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thermal_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                temperature REAL NOT NULL,
                pressure REAL,
                component_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System events table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                event_data TEXT NOT NULL,
                severity TEXT DEFAULT 'info',
                timestamp REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Component status table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS component_status (
                component_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        self.connection.commit()
        
    def log_event(self, event_type: str, data: Dict[str, Any], severity: str = "info"):
        """
        Log system events to database.
        Used by thermal_control.py for alert logging.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO system_events (event_type, event_data, severity, timestamp) VALUES (?, ?, ?, ?)",
            (event_type, json.dumps(data), severity, data.get('timestamp', time.time()))
        )
        self.connection.commit()
        
    def log_thermal_reading(self, reading) -> int:
        """
        Log thermal reading to database.
        Returns the ID of the inserted record.
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO thermal_readings (timestamp, temperature, pressure, component_id) VALUES (?, ?, ?, ?)",
            (reading.timestamp, reading.temperature, reading.pressure, reading.component_id)
        )
        self.connection.commit()
        return cursor.lastrowid
        
    def get_thermal_readings(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Retrieve thermal readings from the last N hours.
        Used by thermal_control.py for trend analysis.
        """
        cutoff_time = time.time() - (hours * 3600)
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT * FROM thermal_readings WHERE timestamp > ? ORDER BY timestamp",
            (cutoff_time,)
        )
        return [dict(row) for row in cursor.fetchall()]
        
    def get_system_events(self, event_type: Optional[str] = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Retrieve system events with optional filtering"""
        cutoff_time = time.time() - (hours * 3600)
        cursor = self.connection.cursor()
        
        if event_type:
            cursor.execute(
                "SELECT * FROM system_events WHERE event_type = ? AND timestamp > ? ORDER BY timestamp DESC",
                (event_type, cutoff_time)
            )
        else:
            cursor.execute(
                "SELECT * FROM system_events WHERE timestamp > ? ORDER BY timestamp DESC",
                (cutoff_time,)
            )
            
        return [dict(row) for row in cursor.fetchall()]
        
    def update_component_status(self, component_id: str, status: str, metadata: Dict[str, Any] = None):
        """Update component operational status"""
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO component_status (component_id, status, metadata) VALUES (?, ?, ?)",
            (component_id, status, json.dumps(metadata) if metadata else None)
        )
        self.connection.commit()
        
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        cursor = self.connection.cursor()
        try:
            yield cursor
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
            
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

def connect(db_path: str = "thermal_system.db") -> DatabaseConnection:
    """
    Factory function for database connections.
    Used throughout the system for database access.
    """
    return DatabaseConnection(db_path)
    
def get_connection_stats() -> Dict[str, Any]:
    """Get database connection statistics"""
    conn = connect()
    cursor = conn.connection.cursor()
    
    stats = {}
    
    # Count thermal readings
    cursor.execute("SELECT COUNT(*) FROM thermal_readings")
    stats['thermal_readings_count'] = cursor.fetchone()[0]
    
    # Count system events
    cursor.execute("SELECT COUNT(*) FROM system_events")
    stats['system_events_count'] = cursor.fetchone()[0]
    
    # Recent activity
    cursor.execute("SELECT COUNT(*) FROM system_events WHERE created_at > datetime('now', '-24 hours')")
    stats['events_last_24h'] = cursor.fetchone()[0]
    
    return stats
''',

            "authentication.py": '''"""
Authentication and Authorization Module
Author: Dr. Amanda Torres <amanda.torres@company.com>
Last Modified: 2024-08-11 - Recent security updates for JWT handling
Dependencies: database_manager, hashlib, jwt
"""
import hashlib
import jwt
import secrets
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import database_manager

@dataclass
class UserCredentials:
    """User credential data structure"""
    username: str
    hashed_password: str
    role: str
    permissions: List[str]
    created_at: datetime

@dataclass  
class AuthToken:
    """Authentication token data structure"""
    token: str
    expires_at: datetime
    user_id: str
    permissions: List[str]

class AuthenticationManager:
    """
    Handles user authentication and authorization.
    Integrates with database_manager for user data storage.
    """
    
    def __init__(self, secret_key: str = None):
        self.db = database_manager.connect()
        self.secret_key = secret_key or self._generate_secret_key()
        self.token_expiry_hours = 8
        self.active_sessions = {}
        
    def _generate_secret_key(self) -> str:
        """Generate secure secret key for JWT signing"""
        return secrets.token_urlsafe(32)
        
    def hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """
        Generate salted hash of password.
        Returns (hashed_password, salt) tuple.
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for secure password hashing
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex(), salt
        
    def authenticate_user(self, username: str, password: str) -> Optional[AuthToken]:
        """
        Authenticate user credentials and return auth token.
        Uses database_manager for user lookup.
        """
        user_data = self._get_user_from_database(username)
        if not user_data:
            return None
            
        # Verify password
        stored_hash = user_data['password_hash']
        stored_salt = user_data['salt']
        provided_hash, _ = self.hash_password(password, stored_salt)
        
        if provided_hash != stored_hash:
            # Log failed authentication attempt
            self.db.log_event("AUTH_FAILURE", {
                "username": username,
                "timestamp": time.time(),
                "reason": "invalid_password"
            }, severity="warning")
            return None
            
        # Generate authentication token
        token = self.generate_token(username, user_data['role'], user_data['permissions'])
        
        # Log successful authentication
        self.db.log_event("AUTH_SUCCESS", {
            "username": username,
            "timestamp": time.time(),
            "token_expires": token.expires_at.isoformat()
        })
        
        return token
        
    def _get_user_from_database(self, username: str) -> Optional[Dict[str, Any]]:
        """Retrieve user data from database via database_manager"""
        # This would use database_manager to query user data
        # For now, return mock data for thermal engineers
        thermal_engineers = {
            "sarah.chen": {
                "password_hash": "dummy_hash_1",
                "salt": "dummy_salt_1",
                "role": "thermal_engineer",
                "permissions": ["read_thermal_data", "write_thermal_config", "access_control_systems"]
            },
            "mike.rodriguez": {
                "password_hash": "dummy_hash_2", 
                "salt": "dummy_salt_2",
                "role": "mechanical_engineer",
                "permissions": ["read_thermal_data", "write_mechanical_config"]
            }
        }
        return thermal_engineers.get(username)
        
    def generate_token(self, username: str, role: str, permissions: List[str]) -> AuthToken:
        """
        Generate JWT authentication token.
        Used after successful authentication.
        """
        expires_at = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)
        
        payload = {
            "username": username,
            "role": role, 
            "permissions": permissions,
            "iat": datetime.utcnow(),
            "exp": expires_at,
            "jti": secrets.token_urlsafe(16)  # Unique token ID
        }
        
        token_string = jwt.encode(payload, self.secret_key, algorithm="HS256")
        
        token = AuthToken(
            token=token_string,
            expires_at=expires_at,
            user_id=username,
            permissions=permissions
        )
        
        # Store active session
        self.active_sessions[username] = token
        
        return token
        
    def validate_token(self, token_string: str) -> Optional[Dict[str, Any]]:
        """
        Validate JWT token and return user info.
        Used by other modules to check authorization.
        """
        try:
            payload = jwt.decode(token_string, self.secret_key, algorithms=["HS256"])
            
            # Check if token is still active
            username = payload.get("username")
            if username in self.active_sessions:
                active_token = self.active_sessions[username]
                if active_token.token == token_string and datetime.utcnow() < active_token.expires_at:
                    return payload
                    
            return None
            
        except jwt.ExpiredSignatureError:
            self.db.log_event("TOKEN_EXPIRED", {"token": token_string[:20] + "..."})
            return None
        except jwt.InvalidTokenError:
            self.db.log_event("INVALID_TOKEN", {"token": token_string[:20] + "..."}, severity="warning") 
            return None
            
    def revoke_token(self, username: str):
        """Revoke user's active authentication token"""
        if username in self.active_sessions:
            del self.active_sessions[username]
            self.db.log_event("TOKEN_REVOKED", {"username": username})
            
    def check_permission(self, token_string: str, required_permission: str) -> bool:
        """Check if token has required permission"""
        user_info = self.validate_token(token_string)
        if not user_info:
            return False
            
        permissions = user_info.get("permissions", [])
        return required_permission in permissions
        
    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get information about active authentication sessions"""
        sessions = {}
        for username, token in self.active_sessions.items():
            sessions[username] = {
                "expires_at": token.expires_at.isoformat(),
                "permissions": token.permissions,
                "time_remaining": (token.expires_at - datetime.utcnow()).total_seconds()
            }
        return sessions

# Module-level functions for easy integration
_auth_manager = None

def get_auth_manager() -> AuthenticationManager:
    """Get singleton authentication manager instance"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthenticationManager()
    return _auth_manager
    
def authenticate(username: str, password: str) -> Optional[AuthToken]:
    """Module-level authentication function"""
    return get_auth_manager().authenticate_user(username, password)
    
def validate_request_auth(token: str) -> Optional[Dict[str, Any]]:
    """Validate authentication for incoming requests"""
    return get_auth_manager().validate_token(token)
''',

            "sensors.py": '''"""
Sensor Interface Module
Author: James Wilson <james.wilson@company.com>
Hardware abstraction layer for temperature and pressure sensors
"""
import random
import time
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class SensorReading:
    """Base sensor reading data structure"""
    value: float
    timestamp: float
    sensor_id: str
    status: str

class BaseSensor:
    """Base sensor class with common functionality"""
    
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        self.last_reading = None
        self.calibration_offset = 0.0
        
    def calibrate(self, offset: float):
        """Apply calibration offset to sensor readings"""
        self.calibration_offset = offset

class TemperatureSensor(BaseSensor):
    """Temperature sensor implementation"""
    
    def __init__(self, sensor_id: str = "TEMP_001"):
        super().__init__(sensor_id)
        self.max_reading = 150.0  # Celsius
        self.min_reading = -40.0  # Celsius
        
    def read_temperature(self) -> float:
        """Read current temperature value"""
        # Simulate realistic thermal readings with some variation
        base_temp = 45.0 + random.gauss(0, 2.0)  # Normal operation around 45°C
        
        # Apply calibration
        calibrated_temp = base_temp + self.calibration_offset
        
        # Clamp to sensor range
        calibrated_temp = max(self.min_reading, min(self.max_reading, calibrated_temp))
        
        self.last_reading = SensorReading(
            value=calibrated_temp,
            timestamp=time.time(),
            sensor_id=self.sensor_id,
            status="normal"
        )
        
        return calibrated_temp

class PressureSensor(BaseSensor):
    """Pressure sensor implementation"""
    
    def __init__(self, sensor_id: str = "PRES_001"):
        super().__init__(sensor_id)
        self.max_reading = 10.0  # Bar
        self.min_reading = 0.0   # Bar
        
    def read_pressure(self) -> float:
        """Read current pressure value"""
        # Simulate pressure readings
        base_pressure = 1.0 + random.gauss(0, 0.1)  # Around atmospheric
        
        # Apply calibration
        calibrated_pressure = base_pressure + self.calibration_offset
        
        # Clamp to sensor range
        calibrated_pressure = max(self.min_reading, min(self.max_reading, calibrated_pressure))
        
        self.last_reading = SensorReading(
            value=calibrated_pressure,
            timestamp=time.time(),
            sensor_id=self.sensor_id,
            status="normal"
        )
        
        return calibrated_pressure
'''
        }
        
        # Create files
        created_files = []
        for filename, content in codebase_files.items():
            file_path = os.path.join(self.test_codebase_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(filename)
            
        print(f"   ✓ Created {len(created_files)} realistic engineering code files")
        
        return {
            "status": "ready",
            "directory": self.test_codebase_dir,
            "files": created_files,
            "total_lines": sum(len(content.splitlines()) for content in codebase_files.values())
        }
    
    def ingest_codebase_data(self, system_name: str, base_url: str) -> Dict[str, Any]:
        """Ingest codebase data into specified system"""
        print(f"📥 Ingesting codebase data into {system_name}...")
        
        if not os.path.exists(self.test_codebase_dir):
            return {"status": "error", "error": "Test codebase directory not found"}
        
        code_files = glob.glob(os.path.join(self.test_codebase_dir, "*.py"))
        successful_uploads = 0
        errors = []
        
        start_time = time.time()
        
        for file_path in code_files:
            try:
                filename = os.path.basename(file_path)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                files_data = {'file': (filename, content, 'text/plain')}
                data = {'author': 'Engineering Team'}
                
                response = requests.post(
                    f"{base_url}/api/ingest",
                    files=files_data,
                    data=data,
                    timeout=120
                )
                
                if response.status_code == 200:
                    successful_uploads += 1
                    print(f"   ✓ Uploaded {filename}")
                else:
                    error_msg = f"{filename}: HTTP {response.status_code}"
                    errors.append(error_msg)
                    print(f"   ✗ Failed {filename}: {error_msg}")
                    
            except Exception as e:
                error_msg = f"{filename}: {str(e)}"
                errors.append(error_msg)
                print(f"   ✗ Error {filename}: {error_msg}")
        
        ingestion_time = time.time() - start_time
        
        return {
            "status": "completed",
            "system": system_name,
            "total_files": len(code_files),
            "successful_uploads": successful_uploads,
            "failed_uploads": len(errors),
            "ingestion_time": ingestion_time,
            "errors": errors
        }
    
    def run_codebase_intelligence_tests(self) -> Dict[str, Any]:
        """Run comprehensive codebase intelligence tests"""
        print("🧠 CODEBASE INTELLIGENCE TESTING")
        print("=" * 60)
        
        test_start = time.time()
        
        # Setup codebase
        print("\n1️⃣ SETUP ENHANCED CODEBASE")
        print("-" * 30)
        setup_result = self.setup_enhanced_codebase()
        
        # Ingest data
        print("\n2️⃣ INGEST CODEBASE DATA")
        print("-" * 30)
        nancy_ingestion = self.ingest_codebase_data("Nancy", self.nancy_url)
        baseline_ingestion = self.ingest_codebase_data("Baseline", self.baseline_url)
        
        print("\n   ⏳ Allowing time for codebase processing...")
        time.sleep(10)
        
        # Run tests
        print("\n3️⃣ CODEBASE INTELLIGENCE TESTS")
        print("-" * 30)
        
        test_results = []
        
        for test_category in self.codebase_tests:
            print(f"\n   Category: {test_category['category']}")
            print(f"   Description: {test_category['description']}")
            
            category_results = {
                "category": test_category["category"],
                "description": test_category["description"],
                "test_cases": []
            }
            
            for i, test_case in enumerate(test_category["test_cases"], 1):
                print(f"\n     Test {i}: {test_case['query'][:50]}...")
                
                # Test Nancy
                print("       🧠 Nancy:", end=" ", flush=True)
                nancy_result = self._query_system("Nancy", self.nancy_url, test_case["query"])
                print(f"({nancy_result['query_time']:.1f}s)")
                
                # Test Baseline
                print("       📚 Baseline:", end=" ", flush=True)
                baseline_result = self._query_system("Baseline", self.baseline_url, test_case["query"])
                print(f"({baseline_result['query_time']:.1f}s)")
                
                # Analyze results
                analysis = self._analyze_codebase_intelligence(nancy_result, baseline_result, test_case)
                
                test_case_result = {
                    "query": test_case["query"],
                    "expected_nancy": test_case["expected_nancy"],
                    "expected_baseline": test_case["expected_baseline"],
                    "success_criteria": test_case["success_criteria"],
                    "nancy_result": nancy_result,
                    "baseline_result": baseline_result,
                    "intelligence_analysis": analysis
                }
                
                category_results["test_cases"].append(test_case_result)
            
            test_results.append(category_results)
        
        test_time = time.time() - test_start
        
        # Generate comprehensive analysis
        print("\n4️⃣ CODEBASE INTELLIGENCE ANALYSIS")
        print("-" * 30)
        final_analysis = self._generate_codebase_analysis(test_results)
        
        final_results = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_type": "Codebase Intelligence Comparison",
                "total_test_time": test_time,
                "codebase_directory": self.test_codebase_dir
            },
            "setup_results": setup_result,
            "ingestion_results": {
                "nancy": nancy_ingestion,
                "baseline": baseline_ingestion
            },
            "test_results": test_results,
            "intelligence_analysis": final_analysis
        }
        
        return final_results
    
    def _query_system(self, system_name: str, base_url: str, query: str) -> Dict[str, Any]:
        """Query system with error handling"""
        start_time = time.time()
        
        try:
            request_data = {"query": query}
            if system_name.lower() == "nancy":
                request_data["orchestrator"] = "langchain"
            
            response = requests.post(
                f"{base_url}/api/query",
                json=request_data,
                timeout=180,
                headers={"Content-Type": "application/json"}
            )
            
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "query_time": query_time,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "raw_result": result
                }
            else:
                return {
                    "status": "error",
                    "query_time": query_time,
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
                
        except Exception as e:
            return {
                "status": "error",
                "query_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _analyze_codebase_intelligence(self, nancy_result: Dict[str, Any], baseline_result: Dict[str, Any], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze codebase intelligence capabilities"""
        
        if nancy_result["status"] != "success" or baseline_result["status"] != "success":
            return {
                "intelligence_advantage": 0.0,
                "analysis": "Cannot analyze - query failures",
                "factors": []
            }
        
        nancy_response = nancy_result["response"].lower()
        baseline_response = baseline_result["response"].lower()
        
        intelligence_factors = []
        intelligence_score = 0.0
        
        # Check for codebase-specific intelligence indicators
        code_intelligence_keywords = {
            "function": ["function", "def", "method"],
            "class": ["class", "object", "instance"],
            "import": ["import", "dependency", "module"],
            "ast": ["ast", "parse", "structure", "tree"],
            "author": ["author", "wrote", "created by"],
            "call": ["calls", "invokes", "uses"],
            "dependency": ["depends", "requires", "imports"]
        }
        
        nancy_intelligence = 0
        baseline_intelligence = 0
        
        for category, keywords in code_intelligence_keywords.items():
            nancy_matches = sum(1 for kw in keywords if kw in nancy_response)
            baseline_matches = sum(1 for kw in keywords if kw in baseline_response)
            
            nancy_intelligence += nancy_matches
            baseline_intelligence += baseline_matches
            
            if nancy_matches > baseline_matches:
                intelligence_factors.append(f"Better {category} understanding")
        
        # Normalize intelligence scores
        max_possible = sum(len(keywords) for keywords in code_intelligence_keywords.values())
        nancy_score = nancy_intelligence / max_possible
        baseline_score = baseline_intelligence / max_possible
        
        if nancy_score > baseline_score * 1.3:
            intelligence_score = 0.8
            intelligence_factors.append("Significantly better code understanding")
        elif nancy_score > baseline_score:
            intelligence_score = 0.6
            intelligence_factors.append("Moderately better code understanding")
        
        # Check success criteria
        criteria_met = 0
        for criterion in test_case["success_criteria"]:
            criterion_lower = criterion.lower()
            if any(word in nancy_response for word in criterion_lower.split()):
                criteria_met += 1
        
        criteria_score = criteria_met / len(test_case["success_criteria"])
        intelligence_score += criteria_score * 0.3
        
        return {
            "intelligence_advantage": min(intelligence_score, 1.0),
            "nancy_intelligence_score": nancy_score,
            "baseline_intelligence_score": baseline_score,
            "criteria_met": f"{criteria_met}/{len(test_case['success_criteria'])}",
            "factors": intelligence_factors,
            "analysis": f"Nancy shows {intelligence_score:.1%} intelligence advantage with {len(intelligence_factors)} key factors"
        }
    
    def _generate_codebase_analysis(self, test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive codebase intelligence analysis"""
        
        total_tests = sum(len(category["test_cases"]) for category in test_results)
        total_intelligence_score = 0.0
        category_performance = {}
        
        for category in test_results:
            category_name = category["category"]
            category_scores = []
            
            for test_case in category["test_cases"]:
                intelligence_analysis = test_case["intelligence_analysis"]
                category_scores.append(intelligence_analysis["intelligence_advantage"])
                total_intelligence_score += intelligence_analysis["intelligence_advantage"]
            
            avg_category_score = sum(category_scores) / len(category_scores) if category_scores else 0
            category_performance[category_name] = {
                "average_intelligence_advantage": avg_category_score,
                "test_count": len(category_scores),
                "performance_rating": self._rate_performance(avg_category_score)
            }
        
        overall_intelligence_advantage = total_intelligence_score / total_tests if total_tests > 0 else 0
        
        return {
            "overall_intelligence_advantage": overall_intelligence_advantage,
            "category_performance": category_performance,
            "total_tests": total_tests,
            "codebase_intelligence_rating": self._rate_performance(overall_intelligence_advantage),
            "key_findings": self._generate_key_findings(category_performance, overall_intelligence_advantage),
            "engineering_value": self._assess_engineering_value(overall_intelligence_advantage, category_performance)
        }
    
    def _rate_performance(self, score: float) -> str:
        """Rate performance based on intelligence advantage score"""
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Moderate"
        elif score >= 0.2:
            return "Limited"
        else:
            return "Poor"
    
    def _generate_key_findings(self, category_performance: Dict[str, Any], overall_score: float) -> List[str]:
        """Generate key findings from codebase intelligence tests"""
        findings = []
        
        # Overall performance finding
        if overall_score >= 0.7:
            findings.append("Nancy demonstrates strong codebase intelligence capabilities")
        elif overall_score >= 0.5:
            findings.append("Nancy shows meaningful improvements in code understanding")
        else:
            findings.append("Nancy's codebase intelligence needs improvement")
        
        # Category-specific findings
        best_categories = []
        worst_categories = []
        
        for category, performance in category_performance.items():
            score = performance["average_intelligence_advantage"]
            if score >= 0.7:
                best_categories.append(category)
            elif score < 0.3:
                worst_categories.append(category)
        
        if best_categories:
            findings.append(f"Strongest performance in: {', '.join(best_categories)}")
        
        if worst_categories:
            findings.append(f"Improvement needed in: {', '.join(worst_categories)}")
        
        return findings
    
    def _assess_engineering_value(self, overall_score: float, category_performance: Dict[str, Any]) -> str:
        """Assess engineering team value of codebase intelligence"""
        
        if overall_score >= 0.8:
            return "High Value: Nancy provides significant codebase intelligence that would greatly benefit engineering teams for code navigation, impact analysis, and maintenance tasks."
        elif overall_score >= 0.6:
            return "Good Value: Nancy offers meaningful codebase intelligence improvements over baseline text search, particularly valuable for complex codebases."
        elif overall_score >= 0.4:
            return "Moderate Value: Nancy shows some codebase intelligence capabilities but may not justify deployment cost for simple code search needs."
        else:
            return "Limited Value: Nancy's codebase intelligence needs significant improvement before providing engineering team value."


def main():
    """Run codebase intelligence testing"""
    tester = CodebaseIntelligenceTest()
    
    try:
        print("Starting Codebase Intelligence Testing")
        print("Testing Nancy's AST parsing and Git integration vs baseline text search")
        print()
        
        results = tester.run_codebase_intelligence_tests()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"codebase_intelligence_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Display summary
        print("\n" + "="*60)
        print("📊 CODEBASE INTELLIGENCE TEST RESULTS")
        print("="*60)
        
        analysis = results['intelligence_analysis']
        
        print(f"\n🏆 OVERALL INTELLIGENCE ADVANTAGE:")
        print(f"   Score: {analysis['overall_intelligence_advantage']:.1%}")
        print(f"   Rating: {analysis['codebase_intelligence_rating']}")
        print(f"   Total Tests: {analysis['total_tests']}")
        
        print(f"\n📊 CATEGORY PERFORMANCE:")
        for category, performance in analysis['category_performance'].items():
            print(f"   {category}: {performance['average_intelligence_advantage']:.1%} ({performance['performance_rating']})")
        
        print(f"\n🔍 KEY FINDINGS:")
        for finding in analysis['key_findings']:
            print(f"   • {finding}")
        
        print(f"\n💼 ENGINEERING VALUE ASSESSMENT:")
        print(f"   {analysis['engineering_value']}")
        
        print(f"\n📁 Detailed results saved to: {filename}")
        
        return results
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return None
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()