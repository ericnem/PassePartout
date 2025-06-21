import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

export async function generateNarration(poi) {
  const response = await axios.post(`${BASE_URL}/generate_narration?poi=${encodeURIComponent(poi)}`);
  return response.data.narration;
}