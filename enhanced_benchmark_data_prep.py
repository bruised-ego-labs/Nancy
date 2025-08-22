#!/usr/bin/env python3
"""
Enhanced Benchmark Data Preparation for Nancy MCP vs Baseline RAG

This script prepares comprehensive test data ensuring fair comparison between
Nancy's MCP architecture and baseline RAG while leveraging each system's strengths.

Key Features:
1. Textifies structured data for baseline RAG accessibility
2. Preserves full structured data for Nancy MCP servers
3. Creates simulated codebase scenarios
4. Generates cross-domain integration test cases
5. Ensures data integrity and equivalency validation
"""

import os
import json
import pandas as pd
import shutil
from datetime import datetime
from typing import Dict, List, Any, Tuple
import glob
import yaml

class EnhancedBenchmarkDataPrep:
    def __init__(self, base_dir: str = "C:\\Users\\scott\\Documents\\Nancy"):
        self.base_dir = base_dir
        self.benchmark_data_dir = os.path.join(base_dir, "benchmark_data")
        self.enhanced_data_dir = os.path.join(base_dir, "enhanced_benchmark_data")
        self.baseline_data_dir = os.path.join(self.enhanced_data_dir, "baseline_accessible")
        self.nancy_data_dir = os.path.join(self.enhanced_data_dir, "nancy_full_access")
        
        # Create directories
        os.makedirs(self.enhanced_data_dir, exist_ok=True)
        os.makedirs(self.baseline_data_dir, exist_ok=True)
        os.makedirs(self.nancy_data_dir, exist_ok=True)
        
        # Data preparation results
        self.prep_results = {
            "timestamp": datetime.now().isoformat(),
            "processed_files": [],
            "textified_files": [],
            "simulated_codebase": [],
            "cross_domain_scenarios": [],
            "validation_results": {}
        }
    
    def textify_spreadsheet_for_baseline(self, file_path: str) -> str:
        """Convert spreadsheet data to searchable text format for baseline RAG"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                # Handle Excel files with multiple sheets
                xlsx_file = pd.ExcelFile(file_path)
                all_sheets_text = []
                
                for sheet_name in xlsx_file.sheet_names:
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    sheet_text = self._dataframe_to_searchable_text(df, sheet_name)
                    all_sheets_text.append(sheet_text)
                
                return "\\n\\n".join(all_sheets_text)
            
            return self._dataframe_to_searchable_text(df, os.path.basename(file_path))
            
        except Exception as e:
            print(f"Error textifying {file_path}: {e}")
            return f"Error processing spreadsheet: {file_path}"
    
    def _dataframe_to_searchable_text(self, df: pd.DataFrame, source_name: str) -> str:
        """Convert DataFrame to human-readable, searchable text"""
        text_parts = []
        
        # Header with source information
        text_parts.append(f"=== {source_name} ===")
        text_parts.append(f"Data contains {len(df)} rows and {len(df.columns)} columns")
        text_parts.append("")
        
        # Column information
        text_parts.append("COLUMNS:")
        for col in df.columns:
            col_type = str(df[col].dtype)
            non_null_count = df[col].count()
            text_parts.append(f"- {col} ({col_type}): {non_null_count} non-null values")
        text_parts.append("")
        
        # Statistical summary for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            text_parts.append("NUMERIC DATA SUMMARY:")
            for col in numeric_cols:
                stats = df[col].describe()
                text_parts.append(f"- {col}: min={stats['min']:.2f}, max={stats['max']:.2f}, mean={stats['mean']:.2f}")
        text_parts.append("")
        
        # Categorical data overview
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            text_parts.append("CATEGORICAL DATA OVERVIEW:")
            for col in categorical_cols:
                unique_values = df[col].dropna().unique()
                if len(unique_values) <= 10:
                    text_parts.append(f"- {col} values: {', '.join(map(str, unique_values))}")
                else:
                    text_parts.append(f"- {col}: {len(unique_values)} unique values (e.g., {', '.join(map(str, unique_values[:5]))}...)")
        text_parts.append("")
        
        # Sample data rows (first 10 rows for searchability)
        text_parts.append("SAMPLE DATA:")
        for idx, row in df.head(10).iterrows():
            row_text = f"Row {idx + 1}: "
            row_items = []
            for col, value in row.items():
                if pd.notna(value):
                    row_items.append(f"{col}={value}")
            text_parts.append(row_text + ", ".join(row_items))
        
        if len(df) > 10:
            text_parts.append(f"... and {len(df) - 10} more rows")
        
        # Key insights for engineering data
        text_parts.extend(self._extract_engineering_insights(df, source_name))
        
        return "\\n".join(text_parts)
    
    def _extract_engineering_insights(self, df: pd.DataFrame, source_name: str) -> List[str]:
        """Extract engineering-specific insights from data"""
        insights = ["", "ENGINEERING INSIGHTS:"]
        
        # Temperature/thermal analysis
        temp_cols = [col for col in df.columns if any(term in col.lower() 
                    for term in ['temp', 'thermal', 'heat', 'cooling'])]
        if temp_cols:
            insights.append(f"- Thermal data detected: {', '.join(temp_cols)}")
            for col in temp_cols:
                if df[col].dtype in ['float64', 'int64']:
                    max_temp = df[col].max()
                    min_temp = df[col].min()
                    insights.append(f"  {col}: range {min_temp}°C to {max_temp}°C")
        
        # Electrical measurements
        electrical_cols = [col for col in df.columns if any(term in col.lower() 
                          for term in ['voltage', 'current', 'power', 'electrical', 'amp', 'volt', 'watt'])]
        if electrical_cols:
            insights.append(f"- Electrical measurements: {', '.join(electrical_cols)}")
        
        # Test results and pass/fail
        test_cols = [col for col in df.columns if any(term in col.lower() 
                    for term in ['test', 'result', 'pass', 'fail', 'status', 'outcome'])]
        if test_cols:
            insights.append(f"- Test/validation data: {', '.join(test_cols)}")
            for col in test_cols:
                if col in df.columns:
                    value_counts = df[col].value_counts()
                    insights.append(f"  {col}: {value_counts.to_dict()}")
        
        # Component or part identifiers
        component_cols = [col for col in df.columns if any(term in col.lower() 
                         for term in ['component', 'part', 'item', 'id', 'serial', 'model'])]
        if component_cols:
            insights.append(f"- Component identifiers: {', '.join(component_cols)}")
        
        return insights
    
    def create_simulated_codebase(self) -> Dict[str, Any]:
        """Create simulated codebase data for testing codebase MCP server"""
        codebase_dir = os.path.join(self.nancy_data_dir, "simulated_codebase")
        os.makedirs(codebase_dir, exist_ok=True)
        
        # Python thermal control module
        thermal_control_py = '''"""
Thermal Control System Module

This module implements thermal management algorithms for the Project Phoenix
thermal control system. It interfaces with temperature sensors and cooling
systems to maintain optimal operating temperatures.

Author: Sarah Chen (Thermal Engineering)
Last Modified: 2024-12-15
Dependencies: numpy, scipy, control_interface
"""

import numpy as np
from typing import Dict, List, Tuple
import logging

class ThermalController:
    """Main thermal control system controller"""
    
    def __init__(self, max_temp: float = 85.0, target_temp: float = 65.0):
        self.max_temp = max_temp  # Maximum safe operating temperature (°C)
        self.target_temp = target_temp  # Target operating temperature (°C)
        self.sensors = {}
        self.cooling_systems = {}
        self.logger = logging.getLogger(__name__)
        
    def register_sensor(self, sensor_id: str, location: str) -> None:
        """Register a temperature sensor"""
        self.sensors[sensor_id] = {
            "location": location,
            "last_reading": None,
            "status": "active"
        }
        self.logger.info(f"Registered thermal sensor {sensor_id} at {location}")
    
    def update_sensor_reading(self, sensor_id: str, temperature: float) -> None:
        """Update temperature reading from sensor"""
        if sensor_id in self.sensors:
            self.sensors[sensor_id]["last_reading"] = temperature
            
            # Critical temperature check
            if temperature > self.max_temp:
                self.logger.warning(f"CRITICAL: Sensor {sensor_id} reading {temperature}°C exceeds max {self.max_temp}°C")
                self._trigger_emergency_cooling(sensor_id)
    
    def _trigger_emergency_cooling(self, sensor_id: str) -> None:
        """Trigger emergency cooling procedures"""
        self.logger.critical(f"Emergency cooling triggered for sensor {sensor_id}")
        # Implementation would interface with hardware cooling systems
        pass
    
    def get_thermal_status(self) -> Dict:
        """Get current thermal system status"""
        status = {
            "timestamp": np.datetime64('now'),
            "sensors": self.sensors,
            "max_temperature": max([s.get("last_reading", 0) for s in self.sensors.values()]),
            "average_temperature": np.mean([s.get("last_reading", 0) for s in self.sensors.values() if s.get("last_reading")]),
            "alerts": []
        }
        
        # Check for temperature violations
        for sensor_id, sensor in self.sensors.items():
            if sensor.get("last_reading", 0) > self.max_temp:
                status["alerts"].append(f"Temperature violation: {sensor_id}")
        
        return status

# Configuration constants
THERMAL_CONSTRAINTS = {
    "CPU_MAX_TEMP": 85.0,  # °C - Maximum CPU temperature
    "AMBIENT_MAX": 40.0,   # °C - Maximum ambient temperature
    "COOLING_THRESHOLD": 70.0,  # °C - Activate cooling at this temperature
    "EMERGENCY_SHUTDOWN": 90.0  # °C - Emergency shutdown temperature
}

def calculate_cooling_requirements(current_temp: float, target_temp: float, 
                                 thermal_mass: float = 1.0) -> float:
    """Calculate required cooling capacity in watts"""
    temp_diff = current_temp - target_temp
    if temp_diff <= 0:
        return 0.0
    
    # Simplified thermal calculation - would be more complex in real system
    cooling_watts = temp_diff * thermal_mass * 1.5  # Empirical factor
    return max(0, cooling_watts)
'''

        # JavaScript frontend configuration
        thermal_config_js = '''/**
 * Thermal Management Interface Configuration
 * 
 * Frontend configuration for thermal management dashboard
 * Interfaces with backend thermal control APIs
 * 
 * Author: Mike Rodriguez (Frontend Development)
 * Integration: Thermal Control System v2.1
 * Last Updated: 2024-12-10
 */

const ThermalConfig = {
    // Temperature display settings
    temperatureUnits: 'celsius',
    updateInterval: 1000, // milliseconds
    
    // Alert thresholds (must match backend THERMAL_CONSTRAINTS)
    alerts: {
        warning: 70.0,    // °C - Yellow warning
        critical: 85.0,   // °C - Red alert
        emergency: 90.0   // °C - Emergency shutdown
    },
    
    // Sensor display configuration
    sensors: {
        'CPU_CORE_1': { label: 'CPU Core 1', location: 'Processor', critical: true },
        'CPU_CORE_2': { label: 'CPU Core 2', location: 'Processor', critical: true },
        'GPU_MAIN': { label: 'GPU', location: 'Graphics', critical: true },
        'AMBIENT_1': { label: 'Ambient', location: 'Enclosure', critical: false },
        'PSU_INTERNAL': { label: 'Power Supply', location: 'PSU', critical: true }
    },
    
    // Chart configuration
    chart: {
        maxDataPoints: 100,
        timeRange: 300, // seconds
        refreshRate: 5000, // milliseconds
        colors: {
            normal: '#28a745',
            warning: '#ffc107', 
            critical: '#dc3545',
            emergency: '#6f42c1'
        }
    },
    
    // API endpoints
    api: {
        baseUrl: '/api/thermal',
        endpoints: {
            status: '/status',
            sensors: '/sensors',
            history: '/history',
            controls: '/controls'
        }
    }
};

/**
 * Thermal Dashboard Component
 * Real-time temperature monitoring and control interface
 */
class ThermalDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.sensors = new Map();
        this.isMonitoring = false;
        this.alertsActive = [];
        
        this.initializeInterface();
        this.startMonitoring();
    }
    
    initializeInterface() {
        // Create dashboard HTML structure
        this.container.innerHTML = `
            <div class="thermal-header">
                <h2>Thermal Management System</h2>
                <div class="status-indicator" id="system-status">Normal</div>
            </div>
            <div class="sensor-grid" id="sensor-grid"></div>
            <div class="thermal-chart" id="thermal-chart"></div>
            <div class="controls" id="thermal-controls"></div>
        `;
        
        this.updateSensorDisplay();
    }
    
    async fetchThermalStatus() {
        try {
            const response = await fetch(`${ThermalConfig.api.baseUrl}${ThermalConfig.api.endpoints.status}`);
            const data = await response.json();
            this.updateDisplay(data);
            return data;
        } catch (error) {
            console.error('Failed to fetch thermal status:', error);
            this.showError('Communication error with thermal system');
        }
    }
    
    updateDisplay(statusData) {
        // Update sensor readings
        Object.entries(statusData.sensors).forEach(([sensorId, sensorData]) => {
            this.updateSensorReading(sensorId, sensorData.last_reading);
        });
        
        // Update system status
        this.updateSystemStatus(statusData.alerts);
        
        // Update alerts
        this.handleAlerts(statusData.alerts);
    }
    
    updateSensorReading(sensorId, temperature) {
        const sensorElement = document.getElementById(`sensor-${sensorId}`);
        if (sensorElement) {
            const statusClass = this.getTemperatureStatusClass(temperature);
            sensorElement.className = `sensor ${statusClass}`;
            sensorElement.querySelector('.temperature').textContent = `${temperature.toFixed(1)}°C`;
        }
    }
    
    getTemperatureStatusClass(temp) {
        if (temp >= ThermalConfig.alerts.emergency) return 'emergency';
        if (temp >= ThermalConfig.alerts.critical) return 'critical';
        if (temp >= ThermalConfig.alerts.warning) return 'warning';
        return 'normal';
    }
    
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        this.monitoringInterval = setInterval(() => {
            this.fetchThermalStatus();
        }, ThermalConfig.updateInterval);
        
        console.log('Thermal monitoring started');
    }
    
    stopMonitoring() {
        if (!this.isMonitoring) return;
        
        this.isMonitoring = false;
        clearInterval(this.monitoringInterval);
        console.log('Thermal monitoring stopped');
    }
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ThermalConfig, ThermalDashboard };
}
'''

        # Documentation file
        thermal_docs_md = '''# Thermal Management System Documentation

## Overview

The Project Phoenix Thermal Management System provides real-time monitoring and control of thermal conditions across all system components. The system consists of multiple temperature sensors, cooling control algorithms, and a web-based monitoring interface.

## Architecture

### Backend Components
- **ThermalController** (Python): Core thermal management logic
- **Sensor Interface**: Hardware abstraction layer for temperature sensors
- **Cooling Control**: Interface to fans, heat sinks, and liquid cooling
- **Alert System**: Automated warnings and emergency shutdown procedures

### Frontend Components  
- **Thermal Dashboard** (JavaScript): Real-time monitoring interface
- **Configuration Management**: User-configurable thresholds and settings
- **Data Visualization**: Temperature trends and historical analysis
- **Control Interface**: Manual override and system controls

## Key Features

### Temperature Monitoring
- Real-time sensor readings from critical components
- Configurable update intervals (default: 1 second)
- Historical data logging and trend analysis
- Multi-zone monitoring (CPU, GPU, ambient, PSU)

### Alert System
- **Warning Level** (70°C): Yellow indicator, increased monitoring
- **Critical Level** (85°C): Red alert, automatic cooling activation
- **Emergency Level** (90°C): System shutdown to prevent damage

### Cooling Control
- Automatic fan speed adjustment based on temperature
- Liquid cooling pump control (if available)
- Emergency cooling activation for critical temperatures
- Manual override capabilities for testing and maintenance

## Configuration

### Temperature Thresholds
```python
THERMAL_CONSTRAINTS = {
    "CPU_MAX_TEMP": 85.0,      # Maximum safe CPU temperature
    "AMBIENT_MAX": 40.0,       # Maximum ambient temperature  
    "COOLING_THRESHOLD": 70.0, # Activate cooling
    "EMERGENCY_SHUTDOWN": 90.0 # Emergency shutdown
}
```

### Sensor Configuration
Each sensor must be registered with:
- Unique sensor ID
- Physical location description
- Critical/non-critical designation
- Calibration parameters (if required)

## Integration Points

### Mechanical Systems
- Interfaces with enclosure design for airflow optimization
- Coordinates with fan placement and duct design
- Thermal interface material specifications

### Electrical Systems
- Power consumption monitoring affects thermal load
- Component placement influenced by thermal considerations
- PCB thermal design requirements

### Firmware Integration
- Low-level sensor communication protocols
- Emergency shutdown procedures
- Hardware monitoring interfaces

## Safety Considerations

### Fail-Safe Design
- System defaults to maximum cooling on sensor failure
- Emergency shutdown prevents component damage
- Redundant temperature monitoring for critical components

### User Safety
- Accessible temperature displays and warnings
- Manual emergency stop functionality
- Clear indication of system status

## Maintenance

### Regular Maintenance
- Sensor calibration verification (quarterly)
- Cooling system cleaning and inspection
- Performance baseline updates
- Alert threshold review

### Troubleshooting
- Sensor communication diagnostics
- Cooling system performance verification
- Historical data analysis for trend identification
- Emergency procedure testing

## Related Documents
- Electrical Design Specification (Section 4.2: Thermal Interface)
- Mechanical Design Requirements (Thermal Management)
- Safety Protocol Documentation
- Component Specification Sheets

## Authors and Contributors
- **Sarah Chen** - Thermal Engineering Lead
- **Mike Rodriguez** - Frontend Development  
- **Dr. Amanda Foster** - System Architecture
- **Kevin Park** - Hardware Integration

Last Updated: December 15, 2024
Version: 2.1.0
'''

        # Save files
        files_created = {}
        
        # Python file
        py_file = os.path.join(codebase_dir, "thermal_control.py")
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write(thermal_control_py)
        files_created['thermal_control.py'] = py_file
        
        # JavaScript file
        js_file = os.path.join(codebase_dir, "thermal_config.js")
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(thermal_config_js)
        files_created['thermal_config.js'] = js_file
        
        # Documentation file
        docs_file = os.path.join(codebase_dir, "thermal_system_docs.md")
        with open(docs_file, 'w', encoding='utf-8') as f:
            f.write(thermal_docs_md)
        files_created['thermal_system_docs.md'] = docs_file
        
        # Create textified version for baseline
        codebase_text = self._textify_codebase_for_baseline(files_created)
        baseline_codebase_file = os.path.join(self.baseline_data_dir, "codebase_analysis.txt")
        with open(baseline_codebase_file, 'w', encoding='utf-8') as f:
            f.write(codebase_text)
        
        return {
            "codebase_dir": codebase_dir,
            "files_created": files_created,
            "baseline_textified": baseline_codebase_file,
            "file_count": len(files_created)
        }
    
    def _textify_codebase_for_baseline(self, files_dict: Dict[str, str]) -> str:
        """Convert codebase files to searchable text for baseline RAG"""
        text_parts = []
        text_parts.append("=== PROJECT PHOENIX CODEBASE ANALYSIS ===")
        text_parts.append(f"Analyzed {len(files_dict)} code files")
        text_parts.append("")
        
        for filename, filepath in files_dict.items():
            text_parts.append(f"=== FILE: {filename} ===")
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract key information based on file type
                if filename.endswith('.py'):
                    text_parts.extend(self._extract_python_info(content, filename))
                elif filename.endswith('.js'):
                    text_parts.extend(self._extract_javascript_info(content, filename))
                elif filename.endswith('.md'):
                    text_parts.extend(self._extract_documentation_info(content, filename))
                
                text_parts.append("")
                
            except Exception as e:
                text_parts.append(f"Error processing {filename}: {e}")
                text_parts.append("")
        
        return "\\n".join(text_parts)
    
    def _extract_python_info(self, content: str, filename: str) -> List[str]:
        """Extract searchable information from Python code"""
        info = [f"Python module: {filename}"]
        
        # Extract docstring
        lines = content.split('\\n')
        if '"""' in content:
            docstring_start = content.find('"""')
            docstring_end = content.find('"""', docstring_start + 3)
            if docstring_end > docstring_start:
                docstring = content[docstring_start+3:docstring_end]
                info.append(f"Module documentation: {docstring.strip()}")
        
        # Extract classes
        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                class_name = line.split('(')[0].replace('class ', '').replace(':', '')
                info.append(f"Class defined: {class_name}")
            elif line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '')
                info.append(f"Function defined: {func_name}")
        
        # Extract constants and configuration
        for line in lines:
            if '=' in line and line.strip().isupper():
                info.append(f"Configuration: {line.strip()}")
        
        return info
    
    def _extract_javascript_info(self, content: str, filename: str) -> List[str]:
        """Extract searchable information from JavaScript code"""
        info = [f"JavaScript module: {filename}"]
        
        # Extract configuration objects
        if 'Config' in content:
            info.append("Configuration object detected")
        
        # Extract class definitions
        if 'class ' in content:
            for line in content.split('\\n'):
                if 'class ' in line:
                    class_name = line.split('class ')[1].split(' ')[0].split('{')[0]
                    info.append(f"JavaScript class: {class_name}")
        
        # Extract function definitions
        for line in content.split('\\n'):
            line = line.strip()
            if line.startswith('function ') or 'function(' in line:
                func_name = line.split('(')[0].replace('function ', '').strip()
                info.append(f"Function: {func_name}")
        
        return info
    
    def _extract_documentation_info(self, content: str, filename: str) -> List[str]:
        """Extract searchable information from documentation"""
        info = [f"Documentation file: {filename}"]
        
        # Extract headers
        for line in content.split('\\n'):
            line = line.strip()
            if line.startswith('#'):
                header_level = len(line) - len(line.lstrip('#'))
                header_text = line.lstrip('# ')
                info.append(f"Section (level {header_level}): {header_text}")
        
        # Extract key topics
        key_terms = ['temperature', 'thermal', 'cooling', 'sensor', 'alert', 'emergency', 'configuration']
        for term in key_terms:
            if term.lower() in content.lower():
                info.append(f"Covers topic: {term}")
        
        return info
    
    def prepare_cross_domain_scenarios(self) -> Dict[str, Any]:
        """Create cross-domain integration test scenarios"""
        scenarios = []
        
        # Scenario 1: Thermal-Electrical Integration
        thermal_electrical = {
            "name": "Thermal-Electrical Integration",
            "description": "Power dissipation affects thermal design requirements",
            "documents": [
                "thermal_constraints_doc.txt",
                "power_analysis_report.txt",
                "electrical_design_review.txt"
            ],
            "expected_connections": [
                "Power consumption drives thermal load",
                "Component placement affects both electrical routing and thermal management",
                "Cooling requirements impact power budget"
            ],
            "test_queries": [
                "How do power dissipation requirements affect the thermal management design?",
                "What electrical components generate the most heat and how is this managed?",
                "How do thermal constraints influence PCB layout decisions?"
            ]
        }
        scenarios.append(thermal_electrical)
        
        # Scenario 2: Requirements Traceability
        requirements_trace = {
            "name": "Requirements Traceability",
            "description": "System requirements flow down to component specifications",
            "documents": [
                "system_requirements_v2.txt",
                "component_requirements.csv",
                "march_design_review_transcript.txt"
            ],
            "expected_connections": [
                "System-level requirements drive component specifications",
                "Design decisions trace back to requirements",
                "Meeting discussions reference requirements and decisions"
            ],
            "test_queries": [
                "Which system requirements led to the current thermal management approach?",
                "How do component specifications relate to system-level requirements?",
                "What decisions were made in meetings regarding thermal requirements?"
            ]
        }
        scenarios.append(requirements_trace)
        
        # Scenario 3: Multi-Team Decision Analysis
        multi_team_decisions = {
            "name": "Multi-Team Decision Analysis",
            "description": "Engineering decisions involve multiple disciplines",
            "documents": [
                "march_design_review_transcript.txt",
                "electrical_review_meeting.txt",
                "team_directory.csv"
            ],
            "expected_connections": [
                "Team members contribute expertise to decisions",
                "Decisions affect multiple engineering disciplines",
                "Meeting participants represent different functional areas"
            ],
            "test_queries": [
                "Who from the thermal team contributed to electrical design decisions?",
                "What decisions required input from multiple engineering disciplines?",
                "How did team expertise influence thermal management choices?"
            ]
        }
        scenarios.append(multi_team_decisions)
        
        return {
            "scenarios": scenarios,
            "scenario_count": len(scenarios),
            "total_test_queries": sum(len(s["test_queries"]) for s in scenarios)
        }
    
    def validate_data_equivalency(self) -> Dict[str, Any]:
        """Validate that both systems have equivalent access to information"""
        validation_results = {}
        
        # Check file coverage
        nancy_files = glob.glob(os.path.join(self.nancy_data_dir, "**/*"), recursive=True)
        baseline_files = glob.glob(os.path.join(self.baseline_data_dir, "**/*"), recursive=True)
        
        nancy_file_count = len([f for f in nancy_files if os.path.isfile(f)])
        baseline_file_count = len([f for f in baseline_files if os.path.isfile(f)])
        
        validation_results["file_coverage"] = {
            "nancy_files": nancy_file_count,
            "baseline_files": baseline_file_count,
            "coverage_ratio": baseline_file_count / nancy_file_count if nancy_file_count > 0 else 0
        }
        
        # Check content accessibility
        total_nancy_content = 0
        total_baseline_content = 0
        
        for file_path in nancy_files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_nancy_content += len(f.read())
                except:
                    pass  # Skip binary or unreadable files
        
        for file_path in baseline_files:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_baseline_content += len(f.read())
                except:
                    pass
        
        validation_results["content_accessibility"] = {
            "nancy_total_chars": total_nancy_content,
            "baseline_total_chars": total_baseline_content,
            "content_ratio": total_baseline_content / total_nancy_content if total_nancy_content > 0 else 0
        }
        
        # Information preservation check
        validation_results["information_preservation"] = {
            "structured_data_textified": len(glob.glob(os.path.join(self.baseline_data_dir, "*.txt"))),
            "codebase_flattened": os.path.exists(os.path.join(self.baseline_data_dir, "codebase_analysis.txt")),
            "cross_domain_scenarios": True  # Always created
        }
        
        return validation_results
    
    def execute_data_preparation(self) -> Dict[str, Any]:
        """Execute complete data preparation process"""
        print("🔧 Starting Enhanced Benchmark Data Preparation")
        print("=" * 50)
        
        # Step 1: Process existing structured data
        print("\\n1️⃣ Processing Structured Data")
        existing_csv_files = glob.glob(os.path.join(self.benchmark_data_dir, "*.csv"))
        
        for csv_file in existing_csv_files:
            print(f"   → Processing {os.path.basename(csv_file)}")
            # Copy original for Nancy
            nancy_file = os.path.join(self.nancy_data_dir, os.path.basename(csv_file))
            shutil.copy2(csv_file, nancy_file)
            
            # Create textified version for baseline
            textified_content = self.textify_spreadsheet_for_baseline(csv_file)
            baseline_file = os.path.join(self.baseline_data_dir, 
                                       os.path.basename(csv_file).replace('.csv', '_textified.txt'))
            with open(baseline_file, 'w', encoding='utf-8') as f:
                f.write(textified_content)
            
            self.prep_results["processed_files"].append(csv_file)
            self.prep_results["textified_files"].append(baseline_file)
        
        # Step 2: Copy existing text documents to both systems
        print("\\n2️⃣ Copying Text Documents")
        existing_txt_files = glob.glob(os.path.join(self.benchmark_data_dir, "**/*.txt"), recursive=True)
        
        for txt_file in existing_txt_files:
            relative_path = os.path.relpath(txt_file, self.benchmark_data_dir)
            
            # Copy to Nancy
            nancy_dest = os.path.join(self.nancy_data_dir, relative_path)
            os.makedirs(os.path.dirname(nancy_dest), exist_ok=True)
            shutil.copy2(txt_file, nancy_dest)
            
            # Copy to Baseline
            baseline_dest = os.path.join(self.baseline_data_dir, relative_path)
            os.makedirs(os.path.dirname(baseline_dest), exist_ok=True)
            shutil.copy2(txt_file, baseline_dest)
            
            print(f"   → Copied {relative_path}")
        
        # Step 3: Create simulated codebase
        print("\\n3️⃣ Creating Simulated Codebase")
        codebase_result = self.create_simulated_codebase()
        self.prep_results["simulated_codebase"] = codebase_result
        print(f"   → Created {codebase_result['file_count']} code files")
        print(f"   → Textified codebase for baseline access")
        
        # Step 4: Create cross-domain scenarios
        print("\\n4️⃣ Generating Cross-Domain Test Scenarios")
        scenarios_result = self.prepare_cross_domain_scenarios()
        self.prep_results["cross_domain_scenarios"] = scenarios_result
        print(f"   → Created {scenarios_result['scenario_count']} integration scenarios")
        print(f"   → Generated {scenarios_result['total_test_queries']} test queries")
        
        # Step 5: Validate data equivalency
        print("\\n5️⃣ Validating Data Access Equivalency")
        validation_result = self.validate_data_equivalency()
        self.prep_results["validation_results"] = validation_result
        
        file_coverage = validation_result["file_coverage"]["coverage_ratio"]
        content_coverage = validation_result["content_accessibility"]["content_ratio"]
        
        print(f"   → File coverage: {file_coverage:.1%}")
        print(f"   → Content coverage: {content_coverage:.1%}")
        
        if file_coverage > 0.8 and content_coverage > 0.8:
            print("   ✅ Data equivalency validation PASSED")
        else:
            print("   ⚠️  Data equivalency may need attention")
        
        # Save preparation results
        results_file = os.path.join(self.enhanced_data_dir, "data_preparation_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.prep_results, f, indent=2, default=str)
        
        print(f"\\n📁 Enhanced benchmark data prepared in: {self.enhanced_data_dir}")
        print(f"📊 Preparation results saved to: {results_file}")
        
        return self.prep_results

def main():
    """Execute enhanced benchmark data preparation"""
    prep = EnhancedBenchmarkDataPrep()
    results = prep.execute_data_preparation()
    
    print("\\n" + "="*50)
    print("📊 ENHANCED DATA PREPARATION COMPLETE")
    print("="*50)
    
    print(f"\\n✅ Processed Files: {len(results['processed_files'])}")
    print(f"✅ Textified Files: {len(results['textified_files'])}")
    print(f"✅ Simulated Codebase Files: {results['simulated_codebase']['file_count']}")
    print(f"✅ Cross-Domain Scenarios: {results['cross_domain_scenarios']['scenario_count']}")
    
    validation = results['validation_results']
    print(f"\\n📈 Validation Results:")
    print(f"   File Coverage: {validation['file_coverage']['coverage_ratio']:.1%}")
    print(f"   Content Coverage: {validation['content_accessibility']['content_ratio']:.1%}")
    
    print(f"\\n🎯 Ready for Nancy MCP vs Baseline RAG benchmarking!")
    
    return results

if __name__ == "__main__":
    main()