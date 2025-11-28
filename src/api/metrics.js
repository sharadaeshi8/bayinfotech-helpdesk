import { API_BASE_URL } from '../config/api';


export const fetchMetricsSummary = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics/summary`);
    if (!response.ok) {
      throw new Error('Failed to fetch metrics summary');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics:', error);
    throw error;
  }
};

export const fetchTrends = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics/trends`);
    if (!response.ok) {
      throw new Error('Failed to fetch metrics trends');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching trends:', error);
    throw error;
  }
};
