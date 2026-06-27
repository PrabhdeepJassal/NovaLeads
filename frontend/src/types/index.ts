// ============================================================
// NovaLeads — Type Definitions
// ============================================================

// --- User & Auth ---
export type UserRole = 'employee' | 'admin';

export interface User {
  id: string;
  emp_id?: string;
  name: string;
  email: string;
  role: UserRole;
  company_name: string;
  is_active: boolean;
  employee_tenure_days: number;
  prev_conversion_rate: number;
  created_at: string;
  updated_at: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  company_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// --- Leads ---
export type LeadStatus = 'new' | 'active' | 'cold' | 'rejected' | 'successful';

export interface Lead {
  id: string;
  employee_id: string;
  company_name: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string | null;
  lead_source: string;
  industry: string;
  company_size: number;
  website_visits: number;
  emails_opened: number;
  emails_clicked: number;
  calls_made: number;
  calls_connected: number;
  call_duration_minutes: number;
  meetings_scheduled: number;
  meetings_done: number;
  days_since_first_contact: number;
  follow_ups_total: number;
  demo_requested: boolean;
  budget_available: boolean;
  decision_maker_contacted: boolean;
  competitor_considering: boolean;
  revenue: number;
  status: LeadStatus;
  notes: string | null;
  predicted_outcome: string;
  prediction_confidence: number;
  predicted_at: string;
  created_at: string;
  updated_at: string;
}

export interface CreateLeadData {
  company_name: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string | null;
  lead_source: string;
  industry: string;
  company_size: number;
  notes?: string;
  website_visits?: number;
  emails_opened?: number;
  emails_clicked?: number;
  calls_made?: number;
  calls_connected?: number;
  call_duration_minutes?: number;
  meetings_scheduled?: number;
  meetings_done?: number;
  days_since_first_contact?: number;
  follow_ups_total?: number;
  demo_requested?: boolean;
  budget_available?: boolean;
  decision_maker_contacted?: boolean;
  competitor_considering?: boolean;
  revenue?: number;
}

// --- Activity Log ---
export interface ActivityLog {
  id: string;
  lead_id: string;
  action: string;
  description: string;
  user_name: string;
  created_at: string;
}

// --- Dashboard: Employee ---
export interface EmployeeDashboard {
  total_leads: number;
  cold_leads: number;
  rejected_leads: number;
  successful_leads: number;
  pending_leads: number;
  conversion_rate: number;
  monthly_trend: MonthlyTrend[];
  recent_activity: ActivityLog[];
}

// --- Dashboard: Admin ---
export interface AdminDashboard {
  total_employees: number;
  total_leads: number;
  total_converted: number;
  team_conversion_rate: number;
  leaderboard: EmployeeLeaderboardEntry[];
  monthly_trend: MonthlyTrend[];
  status_distribution: Record<string, number>;
  model_accuracy: number;
  // Optional date-filter range
  start_date?: string;
  end_date?: string;
}

// --- Dashboard date filter ---
export interface DashboardDateParams {
  start_date?: string;
  end_date?: string;
}

// --- Activity Feed (from GET /admin/activity-feed) ---
export interface ActivityFeedItem {
  id: string;
  lead_id?: string;
  lead_name?: string;
  user_name: string;
  action: string;
  description: string;
  created_at: string;
}

// --- Lead Insights (from GET /admin/lead-insights) ---
export interface SourcePerformance {
  source: string;
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
}

export interface IndustryPerformance {
  industry: string;
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
}

export interface LeadInsight {
  best_source: SourcePerformance | null;
  best_industry: IndustryPerformance | null;
  top_sources: SourcePerformance[];
  top_industries: IndustryPerformance[];
  stale_leads: number;
  avg_meeting_completion: number;
}

// --- Salary Rules ---
export interface SalaryRule {
  id: string;
  role: string;
  min_leads: number;
  max_leads: number | null;
  base_salary: number;
  bonus_per_lead: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateSalaryRuleData {
  role: string;
  min_leads: number;
  max_leads?: number | null;
  base_salary: number;
  bonus_per_lead: number;
  is_active?: boolean;
}

// --- Performance Targets ---
export interface PerformanceTarget {
  id: string;
  employee_id: string;
  employee_name?: string;
  target_leads: number;
  target_conversions: number;
  period_start: string;
  period_end: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UpdatePerformanceTargetData {
  target_leads?: number;
  target_conversions?: number;
  is_active?: boolean;
}

// --- Employee salary detail (popover/detail) ---
export interface EmployeeSalaryDetail {
  employee_id: string;
  name: string;
  current_salary: number;
  total_leads: number;
  converted_leads: number;
  bonus_earned: number;
  total_compensation: number;
}

export interface EmployeeLeaderboardEntry {
  employee_id: string;
  id?: string;
  emp_id?: string;
  name: string;
  email?: string;
  is_active?: boolean;
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
}

export interface MonthlyTrend {
  month: string;
  leads_created: number;
  leads_converted: number;
}

// --- API Response Wrappers ---
export interface PaginatedLeadsResponse {
  items: Lead[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  [key: string]: string | string[] | undefined;
}

// --- Salary Deduction Rules ---
export interface SalaryDeductionRule {
  id: string;
  rule_name: string;
  min_revenue: number;
  max_revenue: number;
  deduction_percent: number;
  created_at?: string;
  updated_at?: string;
}

// --- Employee Salary Info ---
export interface EmployeeSalaryInfo {
  employee_name: string;
  emp_id: string;
  target_revenue: number;
  actual_revenue: number;
  applicable_rule: string;
  deduction_percent: number;
  take_home_percent: number;
}

// --- Performance Targets ---
export interface EmployeePerformanceTarget {
  employee_id?: string;
  employee_name: string;
  target_revenue: number;
  actual_revenue: number;
}

// --- Stale Leads ---
export interface StaleLeadsInfo {
  count: number;
}
