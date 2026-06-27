// ============================================================
// NovaLeads — Admin Service
// ============================================================

import api from './api';
import type {
  AdminDashboard,
  EmployeeLeaderboardEntry,
  EmployeePerformanceTarget,
  Lead,
  DashboardDateParams,
  ActivityFeedItem,
  LeadInsight,
  SalaryDeductionRule,
  SalaryRule,
  CreateSalaryRuleData,
  PerformanceTarget,
  UpdatePerformanceTargetData,
} from '../types';

export async function getDashboard(params?: DashboardDateParams): Promise<AdminDashboard> {
  const { data } = await api.get<AdminDashboard>('/admin/dashboard', { params });
  return data;
}

export async function getEmployees(): Promise<EmployeeLeaderboardEntry[]> {
  const { data } = await api.get<{ items: any[] }>('/admin/employees');
  return (data.items || []).map((emp: any) => ({
    employee_id: emp.id,
    emp_id: emp.emp_id,
    name: emp.name,
    email: emp.email,
    total_leads: emp.total_leads,
    converted_leads: emp.converted_leads,
    conversion_rate: emp.conversion_rate,
    is_active: emp.is_active,
  }));
}

export async function getEmployeeLeads(employeeId: string): Promise<{ items: Lead[]; total: number }> {
  const { data } = await api.get<Lead[]>(`/admin/employees/${employeeId}/leads`);
  return { items: data || [], total: (data || []).length };
}

// --- Activity Feed ---
export async function getActivityFeed(): Promise<ActivityFeedItem[]> {
  const { data } = await api.get<ActivityFeedItem[]>('/admin/activity-feed');
  return data || [];
}

// --- Lead Insights ---
export async function getLeadInsights(): Promise<LeadInsight> {
  const { data } = await api.get<LeadInsight>('/admin/lead-insights');
  return data;
}

// --- CSV Exports ---
export function getExportLeadsURL(): string {
  return `${api.defaults.baseURL}/admin/export/leads`;
}

export function getExportEmployeesURL(): string {
  return `${api.defaults.baseURL}/admin/export/employees`;
}

// --- Salary Rules ---
export async function getSalaryRules(): Promise<SalaryRule[]> {
  const { data } = await api.get<SalaryRule[]>('/admin/salary-rules');
  return data || [];
}

export async function createSalaryRule(rule: CreateSalaryRuleData): Promise<SalaryRule> {
  const { data } = await api.post<SalaryRule>('/admin/salary-rules', rule);
  return data;
}

export async function updateSalaryRule(id: string, rule: Partial<CreateSalaryRuleData>): Promise<SalaryRule> {
  const { data } = await api.put<SalaryRule>(`/admin/salary-rules/${id}`, rule);
  return data;
}

export async function deleteSalaryRule(id: string): Promise<void> {
  await api.delete(`/admin/salary-rules/${id}`);
}

// --- Performance Targets ---
export async function getPerformanceTargets(): Promise<PerformanceTarget[]> {
  const { data } = await api.get<PerformanceTarget[]>('/admin/performance-targets');
  return data || [];
}

export async function updatePerformanceTarget(id: string, updates: UpdatePerformanceTargetData): Promise<PerformanceTarget> {
  const { data } = await api.put<PerformanceTarget>(`/admin/performance-targets/${id}`, updates);
  return data;
}

export async function retrainModel(): Promise<{ detail: string; accuracy?: number }> {
  const { data } = await api.post<{ detail: string; accuracy?: number }>('/predict/retrain');
  return data;
}

// ─── Salary Deduction Rules (revenue-based) ────────────────────────

export async function getSalaryDeductionRules(): Promise<SalaryDeductionRule[]> {
  const { data } = await api.get<SalaryDeductionRule[]>('/admin/salary-deduction-rules');
  return data || [];
}

export async function createSalaryDeductionRule(
  rule: Omit<SalaryDeductionRule, 'id' | 'created_at' | 'updated_at'>
): Promise<SalaryDeductionRule> {
  const { data } = await api.post<SalaryDeductionRule>('/admin/salary-deduction-rules', rule);
  return data;
}

export async function updateSalaryDeductionRule(
  id: string,
  rule: Partial<Omit<SalaryDeductionRule, 'id' | 'created_at' | 'updated_at'>>
): Promise<SalaryDeductionRule> {
  const { data } = await api.put<SalaryDeductionRule>(`/admin/salary-deduction-rules/${id}`, rule);
  return data;
}

export async function deleteSalaryDeductionRule(id: string): Promise<void> {
  await api.delete(`/admin/salary-deduction-rules/${id}`);
}

// ─── Employee Performance Targets (revenue-based) ──────────────────

export async function getEmployeePerformanceTargets(): Promise<EmployeePerformanceTarget[]> {
  const { data } = await api.get<EmployeePerformanceTarget[]>('/admin/employee-performance-targets');
  return data || [];
}
