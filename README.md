# PassePartout AI

PassePartout AI is a context-aware, audio-first tour guide web application that leverages advanced AI to generate personalized walking routes and engaging, narrated scripts for points of interest (POIs). The project combines natural language understanding, real-time mapping, and generative AI to deliver a unique, interactive city exploration experience. See it in action: https://passe-partout.vercel.app/

## Features
- **AI-Powered Route Generation:** Users can request custom walking tours using natural language. The backend parses requests, geocodes locations, and finds relevant POIs.
- **Context-Aware Narration:** Each POI on the route receives a unique, AI-generated script suitable for audio narration, including interesting facts and historical details.
- **Chat-Driven Experience:** The system supports chat history, allowing for context-rich, follow-up queries and dynamic route adjustments.
- **Live Mapping:** Interactive maps display the generated route and POIs, with concise AI scripts shown for each location.
- **Weather Integration:** Real-time weather data is displayed for the user's current location.

## Technologies & APIs Used
- **FastAPI** (Python) for the backend API
- **React** and **Leaflet** for the frontend UI and mapping
- **Google Gemini API** for natural language understanding and script generation
- **OpenStreetMap Overpass API** for POI data
- **Nominatim** for geocoding
- **OSRM** for route and distance calculations
- **OpenWeatherMap** for weather data

## Setup Instructions
**Please see `setup.txt` in the project root for all setup and installation instructions.**

---

For questions or contributions, please open an issue or pull request.
