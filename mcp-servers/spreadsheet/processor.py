"""
Spreadsheet Processing Logic for Nancy MCP Server
Extracted from nancy-services/core/ingestion.py to provide standalone spreadsheet capabilities.
"""

import pandas as pd
import io
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime


class SpreadsheetProcessor:
    """
    Comprehensive spreadsheet processor that handles Excel and CSV files.
    Extracts data for Nancy's Four-Brain architecture via Knowledge Packets.
    """
    
    def __init__(self):
        self.supported_extensions = ['.xlsx', '.xls', '.csv']
    
    def process_spreadsheet(self, filename: str, content: bytes, author: str = "Unknown") -> Dict[str, Any]:
        """
        Process spreadsheet file and generate structured data for Knowledge Packet creation.
        
        Args:
            filename: Name of the spreadsheet file
            content: Binary content of the file
            author: Author attribution for the file
            
        Returns:
            Dictionary containing processed data ready for Knowledge Packet generation
        """
        try:
            file_type = self._get_file_type(filename)
            if file_type not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Parse the spreadsheet
            sheets_data = self._parse_spreadsheet(filename, content, file_type)
            
            if not sheets_data:
                raise ValueError(f"No valid sheets found in {filename}")
            
            # Process each sheet through comprehensive analysis
            processed_sheets = []
            vector_chunks = []
            analytical_tables = []
            graph_entities = []
            graph_relationships = []
            
            for sheet_name, df in sheets_data.items():
                if df.empty:
                    continue
                
                print(f"Processing sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns")
                
                # Generate vector content (summary for semantic search)
                summary_text = self._generate_spreadsheet_summary(filename, sheet_name, df)
                if summary_text:
                    chunk_id = f"{sheet_name}_summary"
                    vector_chunks.append({
                        "chunk_id": chunk_id,
                        "text": summary_text,
                        "chunk_metadata": {
                            "sheet_name": sheet_name,
                            "source_file": filename,
                            "chunk_type": "spreadsheet_summary",
                            "row_count": len(df),
                            "column_count": len(df.columns)
                        }
                    })
                
                # Generate analytical data (structured table data)
                table_data = self._extract_table_data(sheet_name, df)
                if table_data:
                    analytical_tables.append(table_data)
                
                # Generate graph data (entities and relationships)
                sheet_entities, sheet_relationships = self._extract_graph_data(filename, sheet_name, df)
                graph_entities.extend(sheet_entities)
                graph_relationships.extend(sheet_relationships)
                
                processed_sheets.append(sheet_name)
            
            # Calculate quality metrics
            total_rows = sum(len(df) for df in sheets_data.values())
            total_cols = max(len(df.columns) for df in sheets_data.values() if not df.empty)
            
            quality_metrics = {
                "extraction_confidence": 0.95,  # High confidence for structured data
                "content_completeness": 1.0 if processed_sheets else 0.0,
                "relationship_accuracy": 0.9,
                "text_quality_score": 0.85,
                "metadata_richness": 0.8
            }
            
            # Prepare result for Knowledge Packet generation
            result = {
                "filename": filename,
                "file_type": file_type,
                "author": author,
                "sheets_processed": processed_sheets,
                "total_rows": total_rows,
                "total_columns": total_cols,
                "content": {
                    "vector_data": {
                        "chunks": vector_chunks,
                        "embedding_model": "BAAI/bge-small-en-v1.5",
                        "chunk_strategy": "spreadsheet_summary"
                    },
                    "analytical_data": {
                        "table_data": analytical_tables,
                        "structured_fields": {
                            "sheet_count": len(processed_sheets),
                            "total_rows": total_rows,
                            "total_columns": total_cols,
                            "sheet_names": processed_sheets
                        }
                    },
                    "graph_data": {
                        "entities": graph_entities,
                        "relationships": graph_relationships
                    }
                },
                "processing_hints": {
                    "priority_brain": "analytical",
                    "semantic_weight": 0.7,
                    "relationship_importance": 0.8,
                    "content_classification": "technical",
                    "indexing_priority": "high"
                },
                "quality_metrics": quality_metrics
            }
            
            print(f"Successfully processed spreadsheet {filename}: {len(processed_sheets)} sheets")
            return result
            
        except Exception as e:
            print(f"Error processing spreadsheet {filename}: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error information
            return {
                "filename": filename,
                "error": str(e),
                "status": "failed",
                "quality_metrics": {
                    "extraction_confidence": 0.0,
                    "content_completeness": 0.0,
                    "processing_errors": [{
                        "error_type": "processing_failure",
                        "error_message": str(e),
                        "severity": "high",
                        "component": "spreadsheet_processor"
                    }]
                }
            }
    
    def _get_file_type(self, filename: str) -> str:
        """Extract file extension from filename."""
        return '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _parse_spreadsheet(self, filename: str, content: bytes, file_type: str) -> Dict[str, pd.DataFrame]:
        """Parse spreadsheet content into DataFrames by sheet."""
        sheets_data = {}
        
        if file_type == '.csv':
            try:
                # Try UTF-8 first, then fallback to other encodings
                try:
                    df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
                except UnicodeDecodeError:
                    df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
                
                sheets_data = {"Sheet1": df}
                print(f"Successfully parsed CSV file {filename} with {len(df)} rows and {len(df.columns)} columns")
            except Exception as csv_error:
                print(f"Error parsing CSV file {filename}: {csv_error}")
                raise csv_error
        else:
            # For Excel files, read all sheets with enhanced error handling
            try:
                excel_file = pd.ExcelFile(io.BytesIO(content), engine='openpyxl')
                print(f"Excel file {filename} contains sheets: {excel_file.sheet_names}")
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, engine='openpyxl')
                        if not df.empty:
                            sheets_data[sheet_name] = df
                            print(f"Successfully parsed sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns")
                        else:
                            print(f"Sheet '{sheet_name}' is empty, skipping")
                    except Exception as sheet_error:
                        print(f"Error reading sheet '{sheet_name}': {sheet_error}")
                        continue
            except Exception as excel_error:
                print(f"Error parsing Excel file {filename}: {excel_error}")
                # Try fallback with xlrd for older Excel files
                if file_type == '.xls':
                    try:
                        excel_file = pd.ExcelFile(io.BytesIO(content), engine='xlrd')
                        for sheet_name in excel_file.sheet_names:
                            try:
                                df = pd.read_excel(io.BytesIO(content), sheet_name=sheet_name, engine='xlrd')
                                if not df.empty:
                                    sheets_data[sheet_name] = df
                                    print(f"Successfully parsed sheet '{sheet_name}' with xlrd engine")
                            except Exception as xlrd_error:
                                print(f"xlrd fallback failed for sheet '{sheet_name}': {xlrd_error}")
                                continue
                    except Exception as xlrd_error:
                        print(f"xlrd fallback failed completely: {xlrd_error}")
                        raise excel_error
                else:
                    raise excel_error
        
        return sheets_data
    
    def _generate_spreadsheet_summary(self, filename: str, sheet_name: str, df: pd.DataFrame) -> Optional[str]:
        """
        Generate a comprehensive, searchable text summary of the spreadsheet for vector search.
        Enhanced with domain-specific terminology and engineering context.
        """
        try:
            if df.empty:
                return None
            
            # Basic statistics
            num_rows = len(df)
            num_cols = len(df.columns)
            
            # Enhanced column analysis
            column_info = []
            numeric_cols = []
            categorical_cols = []
            identifier_cols = []
            domain_keywords = set()
            
            # Engineering domain keyword detection
            engineering_domains = {
                'thermal': ['temperature', 'thermal', 'heat', 'cooling', 'temp'],
                'mechanical': ['stress', 'strain', 'force', 'pressure', 'material', 'strength'],
                'electrical': ['voltage', 'current', 'power', 'resistance', 'frequency', 'circuit'],
                'quality': ['pass', 'fail', 'test', 'result', 'status', 'compliance'],
                'manufacturing': ['assembly', 'production', 'yield', 'defect', 'process'],
                'design': ['specification', 'requirement', 'target', 'limit', 'tolerance']
            }
            
            for col_name in df.columns:
                col_data = df[col_name].dropna()
                if col_data.empty:
                    continue
                
                # Analyze column characteristics
                col_characteristics = self._analyze_column_characteristics(col_name, col_data)
                
                # Detect domain keywords in column names
                col_name_lower = col_name.lower()
                for domain, keywords in engineering_domains.items():
                    if any(keyword in col_name_lower for keyword in keywords):
                        domain_keywords.add(domain)
                
                if col_characteristics['data_type'] == 'numeric':
                    numeric_cols.append(col_name)
                    try:
                        stats = f"{col_name}: numeric data with {col_characteristics['row_count']} values, range {col_characteristics['min_value']:.2f} to {col_characteristics['max_value']:.2f}, average {col_characteristics['mean_value']:.2f}"
                        
                        # Add engineering context if detected
                        if 'temperature' in col_name_lower or 'temp' in col_name_lower:
                            stats += " (thermal measurement)"
                        elif any(word in col_name_lower for word in ['stress', 'force', 'pressure']):
                            stats += " (mechanical property)"
                        elif any(word in col_name_lower for word in ['voltage', 'current', 'power']):
                            stats += " (electrical measurement)"
                        elif 'cost' in col_name_lower or 'price' in col_name_lower:
                            stats += " (cost analysis)"
                        
                        column_info.append(stats)
                    except:
                        column_info.append(f"{col_name}: numeric column with {col_characteristics['row_count']} values")
                
                elif col_characteristics['data_type'] == 'categorical':
                    categorical_cols.append(col_name)
                    unique_count = col_characteristics['unique_count']
                    
                    if unique_count <= 10:
                        sample_values = ", ".join(str(v) for v in col_characteristics.get('sample_values', [])[:5])
                        column_info.append(f"{col_name}: categorical data with values [{sample_values}{'...' if unique_count > 5 else ''}]")
                    else:
                        column_info.append(f"{col_name}: categorical data with {unique_count} distinct values")
                    
                    # Add context for engineering categories
                    if any(word in col_name_lower for word in ['status', 'result', 'pass', 'fail']):
                        column_info[-1] += " (test/quality status)"
                    elif any(word in col_name_lower for word in ['material', 'component', 'part']):
                        column_info[-1] += " (component/material type)"
                
                if col_characteristics.get('is_identifier'):
                    identifier_cols.append(col_name)
            
            # Generate comprehensive, searchable summary
            summary_parts = [
                f"Engineering Data Spreadsheet: {filename}",
                f"Sheet: {sheet_name} containing {num_rows} rows and {num_cols} columns of data",
                f"Data structure: {len(numeric_cols)} numeric measurements, {len(categorical_cols)} categorical classifications"
            ]
            
            # Add domain context for better searchability
            if domain_keywords:
                summary_parts.append(f"Engineering domains: {', '.join(sorted(domain_keywords))} analysis")
            
            # Add column listings with searchable terms
            if numeric_cols:
                summary_parts.append(f"Numeric data columns for measurements and calculations: {', '.join(numeric_cols)}")
            
            if categorical_cols:
                summary_parts.append(f"Categorical data columns for classification and status: {', '.join(categorical_cols)}")
            
            if identifier_cols:
                summary_parts.append(f"Identifier columns for referencing and tracking: {', '.join(identifier_cols)}")
            
            # Add detailed column information
            if column_info:
                summary_parts.append("Detailed column analysis:")
                summary_parts.extend(column_info[:15])  # Show more columns for better searchability
            
            # Add content context and patterns
            try:
                # Look for patterns in data that might be relevant for search
                content_patterns = []
                
                # Check for test/quality data patterns
                if any('pass' in str(val).lower() or 'fail' in str(val).lower() for col in categorical_cols for val in df[col].dropna().unique()[:10]):
                    content_patterns.append("contains test results and quality status information")
                
                # Check for cost/budget patterns
                if any('cost' in col.lower() or 'price' in col.lower() for col in df.columns):
                    content_patterns.append("includes cost analysis and budget information")
                
                # Check for requirements/specifications
                if any(word in col.lower() for col in df.columns for word in ['requirement', 'spec', 'target', 'limit']):
                    content_patterns.append("contains requirements and specifications data")
                
                if content_patterns:
                    summary_parts.append(f"Data patterns: This spreadsheet {', '.join(content_patterns)}")
                
                # Add sample data for context (more selective)
                if not df.empty and len(df.columns) <= 8:  # Only for smaller spreadsheets
                    sample_data = df.head(2).to_string(max_cols=6, max_colwidth=30)
                    summary_parts.append(f"Sample data preview:\n{sample_data}")
            
            except Exception as pattern_error:
                print(f"Error analyzing content patterns: {pattern_error}")
            
            # Create searchable summary
            summary = "\n".join(summary_parts)
            
            # Add additional searchable terms based on filename and content
            searchable_terms = []
            filename_lower = filename.lower()
            if 'test' in filename_lower:
                searchable_terms.append("test data analysis")
            if 'result' in filename_lower:
                searchable_terms.append("measurement results")
            if 'component' in filename_lower or 'part' in filename_lower:
                searchable_terms.append("component analysis")
            if 'thermal' in filename_lower:
                searchable_terms.append("thermal analysis")
            if 'mechanical' in filename_lower:
                searchable_terms.append("mechanical engineering")
            
            if searchable_terms:
                summary += f"\n\nSearchable context: {', '.join(searchable_terms)}"
            
            return summary
        
        except Exception as e:
            print(f"Error generating spreadsheet summary for {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            # Return basic summary as fallback
            return f"Engineering Spreadsheet: {filename}, Sheet: {sheet_name} with {len(df)} rows and {len(df.columns)} columns of data"
    
    def _analyze_column_characteristics(self, col_name: str, col_data: pd.Series) -> Dict[str, Any]:
        """
        Analyze individual column characteristics to determine data type, patterns, and purpose.
        """
        try:
            characteristics = {
                'name': col_name,
                'row_count': len(col_data),
                'null_count': col_data.isna().sum(),
                'unique_count': col_data.nunique(),
                'is_identifier': False,
                'is_calculated': False,
                'data_type': 'unknown'
            }
            
            # Determine basic data type
            if col_data.dtype in ['int64', 'float64']:
                characteristics['data_type'] = 'numeric'
                characteristics['min_value'] = float(col_data.min())
                characteristics['max_value'] = float(col_data.max())
                characteristics['mean_value'] = float(col_data.mean())
                
                # Check if it might be an identifier (sequential, unique)
                if characteristics['unique_count'] == characteristics['row_count']:
                    # All values are unique - might be an ID column
                    if col_name.lower() in ['id', 'key', 'index', 'number', 'sequence']:
                        characteristics['is_identifier'] = True
                
                # Check if it might be calculated (certain naming patterns)
                calc_keywords = ['total', 'sum', 'avg', 'average', 'calc', 'computed', 'result', 'score']
                if any(keyword in col_name.lower() for keyword in calc_keywords):
                    characteristics['is_calculated'] = True
            
            elif col_data.dtype == 'object':
                characteristics['data_type'] = 'categorical'
                
                # Sample some values for analysis
                sample_values = col_data.dropna().head(10).tolist()
                characteristics['sample_values'] = [str(v)[:50] for v in sample_values]
                
                # Check if it's an identifier column
                if characteristics['unique_count'] == characteristics['row_count']:
                    id_keywords = ['id', 'key', 'name', 'code', 'reference', 'part']
                    if any(keyword in col_name.lower() for keyword in id_keywords):
                        characteristics['is_identifier'] = True
            
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                characteristics['data_type'] = 'datetime'
                characteristics['min_date'] = str(col_data.min())
                characteristics['max_date'] = str(col_data.max())
            
            return characteristics
        
        except Exception as e:
            print(f"Error analyzing column characteristics for {col_name}: {e}")
            return {'name': col_name, 'data_type': 'unknown', 'error': str(e)}
    
    def _extract_table_data(self, sheet_name: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Extract structured table data for the Analytical Brain."""
        try:
            if df.empty:
                return None
            
            # Convert DataFrame to structured format for Knowledge Packet
            columns = df.columns.tolist()
            rows = df.values.tolist()
            
            # Determine column types
            column_types = []
            for col in df.columns:
                col_data = df[col].dropna()
                if col_data.empty:
                    column_types.append("string")
                elif col_data.dtype in ['int64', 'int32']:
                    column_types.append("integer")
                elif col_data.dtype in ['float64', 'float32']:
                    column_types.append("float")
                elif pd.api.types.is_datetime64_any_dtype(col_data):
                    column_types.append("datetime")
                elif col_data.dtype == 'bool':
                    column_types.append("boolean")
                else:
                    column_types.append("string")
            
            return {
                "table_name": f"sheet_{sheet_name}",
                "columns": columns,
                "rows": rows,
                "column_types": column_types
            }
        
        except Exception as e:
            print(f"Error extracting table data for {sheet_name}: {e}")
            return None
    
    def _extract_graph_data(self, filename: str, sheet_name: str, df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
        """
        Extract entities and relationships for the Graph Brain.
        Creates nodes for the spreadsheet, columns, and important values.
        """
        entities = []
        relationships = []
        
        try:
            sheet_identifier = f"{filename}:{sheet_name}"
            
            # Create sheet entity
            entities.append({
                "type": "Document",
                "name": sheet_identifier,
                "properties": {
                    "document_type": "spreadsheet",
                    "sheet_name": sheet_name,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "source_file": filename
                }
            })
            
            # Create column entities and relationships
            for col_name in df.columns:
                col_identifier = f"{sheet_identifier}:{col_name}"
                col_data = df[col_name].dropna()
                
                if col_data.empty:
                    continue
                
                # Analyze column characteristics
                col_info = self._analyze_column_characteristics(col_name, col_data)
                
                # Create column entity
                entities.append({
                    "type": "TechnicalConcept",
                    "name": col_identifier,
                    "properties": {
                        "concept_type": "spreadsheet_column",
                        "column_name": col_name,
                        "data_type": col_info['data_type'],
                        "row_count": col_info['row_count'],
                        "unique_count": col_info['unique_count'],
                        "is_identifier": col_info.get('is_identifier', False),
                        "is_calculated": col_info.get('is_calculated', False)
                    }
                })
                
                # Create relationship between sheet and column
                relationships.append({
                    "source": {"type": "Document", "name": sheet_identifier},
                    "relationship": "CONTAINS",
                    "target": {"type": "TechnicalConcept", "name": col_identifier},
                    "properties": {
                        "column_name": col_name,
                        "data_type": col_info['data_type']
                    }
                })
                
                # For categorical columns with limited values, create value entities
                if col_info['data_type'] == 'categorical' and col_info['unique_count'] <= 20:
                    for value in col_data.unique():
                        if pd.notna(value) and len(str(value).strip()) > 0:
                            value_str = str(value)[:50]
                            value_identifier = f"{col_identifier}:{value_str}"
                            
                            # Create value entity
                            entities.append({
                                "type": "TechnicalConcept",
                                "name": value_identifier,
                                "properties": {
                                    "concept_type": "categorical_value",
                                    "value": value_str,
                                    "column_name": col_name
                                }
                            })
                            
                            # Create relationship between column and value
                            relationships.append({
                                "source": {"type": "TechnicalConcept", "name": col_identifier},
                                "relationship": "CONTAINS",
                                "target": {"type": "TechnicalConcept", "name": value_identifier},
                                "properties": {
                                    "value": value_str
                                }
                            })
        
        except Exception as e:
            print(f"Error extracting graph data for {sheet_name}: {e}")
        
        return entities, relationships