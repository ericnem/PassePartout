import axios from 'axios';

// Use environment variable or fallback to localhost
const BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

export async function generateNarration(poi) {
  const response = await axios.post(`${BASE_URL}/generate_narration?poi=${encodeURIComponent(poi)}`);
  return response.data.narration;
}

// Add a generic POST helper for other endpoints
export async function postToBackend(endpoint, data) {
  const response = await axios.post(`${BASE_URL}${endpoint}`, data);
  return response.data;
}