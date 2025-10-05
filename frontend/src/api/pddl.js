/**
 * API service for PDDL RLHF backend
 */

import axios from 'axios';

// API base URL - will be replaced with Railway URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 seconds for plan generation
});

/**
 * Generate a PDDL plan from a prompt
 */
export const generatePlan = async (prompt, temperature = 0.5, maxTokens = 10000) => {
  try {
    const response = await api.post('/api/generate-plan', {
      prompt,
      temperature,
      max_tokens: maxTokens,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to generate plan. Please try again.'
    );
  }
};

/**
 * Submit human feedback and generate training dataset
 */
export const submitFeedback = async (sessionId, prompt, planText, feedback, metadata) => {
  try {
    const response = await api.post('/api/submit-feedback', {
      session_id: sessionId,
      prompt,
      plan_text: planText,
      feedback,
      metadata,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to submit feedback. Please try again.'
    );
  }
};

/**
 * Export dataset by session ID
 */
export const exportDataset = async (sessionId, format = 'json') => {
  try {
    const response = await api.get(`/api/export-dataset/${sessionId}`, {
      params: { format },
    });
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 'Failed to export dataset. Please try again.'
    );
  }
};

export default api;

