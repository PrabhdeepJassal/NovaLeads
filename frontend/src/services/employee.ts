// ============================================================
// NovaLeads — Employee Dashboard Service
// ============================================================

import api from './api';
import type {
  EmployeeDashboard,
  EmployeePerformanceTarget,
  EmployeeSalaryInfo,
  StaleLeadsInfo,
} from '../types';

export async function getEmployeeDashboard(): Promise<EmployeeDashboard> {
  const { data } = await api.get<EmployeeDashboard>('/employee/dashboard');
  return data;
}

// ─── My Salary Info ────────────────────────────────────────────────

export async function getMySalaryInfo(): Promise<EmployeeSalaryInfo> {
  const { data } = await api.get<EmployeeSalaryInfo>('/salary/my-info');
  return data;
}

// ─── My Target ─────────────────────────────────────────────────────

export async function getMyTarget(): Promise<EmployeePerformanceTarget> {
  const { data } = await api.get<EmployeePerformanceTarget>('/salary/my-target');
  return data;
}

// ─── Stale Leads Count ─────────────────────────────────────────────

export async function getStaleLeadsCount(): Promise<StaleLeadsInfo> {
  const { data } = await api.get<StaleLeadsInfo>('/leads/stale-count');
  return data;
}
