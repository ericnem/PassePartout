"""
Simplified Roam service that generates tour summaries
"""

import time

from models import RoamRequest, RoamResponse
from roam_summary_generator import RoamSummaryGenerator


class RoamService:
    """Simplified service for the Roam feature"""

    def __init__(self):
        self.summary_generator = RoamSummaryGenerator()

    async def generate_roam_response(self, request: RoamRequest) -> RoamResponse:
        """
        Generate a Roam response with tour summary

        Args:
            request: RoamRequest with coordinates string

        Returns:
            RoamResponse with summary
        """
        start_time = time.time()

        print(f"📍 Generating tour for coordinates: {request.coordinates}")
        # Generate tour summary, passing context if available
        summary = self.summary_generator.generate_tour_summary(
            request.coordinates, context=request.context
        )

        # Create response
        response = RoamResponse(summary=summary)

        # Log performance
        elapsed_time = (time.time() - start_time) * 1000
        print(f"⏱️ Tour generated in {elapsed_time:.1f}ms")

        return response

    async def get_roam_with_fallback(self, request: RoamRequest) -> RoamResponse:
        """
        Get Roam response with fallback handling

        Args:
            request: RoamRequest with coordinates string

        Returns:
            RoamResponse with summary
        """
        try:
            return await self.generate_roam_response(request)
        except Exception as e:
            print(f"❌ Error in Roam service: {e}")

            # Return fallback response
            return RoamResponse(
                summary="Welcome to this exciting area! This location offers amazing opportunities for visitors. Take a stroll around and discover local attractions, historical landmarks, and hidden gems."
            )
