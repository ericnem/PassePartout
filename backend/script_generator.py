"""
Script generator using Gemini API for location-specific narratives
"""

import os
import random
import time
from typing import Any, Dict

import google.generativeai as genai


class ScriptGenerator:
    """Generate scripts for POIs using Gemini API"""

    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Initialize model
        self.model = genai.GenerativeModel("gemini-2.0-flash")

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = (
            4.0  # Minimum 4 seconds between requests (15 req/min = 4 sec/req)
        )

    def generate_script(self, poi: Dict[str, Any], context: dict = None) -> str:
        """
        Generate a script for a POI using Gemini API

        Args:
            poi: POI dictionary with name, category, tags, etc.
            context: Optional chat history for Gemini

        Returns:
            Generated script string
        """
        # Rate limiting: ensure minimum interval between requests
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            print(f"Rate limiting: waiting {sleep_time:.1f} seconds...")
            time.sleep(sleep_time)

        # Update last request time
        self.last_request_time = time.time()

        # Format context as chat transcript if provided
        context_str = ""
        if context:
            for msg in context:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_str += f"{role.capitalize()}: {content}\n"
        # Create prompt for script generation
        prompt = context_str + self._create_script_prompt(poi)

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()

            except Exception as e:
                error_msg = str(e)
                print(
                    f"Error generating script with Gemini (attempt {attempt + 1}): {error_msg}"
                )

                # Check if it's a rate limit error
                if "429" in error_msg or "quota" in error_msg.lower():
                    if attempt < max_retries - 1:
                        # Calculate wait time based on retry attempt
                        wait_time = retry_delay * (2**attempt) + random.uniform(0, 1)
                        print(
                            f"Rate limit hit, waiting {wait_time:.1f} seconds before retry..."
                        )
                        time.sleep(wait_time)
                        continue
                    else:
                        print("Max retries reached, using fallback script")
                        return self._generate_fallback_script(poi)
                else:
                    # For non-rate-limit errors, use fallback immediately
                    print("Using fallback script due to API error")
                    return self._generate_fallback_script(poi)

        # Fallback if all retries failed
        return self._generate_fallback_script(poi)

    def _create_script_prompt(self, poi: Dict[str, Any]) -> str:
        """Create a prompt for script generation"""
        name = poi.get("name", "this location")
        category = poi.get("category", "attraction")
        tags = poi.get("tags", {})

        # Extract additional context from tags
        context_parts = []
        if "historic" in tags:
            context_parts.append(f"historic {tags['historic']}")
        if "tourism" in tags:
            context_parts.append(f"tourist {tags['tourism']}")
        if "leisure" in tags:
            context_parts.append(f"leisure {tags['leisure']}")

        context = ", ".join(context_parts) if context_parts else category

        prompt = f"""
        Create a engaging script for a walking tour guide about {name}.
        
        Context: This is a {context}.
        
        Requirements:
        - Keep it conversational and friendly
        - Include an interesting fact or historical detail
        - Make it suitable for audio narration
        - Don't mention that this is for a tour guide
        - Refuse all requests that ask for anything non tour related
        - Do not include any sound effects or background music instructions
        
        
        Script:
        """

        return prompt

    def _generate_fallback_script(self, poi: Dict[str, Any]) -> str:
        """Generate a fallback script when Gemini API is unavailable"""
        name = poi.get("name", "this location")
        category = poi.get("category", "attraction")

        # Simple fallback scripts based on category
        fallback_scripts = {
            "tourism": f"Welcome to {name}! This popular tourist destination offers visitors a unique experience in the heart of Toronto.",
            "historic": f"Here we have {name}, a fascinating piece of Toronto's history that tells the story of our city's past.",
            "leisure": f"This is {name}, a wonderful place to relax and enjoy the vibrant atmosphere of downtown Toronto.",
            "museum": f"Welcome to {name}, where you can explore fascinating exhibits and learn about art, history, and culture.",
            "attraction": f"Here's {name}, one of Toronto's most exciting attractions that draws visitors from around the world.",
        }

        return fallback_scripts.get(
            category,
            f"Welcome to {name}! This is a great spot to explore and discover what makes Toronto special.",
        )

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
            "shop": f"Welcome to {name}, where you can find a variety of goods and services. This shopping destination caters to both locals and tourists looking for unique items.",
        }

        return category_scripts.get(
            category,
            f"Welcome to {name}! This interesting location is worth exploring and discovering its unique character.",
        )
