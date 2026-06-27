// ============================================================
// NovaLeads — Admin Dashboard
// ============================================================

import { useState, useEffect, useCallback } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
  AreaChart,
  Area,
} from 'recharts';
import {
  Users,
  Target,
  TrendingUp,
  RefreshCw,
  Award,
  ChevronDown,
  ChevronUp,
  BarChart3,
  PieChart as PieChartIcon,
  Activity,
  Clock,
  Download,
  Filter,
  Calendar,
  TrendingDown,
  AlertTriangle,
  Zap,
  Building2,
  Users2,
  ListFilter,
  DollarSign,
  Plus,
  Trash2,
  Edit3,
  X,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import * as adminService from '../services/admin';
import type {
  AdminDashboard,
  EmployeeLeaderboardEntry,
  EmployeePerformanceTarget,
  Lead,
  ActivityFeedItem,
  LeadInsight,
  SalaryDeductionRule,
} from '../types';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import LeadTable from '../components/LeadTable';
import LeadModal from '../components/LeadModal';
import LoadingSpinner from '../components/LoadingSpinner';
import { getErrorMessage } from '../services/api';

const PIE_COLORS: Record<string, string> = {
  new: '#6366F1',
  active: '#818CF8',
  cold: '#EF4444',
  rejected: '#F59E0B',
  successful: '#10B981',
  pending: '#9CA3AF',
};

const STATUS_COLORS: Record<string, string> = {
  new: '#6366F1',
  active: '#818CF8',
  cold: '#EF4444',
  rejected: '#F59E0B',
  successful: '#10B981',
  pending: '#9CA3AF',
};

function timeAgo(dateStr: string): string {
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffSec = Math.floor((now - then) / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

function getActivityIcon(action: string) {
  const a = action.toLowerCase();
  if (a.includes('call') || a.includes('phone')) return '📞';
  if (a.includes('status') || a.includes('update')) return '✏️';
  if (a.includes('create') || a.includes('new') || a.includes('add')) return '➕';
  if (a.includes('meeting') || a.includes('schedule')) return '📅';
  if (a.includes('email') || a.includes('mail')) return '📧';
  if (a.includes('delete') || a.includes('remove')) return '🗑️';
  if (a.includes('convert') || a.includes('success')) return '✅';
  return '•';
}

function getToday(): string {
  return new Date().toISOString().slice(0, 10);
}

function getThirtyDaysAgo(): string {
  const d = new Date();
  d.setDate(d.getDate() - 30);
  return d.toISOString().slice(0, 10);
}

export default function AdminDashboard() {
  const { user } = useAuth();

  // ================================================================
  // Data states
  // ================================================================
  const [dashboard, setDashboard] = useState<AdminDashboard | null>(null);
  const [employees, setEmployees] = useState<EmployeeLeaderboardEntry[]>([]);
  const [activityFeed, setActivityFeed] = useState<ActivityFeedItem[]>([]);
  const [leadInsights, setLeadInsights] = useState<LeadInsight | null>(null);

  // ================================================================
  // Loading states
  // ================================================================
  const [statsLoading, setStatsLoading] = useState(true);
  const [activityLoading, setActivityLoading] = useState(false);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ================================================================
  // Date range filter
  // ================================================================
  const [startDate, setStartDate] = useState(getThirtyDaysAgo());
  const [endDate, setEndDate] = useState(getToday());
  const [appliedStartDate, setAppliedStartDate] = useState(getThirtyDaysAgo());
  const [appliedEndDate, setAppliedEndDate] = useState(getToday());

  // ================================================================
  // Employee detail drill-down
  // ================================================================
  const [selectedEmployee, setSelectedEmployee] = useState<EmployeeLeaderboardEntry | null>(null);
  const [employeeLeads, setEmployeeLeads] = useState<Lead[]>([]);
  const [employeeLeadsLoading, setEmployeeLeadsLoading] = useState(false);
  const [leadModalOpen, setLeadModalOpen] = useState(false);
  const [leadModalMode, setLeadModalMode] = useState<'create' | 'view' | 'edit'>('view');
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);

  // Employee lead table pagination/filters
  const [empSearch, setEmpSearch] = useState('');
  const [empStatusFilter, setEmpStatusFilter] = useState('');
  const [empPage, setEmpPage] = useState(1);
  const [empSortField, setEmpSortField] = useState('created_at');
  const [empSortOrder, setEmpSortOrder] = useState<'asc' | 'desc'>('desc');
  const [empTotalCount, setEmpTotalCount] = useState(0);

  // Sort for leaderboard
  const [leaderSortField, setLeaderSortField] = useState('conversion_rate');
  const [leaderSortOrder, setLeaderSortOrder] = useState<'asc' | 'desc'>('desc');

  // ================================================================
  // Salary Deduction Rules
  // ================================================================
  const [salaryRules, setSalaryRules] = useState<SalaryDeductionRule[]>([]);
  const [salaryRulesLoading, setSalaryRulesLoading] = useState(true);
  const [salaryRulesError, setSalaryRulesError] = useState<string | null>(null);

  // Salary rule modal
  const [ruleModalOpen, setRuleModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<SalaryDeductionRule | null>(null);
  const [ruleFormName, setRuleFormName] = useState('');
  const [ruleFormMinRev, setRuleFormMinRev] = useState('');
  const [ruleFormMaxRev, setRuleFormMaxRev] = useState('');
  const [ruleFormDeduction, setRuleFormDeduction] = useState('');
  const [ruleFormError, setRuleFormError] = useState<string | null>(null);
  const [ruleSaving, setRuleSaving] = useState(false);

  // Performance targets
  const [performanceTargets, setPerformanceTargets] = useState<EmployeePerformanceTarget[]>([]);
  const [targetsLoading, setTargetsLoading] = useState(true);

  // ================================================================
  // Fetch all admin data (with optional date range)
  // ================================================================
  const fetchAllData = useCallback(async (start?: string, end?: string) => {
    setStatsLoading(true);
    setError(null);
    try {
      const params = start && end ? { start_date: start, end_date: end } : undefined;
      const [dash, empl] = await Promise.all([
        adminService.getDashboard(params),
        adminService.getEmployees(),
      ]);
      setDashboard(dash);
      setEmployees(empl);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setStatsLoading(false);
    }
  }, []);

  // ================================================================
  // Fetch activity feed
  // ================================================================
  const fetchActivityFeed = useCallback(async () => {
    setActivityLoading(true);
    try {
      const feed = await adminService.getActivityFeed();
      setActivityFeed(feed.slice(0, 10));
    } catch {
      // Non-critical — keep existing or empty
      setActivityFeed([]);
    } finally {
      setActivityLoading(false);
    }
  }, []);

  // ================================================================
  // Fetch lead insights
  // ================================================================
  const fetchLeadInsights = useCallback(async () => {
    setInsightsLoading(true);
    try {
      const insights = await adminService.getLeadInsights();
      setLeadInsights(insights);
    } catch {
      setLeadInsights(null);
    } finally {
      setInsightsLoading(false);
    }
  }, []);

  // ================================================================
  // Date filter handlers
  // ================================================================
  const handleApplyDateFilter = () => {
    setAppliedStartDate(startDate);
    setAppliedEndDate(endDate);
    fetchAllData(startDate, endDate);
  };

  const handleResetDateFilter = () => {
    const today = getToday();
    const thirtyAgo = getThirtyDaysAgo();
    setStartDate(thirtyAgo);
    setEndDate(today);
    setAppliedStartDate(thirtyAgo);
    setAppliedEndDate(today);
    fetchAllData();
  };

  // ================================================================
  // Initial load
  // ================================================================
  useEffect(() => {
    fetchAllData();
    fetchActivityFeed();
    fetchLeadInsights();
  }, [fetchAllData, fetchActivityFeed, fetchLeadInsights]);

  // ================================================================
  // Fetch salary deduction rules
  // ================================================================
  const fetchSalaryRules = useCallback(async () => {
    setSalaryRulesLoading(true);
    setSalaryRulesError(null);
    try {
      const rules = await adminService.getSalaryDeductionRules();
      setSalaryRules(rules);
    } catch (err) {
      setSalaryRulesError(getErrorMessage(err));
    } finally {
      setSalaryRulesLoading(false);
    }
  }, []);

  // ================================================================
  // Fetch performance targets
  // ================================================================
  const fetchPerformanceTargets = useCallback(async () => {
    setTargetsLoading(true);
    try {
      const targets = await adminService.getEmployeePerformanceTargets();
      setPerformanceTargets(targets);
    } catch {
      setPerformanceTargets([]);
    } finally {
      setTargetsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSalaryRules();
    fetchPerformanceTargets();
  }, [fetchSalaryRules, fetchPerformanceTargets]);

  // ================================================================
  // Fetch employee leads (admin endpoint)
  // ================================================================
  const fetchEmployeeLeads = useCallback(async (empId: string) => {
    setEmployeeLeadsLoading(true);
    try {
      const data = await adminService.getEmployeeLeads(empId);
      setEmployeeLeads(data.items);
      setEmpTotalCount(data.total);
    } catch {
      setEmployeeLeads([]);
      setEmpTotalCount(0);
    } finally {
      setEmployeeLeadsLoading(false);
    }
  }, []);

  // ================================================================
  // Handlers
  // ================================================================
  const handleEmployeeClick = (emp: EmployeeLeaderboardEntry) => {
    setSelectedEmployee(emp);
    setEmpPage(1);
    setEmpSearch('');
    setEmpStatusFilter('');
    fetchEmployeeLeads(emp.employee_id);
  };

  const handleLeadClick = (lead: Lead) => {
    setSelectedLead(lead);
    setLeadModalMode('view');
    setLeadModalOpen(true);
  };

  const handleFullRefresh = () => {
    fetchAllData(appliedStartDate, appliedEndDate);
    fetchActivityFeed();
    fetchLeadInsights();
  };

  // ================================================================
  // Salary Rule modal handlers
  // ================================================================
  const openAddRuleModal = () => {
    setEditingRule(null);
    setRuleFormName('');
    setRuleFormMinRev('');
    setRuleFormMaxRev('');
    setRuleFormDeduction('');
    setRuleFormError(null);
    setRuleModalOpen(true);
  };

  const openEditRuleModal = (rule: SalaryDeductionRule) => {
    setEditingRule(rule);
    setRuleFormName(rule.rule_name);
    setRuleFormMinRev(String(rule.min_revenue));
    setRuleFormMaxRev(rule.max_revenue >= 999999999 ? '' : String(rule.max_revenue));
    setRuleFormDeduction(String(rule.deduction_percent));
    setRuleFormError(null);
    setRuleModalOpen(true);
  };

  const handleSaveRule = async () => {
    if (!ruleFormName.trim()) {
      setRuleFormError('Rule name is required');
      return;
    }
    const minRev = Number(ruleFormMinRev);
    const maxRev = ruleFormMaxRev ? Number(ruleFormMaxRev) : 999999999;
    const deduction = Number(ruleFormDeduction);

    if (isNaN(minRev) || minRev < 0) {
      setRuleFormError('Min revenue must be a positive number');
      return;
    }
    if (isNaN(deduction) || deduction < 0 || deduction > 100) {
      setRuleFormError('Deduction % must be between 0 and 100');
      return;
    }
    if (maxRev !== 999999999 && maxRev <= minRev) {
      setRuleFormError('Max revenue must be greater than min revenue');
      return;
    }

    setRuleSaving(true);
    setRuleFormError(null);
    try {
      if (editingRule) {
        await adminService.updateSalaryDeductionRule(editingRule.id, {
          rule_name: ruleFormName.trim(),
          min_revenue: minRev,
          max_revenue: maxRev,
          deduction_percent: deduction,
        });
      } else {
        await adminService.createSalaryDeductionRule({
          rule_name: ruleFormName.trim(),
          min_revenue: minRev,
          max_revenue: maxRev,
          deduction_percent: deduction,
        });
      }
      setRuleModalOpen(false);
      fetchSalaryRules();
    } catch (err) {
      setRuleFormError(getErrorMessage(err));
    } finally {
      setRuleSaving(false);
    }
  };

  const handleDeleteRule = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this salary deduction rule?')) return;
    try {
      await adminService.deleteSalaryDeductionRule(id);
      fetchSalaryRules();
    } catch (err) {
      console.error('Failed to delete rule:', getErrorMessage(err));
    }
  };

  // ================================================================
  // Computed data
  // ================================================================
  const sortedEmployees = [...employees].sort((a, b) => {
    const fieldA = a[leaderSortField as keyof EmployeeLeaderboardEntry];
    const fieldB = b[leaderSortField as keyof EmployeeLeaderboardEntry];
    const aVal = fieldA ?? 0;
    const bVal = fieldB ?? 0;
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return leaderSortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return leaderSortOrder === 'asc'
      ? (aVal as number) - (bVal as number)
      : (bVal as number) - (aVal as number);
  });

  // Convert status_distribution to array
  const statusDistArray = dashboard
    ? Object.entries(dashboard.status_distribution || {}).map(([status, count]) => ({
        status,
        count,
      }))
    : [];

  // Status distribution for funnel
  const statusTotal = statusDistArray.reduce((sum, s) => sum + s.count, 0) || 1;

  const formatMonth = (m: string) => {
    const d = new Date(m + '-01');
    return d.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  };

  // Export handlers
  const handleExportLeads = () => {
    const token = localStorage.getItem('lp_access_token');
    const url = `${adminService.getExportLeadsURL()}?token=${encodeURIComponent(token || '')}`;
    window.open(url, '_blank');
  };

  const handleExportEmployees = () => {
    const token = localStorage.getItem('lp_access_token');
    const url = `${adminService.getExportEmployeesURL()}?token=${encodeURIComponent(token || '')}`;
    window.open(url, '_blank');
  };

  // ================================================================
  // Render
  // ================================================================
  return (
    <Layout>
      <div className="page-container">
        {/* ================================================================ */}
        {/* Header */}
        {/* ================================================================ */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h1 className="page-title">Admin Dashboard</h1>
            <p className="page-subtitle">Full team overview and performance analytics.</p>
          </div>
          <button className="btn-secondary" onClick={handleFullRefresh}>
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* ================================================================ */}
        {/* Date Range Filter + Export Buttons */}
        {/* ================================================================ */}
        <div className="card p-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-end gap-3">
            {/* Date inputs */}
            <div className="flex items-center gap-3 flex-1 flex-wrap">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600 font-medium">From:</span>
              </div>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="input-field w-40 text-sm"
              />
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600 font-medium">To:</span>
              </div>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="input-field w-40 text-sm"
              />
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-2">
              <button className="btn-primary text-sm" onClick={handleApplyDateFilter}>
                <Filter className="w-4 h-4" />
                Apply
              </button>
              <button className="btn-ghost text-sm" onClick={handleResetDateFilter}>
                Reset
              </button>

              <div className="w-px h-6 bg-gray-200 mx-1" />

              <button className="btn-secondary text-sm" onClick={handleExportLeads}>
                <Download className="w-4 h-4" />
                Export Leads
              </button>
              <button className="btn-secondary text-sm" onClick={handleExportEmployees}>
                <Download className="w-4 h-4" />
                Export Employees
              </button>
            </div>
          </div>

          {/* Active filter indicator */}
          {(appliedStartDate !== getThirtyDaysAgo() || appliedEndDate !== getToday()) && (
            <div className="mt-3 flex items-center gap-2 text-xs text-primary-600 bg-primary-50 px-3 py-1.5 rounded-lg">
              <Filter className="w-3.5 h-3.5" />
              Active filter: <span className="font-semibold">{appliedStartDate}</span> to{' '}
              <span className="font-semibold">{appliedEndDate}</span>
            </div>
          )}
        </div>

        {/* ================================================================ */}
        {/* Error */}
        {/* ================================================================ */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-cold-50 border border-cold-200 text-sm text-cold-700 animate-fade-in">
            {error}
          </div>
        )}

        {/* ================================================================ */}
        {/* Main Content */}
        {/* ================================================================ */}
        {statsLoading && !dashboard ? (
          <LoadingSpinner size="lg" text="Loading dashboard data..." className="py-20" />
        ) : (
          <div className="space-y-8">
            {/* ============================================================ */}
            {/* Team Overview Stats */}
            {/* ============================================================ */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                icon={<Users className="w-5 h-5" />}
                label="Total Employees"
                value={dashboard?.total_employees || 0}
                colorClass="text-primary-600 bg-primary-50"
              />
              <StatCard
                icon={<Target className="w-5 h-5" />}
                label="Total Leads"
                value={dashboard?.total_leads || 0}
                colorClass="text-indigo-500 bg-indigo-50"
              />
              <StatCard
                icon={<TrendingUp className="w-5 h-5" />}
                label="Converted"
                value={dashboard?.total_converted || 0}
                colorClass="text-successful-500 bg-successful-50"
              />
              <StatCard
                icon={<BarChart3 className="w-5 h-5" />}
                label="Team Conversion Rate"
                value={`${((dashboard?.team_conversion_rate || 0) * 100).toFixed(1)}%`}
                colorClass="text-primary-500 bg-primary-50"
              />
            </div>

            {/* ============================================================ */}
            {/* Activity Feed + Lead Insights + Conversion Funnel Row */}
            {/* ============================================================ */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* --- Activity Feed --- */}
              <div className="card">
                <div className="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-primary-600" />
                  <h2 className="section-title">Recent Activity</h2>
                  {activityLoading && (
                    <span className="ml-auto">
                      <span className="loading-spinner" />
                    </span>
                  )}
                </div>
                <div className="divide-y divide-gray-100 max-h-[320px] overflow-y-auto">
                  {activityFeed.length === 0 && !activityLoading ? (
                    <div className="px-5 py-8 text-center text-sm text-gray-400">
                      No recent activity found.
                    </div>
                  ) : (
                    activityFeed.map((item) => (
                      <div key={item.id} className="px-5 py-3 hover:bg-gray-50 transition-colors">
                        <div className="flex items-start gap-3">
                          <span className="text-base leading-none mt-0.5 shrink-0">
                            {getActivityIcon(item.action)}
                          </span>
                          <div className="min-w-0 flex-1">
                            <p className="text-sm text-gray-800 leading-snug">
                              <span className="font-semibold text-gray-900">{item.user_name}</span>{' '}
                              {item.description}
                            </p>
                            <span className="text-xs text-gray-400 mt-0.5 block">
                              {timeAgo(item.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* --- Lead Quality Insights --- */}
              <div className="card">
                <div className="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-rejected-500" />
                  <h2 className="section-title">Lead Insights</h2>
                  {insightsLoading && (
                    <span className="ml-auto">
                      <span className="loading-spinner" />
                    </span>
                  )}
                </div>
                <div className="p-5 space-y-4">
                  {!leadInsights ? (
                    !insightsLoading && (
                      <div className="text-center text-sm text-gray-400 py-4">
                        No insight data available.
                      </div>
                    )
                  ) : (
                    <>
                      {/* Best Source */}
                      {leadInsights.best_source && (
                        <div className="flex items-start gap-3">
                          <div className="p-1.5 rounded-lg bg-primary-50 shrink-0">
                            <Users2 className="w-4 h-4 text-primary-600" />
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Best Source</p>
                            <p className="text-sm font-semibold text-gray-900">
                              {leadInsights.best_source.source}
                            </p>
                            <p className="text-xs text-successful-600 font-medium">
                              {leadInsights.best_source.conversion_rate.toFixed(1)}% conversion
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Best Industry */}
                      {leadInsights.best_industry && (
                        <div className="flex items-start gap-3">
                          <div className="p-1.5 rounded-lg bg-indigo-50 shrink-0">
                            <Building2 className="w-4 h-4 text-indigo-500" />
                          </div>
                          <div>
                            <p className="text-xs text-gray-500">Best Industry</p>
                            <p className="text-sm font-semibold text-gray-900">
                              {leadInsights.best_industry.industry}
                            </p>
                            <p className="text-xs text-successful-600 font-medium">
                              {leadInsights.best_industry.conversion_rate.toFixed(1)}% conversion
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Stale leads & Meeting completion */}
                      <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
                        <div className="text-center p-2.5 rounded-lg bg-gray-50">
                          <div className="flex items-center justify-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5 text-rejected-500" />
                            <span className="text-lg font-bold text-gray-900">
                              {leadInsights.stale_leads}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-0.5">Stale Leads</p>
                        </div>
                        <div className="text-center p-2.5 rounded-lg bg-gray-50">
                          <span className="text-lg font-bold text-primary-600">
                            {leadInsights.avg_meeting_completion.toFixed(0)}%
                          </span>
                          <p className="text-xs text-gray-500 mt-0.5">Meeting Completion</p>
                        </div>
                      </div>

                      {/* Top Sources mini list */}
                      {leadInsights.top_sources && leadInsights.top_sources.length > 0 && (
                        <div className="pt-1">
                          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                            Top Sources
                          </p>
                          <div className="space-y-1.5">
                            {leadInsights.top_sources.slice(0, 3).map((s) => (
                              <div key={s.source} className="flex items-center justify-between text-sm">
                                <span className="text-gray-700 truncate">{s.source}</span>
                                <span className="text-gray-500 font-mono text-xs ml-2">
                                  {s.conversion_rate.toFixed(0)}%
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Top Industries mini list */}
                      {leadInsights.top_industries && leadInsights.top_industries.length > 0 && (
                        <div className="pt-1">
                          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                            Top Industries
                          </p>
                          <div className="space-y-1.5">
                            {leadInsights.top_industries.slice(0, 3).map((ind) => (
                              <div key={ind.industry} className="flex items-center justify-between text-sm">
                                <span className="text-gray-700 truncate">{ind.industry}</span>
                                <span className="text-gray-500 font-mono text-xs ml-2">
                                  {ind.conversion_rate.toFixed(0)}%
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>

              {/* --- Conversion Funnel --- */}
              <div className="card">
                <div className="px-5 py-4 border-b border-gray-200 flex items-center gap-2">
                  <ListFilter className="w-5 h-5 text-primary-600" />
                  <h2 className="section-title">Conversion Funnel</h2>
                </div>
                <div className="p-5 space-y-4">
                  {statusDistArray.length === 0 ? (
                    <div className="text-center text-sm text-gray-400 py-4">
                      No status data available.
                    </div>
                  ) : (
                    ['new', 'active', 'successful', 'rejected', 'cold'].map((status) => {
                      const entry = statusDistArray.find((s) => s.status === status);
                      const count = entry?.count || 0;
                      const pct = (count / statusTotal) * 100;
                      const color = STATUS_COLORS[status] || '#9CA3AF';

                      return (
                        <div key={status}>
                          <div className="flex items-center justify-between text-sm mb-1">
                            <span className="font-medium text-gray-700 capitalize">{status}</span>
                            <span className="font-mono text-gray-500 text-xs font-semibold">
                              {count}
                            </span>
                          </div>
                          <div className="w-full h-2.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all duration-500 ease-out"
                              style={{
                                width: `${pct}%`,
                                backgroundColor: color,
                              }}
                            />
                          </div>
                        </div>
                      );
                    })
                  )}

                  {/* Summary stat */}
                  {dashboard && (
                    <div className="pt-3 border-t border-gray-100 grid grid-cols-2 gap-3">
                      <div className="text-center p-2 rounded-lg bg-successful-50">
                        <p className="text-lg font-bold text-successful-600">
                          {dashboard.total_converted}
                        </p>
                        <p className="text-xs text-gray-500">Converted</p>
                      </div>
                      <div className="text-center p-2 rounded-lg bg-gray-50">
                        <p className="text-lg font-bold text-gray-900">
                          {dashboard.total_leads}
                        </p>
                        <p className="text-xs text-gray-500">Total Leads</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* ============================================================ */}
            {/* Leaderboard */}
            {/* ============================================================ */}
            <div className="card">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-rejected-500" />
                  <h2 className="section-title">Employee Leaderboard</h2>
                </div>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="table-header w-12">#</th>
                      <th className="table-header">Employee</th>
                      <th className="table-header">EMP ID</th>
                      {[
                        { field: 'total_leads', label: 'Total Leads' },
                        { field: 'converted_leads', label: 'Converted' },
                        { field: 'conversion_rate', label: 'Conv. Rate' },
                      ].map((col) => (
                        <th key={col.field} className="table-header">
                          <button
                            className="flex items-center gap-1 hover:text-gray-700"
                            onClick={() => {
                              if (leaderSortField === col.field) {
                                setLeaderSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
                              } else {
                                setLeaderSortField(col.field);
                                setLeaderSortOrder('desc');
                              }
                            }}
                          >
                            {col.label}
                            {leaderSortField === col.field ? (
                              leaderSortOrder === 'asc' ? (
                                <ChevronUp className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronDown className="w-3.5 h-3.5" />
                              )
                            ) : (
                              <ChevronDown className="w-3.5 h-3.5 text-gray-300" />
                            )}
                          </button>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-100">
                    {sortedEmployees.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="px-4 py-12 text-center text-sm text-gray-400">
                          No employees found.
                        </td>
                      </tr>
                    ) : (
                      sortedEmployees.map((emp, idx) => {
                        const isTop = idx === 0;
                        return (
                          <tr
                            key={emp.employee_id}
                            onClick={() => handleEmployeeClick(emp)}
                            className={`hover:bg-gray-50 cursor-pointer transition-colors ${
                              isTop ? 'bg-rejected-50/30' : ''
                            }`}
                          >
                            <td className="table-cell">
                              <span
                                className={`inline-flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold ${
                                  isTop
                                    ? 'bg-rejected-500 text-white'
                                    : idx < 3
                                    ? 'bg-gray-100 text-gray-600'
                                    : 'text-gray-400'
                                }`}
                              >
                                {idx + 1}
                              </span>
                            </td>
                            <td className="table-cell">
                              <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                                  <span className="text-sm font-semibold text-primary-600">
                                    {emp.name.charAt(0)}
                                  </span>
                                </div>
                                <div>
                                  <p className="font-medium text-gray-900">{emp.name}</p>
                                </div>
                              </div>
                            </td>
                            <td className="table-cell text-gray-500 font-mono text-xs">
                              {emp.emp_id || '—'}
                            </td>
                            <td className="table-cell font-medium">{emp.total_leads}</td>
                            <td className="table-cell">{emp.converted_leads}</td>
                            <td className="table-cell">
                              <span
                                className={`font-medium ${
                                  emp.conversion_rate >= 0.5
                                    ? 'text-successful-600'
                                    : emp.conversion_rate >= 0.25
                                    ? 'text-rejected-500'
                                    : 'text-gray-500'
                                }`}
                              >
                                {(emp.conversion_rate * 100).toFixed(1)}%
                              </span>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* ============================================================ */}
            {/* Salary Deduction Rules */}
            {/* ============================================================ */}
            <div className="card">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-primary-600" />
                  <h2 className="section-title">Salary Deduction Rules</h2>
                </div>
                <button className="btn-primary text-sm" onClick={openAddRuleModal}>
                  <Plus className="w-4 h-4" />
                  Add Rule
                </button>
              </div>
              <div className="overflow-x-auto">
                {salaryRulesLoading ? (
                  <div className="flex items-center justify-center py-10">
                    <span className="loading-spinner-lg" />
                  </div>
                ) : salaryRulesError ? (
                  <div className="p-6 text-sm text-cold-600 text-center">{salaryRulesError}</div>
                ) : salaryRules.length === 0 ? (
                  <div className="px-6 py-12 text-center text-sm text-gray-400">
                    No salary deduction rules configured. Click "Add Rule" to create one.
                  </div>
                ) : (
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="table-header">Rule Name</th>
                        <th className="table-header text-right">Min Revenue (₹)</th>
                        <th className="table-header text-right">Max Revenue (₹)</th>
                        <th className="table-header text-right">Deduction %</th>
                        <th className="table-header w-24 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                      {salaryRules.map((rule) => (
                        <tr key={rule.id} className="hover:bg-gray-50 transition-colors">
                          <td className="table-cell font-medium text-gray-900">{rule.rule_name}</td>
                          <td className="table-cell text-right font-mono text-gray-700">
                            ₹{rule.min_revenue.toLocaleString('en-IN')}
                          </td>
                          <td className="table-cell text-right font-mono text-gray-700">
                            {rule.max_revenue >= 999999999
                              ? '∞'
                              : `₹${rule.max_revenue.toLocaleString('en-IN')}`}
                          </td>
                          <td className="table-cell text-right">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                                rule.deduction_percent >= 50
                                  ? 'bg-cold-50 text-cold-700'
                                  : rule.deduction_percent >= 25
                                  ? 'bg-rejected-50 text-rejected-700'
                                  : 'bg-successful-50 text-successful-700'
                              }`}
                            >
                              {rule.deduction_percent}%
                            </span>
                          </td>
                          <td className="table-cell text-right">
                            <div className="flex items-center justify-end gap-1">
                              <button
                                className="btn-ghost p-1.5"
                                title="Edit rule"
                                onClick={() => openEditRuleModal(rule)}
                              >
                                <Edit3 className="w-4 h-4" />
                              </button>
                              <button
                                className="btn-ghost p-1.5 text-cold-500 hover:text-cold-700 hover:bg-cold-50"
                                title="Delete rule"
                                onClick={() => handleDeleteRule(rule.id)}
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* ============================================================ */}
            {/* Monthly Performance Targets */}
            {/* ============================================================ */}
            <div className="card">
              <div className="px-6 py-4 border-b border-gray-200 flex items-center gap-2">
                <Target className="w-5 h-5 text-primary-600" />
                <h2 className="section-title">Monthly Performance Targets</h2>
                {targetsLoading && (
                  <span className="ml-auto">
                    <span className="loading-spinner" />
                  </span>
                )}
              </div>
              <div className="overflow-x-auto">
                {targetsLoading && performanceTargets.length === 0 ? (
                  <div className="flex items-center justify-center py-10">
                    <span className="loading-spinner-lg" />
                  </div>
                ) : performanceTargets.length === 0 ? (
                  <div className="px-6 py-12 text-center text-sm text-gray-400">
                    No performance targets set for this month.
                  </div>
                ) : (
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="table-header">Employee</th>
                        <th className="table-header text-right">Target (₹)</th>
                        <th className="table-header text-right">Actual (₹)</th>
                        <th className="table-header text-right">Progress</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                      {performanceTargets.map((target, idx) => {
                        const progress =
                          target.target_revenue > 0
                            ? Math.min((target.actual_revenue / target.target_revenue) * 100, 100)
                            : 0;
                        return (
                          <tr key={target.employee_id || idx} className="hover:bg-gray-50 transition-colors">
                            <td className="table-cell font-medium text-gray-900">
                              {target.employee_name}
                            </td>
                            <td className="table-cell text-right font-mono">
                              ₹{target.target_revenue.toLocaleString('en-IN')}
                            </td>
                            <td className="table-cell text-right font-mono">
                              ₹{target.actual_revenue.toLocaleString('en-IN')}
                            </td>
                            <td className="table-cell text-right">
                              <div className="flex items-center justify-end gap-3">
                                <div className="w-32 bg-gray-200 rounded-full h-2.5 overflow-hidden">
                                  <div
                                    className={`h-full rounded-full transition-all duration-500 ${
                                      progress >= 100
                                        ? 'bg-successful-500'
                                        : progress >= 50
                                        ? 'bg-primary-500'
                                        : 'bg-rejected-500'
                                    }`}
                                    style={{ width: `${progress}%` }}
                                  />
                                </div>
                                <span className="text-xs font-semibold text-gray-600 min-w-[3rem] text-right">
                                  {progress.toFixed(0)}%
                                </span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            {/* ============================================================ */}
            {/* Charts Row */}
            {/* ============================================================ */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Monthly Trend Chart */}
              <div className="card p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Activity className="w-5 h-5 text-primary-600" />
                  <h2 className="section-title">Monthly Trends</h2>
                </div>
                {dashboard?.monthly_trend && dashboard.monthly_trend.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <AreaChart data={dashboard.monthly_trend}>
                      <defs>
                        <linearGradient id="createdGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#6366F1" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="convertedGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                          <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                      <XAxis
                        dataKey="month"
                        tickFormatter={formatMonth}
                        tick={{ fontSize: 12, fill: '#9CA3AF' }}
                        axisLine={{ stroke: '#E5E7EB' }}
                      />
                      <YAxis tick={{ fontSize: 12, fill: '#9CA3AF' }} axisLine={false} />
                      <Tooltip
                        contentStyle={{
                          background: '#fff',
                          border: '1px solid #E5E7EB',
                          borderRadius: '8px',
                          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                        }}
                        labelFormatter={(label) => formatMonth(label)}
                      />
                      <Area
                        type="monotone"
                        dataKey="total"
                        stroke="#6366F1"
                        fill="url(#createdGrad)"
                        strokeWidth={2}
                        name="Total Leads"
                      />
                      <Area
                        type="monotone"
                        dataKey="successful"
                        stroke="#10B981"
                        fill="url(#convertedGrad)"
                        strokeWidth={2}
                        name="Converted"
                      />
                      <Legend />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[280px] text-sm text-gray-400">
                    No monthly trend data available.
                  </div>
                )}
              </div>

              {/* Status Distribution Pie */}
              <div className="card p-6">
                <div className="flex items-center gap-2 mb-4">
                  <PieChartIcon className="w-5 h-5 text-primary-600" />
                  <h2 className="section-title">Status Distribution</h2>
                </div>
                {statusDistArray.length > 0 ? (
                  <ResponsiveContainer width="100%" height={280}>
                    <PieChart>
                      <Pie
                        data={statusDistArray}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={100}
                        paddingAngle={3}
                        dataKey="count"
                        nameKey="status"
                        label={({ status, count, percent }) =>
                          `${status} ${(percent * 100).toFixed(0)}%`
                        }
                        labelLine={false}
                      >
                        {statusDistArray.map((entry) => (
                          <Cell
                            key={entry.status}
                            fill={PIE_COLORS[entry.status] || '#9CA3AF'}
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-[280px] text-sm text-gray-400">
                    No status data available.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ================================================================ */}
      {/* Employee Detail Modal (drill-down) */}
      {/* ================================================================ */}
      {selectedEmployee && (
        <div className="modal-overlay animate-fade-in" onClick={() => setSelectedEmployee(null)}>
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-y-auto border border-gray-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
                    <span className="text-lg font-bold text-primary-600">
                      {selectedEmployee.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">{selectedEmployee.name}</h2>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedEmployee(null)}
                  className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                >
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              {/* Mini stats */}
              <div className="grid grid-cols-3 gap-4 mt-4">
                <div className="text-center p-2 rounded-lg bg-gray-50">
                  <p className="text-xs text-gray-500">Total Leads</p>
                  <p className="text-lg font-bold text-gray-900">{selectedEmployee.total_leads}</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-gray-50">
                  <p className="text-xs text-gray-500">Converted</p>
                  <p className="text-lg font-bold text-successful-600">{selectedEmployee.converted_leads}</p>
                </div>
                <div className="text-center p-2 rounded-lg bg-gray-50">
                  <p className="text-xs text-gray-500">Conv. Rate</p>
                  <p className="text-lg font-bold text-primary-600">{(selectedEmployee.conversion_rate * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>

            {/* Employee's leads table */}
            <div className="p-6">
              <LeadTable
                leads={employeeLeads}
                loading={employeeLeadsLoading}
                totalCount={empTotalCount}
                page={empPage}
                pageSize={10}
                search={empSearch}
                statusFilter={empStatusFilter}
                onSearchChange={(v) => { setEmpSearch(v); setEmpPage(1); }}
                onStatusFilterChange={(v) => { setEmpStatusFilter(v); setEmpPage(1); }}
                onPageChange={setEmpPage}
                onSortChange={(f) => {
                  if (empSortField === f) setEmpSortOrder((o) => (o === 'asc' ? 'desc' : 'asc'));
                  else { setEmpSortField(f); setEmpSortOrder('desc'); }
                }}
                sortField={empSortField}
                sortOrder={empSortOrder}
                onAddLead={() => {}}
                onLeadClick={handleLeadClick}
              />
            </div>
          </div>
        </div>
      )}

      {/* Lead View Modal */}
      <LeadModal
        open={leadModalOpen}
        onClose={() => setLeadModalOpen(false)}
        lead={selectedLead}
        mode={leadModalMode}
      />

      {/* ================================================================ */}
      {/* Salary Rule Modal (Add / Edit) */}
      {/* ================================================================ */}
      {ruleModalOpen && (
        <div className="modal-overlay animate-fade-in" onClick={() => !ruleSaving && setRuleModalOpen(false)}>
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-gray-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                {editingRule ? 'Edit Salary Deduction Rule' : 'Add Salary Deduction Rule'}
              </h2>
              <button
                onClick={() => !ruleSaving && setRuleModalOpen(false)}
                className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100"
                disabled={ruleSaving}
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Form */}
            <div className="p-6 space-y-5">
              {/* Rule Name */}
              <div>
                <label className="input-label">Rule Name</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Below 50K"
                  value={ruleFormName}
                  onChange={(e) => setRuleFormName(e.target.value)}
                  disabled={ruleSaving}
                />
              </div>

              {/* Min Revenue */}
              <div>
                <label className="input-label">Min Revenue (₹)</label>
                <input
                  type="number"
                  className="input-field"
                  placeholder="0"
                  min={0}
                  value={ruleFormMinRev}
                  onChange={(e) => setRuleFormMinRev(e.target.value)}
                  disabled={ruleSaving}
                />
              </div>

              {/* Max Revenue */}
              <div>
                <label className="input-label">
                  Max Revenue (₹) <span className="text-gray-400 font-normal">— leave empty for unlimited</span>
                </label>
                <input
                  type="number"
                  className="input-field"
                  placeholder="Leave empty for ∞"
                  min={0}
                  value={ruleFormMaxRev}
                  onChange={(e) => setRuleFormMaxRev(e.target.value)}
                  disabled={ruleSaving}
                />
              </div>

              {/* Deduction % */}
              <div>
                <label className="input-label">Deduction %</label>
                <input
                  type="number"
                  className="input-field"
                  placeholder="0 – 100"
                  min={0}
                  max={100}
                  value={ruleFormDeduction}
                  onChange={(e) => setRuleFormDeduction(e.target.value)}
                  disabled={ruleSaving}
                />
              </div>

              {/* Error */}
              {ruleFormError && (
                <div className="p-3 rounded-lg bg-cold-50 border border-cold-200 text-sm text-cold-700">
                  {ruleFormError}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  className="btn-secondary"
                  onClick={() => setRuleModalOpen(false)}
                  disabled={ruleSaving}
                >
                  Cancel
                </button>
                <button className="btn-primary" onClick={handleSaveRule} disabled={ruleSaving}>
                  {ruleSaving ? (
                    <>
                      <span className="loading-spinner" />
                      Saving…
                    </>
                  ) : (
                    'Save Rule'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}
