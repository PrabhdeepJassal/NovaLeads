// ============================================================
// NovaLeads — Predictions Service
// ============================================================
// Prediction is auto-performed on lead create/update by the backend.
// This service provides optional batch operations.

import api from './api';

export async function batchPredict(): Promise<{ detail: string; processed: number }> {
  const { data } = await api.post<{ detail: string; processed: number }>('/predict/batch');
  return data;
}
