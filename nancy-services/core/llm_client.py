"""
LLM Client for Nancy's intelligent query orchestration and response synthesis.
Supports Claude and Gemini APIs for various AI tasks.
"""

import os
import json
import requests
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
        system_prompt = """You are an intelligent query analyzer for Nancy, a three-brain AI system with:
1. VectorBrain: Semantic search across document content
2. AnalyticalBrain: Metadata queries (dates, file types, sizes, authors)
3. RelationalBrain: Relationships between documents, people, and concepts

Analyze the user query and return a JSON response with this structure:
{
    "query_type": "semantic|author_attribution|metadata_filter|relationship_discovery|hybrid_complex|temporal_analysis|cross_reference",
    "semantic_terms": ["key", "search", "terms"],
    "entities": ["people", "documents", "concepts"],
    "time_constraints": {"start_date": "2024-03-01", "end_date": "2024-03-31"} or null,
    "metadata_filters": {"file_type": ".txt", "author": "Sarah Chen"} or null,
    "relationship_targets": ["document names", "person names"] or null,
    "confidence": 0.95,
    "reasoning": "Explanation of why this classification was chosen"
}

Examples:
- "What are the power requirements?" → semantic search
- "Who wrote the thermal analysis?" → author_attribution 
- "Show me documents from March" → metadata_filter with time constraints
- "What thermal issues affected electrical design?" → relationship_discovery
- "Find documents by Sarah Chen about power from last month" → hybrid_complex"""

        user_prompt = f"Analyze this query: '{query}'"
        
        if context:
            user_prompt += f"\nContext: {json.dumps(context, indent=2)}"
        
        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_query_intent(response)
        except Exception as e:
            print(f"Error analyzing query intent: {e}")
            # Fallback to semantic search
            return QueryIntent(
                query_type=QueryType.SEMANTIC,
                semantic_terms=query.split(),
                entities=[],
                time_constraints=None,
                metadata_filters=None,
                relationship_targets=None,
                confidence=0.3,
                reasoning="LLM analysis failed, defaulting to semantic search"
            )
    
    def synthesize_response(self, query: str, raw_results: Dict, query_intent: QueryIntent) -> str:
        """
        Use LLM to synthesize raw results into a natural language response
        """
        system_prompt = """You are Nancy, an intelligent AI assistant that helps engineering teams find and understand project information. You have access to three specialized systems:

1. Vector search results (semantic similarity)
2. Document metadata (authors, dates, file types)
3. Knowledge graph relationships (who created what, document connections)

Your job is to synthesize the raw technical results into a clear, helpful response that directly answers the user's question. Focus on:
- Answering the specific question asked
- Highlighting key findings and relationships
- Providing context and background when relevant
- Being concise but comprehensive
- Citing specific documents and authors when available

Format your response in a conversational, professional tone suitable for engineering teams."""

        user_prompt = f"""Original Query: "{query}"
Query Intent: {query_intent.query_type.value} (confidence: {query_intent.confidence})

Raw Results:
{json.dumps(raw_results, indent=2)}

Please synthesize this into a natural language response that directly answers the user's question."""

        try:
            return self._call_llm(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error synthesizing response: {e}")
            # Fallback to basic response
            return self._create_fallback_response(raw_results)
    
    def extract_document_relationships(self, text: str, document_name: str) -> List[Dict[str, str]]:
        """
        Use LLM to extract relationships from document text
        """
        system_prompt = """You are analyzing engineering documents to extract relationships between:
- Documents (references, dependencies, relates to)
- People (mentions, collaborations, decisions)
- Concepts (affects, influences, constrains)

Return a JSON array of relationships in this format:
[
    {
        "source": "current document or entity name",
        "relationship": "REFERENCES|MENTIONS|AFFECTS|INFLUENCES|CONSTRAINS|COLLABORATES_WITH|DECIDES_ON|DEPENDS_ON",
        "target": "target document, person, or concept",
        "context": "brief explanation of the relationship"
    }
]

Focus on engineering-relevant relationships like:
- Technical dependencies
- Decision influences
- Cross-team collaborations
- Document references
- Constraint relationships"""

        user_prompt = f"""Document: {document_name}

Text excerpt:
{text[:3000]}  # Limit text to avoid token limits

Extract relationships from this text."""

        try:
            response = self._call_llm(system_prompt, user_prompt)
            return self._parse_relationships(response)
        except Exception as e:
            print(f"Error extracting relationships: {e}")
            return []
    
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call the preferred LLM with comprehensive fallback support
        """
        # Try local models first (preferred for privacy and cost)
        if self.preferred_llm == "local_gemma" or self.preferred_llm == "ollama":
            try:
                return self._call_local_ollama(system_prompt, user_prompt)
            except Exception as e:
                print(f"Local Ollama failed ({e}), trying transformers fallback...")
                try:
                    return self._call_local_transformers(system_prompt, user_prompt)
                except Exception as e2:
                    print(f"Local transformers failed ({e2}), trying cloud APIs...")
        
        elif self.preferred_llm == "transformers":
            try:
                return self._call_local_transformers(system_prompt, user_prompt)
            except Exception as e:
                print(f"Local transformers failed ({e}), trying Ollama fallback...")
                try:
                    return self._call_local_ollama(system_prompt, user_prompt)
                except Exception as e2:
                    print(f"Ollama failed ({e2}), trying cloud APIs...")
        
        # Try cloud APIs as fallback
        if self.claude_api_key:
            try:
                return self._call_claude(system_prompt, user_prompt)
            except Exception as e:
                print(f"Claude API failed ({e})")
        
        if self.gemini_api_key:
            try:
                return self._call_gemini(system_prompt, user_prompt)
            except Exception as e:
                print(f"Gemini API failed ({e})")
        
        # Final fallback to mock response
        print("All LLM options failed, using mock response")
        return self._mock_llm_response(system_prompt, user_prompt)
    
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_api_key}"
        
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
        Parse LLM response into QueryIntent object
        """
        try:
            data = json.loads(response)
            return QueryIntent(
                query_type=QueryType(data["query_type"]),
                semantic_terms=data.get("semantic_terms", []),
                entities=data.get("entities", []),
                time_constraints=data.get("time_constraints"),
                metadata_filters=data.get("metadata_filters"),
                relationship_targets=data.get("relationship_targets"),
                confidence=data.get("confidence", 0.5),
                reasoning=data.get("reasoning", "No reasoning provided")
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing query intent: {e}")
            # Return fallback
            return QueryIntent(
                query_type=QueryType.SEMANTIC,
                semantic_terms=response.split(),
                entities=[],
                time_constraints=None,
                metadata_filters=None,
                relationship_targets=None,
                confidence=0.3,
                reasoning="Failed to parse LLM response"
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