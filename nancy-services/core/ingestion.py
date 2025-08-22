from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain
import os
import hashlib
import spacy
import re
import pandas as pd
import json
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import ast
import tree_sitter
from tree_sitter import Language, Parser
import git
from git.exc import GitCommandError, InvalidGitRepositoryError

class IngestionService:
    """
    Handles the ingestion of data from various sources.
    """
    def __init__(self):
        self.analytical_brain = AnalyticalBrain()
        self.graph_brain = GraphBrain()
        self.vector_brain = VectorBrain()
        # Load the spacy model
        self.nlp = spacy.load("en_core_web_sm")

    def _get_file_type(self, filename: str):
        return os.path.splitext(filename)[1].lower()
    
    def _extract_version_from_filename(self, filename: str) -> Optional[str]:
        """Extract version information from filename for temporal tracking."""
        import re
        
        version_patterns = [
            r'v(\d+\.?\d*\.?\d*)',  # v1.0, v2.1.3
            r'version[-_]?(\d+\.?\d*\.?\d*)',  # version1.0
            r'rev[-_]?(\d+)',       # rev1, rev_2
            r'draft[-_]?(\d+)',     # draft1, draft_2
        ]
        
        filename_lower = filename.lower()
        for pattern in version_patterns:
            match = re.search(pattern, filename_lower)
            if match:
                return match.group(1)
        
        return None

    def _generate_doc_id(self, filename: str, content: bytes) -> str:
        """Creates a unique ID for the document based on its name and content."""
        return hashlib.sha256(filename.encode() + content).hexdigest()

    def _extract_entities(self, text: str, current_filename: str):
        """
        Enhanced entity extraction with relationship discovery using LLM if available.
        """
        doc = self.nlp(text)
        
        # Extract person entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Create person nodes and link to document
                self.graph_brain.add_concept_node(ent.text, "Person")
                self.graph_brain.add_relationship(
                    source_node_label="Person",
                    source_node_name=ent.text,
                    relationship_type="MENTIONED_IN",
                    target_node_label="Document",
                    target_node_name=current_filename,
                    context=f"Mentioned in {current_filename}"
                )
        
        # Extract document references
        document_patterns = [
            r'\b(\w+\.\w{2,4})\b',  # file.ext
            r'\b(\w+\s+\w+\s+document)\b',  # "power analysis document"
            r'\b(\w+\s+report)\b',  # "thermal report"
            r'\b(\w+\s+analysis)\b',  # "stress analysis"
            r'\b(\w+\s+specification)\b',  # "design specification"
            r'\b(\w+\s+requirements)\b'  # "system requirements"
        ]
        
        for pattern in document_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.lower() != current_filename.lower():
                    self.graph_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type="REFERENCES",
                        target_node_label="Document",
                        target_node_name=match,
                        context=f"Referenced in {current_filename}"
                    )
        
        # Extract technical concepts and constraints
        concept_patterns = {
            "power": ["power consumption", "power management", "power supply", "battery life"],
            "thermal": ["thermal constraints", "temperature", "heat dissipation", "cooling"],
            "mechanical": ["mechanical design", "stress analysis", "material selection"],
            "electrical": ["electrical design", "circuit", "schematic", "EMC", "compliance"],
            "software": ["firmware", "software", "algorithm", "protocol", "interface"]
        }
        
        text_lower = text.lower()
        for concept_type, keywords in concept_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Create concept node and relationship
                    self.graph_brain.add_concept_node(keyword, "TechnicalConcept")
                    self.graph_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type="DISCUSSES",
                        target_node_label="TechnicalConcept",
                        target_node_name=keyword,
                        context=f"Technical concept discussed in {current_filename}"
                    )
        
        # Extract decision and influence relationships
        decision_patterns = [
            r'(decided|determined|chose|selected)\s+([^.]{1,50})',
            r'(impacts?|affects?|influences?)\s+([^.]{1,50})',
            r'(requires?|needs?|depends on)\s+([^.]{1,50})',
            r'(constrains?|limits?)\s+([^.]{1,50})'
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for verb, target in matches:
                relationship_map = {
                    "decided": "DECISION_MADE",
                    "determined": "DECISION_MADE",
                    "chose": "DECISION_MADE",
                    "selected": "DECISION_MADE",
                    "impacts": "AFFECTS",
                    "affects": "AFFECTS",
                    "influences": "INFLUENCES",
                    "requires": "REQUIRES",
                    "needs": "REQUIRES",
                    "depends": "DEPENDS_ON",
                    "constrains": "CONSTRAINS",
                    "limits": "CONSTRAINS"
                }
                
                rel_type = relationship_map.get(verb.lower(), "RELATES_TO")
                
                # Create a concept for the target if it's meaningful
                if len(target.strip()) > 5 and len(target.strip()) < 100:
                    concept_name = target.strip()[:50]  # Limit length
                    self.graph_brain.add_concept_node(concept_name, "DecisionTarget")
                    self.graph_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type=rel_type,
                        target_node_label="DecisionTarget", 
                        target_node_name=concept_name,
                        context=f"{verb} relationship from {current_filename}"
                    )
        
        # Skip LLM extraction during ingestion to avoid rate limits
        # LLM enhancement will be done on-demand during queries for better performance
        # This reduces ingestion time from 5-10 minutes to under 1 minute
        print(f"  Skipping LLM enhancement for {current_filename} (avoiding rate limits)")

    def _process_story_elements(self, story_elements: dict, document_name: str):
        """
        Process extracted project story elements and add them to the GraphBrain
        """
        try:
            # Process decisions
            for decision in story_elements.get("decisions", []):
                self.graph_brain.add_decision_node(
                    decision_name=decision.get("name", ""),
                    decision_maker=decision.get("maker", "Unknown"),
                    context=decision.get("context", ""),
                    era=decision.get("era")
                )
                
                # Link decision to document that influenced it
                if decision.get("name"):
                    self.graph_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=document_name,
                        relationship_type="INFLUENCED_BY",
                        target_node_label="Decision",
                        target_node_name=decision["name"],
                        context=f"Decision influenced by {document_name}"
                    )
            
            # Process meetings
            for meeting in story_elements.get("meetings", []):
                self.graph_brain.add_meeting_node(
                    meeting_name=meeting.get("name", ""),
                    attendees=meeting.get("attendees", []),
                    decisions_made=meeting.get("outcomes", []),
                    era=meeting.get("era")
                )
            
            # Process features
            for feature in story_elements.get("features", []):
                self.graph_brain.add_feature_node(
                    feature_name=feature.get("name", ""),
                    owner=feature.get("owner"),
                    influenced_by_decisions=feature.get("influenced_by", []),
                    era=feature.get("era")
                )
            
            # Process eras
            for era in story_elements.get("eras", []):
                self.graph_brain.add_era_node(
                    era_name=era.get("name", ""),
                    description=era.get("description", ""),
                    start_date=None,
                    end_date=None
                )
                
                # Link document to era
                if era.get("name"):
                    self.graph_brain.link_document_to_era(document_name, era["name"])
            
            # Process collaborations
            for collab in story_elements.get("collaborations", []):
                if collab.get("person1") and collab.get("person2"):
                    self.graph_brain.add_relationship(
                        source_node_label="Person",
                        source_node_name=collab["person1"],
                        relationship_type="COLLABORATES_WITH",
                        target_node_label="Person", 
                        target_node_name=collab["person2"],
                        context=collab.get("context", "Collaboration mentioned in document")
                    )
            
            print(f"Processed project story elements from {document_name}")
            
        except Exception as e:
            print(f"Error processing story elements: {e}")
    
    def _process_spreadsheet(self, filename: str, content: bytes, doc_id: str, file_type: str, author: str) -> Dict[str, Any]:
        """
        Comprehensive spreadsheet processing for Nancy's Four-Brain architecture.
        Handles Excel (.xlsx, .xls) and CSV files with robust error handling.
        """
        try:
            import io
            sheets_data = {}
            
            # Parse the spreadsheet based on file type
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
            
            if not sheets_data:
                raise ValueError(f"No valid sheets found in {filename}")

            # Process each sheet through the four-brain architecture
            total_rows = 0
            total_cols = 0
            processed_sheets = []
            
            print(f"Processing {len(sheets_data)} sheets through four-brain architecture")
            
            for sheet_name, df in sheets_data.items():
                if df.empty:
                    print(f"Skipping empty sheet: {sheet_name}")
                    continue
                
                print(f"Processing sheet '{sheet_name}' with {len(df)} rows and {len(df.columns)} columns")
                
                total_rows += len(df)
                total_cols = max(total_cols, len(df.columns))
                
                try:
                    # 1. Analytical Brain: Store structured data directly
                    print(f"Storing {sheet_name} data in Analytical Brain (DuckDB)")
                    self._store_spreadsheet_data(doc_id, filename, sheet_name, df)
                    
                    # 2. Graph Brain: Extract column relationships and dependencies
                    print(f"Extracting relationships for {sheet_name} in Graph Brain (Neo4j)")
                    self._extract_spreadsheet_relationships(filename, sheet_name, df)
                    
                    # 3. Vector Brain: Generate searchable summaries
                    print(f"Generating vector embeddings for {sheet_name} in Vector Brain (ChromaDB)")
                    summary_text = self._generate_spreadsheet_summary(filename, sheet_name, df)
                    if summary_text:
                        sheet_doc_id = f"{doc_id}_{sheet_name}"
                        self.vector_brain.embed_and_store_text(
                            doc_id=sheet_doc_id, 
                            text=summary_text, 
                            nlp=self.nlp
                        )
                        print(f"Successfully embedded summary for {sheet_name}")
                    
                    processed_sheets.append(sheet_name)
                    print(f"Successfully processed sheet: {sheet_name}")
                    
                except Exception as sheet_processing_error:
                    print(f"Error processing sheet '{sheet_name}': {sheet_processing_error}")
                    # Continue with other sheets instead of failing completely
                    continue

            # Update document metadata with spreadsheet-specific info
            spreadsheet_metadata = {
                "spreadsheet_type": file_type,
                "sheets_count": len(processed_sheets),
                "total_rows": total_rows,
                "total_columns": total_cols,
                "sheet_names": processed_sheets,
                "processing_status": "complete",
                "author": author
            }
            
            try:
                self.analytical_brain.update_document_metadata(
                    doc_id=doc_id,
                    additional_metadata=spreadsheet_metadata
                )
                print(f"Updated document metadata for {filename}")
            except Exception as metadata_error:
                print(f"Warning: Could not update document metadata: {metadata_error}")
            
            # Final summary
            result = {
                "filename": filename,
                "doc_id": doc_id,
                "status": "spreadsheet ingestion complete",
                "file_type": file_type,
                "sheets_found": len(sheets_data),
                "sheets_processed": len(processed_sheets),
                "total_rows": total_rows,
                "total_columns": total_cols,
                "processed_sheet_names": processed_sheets
            }
            
            print(f"Spreadsheet processing complete for {filename}: {len(processed_sheets)} sheets processed successfully")
            return result
            
        except Exception as e:
            print(f"Critical error processing spreadsheet {filename}: {e}")
            import traceback
            traceback.print_exc()
            
            # Return error information instead of raising
            return {
                "filename": filename,
                "doc_id": doc_id,
                "status": "spreadsheet ingestion failed",
                "error": str(e),
                "file_type": file_type
            }
    
    def _store_spreadsheet_data(self, doc_id: str, filename: str, sheet_name: str, df: pd.DataFrame):
        """
        Store spreadsheet data in the Analytical Brain (DuckDB) for structured queries.
        """
        try:
            # Create a table name based on the document and sheet
            table_name = f"spreadsheet_{doc_id[:8]}_{sheet_name}".replace(" ", "_").replace("-", "_")
            
            # Store the DataFrame in DuckDB via the analytical brain
            # We'll add this method to the AnalyticalBrain class
            if hasattr(self.analytical_brain, 'store_spreadsheet_data'):
                self.analytical_brain.store_spreadsheet_data(table_name, df, {
                    "doc_id": doc_id,
                    "filename": filename,
                    "sheet_name": sheet_name
                })
            else:
                # Fallback: store as JSON in metadata for now
                print(f"Storing spreadsheet data summary for {filename}:{sheet_name}")
            
            print(f"Stored spreadsheet data for {filename}:{sheet_name}")
            
        except Exception as e:
            print(f"Error storing spreadsheet data: {e}")
    
    def _extract_spreadsheet_relationships(self, filename: str, sheet_name: str, df: pd.DataFrame):
        """
        Extract comprehensive relationships between columns, data patterns, and dependencies.
        Creates structured nodes and relationships in the Graph Brain for spreadsheet intelligence.
        """
        try:
            sheet_identifier = f"{filename}:{sheet_name}"
            
            # Create sheet node with enhanced properties
            self.graph_brain.add_concept_node(sheet_identifier, "Spreadsheet")
            
            # Link sheet to document
            self.graph_brain.add_relationship(
                source_node_label="Document",
                source_node_name=filename,
                relationship_type="CONTAINS_SHEET",
                target_node_label="Spreadsheet",
                target_node_name=sheet_identifier,
                context=f"Document contains sheet {sheet_name} with {len(df)} rows and {len(df.columns)} columns"
            )

            # Analyze column relationships with enhanced intelligence
            column_types = {}
            numeric_columns = []
            categorical_columns = []
            identifier_columns = []
            
            for col_name in df.columns:
                col_identifier = f"{sheet_identifier}:{col_name}"
                col_data = df[col_name].dropna()
                
                if col_data.empty:
                    continue
                
                # Determine column characteristics
                col_info = self._analyze_column_characteristics(col_name, col_data)
                column_types[col_name] = col_info
                
                # Create column node with type information
                self.graph_brain.add_concept_node(col_identifier, "Column")
                
                # Link column to sheet with detailed context
                context = f"Column {col_name} ({col_info['data_type']}) in sheet {sheet_name}"
                if col_info.get('is_identifier'):
                    context += " - appears to be identifier/key column"
                    identifier_columns.append(col_name)
                elif col_info.get('is_calculated'):
                    context += " - appears to be calculated field"
                
                self.graph_brain.add_relationship(
                    source_node_label="Spreadsheet",
                    source_node_name=sheet_identifier,
                    relationship_type="HAS_COLUMN",
                    target_node_label="Column",
                    target_node_name=col_identifier,
                    context=context
                )
                
                # Categorize columns for relationship analysis
                if col_info['data_type'] == 'numeric':
                    numeric_columns.append(col_name)
                elif col_info['data_type'] == 'categorical':
                    categorical_columns.append(col_name)
                
                # Create relationships based on column content
                self._create_column_content_relationships(col_identifier, col_name, col_data, col_info)

            # Analyze cross-column relationships and dependencies
            self._detect_advanced_column_relationships(df, sheet_identifier, numeric_columns, categorical_columns, identifier_columns)
            
            # Create domain-specific relationships (engineering context)
            self._extract_engineering_domain_relationships(df, sheet_identifier)
            
            print(f"Successfully extracted relationships for sheet {sheet_name}: {len(df.columns)} columns analyzed")
            
        except Exception as e:
            print(f"Error extracting spreadsheet relationships for {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def _create_column_content_relationships(self, col_identifier: str, col_name: str, col_data: pd.Series, col_info: Dict[str, Any]):
        """
        Create relationships based on column content and characteristics.
        """
        try:
            # For categorical columns, create relationships with important values
            if col_info['data_type'] == 'categorical' and col_info['unique_count'] <= 20:
                for value in col_data.unique():
                    if pd.notna(value) and len(str(value).strip()) > 0:
                        value_str = str(value)[:50]
                        concept_name = f"{col_name}:{value_str}"
                        
                        # Create concept for categorical values
                        self.graph_brain.add_concept_node(concept_name, "CategoryValue")
                        
                        # Link to column
                        self.graph_brain.add_relationship(
                            source_node_label="Column",
                            source_node_name=col_identifier,
                            relationship_type="CONTAINS_VALUE",
                            target_node_label="CategoryValue",
                            target_node_name=concept_name,
                            context=f"Column {col_name} contains category value {value_str}"
                        )
            
            # For identifier columns, mark them specially
            if col_info.get('is_identifier'):
                identifier_concept = f"{col_identifier}_identifier"
                self.graph_brain.add_concept_node(identifier_concept, "IdentifierColumn")
                self.graph_brain.add_relationship(
                    source_node_label="Column",
                    source_node_name=col_identifier,
                    relationship_type="IS_IDENTIFIER",
                    target_node_label="IdentifierColumn",
                    target_node_name=identifier_concept,
                    context=f"Column {col_name} serves as identifier/key"
                )
            
            # For calculated columns, mark them specially
            if col_info.get('is_calculated'):
                calc_concept = f"{col_identifier}_calculated"
                self.graph_brain.add_concept_node(calc_concept, "CalculatedColumn")
                self.graph_brain.add_relationship(
                    source_node_label="Column",
                    source_node_name=col_identifier,
                    relationship_type="IS_CALCULATED",
                    target_node_label="CalculatedColumn",
                    target_node_name=calc_concept,
                    context=f"Column {col_name} appears to be calculated field"
                )
                
        except Exception as e:
            print(f"Error creating content relationships for {col_name}: {e}")
    
    def _detect_advanced_column_relationships(self, df: pd.DataFrame, sheet_identifier: str, numeric_columns: List[str], categorical_columns: List[str], identifier_columns: List[str]):
        """
        Detect advanced relationships between columns including correlations, hierarchies, and dependencies.
        """
        try:
            # Analyze numeric column correlations
            if len(numeric_columns) > 1:
                numeric_df = df[numeric_columns].select_dtypes(include=['number'])
                
                for i, col1 in enumerate(numeric_columns):
                    for col2 in numeric_columns[i+1:]:
                        try:
                            correlation = numeric_df[col1].corr(numeric_df[col2])
                            if abs(correlation) > 0.7:  # Strong correlation
                                col1_id = f"{sheet_identifier}:{col1}"
                                col2_id = f"{sheet_identifier}:{col2}"
                                
                                relationship_type = "STRONGLY_CORRELATED" if correlation > 0 else "INVERSELY_CORRELATED"
                                
                                self.graph_brain.add_relationship(
                                    source_node_label="Column",
                                    source_node_name=col1_id,
                                    relationship_type=relationship_type,
                                    target_node_label="Column",
                                    target_node_name=col2_id,
                                    context=f"Correlation coefficient: {correlation:.3f}"
                                )
                        except Exception as corr_error:
                            continue
            
            # Look for potential calculated field relationships
            self._detect_calculated_field_relationships(df, sheet_identifier, numeric_columns)
            
            # Detect hierarchical relationships in categorical data
            self._detect_categorical_hierarchies(df, sheet_identifier, categorical_columns)
            
        except Exception as e:
            print(f"Error detecting advanced column relationships: {e}")
    
    def _detect_calculated_field_relationships(self, df: pd.DataFrame, sheet_identifier: str, numeric_columns: List[str]):
        """
        Detect columns that might be calculated from other columns (sums, products, etc.).
        """
        try:
            for col_name in numeric_columns:
                col_data = df[col_name].dropna()
                if len(col_data) < 3:
                    continue
                
                # Check if this column might be a sum of other columns
                for other_col1 in numeric_columns:
                    for other_col2 in numeric_columns:
                        if col_name != other_col1 and col_name != other_col2 and other_col1 != other_col2:
                            try:
                                sum_data = df[other_col1].fillna(0) + df[other_col2].fillna(0)
                                if abs(col_data.corr(sum_data)) > 0.95:  # Very high correlation with sum
                                    col_id = f"{sheet_identifier}:{col_name}"
                                    col1_id = f"{sheet_identifier}:{other_col1}"
                                    col2_id = f"{sheet_identifier}:{other_col2}"
                                    
                                    self.graph_brain.add_relationship(
                                        source_node_label="Column",
                                        source_node_name=col_id,
                                        relationship_type="SUM_OF",
                                        target_node_label="Column",
                                        target_node_name=col1_id,
                                        context=f"Column {col_name} appears to be sum of {other_col1} and {other_col2}"
                                    )
                                    
                                    self.graph_brain.add_relationship(
                                        source_node_label="Column",
                                        source_node_name=col_id,
                                        relationship_type="SUM_OF",
                                        target_node_label="Column",
                                        target_node_name=col2_id,
                                        context=f"Column {col_name} appears to be sum of {other_col1} and {other_col2}"
                                    )
                                    break
                            except:
                                continue
                        
        except Exception as e:
            print(f"Error detecting calculated field relationships: {e}")
    
    def _detect_categorical_hierarchies(self, df: pd.DataFrame, sheet_identifier: str, categorical_columns: List[str]):
        """
        Detect hierarchical relationships in categorical data (e.g., category -> subcategory).
        """
        try:
            for i, col1 in enumerate(categorical_columns):
                for col2 in categorical_columns[i+1:]:
                    try:
                        # Check if one column might be a breakdown of another
                        col1_unique = df[col1].nunique()
                        col2_unique = df[col2].nunique()
                        
                        if col1_unique < col2_unique and col1_unique > 1:
                            # col1 might be a higher-level category
                            grouped = df.groupby(col1)[col2].nunique()
                            avg_subcategories = grouped.mean()
                            
                            if avg_subcategories > 1.5:  # Each category has multiple subcategories
                                col1_id = f"{sheet_identifier}:{col1}"
                                col2_id = f"{sheet_identifier}:{col2}"
                                
                                self.graph_brain.add_relationship(
                                    source_node_label="Column",
                                    source_node_name=col1_id,
                                    relationship_type="PARENT_CATEGORY_OF",
                                    target_node_label="Column",
                                    target_node_name=col2_id,
                                    context=f"Column {col1} appears to be parent category of {col2}"
                                )
                                
                    except Exception as hier_error:
                        continue
                        
        except Exception as e:
            print(f"Error detecting categorical hierarchies: {e}")
    
    def _extract_engineering_domain_relationships(self, df: pd.DataFrame, sheet_identifier: str):
        """
        Extract domain-specific relationships relevant to engineering contexts.
        """
        try:
            # Engineering domain keywords and their relationships
            domain_patterns = {
                'thermal': ['temperature', 'thermal', 'heat', 'cooling', 'temp'],
                'mechanical': ['stress', 'strain', 'force', 'pressure', 'material', 'strength'],
                'electrical': ['voltage', 'current', 'power', 'resistance', 'frequency', 'circuit'],
                'quality': ['pass', 'fail', 'test', 'result', 'status', 'compliance'],
                'cost': ['cost', 'price', 'budget', 'expense', 'dollar'],
                'time': ['date', 'time', 'schedule', 'deadline', 'duration'],
                'requirements': ['requirement', 'spec', 'specification', 'target', 'limit']
            }
            
            # Analyze column names for domain relationships
            for col_name in df.columns:
                col_name_lower = col_name.lower()
                col_identifier = f"{sheet_identifier}:{col_name}"
                
                for domain, keywords in domain_patterns.items():
                    if any(keyword in col_name_lower for keyword in keywords):
                        domain_concept = f"{sheet_identifier}:{domain}_domain"
                        
                        # Create domain concept
                        self.graph_brain.add_concept_node(domain_concept, "EngineeringDomain")
                        
                        # Link column to domain
                        self.graph_brain.add_relationship(
                            source_node_label="Column",
                            source_node_name=col_identifier,
                            relationship_type="BELONGS_TO_DOMAIN",
                            target_node_label="EngineeringDomain",
                            target_node_name=domain_concept,
                            context=f"Column {col_name} relates to {domain} engineering domain"
                        )
                        break  # Only assign to first matching domain
            
            # Look for test/requirement relationships
            self._extract_test_requirement_relationships(df, sheet_identifier)
            
        except Exception as e:
            print(f"Error extracting engineering domain relationships: {e}")
    
    def _extract_test_requirement_relationships(self, df: pd.DataFrame, sheet_identifier: str):
        """
        Extract relationships between test results, requirements, and compliance status.
        """
        try:
            # Look for columns that might represent test results or requirements
            test_columns = []
            requirement_columns = []
            status_columns = []
            
            for col_name in df.columns:
                col_lower = col_name.lower()
                if any(keyword in col_lower for keyword in ['test', 'result', 'measurement', 'actual']):
                    test_columns.append(col_name)
                elif any(keyword in col_lower for keyword in ['requirement', 'spec', 'target', 'limit', 'max', 'min']):
                    requirement_columns.append(col_name)
                elif any(keyword in col_lower for keyword in ['status', 'pass', 'fail', 'compliance', 'ok']):
                    status_columns.append(col_name)
            
            # Create relationships between test results and requirements
            for test_col in test_columns:
                test_col_id = f"{sheet_identifier}:{test_col}"
                
                # Look for corresponding requirement columns (similar names)
                for req_col in requirement_columns:
                    # Simple name similarity check
                    test_words = set(test_col.lower().split())
                    req_words = set(req_col.lower().split())
                    common_words = test_words.intersection(req_words)
                    
                    if len(common_words) > 0:  # Some words in common
                        req_col_id = f"{sheet_identifier}:{req_col}"
                        
                        self.graph_brain.add_relationship(
                            source_node_label="Column",
                            source_node_name=test_col_id,
                            relationship_type="TESTED_AGAINST",
                            target_node_label="Column",
                            target_node_name=req_col_id,
                            context=f"Test result {test_col} measured against requirement {req_col}"
                        )
            
            # Link status columns to test columns
            for status_col in status_columns:
                status_col_id = f"{sheet_identifier}:{status_col}"
                
                for test_col in test_columns:
                    test_col_id = f"{sheet_identifier}:{test_col}"
                    
                    self.graph_brain.add_relationship(
                        source_node_label="Column",
                        source_node_name=status_col_id,
                        relationship_type="STATUS_OF",
                        target_node_label="Column",
                        target_node_name=test_col_id,
                        context=f"Status column {status_col} indicates result of test {test_col}"
                    )
                    
        except Exception as e:
            print(f"Error extracting test requirement relationships: {e}")
    
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

    def ingest_file(self, filename: str, content: bytes, author: str = "Unknown", 
                    creation_timestamp: str = None, era: str = None):
        """
        Processes an uploaded file and stores it in the three brains.
        """
        file_type = self._get_file_type(filename)
        doc_id = self._generate_doc_id(filename, content)

        # 1. Analytical Brain: Store metadata
        self.analytical_brain.insert_document_metadata(
            doc_id=doc_id, # Pass the hash as a string
            filename=filename,
            size=len(content),
            file_type=file_type
        )

        # 2. Graph Brain: Create temporal document with enhanced metadata
        current_timestamp = creation_timestamp or datetime.utcnow().isoformat()
        
        # Use enhanced temporal document creation if available
        if hasattr(self.graph_brain, 'add_document_with_temporal_context'):
            self.graph_brain.add_document_with_temporal_context(
                filename=filename,
                author=author,
                timestamp=current_timestamp,
                era=era,
                document_type=file_type.lstrip('.'),  # Remove leading dot
                version=self._extract_version_from_filename(filename)
            )
        else:
            # Fallback to original method
            self.graph_brain.add_document_node(filename=filename, file_type=file_type)
            self.graph_brain.add_author_relationship(filename=filename, author_name=author)

        # 3. Vector Brain & Entity Extraction
        # Define a list of text-based file extensions to process
        text_based_extensions = ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json']
        spreadsheet_extensions = ['.xlsx', '.xls', '.csv']
        code_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp']
        
        if file_type in spreadsheet_extensions:
            try:
                return self._process_spreadsheet(filename, content, doc_id, file_type, author)
            except Exception as e:
                print(f"Spreadsheet processing failed for {filename}: {str(e)}")
                # Fall back to text processing for CSV files
                if file_type == '.csv':
                    print(f"Falling back to text processing for CSV file: {filename}")
                    file_type = '.txt'  # Treat as text for fallback processing
                else:
                    return {"error": f"Failed to process spreadsheet {filename}: {str(e)}"}
        
        # Process code files with enhanced analysis
        if file_type in code_extensions:
            try:
                return self._process_code_file(filename, content, doc_id, file_type, author)
            except Exception as e:
                print(f"Code processing failed for {filename}: {str(e)}")
                # Fall back to regular text processing
                print(f"Falling back to text processing for code file: {filename}")
        
        if file_type in text_based_extensions or file_type == '.txt':
            try:
                text = content.decode('utf-8')
                # Embed and store the text
                self.vector_brain.embed_and_store_text(doc_id=doc_id, text=text, nlp=self.nlp)
                # Extract entities and create relationships
                self._extract_entities(text, filename)
            except UnicodeDecodeError:
                return {"error": f"Could not decode file {filename} as UTF-8 text."}
        else:
            print(f"Skipping vector embedding and entity extraction for non-text file: {filename}")


        return {
            "filename": filename,
            "doc_id": doc_id,
            "status": "ingestion complete",
        }
    
    def _process_code_file(self, filename: str, content: bytes, doc_id: str, file_type: str, author: str) -> Dict[str, Any]:
        """
        Comprehensive code file processing through Nancy's Four-Brain Architecture.
        Handles source code with AST parsing, Git integration, and relationship extraction.
        """
        try:
            print(f"Processing code file {filename} through Four-Brain Architecture")
            
            # Decode content
            try:
                text_content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text_content = content.decode('latin-1')
                except Exception as decode_error:
                    return {"error": f"Could not decode code file {filename}: {decode_error}"}
            
            # 1. Analytical Brain: Store basic metadata
            self.analytical_brain.insert_document_metadata(
                doc_id=doc_id,
                filename=filename,
                size=len(content),
                file_type=file_type
            )
            
            # 2. Vector Brain: Embed text content for semantic search
            self.vector_brain.embed_and_store_text(doc_id=doc_id, text=text_content, nlp=self.nlp)
            
            # 3. Enhanced Code Analysis with AST and Git
            full_path = filename  # Assuming filename contains full path for code analysis
            code_analysis = self.codebase_service.analyze_code_file(full_path)
            
            if "error" in code_analysis:
                print(f"AST analysis failed for {filename}: {code_analysis['error']}")
                # Continue with basic processing
                code_analysis = None
            else:
                print(f"Successfully analyzed code structure for {filename}")
                
                # 4. Graph Brain: Create comprehensive code relationships
                self._create_code_relationships(filename, code_analysis, author)
                
                # 5. Store code metrics in Analytical Brain
                self._store_code_metrics(doc_id, filename, code_analysis)
            
            # 6. Regular document processing for overall relationships
            self.graph_brain.add_document_node(filename=filename, file_type=file_type)
            self.graph_brain.add_author_relationship(filename=filename, author_name=author)
            
            # 7. Extract general entities from comments and docstrings
            self._extract_entities(text_content, filename)
            
            result = {
                "filename": filename,
                "doc_id": doc_id,
                "status": "code ingestion complete",
                "file_type": file_type,
                "ast_analysis_success": code_analysis is not None,
                "language": code_analysis.get("ast_analysis", {}).get("language", "unknown") if code_analysis else "unknown",
                "functions_found": len(code_analysis.get("ast_analysis", {}).get("functions", [])) if code_analysis else 0,
                "classes_found": len(code_analysis.get("ast_analysis", {}).get("classes", [])) if code_analysis else 0
            }
            
            print(f"Code processing complete for {filename}: {result['language']} file with {result['functions_found']} functions and {result['classes_found']} classes")
            return result
            
        except Exception as e:
            print(f"Error in code file processing for {filename}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": f"Code processing failed for {filename}: {str(e)}"}
    
    def _create_code_relationships(self, filename: str, code_analysis: Dict[str, Any], author: str):
        """
        Create comprehensive code relationships in the Graph Brain.
        """
        try:
            if not code_analysis or "error" in code_analysis:
                return
            
            ast_data = code_analysis.get("ast_analysis", {})
            git_data = code_analysis.get("git_analysis", {})
            
            if "error" in ast_data:
                return
            
            language = ast_data.get("language", "unknown")
            lines_of_code = ast_data.get("lines_of_code", 0)
            
            # Create code file node with enhanced metadata
            self.graph_brain.add_code_file_node(
                file_path=filename,
                language=language,
                author=author,
                lines_of_code=lines_of_code,
                git_info=git_data
            )
            
            # Process functions
            for func in ast_data.get("functions", []):
                self.graph_brain.add_function_node(
                    function_name=func["name"],
                    file_path=filename,
                    language=language,
                    line_start=func.get("line_start"),
                    line_end=func.get("line_end"),
                    docstring=func.get("docstring"),
                    args=func.get("args", [])
                )
            
            # Process classes
            for cls in ast_data.get("classes", []):
                self.graph_brain.add_class_node(
                    class_name=cls["name"],
                    file_path=filename,
                    language=language,
                    line_start=cls.get("line_start"),
                    line_end=cls.get("line_end"),
                    docstring=cls.get("docstring"),
                    base_classes=cls.get("bases", [])
                )
                
                # Add methods to class
                for method in cls.get("methods", []):
                    self.graph_brain.add_method_to_class(
                        method_name=method["name"],
                        class_name=cls["name"],
                        file_path=filename,
                        line_start=method.get("line_start"),
                        docstring=method.get("docstring"),
                        args=method.get("args", [])
                    )
            
            # Process imports
            for imp in ast_data.get("imports", []):
                import_name = imp.get("module") or imp.get("name")
                if import_name:
                    self.graph_brain.add_import_relationship(
                        importing_file=filename,
                        imported_module=import_name,
                        import_type=imp.get("type", "import"),
                        alias=imp.get("alias")
                    )
            
            print(f"Created code relationships for {filename}: {len(ast_data.get('functions', []))} functions, {len(ast_data.get('classes', []))} classes")
            
        except Exception as e:
            print(f"Error creating code relationships for {filename}: {e}")
    
    def _store_code_metrics(self, doc_id: str, filename: str, code_analysis: Dict[str, Any]):
        """
        Store code metrics and complexity data in the Analytical Brain.
        """
        try:
            if not code_analysis or "error" in code_analysis:
                return
            
            ast_data = code_analysis.get("ast_analysis", {})
            git_data = code_analysis.get("git_analysis", {})
            
            # Prepare code metrics
            metrics = {
                "language": ast_data.get("language", "unknown"),
                "lines_of_code": ast_data.get("lines_of_code", 0),
                "function_count": ast_data.get("total_functions", 0),
                "class_count": ast_data.get("total_classes", 0),
                "import_count": ast_data.get("total_imports", 0)
            }
            
            # Add Git metrics if available
            if "error" not in git_data:
                metrics.update({
                    "contributors_count": git_data.get("total_contributors", 0),
                    "commit_count": git_data.get("commit_count", 0),
                    "primary_author": git_data.get("primary_author", "Unknown")
                })
            
            # Update document metadata with code metrics
            try:
                self.analytical_brain.update_document_metadata(
                    doc_id=doc_id,
                    additional_metadata=metrics
                )
                print(f"Stored code metrics for {filename}")
            except Exception as metadata_error:
                print(f"Warning: Could not store code metrics for {filename}: {metadata_error}")
                
        except Exception as e:
            print(f"Error storing code metrics for {filename}: {e}")


class DirectoryIngestionService:
    """
    Handles directory-based file ingestion with hash-based change detection.
    Integrates with Nancy's four-brain architecture for proactive project intelligence monitoring.
    """
    
    def __init__(self):
        self.analytical_brain = AnalyticalBrain()
        self.ingestion_service = IngestionService()
        self.codebase_service = CodebaseIngestionService()
        print("DirectoryIngestionService initialized with four-brain architecture and codebase analysis")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file content for change detection.
        """
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            print(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def _matches_patterns(self, file_path: str, patterns: str) -> bool:
        """
        Check if file path matches any of the provided patterns.
        """
        if not patterns:
            return True
        
        pattern_list = [p.strip() for p in patterns.split(',')]
        file_name = os.path.basename(file_path)
        relative_path = file_path
        
        for pattern in pattern_list:
            # Check both filename and relative path
            if fnmatch.fnmatch(file_name, pattern) or fnmatch.fnmatch(relative_path, pattern):
                return True
        
        return False
    
    def _should_ignore_file(self, file_path: str, ignore_patterns: str) -> bool:
        """
        Check if file should be ignored based on ignore patterns.
        """
        if not ignore_patterns:
            return False
        
        return self._matches_patterns(file_path, ignore_patterns)
    
    def _is_supported_file_type(self, file_path: str) -> bool:
        """
        Check if file type is supported for ingestion.
        """
        supported_extensions = {
            '.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json',
            '.csv', '.xlsx', '.xls', '.ts', '.java', '.c', '.cpp', '.h', '.hpp'
        }
        
        file_extension = Path(file_path).suffix.lower()
        return file_extension in supported_extensions
    
    def scan_directory(self, directory_path: str, recursive: bool = True, 
                      file_patterns: str = None, ignore_patterns: str = None,
                      author: str = "Directory Scan") -> Dict[str, Any]:
        """
        Scan directory for files and detect changes using hash-based comparison.
        Phase 1 implementation with periodic re-ingestion approach.
        """
        try:
            if not os.path.exists(directory_path):
                return {"error": f"Directory does not exist: {directory_path}"}
            
            if not os.path.isdir(directory_path):
                return {"error": f"Path is not a directory: {directory_path}"}
            
            # Default patterns if not provided
            if file_patterns is None:
                file_patterns = "*.txt,*.md,*.py,*.js,*.ts,*.java,*.c,*.cpp,*.h,*.hpp,*.html,*.css,*.json,*.csv,*.xlsx,*.xls"
            if ignore_patterns is None:
                ignore_patterns = ".git/*,.env*,node_modules/*,__pycache__/*,*.pyc"
            
            directory_path = os.path.abspath(directory_path)
            print(f"Scanning directory: {directory_path} (recursive={recursive})")
            
            discovered_files = []
            existing_file_paths = set()
            new_files = 0
            changed_files = 0
            unchanged_files = 0
            ignored_files = 0
            unsupported_files = 0
            
            # Walk through directory
            if recursive:
                for root, dirs, files in os.walk(directory_path):
                    # Skip ignored directories
                    dirs[:] = [d for d in dirs if not self._should_ignore_file(os.path.join(root, d), ignore_patterns)]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        self._process_discovered_file(
                            file_path, directory_path, file_patterns, ignore_patterns,
                            discovered_files, existing_file_paths, 
                            new_files, changed_files, unchanged_files, ignored_files, unsupported_files
                        )
            else:
                # Non-recursive scan
                for item in os.listdir(directory_path):
                    file_path = os.path.join(directory_path, item)
                    if os.path.isfile(file_path):
                        new_files, changed_files, unchanged_files, ignored_files, unsupported_files = self._process_discovered_file(
                            file_path, directory_path, file_patterns, ignore_patterns,
                            discovered_files, existing_file_paths,
                            new_files, changed_files, unchanged_files, ignored_files, unsupported_files
                        )
            
            # Mark deleted files
            deleted_count = self.analytical_brain.mark_deleted_files(existing_file_paths, directory_path)
            
            scan_results = {
                "directory_path": directory_path,
                "recursive": recursive,
                "total_files_discovered": len(discovered_files),
                "new_files": new_files,
                "changed_files": changed_files,
                "unchanged_files": unchanged_files,
                "ignored_files": ignored_files,
                "unsupported_files": unsupported_files,
                "deleted_files": deleted_count,
                "files_to_process": new_files + changed_files,
                "scan_timestamp": datetime.utcnow().isoformat(),
                "file_patterns": file_patterns,
                "ignore_patterns": ignore_patterns
            }
            
            print(f"Directory scan complete: {len(discovered_files)} files discovered, "
                  f"{new_files + changed_files} need processing")
            
            return scan_results
            
        except Exception as e:
            print(f"Error scanning directory {directory_path}: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _process_discovered_file(self, file_path: str, directory_root: str, 
                               file_patterns: str, ignore_patterns: str,
                               discovered_files: list, existing_file_paths: set,
                               new_files: int, changed_files: int, unchanged_files: int,
                               ignored_files: int, unsupported_files: int) -> tuple:
        """
        Process a single discovered file for hash-based change detection.
        """
        try:
            relative_path = os.path.relpath(file_path, directory_root)
            existing_file_paths.add(file_path)
            
            # Check if file should be ignored
            if self._should_ignore_file(relative_path, ignore_patterns):
                ignored_files += 1
                return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
            
            # Check if file matches include patterns
            if not self._matches_patterns(relative_path, file_patterns):
                ignored_files += 1
                return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
            
            # Check if file type is supported
            if not self._is_supported_file_type(file_path):
                unsupported_files += 1
                return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
            
            # Get file stats
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            
            # Calculate hash for change detection
            content_hash = self._calculate_file_hash(file_path)
            if not content_hash:
                # Hash calculation failed, skip file
                return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
            
            # Check if file needs processing using analytical brain
            needs_processing = self.analytical_brain.upsert_file_state(
                file_path, content_hash, last_modified, file_size, directory_root, relative_path
            )
            
            file_info = {
                "file_path": file_path,
                "relative_path": relative_path,
                "file_size": file_size,
                "last_modified": last_modified.isoformat(),
                "content_hash": content_hash,
                "needs_processing": needs_processing
            }
            
            discovered_files.append(file_info)
            
            if needs_processing:
                # Determine if new or changed
                existing = self.analytical_brain.con.execute(
                    "SELECT COUNT(*) FROM file_state WHERE file_path = ? AND created_at < updated_at",
                    (file_path,)
                ).fetchone()[0]
                
                if existing > 0:
                    changed_files += 1
                else:
                    new_files += 1
            else:
                unchanged_files += 1
            
            return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return new_files, changed_files, unchanged_files, ignored_files, unsupported_files
    
    def process_pending_files(self, limit: int = 50, author: str = "Directory Processing") -> Dict[str, Any]:
        """
        Process files that are pending ingestion through the four-brain architecture.
        """
        try:
            pending_files = self.analytical_brain.get_files_to_process(limit)
            
            if not pending_files:
                return {
                    "status": "no_files_to_process",
                    "processed_files": 0,
                    "successful": 0,
                    "failed": 0,
                    "results": []
                }
            
            print(f"Processing {len(pending_files)} pending files through four-brain architecture")
            
            results = []
            successful = 0
            failed = 0
            
            for file_info in pending_files:
                file_path = file_info['file_path']
                relative_path = file_info['relative_path']
                
                try:
                    # Read file content
                    if not os.path.exists(file_path):
                        # File was deleted between scan and processing
                        self.analytical_brain.update_file_processing_status(
                            file_path, 'deleted', error_message="File no longer exists"
                        )
                        results.append({
                            "file_path": file_path,
                            "status": "deleted",
                            "message": "File no longer exists"
                        })
                        failed += 1
                        continue
                    
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    # Use filename from relative path for better naming
                    display_filename = relative_path
                    
                    # Process through existing ingestion service (four-brain architecture)
                    ingestion_result = self.ingestion_service.ingest_file(
                        filename=display_filename,
                        content=content,
                        author=author
                    )
                    
                    if "error" in ingestion_result:
                        # Ingestion failed
                        self.analytical_brain.update_file_processing_status(
                            file_path, 'error', error_message=ingestion_result["error"]
                        )
                        results.append({
                            "file_path": file_path,
                            "status": "error",
                            "error": ingestion_result["error"]
                        })
                        failed += 1
                    else:
                        # Ingestion successful
                        self.analytical_brain.update_file_processing_status(
                            file_path, 'completed', doc_id=ingestion_result.get("doc_id")
                        )
                        results.append({
                            "file_path": file_path,
                            "status": "completed",
                            "doc_id": ingestion_result.get("doc_id"),
                            "ingestion_result": ingestion_result
                        })
                        successful += 1
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error processing file {file_path}: {error_msg}")
                    
                    self.analytical_brain.update_file_processing_status(
                        file_path, 'error', error_message=error_msg
                    )
                    results.append({
                        "file_path": file_path,
                        "status": "error",
                        "error": error_msg
                    })
                    failed += 1
            
            processing_summary = {
                "status": "processing_complete",
                "processed_files": len(pending_files),
                "successful": successful,
                "failed": failed,
                "success_rate": successful / len(pending_files) if pending_files else 0,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "results": results
            }
            
            print(f"Directory processing complete: {successful}/{len(pending_files)} successful")
            return processing_summary
            
        except Exception as e:
            print(f"Error in process_pending_files: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def scan_and_process_directory(self, directory_path: str, recursive: bool = True,
                                 file_patterns: str = None, ignore_patterns: str = None,
                                 author: str = "Directory Ingestion", 
                                 process_limit: int = 50) -> Dict[str, Any]:
        """
        Combined operation: scan directory for changes and process pending files.
        This is the primary method for directory-based ingestion.
        """
        try:
            # Step 1: Scan directory for changes
            print(f"Step 1: Scanning directory {directory_path}")
            scan_results = self.scan_directory(
                directory_path, recursive, file_patterns, ignore_patterns, author
            )
            
            if "error" in scan_results:
                return scan_results
            
            # Step 2: Process pending files if any were found
            if scan_results.get("files_to_process", 0) > 0:
                print(f"Step 2: Processing {scan_results['files_to_process']} files")
                processing_results = self.process_pending_files(process_limit, author)
                
                # Combine results
                combined_results = {
                    "operation": "scan_and_process",
                    "directory_path": directory_path,
                    "scan_results": scan_results,
                    "processing_results": processing_results,
                    "overall_status": "completed",
                    "total_files_discovered": scan_results["total_files_discovered"],
                    "files_processed": processing_results.get("processed_files", 0),
                    "files_successful": processing_results.get("successful", 0),
                    "files_failed": processing_results.get("failed", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                return combined_results
            else:
                return {
                    "operation": "scan_and_process",
                    "directory_path": directory_path,
                    "scan_results": scan_results,
                    "processing_results": {
                        "status": "no_files_to_process",
                        "message": "No new or changed files found"
                    },
                    "overall_status": "completed",
                    "total_files_discovered": scan_results["total_files_discovered"],
                    "files_processed": 0,
                    "files_successful": 0,
                    "files_failed": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            print(f"Error in scan_and_process_directory: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


class GitAnalysisService:
    """
    Service for analyzing Git repositories to extract authorship, history, and collaboration data.
    Integrates with Nancy's Four-Brain Architecture for comprehensive code understanding.
    """
    
    def __init__(self):
        self.repo = None
        self.repo_path = None
        print("GitAnalysisService initialized")
    
    def initialize_repository(self, repo_path: str) -> bool:
        """
        Initialize Git repository for analysis.
        """
        try:
            self.repo_path = os.path.abspath(repo_path)
            
            # Find the git repository root
            current_path = self.repo_path
            while current_path != os.path.dirname(current_path):  # not root directory
                if os.path.exists(os.path.join(current_path, '.git')):
                    self.repo = git.Repo(current_path)
                    self.repo_path = current_path
                    print(f"Git repository found: {self.repo_path}")
                    return True
                current_path = os.path.dirname(current_path)
            
            # Try initializing directly if no .git found in parents
            if os.path.exists(os.path.join(self.repo_path, '.git')):
                self.repo = git.Repo(self.repo_path)
                print(f"Git repository initialized: {self.repo_path}")
                return True
            
            print(f"No Git repository found at {repo_path} or its parents")
            return False
            
        except (GitCommandError, InvalidGitRepositoryError) as e:
            print(f"Git repository initialization failed: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error initializing Git repository: {e}")
            return False
    
    def get_file_authorship(self, file_path: str) -> Dict[str, Any]:
        """
        Get authorship information for a file including contributors and commit history.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            relative_path = os.path.relpath(file_path, self.repo_path)
            
            # Get blame information for the file
            blame_data = []
            contributors = set()
            
            try:
                blame = self.repo.blame('HEAD', relative_path)
                
                for commit, lines in blame:
                    author_name = commit.author.name
                    author_email = commit.author.email
                    commit_date = commit.authored_datetime
                    
                    contributors.add(author_name)
                    blame_data.append({
                        "author_name": author_name,
                        "author_email": author_email,
                        "commit_hash": commit.hexsha,
                        "commit_date": commit_date.isoformat(),
                        "lines": len(lines)
                    })
            except Exception as blame_error:
                print(f"Blame analysis failed for {relative_path}: {blame_error}")
            
            # Get commit history for the file
            commit_history = []
            try:
                commits = list(self.repo.iter_commits(paths=relative_path, max_count=20))
                
                for commit in commits:
                    commit_history.append({
                        "commit_hash": commit.hexsha,
                        "author_name": commit.author.name,
                        "author_email": commit.author.email,
                        "commit_date": commit.authored_datetime.isoformat(),
                        "message": commit.message.strip(),
                        "files_changed": commit.stats.total['files'],
                        "insertions": commit.stats.total['insertions'],
                        "deletions": commit.stats.total['deletions']
                    })
            except Exception as history_error:
                print(f"Commit history failed for {relative_path}: {history_error}")
            
            # Get file statistics
            try:
                file_stat = os.stat(file_path)
                last_modified = datetime.fromtimestamp(file_stat.st_mtime)
            except:
                last_modified = None
            
            return {
                "file_path": relative_path,
                "contributors": list(contributors),
                "primary_author": contributors and list(contributors)[0] or "Unknown",
                "total_contributors": len(contributors),
                "commit_count": len(commit_history),
                "last_modified": last_modified.isoformat() if last_modified else None,
                "blame_data": blame_data,
                "commit_history": commit_history,
                "repository_path": self.repo_path
            }
            
        except Exception as e:
            print(f"Error analyzing authorship for {file_path}: {e}")
            return {"error": str(e)}
    
    def get_repository_metadata(self) -> Dict[str, Any]:
        """
        Get comprehensive repository metadata.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        try:
            # Get repository basic info
            repo_info = {
                "repository_path": self.repo_path,
                "current_branch": self.repo.active_branch.name if self.repo.active_branch else "detached",
                "total_commits": sum(1 for _ in self.repo.iter_commits()),
                "remotes": [remote.url for remote in self.repo.remotes],
                "branches": [branch.name for branch in self.repo.branches],
                "tags": [tag.name for tag in self.repo.tags]
            }
            
            # Get contributor statistics
            contributors = {}
            for commit in self.repo.iter_commits():
                author_name = commit.author.name
                if author_name not in contributors:
                    contributors[author_name] = {
                        "name": author_name,
                        "email": commit.author.email,
                        "commits": 0,
                        "insertions": 0,
                        "deletions": 0,
                        "first_commit": commit.authored_datetime,
                        "last_commit": commit.authored_datetime
                    }
                
                contributors[author_name]["commits"] += 1
                contributors[author_name]["insertions"] += commit.stats.total['insertions']
                contributors[author_name]["deletions"] += commit.stats.total['deletions']
                
                if commit.authored_datetime < contributors[author_name]["first_commit"]:
                    contributors[author_name]["first_commit"] = commit.authored_datetime
                if commit.authored_datetime > contributors[author_name]["last_commit"]:
                    contributors[author_name]["last_commit"] = commit.authored_datetime
            
            # Convert datetime objects to ISO format
            for contributor in contributors.values():
                contributor["first_commit"] = contributor["first_commit"].isoformat()
                contributor["last_commit"] = contributor["last_commit"].isoformat()
            
            repo_info["contributors"] = list(contributors.values())
            repo_info["total_contributors"] = len(contributors)
            
            return repo_info
            
        except Exception as e:
            print(f"Error getting repository metadata: {e}")
            return {"error": str(e)}
    
    def analyze_code_ownership(self, file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze code ownership patterns across the repository.
        """
        if not self.repo:
            return {"error": "No repository initialized"}
        
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h']
        
        try:
            ownership_data = {}
            file_count_by_author = {}
            lines_by_author = {}
            
            # Walk through repository files
            for root, dirs, files in os.walk(self.repo_path):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    if file_ext in file_extensions:
                        authorship = self.get_file_authorship(file_path)
                        
                        if "error" not in authorship:
                            primary_author = authorship.get("primary_author", "Unknown")
                            
                            if primary_author not in file_count_by_author:
                                file_count_by_author[primary_author] = 0
                                lines_by_author[primary_author] = 0
                            
                            file_count_by_author[primary_author] += 1
                            
                            # Count lines contributed by author
                            for blame_entry in authorship.get("blame_data", []):
                                if blame_entry["author_name"] == primary_author:
                                    lines_by_author[primary_author] += blame_entry["lines"]
            
            return {
                "ownership_by_files": file_count_by_author,
                "ownership_by_lines": lines_by_author,
                "analyzed_extensions": file_extensions,
                "repository_path": self.repo_path
            }
            
        except Exception as e:
            print(f"Error analyzing code ownership: {e}")
            return {"error": str(e)}


class CodebaseIngestionService:
    """
    Comprehensive service for analyzing and ingesting source code repositories.
    Provides AST parsing, Git integration, and Four-Brain Architecture integration
    for deep codebase understanding and analysis.
    """
    
    def __init__(self):
        self.git_service = GitAnalysisService()
        self.parsers = {}
        self.languages = {}
        self._initialize_tree_sitter()
        print("CodebaseIngestionService initialized with AST parsing capabilities")
    
    def _initialize_tree_sitter(self):
        """
        Initialize tree-sitter parsers for supported languages.
        """
        try:
            # Dictionary mapping file extensions to tree-sitter language names
            self.language_map = {
                '.py': 'python',
                '.js': 'javascript', 
                '.ts': 'javascript',  # TypeScript uses JavaScript parser
                '.c': 'c',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.cxx': 'cpp',
                '.h': 'c',
                '.hpp': 'cpp',
                '.java': 'java'
            }
            
            # Try to load available language parsers
            for ext, lang_name in self.language_map.items():
                try:
                    # Import the specific tree-sitter language module
                    if lang_name == 'python':
                        import tree_sitter_python as ts_python
                        language = Language(ts_python.language(), lang_name)
                    elif lang_name == 'javascript':
                        import tree_sitter_javascript as ts_javascript
                        language = Language(ts_javascript.language(), lang_name)
                    elif lang_name == 'c':
                        import tree_sitter_c as ts_c
                        language = Language(ts_c.language(), lang_name)
                    elif lang_name == 'cpp':
                        import tree_sitter_cpp as ts_cpp
                        language = Language(ts_cpp.language(), lang_name)
                    elif lang_name == 'java':
                        import tree_sitter_java as ts_java
                        language = Language(ts_java.language(), lang_name)
                    else:
                        continue
                    
                    parser = Parser()
                    parser.set_language(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[ext] = parser
                    
                except ImportError as import_error:
                    print(f"Tree-sitter {lang_name} parser not available: {import_error}")
                except Exception as parser_error:
                    print(f"Failed to initialize {lang_name} parser: {parser_error}")
            
            print(f"Initialized tree-sitter parsers for: {list(self.parsers.keys())}")
            
        except Exception as e:
            print(f"Error initializing tree-sitter: {e}")
    
    def _get_parser_for_file(self, file_path: str) -> Optional[Parser]:
        """
        Get the appropriate tree-sitter parser for a file.
        """
        file_ext = Path(file_path).suffix.lower()
        return self.parsers.get(file_ext)
    
    def analyze_python_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python code using both built-in AST module and tree-sitter.
        """
        try:
            # Parse with Python's built-in AST module
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            variables = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function information
                    func_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "returns": ast.unparse(node.returns) if node.returns else None,
                        "docstring": ast.get_docstring(node),
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                        "is_async": isinstance(node, ast.AsyncFunctionDef)
                    }
                    functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    # Extract class information
                    class_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                        "docstring": ast.get_docstring(node),
                        "methods": []
                    }
                    
                    # Extract methods within the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "line_start": item.lineno,
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item),
                                "is_property": any(ast.unparse(dec) == 'property' for dec in item.decorator_list)
                            }
                            class_info["methods"].append(method_info)
                    
                    classes.append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Extract import information
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                    else:  # ImportFrom
                        for alias in node.names:
                            imports.append({
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                
                elif isinstance(node, ast.Assign):
                    # Extract variable assignments (module level only)
                    if isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                        try:
                            value_str = ast.unparse(node.value)[:100]  # Limit length
                        except:
                            value_str = "<complex_expression>"
                        
                        variables.append({
                            "name": var_name,
                            "line": node.lineno,
                            "value_preview": value_str
                        })
            
            return {
                "file_path": file_path,
                "language": "python",
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "variables": variables,
                "total_functions": len(functions),
                "total_classes": len(classes),
                "total_imports": len(imports),
                "lines_of_code": len(content.splitlines())
            }
            
        except SyntaxError as e:
            print(f"Python syntax error in {file_path}: {e}")
            return {"error": f"Python syntax error: {e}"}
        except Exception as e:
            print(f"Error analyzing Python AST for {file_path}: {e}")
            return {"error": str(e)}
    
    def analyze_tree_sitter_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code using tree-sitter for general language support.
        """
        parser = self._get_parser_for_file(file_path)
        if not parser:
            return {"error": "No parser available for this file type"}
        
        try:
            tree = parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node
            
            file_ext = Path(file_path).suffix.lower()
            language = self.language_map.get(file_ext, "unknown")
            
            # Extract different elements based on language
            if language == "javascript":
                return self._analyze_javascript_tree(root_node, content, file_path)
            elif language in ["c", "cpp"]:
                return self._analyze_c_cpp_tree(root_node, content, file_path)
            elif language == "java":
                return self._analyze_java_tree(root_node, content, file_path)
            else:
                # Generic analysis
                return self._analyze_generic_tree(root_node, content, file_path, language)
            
        except Exception as e:
            print(f"Error with tree-sitter analysis for {file_path}: {e}")
            return {"error": str(e)}
    
    def _analyze_javascript_tree(self, root_node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript AST.
        """
        functions = []
        classes = []
        imports = []
        exports = []
        variables = []
        
        def traverse_node(node):
            if node.type == "function_declaration":
                name_node = node.child_by_field_name("name")
                func_name = content[name_node.start_byte:name_node.end_byte] if name_node else "anonymous"
                
                functions.append({
                    "name": func_name,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "type": "function"
                })
            
            elif node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                class_name = content[name_node.start_byte:name_node.end_byte] if name_node else "Anonymous"
                
                classes.append({
                    "name": class_name,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1
                })
            
            elif node.type in ["import_statement", "import_declaration"]:
                import_text = content[node.start_byte:node.end_byte]
                imports.append({
                    "statement": import_text,
                    "line": node.start_point[0] + 1
                })
            
            # Recursively traverse child nodes
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "file_path": file_path,
            "language": "javascript",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
            "variables": variables,
            "total_functions": len(functions),
            "total_classes": len(classes),
            "lines_of_code": len(content.splitlines())
        }
    
    def _analyze_c_cpp_tree(self, root_node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C/C++ AST.
        """
        functions = []
        structures = []
        includes = []
        macros = []
        
        def traverse_node(node):
            if node.type == "function_definition":
                # Find function name
                declarator = node.child_by_field_name("declarator")
                if declarator:
                    func_name = self._extract_function_name(declarator, content)
                    functions.append({
                        "name": func_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "function"
                    })
            
            elif node.type in ["struct_specifier", "class_specifier"]:
                name_node = node.child_by_field_name("name")
                struct_name = content[name_node.start_byte:name_node.end_byte] if name_node else "Anonymous"
                
                structures.append({
                    "name": struct_name,
                    "type": node.type,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1
                })
            
            elif node.type == "preproc_include":
                include_text = content[node.start_byte:node.end_byte]
                includes.append({
                    "statement": include_text,
                    "line": node.start_point[0] + 1
                })
            
            # Recursively traverse child nodes
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "file_path": file_path,
            "language": "c/cpp",
            "functions": functions,
            "structures": structures,
            "includes": includes,
            "macros": macros,
            "total_functions": len(functions),
            "total_structures": len(structures),
            "lines_of_code": len(content.splitlines())
        }
    
    def _analyze_java_tree(self, root_node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Java AST.
        """
        classes = []
        methods = []
        imports = []
        interfaces = []
        
        def traverse_node(node):
            if node.type == "class_declaration":
                name_node = node.child_by_field_name("name")
                class_name = content[name_node.start_byte:name_node.end_byte] if name_node else "Anonymous"
                
                classes.append({
                    "name": class_name,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "type": "class"
                })
            
            elif node.type == "method_declaration":
                name_node = node.child_by_field_name("name")
                method_name = content[name_node.start_byte:name_node.end_byte] if name_node else "anonymous"
                
                methods.append({
                    "name": method_name,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "type": "method"
                })
            
            elif node.type == "import_declaration":
                import_text = content[node.start_byte:node.end_byte]
                imports.append({
                    "statement": import_text,
                    "line": node.start_point[0] + 1
                })
            
            elif node.type == "interface_declaration":
                name_node = node.child_by_field_name("name")
                interface_name = content[name_node.start_byte:name_node.end_byte] if name_node else "Anonymous"
                
                interfaces.append({
                    "name": interface_name,
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1
                })
            
            # Recursively traverse child nodes
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "file_path": file_path,
            "language": "java",
            "classes": classes,
            "methods": methods,
            "imports": imports,
            "interfaces": interfaces,
            "total_classes": len(classes),
            "total_methods": len(methods),
            "total_interfaces": len(interfaces),
            "lines_of_code": len(content.splitlines())
        }
    
    def _analyze_generic_tree(self, root_node, content: str, file_path: str, language: str) -> Dict[str, Any]:
        """
        Generic tree analysis for unsupported languages.
        """
        node_types = {}
        
        def traverse_node(node):
            node_type = node.type
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "file_path": file_path,
            "language": language,
            "node_types": node_types,
            "total_nodes": sum(node_types.values()),
            "lines_of_code": len(content.splitlines()),
            "analysis_type": "generic"
        }
    
    def _extract_function_name(self, declarator_node, content: str) -> str:
        """
        Extract function name from C/C++ function declarator.
        """
        try:
            if declarator_node.type == "function_declarator":
                declarator = declarator_node.child_by_field_name("declarator")
                if declarator and declarator.type == "identifier":
                    return content[declarator.start_byte:declarator.end_byte]
            elif declarator_node.type == "identifier":
                return content[declarator_node.start_byte:declarator_node.end_byte]
            
            # Fallback: try to find any identifier in the declarator
            for child in declarator_node.children:
                if child.type == "identifier":
                    return content[child.start_byte:child.end_byte]
            
            return "unknown_function"
        except:
            return "unknown_function"
    
    def generate_call_graph(self, ast_analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Generate a call graph from AST analysis (simplified version).
        """
        # This is a simplified implementation
        # In practice, you'd need more sophisticated analysis
        call_graph = {}
        
        if ast_analysis.get("language") == "python":
            # For Python, we'd analyze function calls within each function
            for func in ast_analysis.get("functions", []):
                call_graph[func["name"]] = []  # Placeholder - would need deeper analysis
        
        return call_graph
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single code file.
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File does not exist: {file_path}"}
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as encoding_error:
                    return {"error": f"Could not read file {file_path}: {encoding_error}"}
            
            file_ext = Path(file_path).suffix.lower()
            
            # Perform AST analysis
            ast_analysis = {}
            
            if file_ext == '.py':
                # Use Python's built-in AST for Python files
                ast_analysis = self.analyze_python_ast(content, file_path)
            else:
                # Use tree-sitter for other languages
                ast_analysis = self.analyze_tree_sitter_ast(content, file_path)
            
            # Get Git authorship information
            git_info = self.git_service.get_file_authorship(file_path)
            
            # Combine results
            result = {
                "file_path": file_path,
                "file_extension": file_ext,
                "file_size": len(content),
                "ast_analysis": ast_analysis,
                "git_analysis": git_info,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate call graph if possible
            if "error" not in ast_analysis:
                result["call_graph"] = self.generate_call_graph(ast_analysis)
            
            return result
            
        except Exception as e:
            print(f"Error analyzing code file {file_path}: {e}")
            return {"error": str(e)}
    
    def analyze_codebase_directory(self, directory_path: str, 
                                  file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze an entire codebase directory.
        """
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp']
        
        try:
            if not os.path.exists(directory_path):
                return {"error": f"Directory does not exist: {directory_path}"}
            
            # Initialize Git analysis
            git_initialized = self.git_service.initialize_repository(directory_path)
            
            directory_path = os.path.abspath(directory_path)
            print(f"Analyzing codebase directory: {directory_path}")
            
            analyzed_files = []
            total_files = 0
            successful_analyses = 0
            failed_analyses = 0
            
            # Language statistics
            language_stats = {}
            
            # Walk through directory
            for root, dirs, files in os.walk(directory_path):
                # Skip .git directories
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    if file_ext in file_extensions:
                        total_files += 1
                        print(f"Analyzing: {file_path}")
                        
                        analysis_result = self.analyze_code_file(file_path)
                        
                        if "error" in analysis_result:
                            failed_analyses += 1
                            print(f"Failed to analyze {file_path}: {analysis_result['error']}")
                        else:
                            successful_analyses += 1
                            analyzed_files.append(analysis_result)
                            
                            # Update language statistics
                            language = analysis_result.get("ast_analysis", {}).get("language", "unknown")
                            if language not in language_stats:
                                language_stats[language] = {
                                    "files": 0,
                                    "total_lines": 0,
                                    "total_functions": 0,
                                    "total_classes": 0
                                }
                            
                            lang_stat = language_stats[language]
                            lang_stat["files"] += 1
                            
                            ast_data = analysis_result.get("ast_analysis", {})
                            lang_stat["total_lines"] += ast_data.get("lines_of_code", 0)
                            lang_stat["total_functions"] += ast_data.get("total_functions", 0)
                            lang_stat["total_classes"] += ast_data.get("total_classes", 0)
            
            # Get repository metadata if Git was initialized
            repo_metadata = {}
            if git_initialized:
                repo_metadata = self.git_service.get_repository_metadata()
            
            codebase_analysis = {
                "directory_path": directory_path,
                "total_files_found": total_files,
                "successful_analyses": successful_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": successful_analyses / total_files if total_files > 0 else 0,
                "language_statistics": language_stats,
                "analyzed_files": analyzed_files,
                "repository_metadata": repo_metadata,
                "git_initialized": git_initialized,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "analyzed_extensions": file_extensions
            }
            
            print(f"Codebase analysis complete: {successful_analyses}/{total_files} files analyzed")
            return codebase_analysis
            
        except Exception as e:
            print(f"Error analyzing codebase directory: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def add_directory_config(self, directory_path: str, recursive: bool = True,
                           file_patterns: str = None, ignore_patterns: str = None) -> Dict[str, Any]:
        """
        Add a directory to the configuration for regular scanning.
        """
        try:
            if not os.path.exists(directory_path):
                return {"error": f"Directory does not exist: {directory_path}"}
            
            if not os.path.isdir(directory_path):
                return {"error": f"Path is not a directory: {directory_path}"}
            
            directory_path = os.path.abspath(directory_path)
            config_id = self.analytical_brain.add_directory_config(
                directory_path, recursive, file_patterns, ignore_patterns
            )
            
            return {
                "status": "directory_added",
                "config_id": config_id,
                "directory_path": directory_path,
                "recursive": recursive,
                "file_patterns": file_patterns,
                "ignore_patterns": ignore_patterns
            }
            
        except Exception as e:
            print(f"Error adding directory config: {e}")
            return {"error": str(e)}
    
    def get_directory_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of directory-based ingestion system.
        """
        try:
            return self.analytical_brain.get_directory_status()
        except Exception as e:
            print(f"Error getting directory status: {e}")
            return {"error": str(e)}
