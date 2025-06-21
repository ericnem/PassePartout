"""
Text parser using Gemini API to extract route parameters
"""
import google.generativeai as genai
import os
from typing import Dict, Any

class TextParser:
    """Parse input text using Gemini API to extract route parameters"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def parse_input(self, input_text: str) -> Dict[str, Any]:
        """
        Parse input text to extract route parameters
        
        Args:
            input_text: User's natural language input
            
        Returns:
            Dictionary with extracted parameters
        """
        prompt = f"""
        Parse the following text and extract route planning parameters. Return a JSON object with these fields:
        - max_distance_km: maximum route distance in kilometers (default: 5)
        - start_location: starting point name or coordinates (default: "city center")
        - preferences: list of POI types to visit (e.g., ["monuments", "museums", "parks"])
        - min_distance_km: minimum distance between stops (default: 0.5)
        
        Input text: "{input_text}"
        
        Return only valid JSON, no other text.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            json_text = response.text.strip()
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            
            import json
            parsed = json.loads(json_text)
            
            # Set defaults for missing fields
            defaults = {
                "max_distance_km": 5.0,
                "start_location": "city center",
                "preferences": ["monuments"],
                "min_distance_km": 0.5
            }
            
            for key, default_value in defaults.items():
                if key not in parsed:
                    parsed[key] = default_value
            
            return parsed
            
        except Exception as e:
            print(f"Error parsing text with Gemini: {e}")
            # Return defaults if parsing fails
            return {
                "max_distance_km": 5.0,
                "start_location": "city center",
                "preferences": ["monuments"],
                "min_distance_km": 0.5
            } 