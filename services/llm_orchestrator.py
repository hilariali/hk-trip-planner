"""LLM Orchestrator for HK Travel Planner using Akash Network."""

import openai
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time

from config import get_config, LLMConfig

@dataclass
class LLMRequest:
    """Structure for LLM requests."""
    user_message: str
    context: Dict[str, Any]
    system_prompt: str
    response_format: str = "text"  # "text" or "json"
    max_tokens: int = 2000

@dataclass
class LLMResponse:
    """Structure for LLM responses."""
    content: str
    success: bool
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    raw_response: Optional[Dict] = None

class LLMOrchestrator:
    """Orchestrates LLM interactions using Akash Network with DeepSeek model."""
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM orchestrator."""
        self.config = config or get_config().llm
        self.client = None
        self.logger = logging.getLogger(__name__)
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the OpenAI client for Akash Network."""
        try:
            self.client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url
            )
            self.logger.info("LLM client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        return self.client is not None
    
    def process_message(self, request: LLMRequest) -> LLMResponse:
        """Process a message through the LLM."""
        if not self.is_available():
            return LLMResponse(
                content="I'm sorry, but the AI service is currently unavailable. Please try again later.",
                success=False,
                error_message="LLM client not initialized"
            )
        
        try:
            start_time = time.time()
            
            # Prepare messages
            messages = [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.user_message}
            ]
            
            # Add context if available
            if request.context.get("conversation_history"):
                # Add recent conversation history
                for msg in request.context["conversation_history"][-5:]:  # Last 5 messages
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # Make the API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=self.config.temperature,
                timeout=self.config.timeout
            )
            
            response_time = time.time() - start_time
            
            # Extract response content
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
            
            # Parse JSON if requested
            if request.response_format == "json":
                try:
                    # Try to extract JSON from the response
                    json_content = self._extract_json(content)
                    if json_content:
                        content = json.dumps(json_content, indent=2)
                except Exception as e:
                    self.logger.warning(f"Failed to parse JSON response: {e}")
            
            self.logger.info(f"LLM response generated in {response_time:.2f}s, tokens: {tokens_used}")
            
            return LLMResponse(
                content=content,
                success=True,
                tokens_used=tokens_used,
                response_time=response_time,
                raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
            )
            
        except openai.APITimeoutError:
            return LLMResponse(
                content="The request timed out. Please try again with a shorter message.",
                success=False,
                error_message="API timeout"
            )
        except openai.RateLimitError:
            return LLMResponse(
                content="I'm currently handling many requests. Please wait a moment and try again.",
                success=False,
                error_message="Rate limit exceeded"
            )
        except openai.APIError as e:
            self.logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content="I encountered an error while processing your request. Please try again.",
                success=False,
                error_message=f"API error: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error in LLM processing: {e}")
            return LLMResponse(
                content="An unexpected error occurred. Please try again.",
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _extract_json(self, content: str) -> Optional[Dict]:
        """Extract JSON from LLM response content."""
        # Try to find JSON in the response
        import re
        
        # Look for JSON blocks
        json_pattern = r'```json\s*(.*?)\s*```'
        json_match = re.search(json_pattern, content, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to parse the entire content as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON-like structures
        brace_pattern = r'\{.*\}'
        brace_match = re.search(brace_pattern, content, re.DOTALL)
        
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass
        
        return None
    
    def generate_itinerary(self, user_preferences: Dict[str, Any], context: Dict[str, Any]) -> LLMResponse:
        """Generate a travel itinerary based on user preferences."""
        system_prompt = self._get_itinerary_system_prompt()
        
        user_message = self._format_itinerary_request(user_preferences, context)
        
        request = LLMRequest(
            user_message=user_message,
            context=context,
            system_prompt=system_prompt,
            response_format="json",
            max_tokens=3000
        )
        
        return self.process_message(request)
    
    def _get_itinerary_system_prompt(self) -> str:
        """Get the system prompt for itinerary generation."""
        return """You are an expert Hong Kong travel planner specializing in accessible tourism for families and seniors. 

Your expertise includes:
- Accessibility features of Hong Kong attractions, restaurants, and transportation
- Mobility considerations (wheelchairs, elevators, step-free access)
- Dietary accommodations (soft meals, vegetarian, halal, allergies)
- Budget-conscious planning with senior and child discounts
- Safe, comfortable itineraries with appropriate pacing

When generating itineraries:
1. Prioritize accessibility and safety
2. Limit to 2-3 venues per day to prevent fatigue
3. Include detailed accessibility information
4. Provide cost estimates with available discounts
5. Consider weather and seasonal factors
6. Explain your reasoning for each recommendation

Respond with detailed, practical advice that addresses the specific needs mentioned by the user."""
    
    def _format_itinerary_request(self, preferences: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Format user preferences into a clear request for the LLM."""
        request_parts = ["Please create a Hong Kong travel itinerary with the following requirements:"]
        
        if preferences.get("duration"):
            request_parts.append(f"- Duration: {preferences['duration']} days")
        
        if preferences.get("group_composition"):
            request_parts.append(f"- Travel group: {preferences['group_composition']}")
        
        if preferences.get("accessibility_needs"):
            request_parts.append(f"- Accessibility needs: {', '.join(preferences['accessibility_needs'])}")
        
        if preferences.get("dietary_restrictions"):
            request_parts.append(f"- Dietary requirements: {', '.join(preferences['dietary_restrictions'])}")
        
        if preferences.get("budget_range"):
            request_parts.append(f"- Budget: {preferences['budget_range']}")
        
        if preferences.get("interests"):
            request_parts.append(f"- Interests: {', '.join(preferences['interests'])}")
        
        # Add weather context if available
        if context.get("weather"):
            request_parts.append(f"- Current weather: {context['weather']}")
        
        request_parts.append("\nPlease provide a day-by-day itinerary with:")
        request_parts.append("- Specific venue recommendations with accessibility details")
        request_parts.append("- Transportation instructions")
        request_parts.append("- Cost estimates")
        request_parts.append("- Timing and pacing considerations")
        request_parts.append("- Explanations for why each venue is suitable")
        
        return "\n".join(request_parts)
    
    def test_connection(self) -> LLMResponse:
        """Test the connection to the LLM service."""
        test_request = LLMRequest(
            user_message="Hello, please respond with a brief greeting to confirm you're working.",
            context={},
            system_prompt="You are a helpful assistant. Respond briefly and clearly.",
            max_tokens=100
        )
        
        return self.process_message(test_request)

# Convenience function for easy import
def get_llm_orchestrator() -> LLMOrchestrator:
    """Get a configured LLM orchestrator instance."""
    return LLMOrchestrator()