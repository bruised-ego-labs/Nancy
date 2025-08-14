from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain
import os
import hashlib
import spacy
import re
import pandas as pd
import json
from typing import Dict, List, Any, Optional

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
        
        # Try to use LLM for enhanced project story extraction if available
        try:
            from .llm_client import LLMClient
            llm_client = LLMClient(preferred_llm="gemini")
            
            # Extract enhanced relationships using new prompts
            text_chunk = text[:3000] if len(text) > 3000 else text
            relationships = llm_client.extract_document_relationships(text_chunk, current_filename)
            
            # Extract comprehensive project story elements
            story_elements = llm_client.extract_project_story_elements(text, current_filename)
            
            # Process enhanced relationships
            for rel in relationships:
                self.graph_brain.add_relationship(
                    source_node_label=rel.get("source_type", "Document"),
                    source_node_name=rel["source"],
                    relationship_type=rel["relationship"],
                    target_node_label=rel.get("target_type", "Concept"),
                    target_node_name=rel["target"],
                    context=rel.get("context", f"LLM-extracted from {current_filename}")
                )
            
            # Process project story elements
            self._process_story_elements(story_elements, current_filename)
                
        except Exception as e:
            print(f"LLM project story extraction failed: {e}")
            # Continue without LLM enhancement

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

    def ingest_file(self, filename: str, content: bytes, author: str = "Unknown"):
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

        # 2. Relational Brain: Create a document node and link the author
        self.graph_brain.add_document_node(filename=filename, file_type=file_type)
        self.graph_brain.add_author_relationship(filename=filename, author_name=author)

        # 3. Vector Brain & Entity Extraction
        # Define a list of text-based file extensions to process
        text_based_extensions = ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json']
        spreadsheet_extensions = ['.xlsx', '.xls', '.csv']
        
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
