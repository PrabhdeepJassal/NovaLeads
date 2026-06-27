// ============================================================
// NovaLeads — Leads Service
// ============================================================

import api from './api';
import type { Lead, CreateLeadData, PaginatedLeadsResponse, ActivityLog } from '../types';

export interface LeadsQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  ordering?: string;
  employee_id?: string;
}

export async function getLeads(params: LeadsQueryParams = {}): Promise<PaginatedLeadsResponse> {
  const { data } = await api.get<PaginatedLeadsResponse>('/leads/', { params });
  return data;
}

export async function getLead(id: string): Promise<Lead> {
  const { data } = await api.get<Lead>(`/leads/${id}`);
  return data;
}

export async function createLead(leadData: CreateLeadData): Promise<Lead> {
  const { data } = await api.post<Lead>('/leads/', leadData);
  return data;
}

export async function updateLead(id: string, leadData: Partial<CreateLeadData & { status: string }>): Promise<Lead> {
  const { data } = await api.patch<Lead>(`/leads/${id}`, leadData);
  return data;
}

export async function deleteLead(id: string): Promise<void> {
  await api.delete(`/leads/${id}`);
}

export async function getLeadActivity(leadId: string): Promise<ActivityLog[]> {
  const { data } = await api.get<ActivityLog[]>(`/leads/${leadId}/activity`);
  return data;
}
