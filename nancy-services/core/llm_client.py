"""
LLM Client for Nancy's intelligent query orchestration and response synthesis.
Supports Claude and Gemini APIs for various AI tasks.
"""

import os
import json
import requests
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to import local LLM libraries
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class QueryType(Enum):
    """Types of queries the system can handle"""
    SEMANTIC = "semantic"  # Pure vector search
    AUTHOR_ATTRIBUTION = "author_attribution"  # Who created/wrote something
    METADATA_FILTER = "metadata_filter"  # Filter by date, type, size, etc.
    RELATIONSHIP_DISCOVERY = "relationship_discovery"  # Find connections between documents
    HYBRID_COMPLEX = "hybrid_complex"  # Requires multiple brains
    TEMPORAL_ANALYSIS = "temporal_analysis"  # Time-based queries
    CROSS_REFERENCE = "cross_reference"  # Documents that reference each other

@dataclass
class QueryIntent:
    """Parsed query intent from LLM analysis"""
    query_type: QueryType
    semantic_terms: List[str]
    entities: List[str]
    time_constraints: Optional[Dict[str, str]]
    metadata_filters: Optional[Dict[str, Any]]
    relationship_targets: Optional[List[str]]
    confidence: float
    reasoning: str

class LLMClient:
    """Client for interacting with LLM APIs (Claude, Gemini) for query intelligence"""
    
    def __init__(self, preferred_llm: str = "local_gemma"):
        self.preferred_llm = preferred_llm
        self.claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Local LLM configuration
        self.local_model_name = os.getenv("LOCAL_MODEL_NAME", "gemma2:2b")
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Initialize local model if using transformers directly
        self.local_model = None
        self.local_tokenizer = None
        
        print(f"LLM Client initialized with {preferred_llm}")
        print(f"Claude API key available: {'Yes' if self.claude_api_key else 'No'}")
        print(f"Gemini API key available: {'Yes' if self.gemini_api_key else 'No'}")
        print(f"Ollama available: {'Yes' if OLLAMA_AVAILABLE else 'No'}")
        print(f"Transformers available: {'Yes' if TRANSFORMERS_AVAILABLE else 'No'}")
        print(f"Local model: {self.local_model_name}")
    
    def analyze_query_intent(self, query: str, context: Optional[Dict] = None) -> QueryIntent:
        """
        Use LLM to analyze query intent and determine which brains to use
        """
        system_prompt = """You are a query analyzer for Nancy. You must return ONLY valid JSON, no other text.

CRITICAL: Your response must be EXACTLY this JSON format with NO additional text before or after:

{
    "query_type": "semantic",
    "semantic_terms": ["term1", "term2"],
    "entities": ["entity1"],
    "time_constraints": null,
    "metadata_filters": null,
    "relationship_targets": null,
    "confidence": 0.8,
    "reasoning": "Brief explanation"
}

Query Types:
- semantic: General content search
- author_attribution: "Who wrote/created"
- metadata_filter: Date/file type filters  
- relationship_discovery: "How are X and Y related"
- hybrid_complex: Multiple brains needed
- temporal_analysis: Time-based queries
- cross_reference: Document relationships

Rules:
1. ONLY return the JSON object
2. Use double quotes for all strings
3. Use null (not "null") for empty values
4. Keep reasoning under 50 characters
5. No text before or after the JSON"""

        user_prompt = f"Analyze this query: '{query}'"
        
        if context:
            user_prompt += f"\nContext: {json.dumps(context, indent=2)}"
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_query_intent(response)
        except Exception as e:
            print(f"Error analyzing query intent: {e}")
            # Raise the error instead of silently falling back
            raise RuntimeError(f"Query intent analysis failed: {e}. Nancy requires functional LLM for intelligent query processing.")
    
    def synthesize_response(self, query: str, raw_results: Dict, query_intent: QueryIntent) -> str:
        """
        Use LLM to synthesize raw results into a natural language response
        """
        system_prompt = """You are Nancy, an AI assistant for engineering teams. Provide a clear, direct answer to the user's question based on the search results.

IMPORTANT: Write a natural, conversational response. Do NOT try to format as JSON.

Guidelines:
- Answer the question directly
- Mention specific documents and authors when available
- Keep response under 200 words
- Use professional but friendly tone
- Focus on the most relevant information"""

        user_prompt = f"""Original Query: "{query}"
Query Intent: {query_intent.query_type.value} (confidence: {query_intent.confidence})

Raw Results:
{json.dumps(raw_results, indent=2)}

Please synthesize this into a natural language response that directly answers the user's question."""

        try:
            return self._call_llm(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error synthesizing response: {e}")
            # Raise the error instead of silently falling back
            raise RuntimeError(f"Response synthesis failed: {e}. Nancy requires functional LLM for intelligent response generation.")
    
    def extract_document_relationships(self, text: str, document_name: str) -> List[Dict[str, str]]:
        """
        Use LLM to extract rich project story relationships from document text
        """
        system_prompt = """You are analyzing project documents to build a comprehensive knowledge graph that captures the project's story. Extract relationships between:

**Primary Entities:**
- People (team members, stakeholders, decision makers)
- Documents (specs, designs, reports, meeting notes)
- Decisions (architectural choices, feature decisions, technical choices)
- Features (functionality, components, systems)
- Concepts (technologies, constraints, requirements)
- Meetings (design reviews, planning sessions, standups)
- Eras/Phases (project phases, sprints, milestones)

**Relationship Types:**
- AUTHORED (person created document)
- MADE (person made decision)
- ATTENDED (person attended meeting)
- OWNS (person owns feature/component)
- INFLUENCED_BY (decision influenced by document/meeting)
- LED_TO (decision led to feature/document)
- RESULTED_IN (meeting resulted in decision)
- CREATED_IN (document/decision created in era)
- REFERENCES (document references another)
- DEPENDS_ON (component depends on another)
- AFFECTS (change affects another component)
- INFLUENCES (person/decision influences another)
- CONSTRAINS (requirement constrains design)
- COLLABORATES_WITH (person collaborates with another)

Return a JSON array in this format:
[
    {
        "source": "entity name",
        "source_type": "Person|Document|Decision|Feature|Concept|Meeting|Era",
        "relationship": "relationship type from above",
        "target": "target entity name", 
        "target_type": "Person|Document|Decision|Feature|Concept|Meeting|Era",
        "context": "brief explanation with specific details"
    }
]

**Focus on capturing the project story:**
- Who made what decisions and why?
- What meetings led to decisions?
- Which documents influenced decisions?
- How do team members collaborate?
- What features resulted from decisions?
- What constraints affect the project?
- What era/phase is this from?

**Extract specific mentions of:**
- Decision points ("decided to", "chosen", "selected")
- Collaboration ("worked with", "coordinated with", "reviewed by")
- Dependencies ("requires", "depends on", "affects")
- Meeting outcomes ("meeting resulted in", "discussed in")
- Timeline context ("during", "phase", "sprint", "quarter")"""

        user_prompt = f"""Document: {document_name}

Text excerpt:
{text[:3000]}  # Limit text to avoid token limits

Extract relationships from this text."""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_enhanced_relationships(response)
        except Exception as e:
            print(f"Error extracting relationships: {e}")
            return []
    
    def extract_project_story_elements(self, text: str, document_name: str) -> Dict[str, List[Dict]]:
        """
        Extract comprehensive project story elements: decisions, meetings, features, eras
        """
        system_prompt = """You are analyzing a project document to extract key story elements that build the project's knowledge graph. 

Identify and extract:

1. **Decisions Made** - Look for:
   - "decided to", "chosen", "selected", "approved"
   - Architectural choices, technology selections, process decisions
   - Who made the decision and any context

2. **Meetings Referenced** - Look for:
   - "meeting", "review", "discussion", "standup", "planning session"
   - Who attended, what was discussed, outcomes

3. **Features/Components** - Look for:
   - System components, features, functionality being discussed
   - Who owns/leads each feature

4. **Project Eras/Phases** - Look for:
   - Time periods: "Q1", "Sprint 3", "Phase 1", "Initial Design"
   - Project milestones, phases, development stages

5. **Key Collaborations** - Look for:
   - Cross-team work, coordination, dependencies
   - "worked with", "coordinated with", "input from"

Return JSON in this exact format:
{
    "decisions": [
        {
            "name": "decision name",
            "maker": "person who made it",
            "context": "why this decision was made",
            "era": "time period if mentioned"
        }
    ],
    "meetings": [
        {
            "name": "meeting name/description", 
            "attendees": ["person1", "person2"],
            "outcomes": ["decision1", "decision2"],
            "era": "time period if mentioned"
        }
    ],
    "features": [
        {
            "name": "feature/component name",
            "owner": "person responsible",
            "influenced_by": ["decision1", "decision2"],
            "era": "time period if mentioned"
        }
    ],
    "eras": [
        {
            "name": "era/phase name",
            "description": "what this phase was about",
            "key_activities": ["activity1", "activity2"]
        }
    ],
    "collaborations": [
        {
            "person1": "first person",
            "person2": "second person", 
            "type": "what kind of collaboration",
            "context": "specific details"
        }
    ]
}"""

        user_prompt = f"""Document: {document_name}

Full text:
{text[:4000]}

Extract the project story elements from this document."""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_project_story(response)
        except Exception as e:
            print(f"Error extracting project story: {e}")
            return {"decisions": [], "meetings": [], "features": [], "eras": [], "collaborations": []}
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the preferred LLM with clear error reporting - NO FALLBACKS for security
        """
        if self.preferred_llm == "gemini":
            try:
                return self._call_gemini(system_prompt, user_prompt)
            except Exception as e:
                raise RuntimeError(f"Gemini API failed: {e}. Nancy requires a functional LLM for query intelligence.")
        
        elif self.preferred_llm == "claude":
            try:
                return self._call_claude(system_prompt, user_prompt)
            except Exception as e:
                raise RuntimeError(f"Claude API failed: {e}. Nancy requires a functional LLM for query intelligence.")
        
        elif self.preferred_llm == "local_gemma" or self.preferred_llm == "ollama":
            try:
                return self._call_local_ollama(system_prompt, user_prompt)
            except Exception as e:
                raise RuntimeError(f"Local LLM (Ollama) failed: {e}. Nancy requires a functional local LLM for query intelligence.")
        
        elif self.preferred_llm == "transformers":
            try:
                return self._call_local_transformers(system_prompt, user_prompt)
            except Exception as e:
                raise RuntimeError(f"Local LLM (Transformers) failed: {e}. Nancy requires a functional local LLM for query intelligence.")
        
        else:
            raise RuntimeError(f"Unsupported LLM preference: {self.preferred_llm}. Supported options: gemini, claude, local_gemma, ollama, transformers")
    
    def _call_claude(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Claude API
        """
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.claude_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": f"{system_prompt}\n\n{user_prompt}"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Log token usage
        usage = result.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        print(f"Claude API Call - Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total: {input_tokens + output_tokens}")
        
        return result["content"][0]["text"]
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Gemini API
        """
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3n-e4b-it:generateContent?key={self.gemini_api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
            }]
        }
        
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # Log token usage for Gemini
        usage = result.get("usageMetadata", {})
        input_tokens = usage.get("promptTokenCount", 0)
        output_tokens = usage.get("candidatesTokenCount", 0)
        print(f"Gemini API Call - Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total: {input_tokens + output_tokens}")
        
        return result["candidates"][0]["content"]["parts"][0]["text"]
    
    def _mock_llm_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Mock LLM response for development/testing
        """
        print(f"Mock LLM Call - No tokens used (API keys not configured)")
        print(f"System prompt length: {len(system_prompt)} chars, User prompt length: {len(user_prompt)} chars")
        if "analyze query intent" in system_prompt.lower():
            # Mock query intent analysis
            if "who" in user_prompt.lower():
                return json.dumps({
                    "query_type": "author_attribution",
                    "semantic_terms": user_prompt.split()[2:],
                    "entities": [],
                    "time_constraints": None,
                    "metadata_filters": None,
                    "relationship_targets": None,
                    "confidence": 0.8,
                    "reasoning": "Query asks 'who' - likely author attribution"
                })
            elif "from" in user_prompt.lower() and ("march" in user_prompt.lower() or "month" in user_prompt.lower()):
                return json.dumps({
                    "query_type": "metadata_filter",
                    "semantic_terms": [w for w in user_prompt.split() if w.lower() not in ["from", "march", "last", "month"]],
                    "entities": [],
                    "time_constraints": {"start_date": "2024-03-01", "end_date": "2024-03-31"},
                    "metadata_filters": None,
                    "relationship_targets": None,
                    "confidence": 0.9,
                    "reasoning": "Query includes temporal constraints"
                })
            elif "affected" in user_prompt.lower() or "related" in user_prompt.lower():
                return json.dumps({
                    "query_type": "relationship_discovery",
                    "semantic_terms": user_prompt.split(),
                    "entities": [],
                    "time_constraints": None,
                    "metadata_filters": None,
                    "relationship_targets": ["thermal", "electrical"],
                    "confidence": 0.85,
                    "reasoning": "Query asks about relationships between concepts"
                })
            else:
                return json.dumps({
                    "query_type": "semantic",
                    "semantic_terms": user_prompt.split(),
                    "entities": [],
                    "time_constraints": None,
                    "metadata_filters": None,
                    "relationship_targets": None,
                    "confidence": 0.7,
                    "reasoning": "Default to semantic search"
                })
        
        elif "synthesize" in system_prompt.lower():
            return f"Based on the search results, here's what I found regarding your query: {user_prompt[:100]}... [This is a mock response - configure LLM API keys for full functionality]"
        
        elif "extract relationships" in system_prompt.lower():
            return json.dumps([
                {
                    "source": "current_document",
                    "relationship": "REFERENCES",
                    "target": "related_document",
                    "context": "Mock relationship extraction"
                }
            ])
        
        return "Mock LLM response - configure API keys for full functionality"
    
    def _call_local_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call local Ollama server with Gemma model
        """
        if not OLLAMA_AVAILABLE:
            raise Exception("Ollama library not available")
        
        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:"
        
        # Estimate token usage (rough approximation: 1 token ≈ 4 characters)
        input_tokens = len(full_prompt) // 4
        
        # Configure Ollama client for containerized service
        client = ollama.Client(host=self.ollama_host)
        
        response = client.generate(
            model=self.local_model_name,
            prompt=full_prompt,
            options={'temperature': 0.1, 'top_p': 0.9}
        )
        
        output_text = response['response']
        output_tokens = len(output_text) // 4
        
        print(f"Local Ollama ({self.local_model_name}) - Input tokens: ~{input_tokens}, Output tokens: ~{output_tokens}, Total: ~{input_tokens + output_tokens}")
        
        return output_text
    
    def _call_local_transformers(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call local Transformers model (Gemma) directly
        """
        if not TRANSFORMERS_AVAILABLE:
            raise Exception("Transformers library not available")
        
        # Initialize model if not already done
        if self.local_model is None:
            model_name = "google/gemma-2-2b-it"  # or gemma-2-9b-it for better quality
            print(f"Loading local model: {model_name}")
            
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
        
        # Format prompt for Gemma
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        formatted_prompt = self.local_tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        
        # Tokenize and generate
        inputs = self.local_tokenizer(formatted_prompt, return_tensors="pt", truncate=True, max_length=2048)
        input_tokens = inputs['input_ids'].shape[1]
        
        with torch.no_grad():
            outputs = self.local_model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.1,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.local_tokenizer.eos_token_id
            )
        
        # Decode response
        response = self.local_tokenizer.decode(outputs[0][input_tokens:], skip_special_tokens=True)
        output_tokens = len(outputs[0]) - input_tokens
        
        print(f"Local Transformers (gemma-2-2b-it) - Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total: {input_tokens + output_tokens}")
        
        return response.strip()
    
    def _parse_query_intent(self, response: str) -> QueryIntent:
        """
        Parse LLM response into QueryIntent object with robust error handling
        """
        print(f"Raw LLM response: {response[:200]}...")  # Debug log
        
        # Try direct JSON parsing first
        try:
            data = json.loads(response)
            return self._create_query_intent_from_data(data)
        except json.JSONDecodeError as e:
            print(f"Initial JSON parse failed: {e}")
            
        # Strategy 2: Extract JSON from response text
        cleaned_response = self._extract_json_from_response(response)
        if cleaned_response:
            try:
                data = json.loads(cleaned_response)
                return self._create_query_intent_from_data(data)
            except json.JSONDecodeError as e:
                print(f"Cleaned JSON parse failed: {e}")
        
        # Strategy 3: Try to fix common JSON issues
        fixed_response = self._fix_common_json_issues(response)
        if fixed_response:
            try:
                data = json.loads(fixed_response)
                return self._create_query_intent_from_data(data)
            except json.JSONDecodeError as e:
                print(f"Fixed JSON parse failed: {e}")
        
        # Strategy 4: Re-prompt for better formatting
        print("Attempting re-prompt for better JSON formatting...")
        try:
            retry_response = self._retry_json_prompt(response)
            data = json.loads(retry_response)
            return self._create_query_intent_from_data(data)
        except Exception as e:
            print(f"Re-prompt failed: {e}")
        
        # Final fallback: Create reasonable intent from text analysis
        print("Using text analysis fallback for query intent")
        return self._create_fallback_intent(response)
    
    def _create_query_intent_from_data(self, data: Dict) -> QueryIntent:
        """Create QueryIntent from parsed JSON data"""
        return QueryIntent(
            query_type=QueryType(data.get("query_type", "semantic")),
            semantic_terms=data.get("semantic_terms", []),
            entities=data.get("entities", []),
            time_constraints=data.get("time_constraints"),
            metadata_filters=data.get("metadata_filters"),
            relationship_targets=data.get("relationship_targets"),
            confidence=data.get("confidence", 0.5),
            reasoning=data.get("reasoning", "No reasoning provided")
        )
    
    def _extract_json_from_response(self, response: str) -> Optional[str]:
        """Extract JSON from response text that may have extra content"""
        import re
        
        # Look for JSON object in the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        # Look for JSON array
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return None
    
    def _fix_common_json_issues(self, response: str) -> Optional[str]:
        """Fix common JSON formatting issues in LLM responses"""
        try:
            # Remove common prefixes/suffixes
            cleaned = response.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            # Remove "Here's the JSON:" type prefixes
            import re
            cleaned = re.sub(r'^.*?(?=\{)', '', cleaned, flags=re.DOTALL)
            cleaned = cleaned.strip()
            
            # Fix single quotes to double quotes
            cleaned = cleaned.replace("'", '"')
            
            # Fix Python None/True/False to JSON null/true/false
            cleaned = re.sub(r'\bNone\b', 'null', cleaned)
            cleaned = re.sub(r'\bTrue\b', 'true', cleaned)
            cleaned = re.sub(r'\bFalse\b', 'false', cleaned)
            
            return cleaned
        except Exception:
            return None
    
    def _retry_json_prompt(self, original_response: str) -> str:
        """Re-prompt the LLM specifically for JSON formatting"""
        retry_prompt = f"""The previous response was not valid JSON: "{original_response[:100]}..."

Please return ONLY this exact JSON structure with no other text:
{{
    "query_type": "semantic",
    "semantic_terms": [],
    "entities": [],
    "time_constraints": null,
    "metadata_filters": null,
    "relationship_targets": null,
    "confidence": 0.7,
    "reasoning": "Retry formatting"
}}

Replace the values appropriately but keep the exact structure."""
        
        return self._call_llm("Return only valid JSON, no other text.", retry_prompt)
    
    def _create_fallback_intent(self, response: str) -> QueryIntent:
        """Create a reasonable QueryIntent when JSON parsing completely fails"""
        response_lower = response.lower()
        
        # Basic heuristics for query type
        if any(word in response_lower for word in ['who', 'author', 'wrote', 'created']):
            query_type = QueryType.AUTHOR_ATTRIBUTION
        elif any(word in response_lower for word in ['when', 'date', 'time', 'recent']):
            query_type = QueryType.TEMPORAL_ANALYSIS
        elif any(word in response_lower for word in ['relationship', 'related', 'connected', 'affect']):
            query_type = QueryType.RELATIONSHIP_DISCOVERY
        else:
            query_type = QueryType.SEMANTIC
        
        # Extract potential terms
        words = response.split()
        semantic_terms = [w for w in words if len(w) > 3 and w.isalnum()][:5]
        
        return QueryIntent(
            query_type=query_type,
            semantic_terms=semantic_terms,
            entities=[],
            time_constraints=None,
            metadata_filters=None,
            relationship_targets=None,
            confidence=0.4,
            reasoning="Fallback parsing - JSON format failed"
        )
    
    def _parse_relationships(self, response: str) -> List[Dict[str, str]]:
        """
        Parse relationship extraction response
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Error parsing relationships: {response}")
            return []
    
    def _parse_enhanced_relationships(self, response: str) -> List[Dict[str, str]]:
        """
        Parse enhanced relationship extraction response with entity types
        """
        try:
            relationships = json.loads(response)
            # Convert enhanced format to compatible format for existing code
            converted = []
            for rel in relationships:
                converted.append({
                    "source": rel.get("source", ""),
                    "relationship": rel.get("relationship", "MENTIONS"),
                    "target": rel.get("target", ""),
                    "context": rel.get("context", ""),
                    "source_type": rel.get("source_type", "Unknown"),
                    "target_type": rel.get("target_type", "Unknown")
                })
            return converted
        except json.JSONDecodeError:
            print(f"Error parsing enhanced relationships: {response}")
            return []
    
    def _parse_project_story(self, response: str) -> Dict[str, List[Dict]]:
        """
        Parse project story extraction response
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            print(f"Error parsing project story: {response}")
            return {"decisions": [], "meetings": [], "features": [], "eras": [], "collaborations": []}
    
    def _create_fallback_response(self, raw_results: Dict) -> str:
        """
        Create a basic response when LLM synthesis fails
        """
        results = raw_results.get("results", [])
        if not results:
            return "I couldn't find any relevant documents for your query."
        
        response_parts = []
        response_parts.append(f"I found {len(results)} relevant result(s):")
        
        for i, result in enumerate(results[:3], 1):
            doc_name = "Unknown document"
            author = "Unknown author"
            
            if result.get("document_metadata"):
                doc_name = result["document_metadata"].get("filename", doc_name)
            
            if result.get("author"):
                author = result["author"]
            
            text_snippet = result.get("text", "")[:100] + "..." if result.get("text") else ""
            
            response_parts.append(f"{i}. {doc_name} by {author}: {text_snippet}")
        
        if len(results) > 3:
            response_parts.append(f"... and {len(results) - 3} more results.")
        
        return "\n".join(response_parts)