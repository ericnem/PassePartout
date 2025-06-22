"""
Simplified Gemini API integration for generating tour summaries
"""

import os
import google.generativeai as genai
from typing import Any


class RoamSummaryGenerator:
    """Generates AI tour summaries using Gemini API"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_tour_summary(self, coordinates: str) -> str:
        """
        Generate a tour summary for coordinates using Gemini
        
        Args:
            coordinates: Coordinate string (e.g., "43.6426, -79.3871")
        
        Returns:
            Tour summary string
        """
        prompt = f"""You are a knowledgeable tour guide. Create an engaging 30-second tour summary for the location at coordinates: {coordinates}

Include information about:
- Historical landmarks and facts
- Popular restaurants and food spots
- Local attractions and activities
- Cultural highlights
- Hidden gems and unique features
- What makes this area special

Write in an enthusiastic, engaging tour guide style that makes people excited to explore.

Do NOT mention the coordinates in your response. Keep the summary around 2-3 sentences."""

        try:
            print(f"🤖 Making Gemini API call for coordinates: {coordinates}")
            response = self.model.generate_content(prompt)
            summary_text = response.text.strip()
            print(f"📝 Raw Gemini response: {summary_text[:200]}...")
            if summary_text:
                print("✅ Successfully got Gemini summary")
                return summary_text
            else:
                print("⚠️ Gemini response was empty, using fallback")
                return "Welcome to this amazing area! This location offers incredible opportunities for exploration. Take a stroll around and discover local attractions, historical landmarks, and hidden gems that make this place special."
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            print(f"❌ Error type: {type(e).__name__}")
            return "Welcome to this exciting area! This location offers amazing opportunities for visitors. Take a stroll around and discover local attractions, historical landmarks, and hidden gems. Every location has its unique charm and stories waiting to be uncovered!" 