"""
Script generator using Gemini API for location-specific narratives
"""
import google.generativeai as genai
import os
from typing import Dict, Any

class ScriptGenerator:
    """Generate scripts for POIs using Gemini API"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_script(self, poi: Dict[str, Any]) -> str:
        """
        Generate a script for a POI
        
        Args:
            poi: POI dictionary with name, category, tags, etc.
            
        Returns:
            Generated script text
        """
        name = poi.get("name", "this location")
        category = poi.get("category", "attraction")
        tags = poi.get("tags", {})
        
        # Extract additional context from tags
        context = self._extract_context_from_tags(tags)
        
        prompt = f"""
        Generate a short, engaging tour guide script for {name}. 
        
        Context:
        - Category: {category}
        - Additional info: {context}
        
        Requirements:
        - Keep it under 100 words
        - Make it conversational and friendly
        - Include interesting facts if available
        - End with a call to explore or observe
        
        Write the script as if you're speaking directly to a tourist.
        """
        
        try:
            response = self.model.generate_content(prompt)
            script = response.text.strip()
            
            # Clean up the script
            if script.startswith('"') and script.endswith('"'):
                script = script[1:-1]
            
            return script
            
        except Exception as e:
            print(f"Error generating script with Gemini: {e}")
            return self._fallback_script(name, category)
    
    def _extract_context_from_tags(self, tags: Dict[str, str]) -> str:
        """
        Extract useful context from OSM tags
        
        Args:
            tags: OSM tags dictionary
            
        Returns:
            Context string
        """
        context_parts = []
        
        # Extract relevant information
        if "historic" in tags:
            context_parts.append(f"historic: {tags['historic']}")
        if "tourism" in tags:
            context_parts.append(f"tourism: {tags['tourism']}")
        if "amenity" in tags:
            context_parts.append(f"amenity: {tags['amenity']}")
        if "leisure" in tags:
            context_parts.append(f"leisure: {tags['leisure']}")
        if "description" in tags:
            context_parts.append(f"description: {tags['description']}")
        
        return ", ".join(context_parts) if context_parts else "no additional context"
    
    def _fallback_script(self, name: str, category: str) -> str:
        """
        Generate fallback script when Gemini fails
        
        Args:
            name: POI name
            category: POI category
            
        Returns:
            Fallback script
        """
        category_scripts = {
            "tourism": f"Welcome to {name}! This popular tourist destination offers a unique experience for visitors. Take a moment to soak in the atmosphere and discover what makes this place special.",
            "historic": f"You've arrived at {name}, a site rich with history and cultural significance. This location has witnessed important events and continues to tell stories of the past.",
            "amenity": f"Here you'll find {name}, a convenient amenity that serves the local community and visitors alike. It's a great place to take a break and experience local life.",
            "leisure": f"Enjoy the peaceful atmosphere of {name}, a perfect spot for relaxation and recreation. This green space offers a welcome escape from the urban environment.",
            "shop": f"Welcome to {name}, where you can find a variety of goods and services. This shopping destination caters to both locals and tourists looking for unique items."
        }
        
        return category_scripts.get(category, f"Welcome to {name}! This interesting location is worth exploring and discovering its unique character.") 