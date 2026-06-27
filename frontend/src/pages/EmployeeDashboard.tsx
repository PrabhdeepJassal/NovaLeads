// ============================================================
// NovaLeads — Employee Dashboard
// ============================================================

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  getLeads,
  createLead,
  updateLead,
  type LeadsQueryParams,
} from '../services/leads';
import { getEmployeeDashboard, getMySalaryInfo } from '../services/employee';
import type { Lead, CreateLeadData, EmployeeDashboard as EmployeeDashboardType, EmployeeSalaryInfo } from '../types';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import LeadTable from '../components/LeadTable';
import LeadModal from '../components/LeadModal';
import { getErrorMessage } from '../services/api';
import {
  Users,
  Snowflake,
  XCircle,
  CheckCircle,
  TrendingUp,
  Target,
  BarChart3,
  RefreshCw,
} from 'lucide-react';

export default function EmployeeDashboard() {
  const { user } = useAuth();

  // Data state
  const [leads, setLeads] = useState<Lead[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Employee dashboard stats from backend
  const [dashboardStats, setDashboardStats] = useState<EmployeeDashboardType | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);

  // Salary info
  const [salaryInfo, setSalaryInfo] = useState<EmployeeSalaryInfo | null>(null);
  const [salaryLoading, setSalaryLoading] = useState(true);

  // Filters & pagination
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [sortField, setSortField] = useState('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const pageSize = 10;

  // Modal state
  const [modalOpen, setModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'view' | 'edit'>('create');
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [modalLoading, setModalLoading] = useState(false);

  // Fetch employee dashboard stats + salary info
  const fetchDashboardStats = useCallback(async () => {
    setStatsLoading(true);
    try {
      const data = await getEmployeeDashboard();
      setDashboardStats(data);
    } catch {
      // Stats are optional; don't block the page
    } finally {
      setStatsLoading(false);
    }
    // Fetch salary info
    try {
      const salary = await getMySalaryInfo();
      setSalaryInfo(salary);
    } catch {
      // Optional
    } finally {
      setSalaryLoading(false);
    }
  }, []);

  // Fetch leads
  const fetchLeads = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params: LeadsQueryParams = {
        page,
        page_size: pageSize,
        search: search || undefined,
        status: statusFilter || undefined,
        ordering: `${sortOrder === 'desc' ? '-' : ''}${sortField}`,
      };
      const data = await getLeads(params);
      setLeads(data.items);
      setTotalCount(data.total);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [page, search, statusFilter, sortField, sortOrder]);

  useEffect(() => {
    fetchLeads();
  }, [fetchLeads]);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  // Search debounce
  const [searchTimeout, setSearchTimeout] = useState<ReturnType<typeof setTimeout> | null>(null);
  const handleSearchChange = (value: string) => {
    if (searchTimeout) clearTimeout(searchTimeout);
    const timeout = setTimeout(() => {
      setSearch(value);
      setPage(1);
    }, 300);
    setSearchTimeout(timeout);
  };

  // Status filter
  const handleStatusFilterChange = (value: string) => {
    setStatusFilter(value);
    setPage(1);
  };

  // Sort
  const handleSortChange = (field: string) => {
    if (sortField === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortOrder('desc');
    }
  };

  // Add lead
  const handleAddLead = () => {
    setSelectedLead(null);
    setModalMode('create');
    setModalOpen(true);
  };

  // View lead
  const handleLeadClick = (lead: Lead) => {
    setSelectedLead(lead);
    setModalMode('view');
    setModalOpen(true);
  };

  // Submit new lead — backend auto-predicts, no separate predict call needed
  const handleCreateLead = async (data: CreateLeadData) => {
    setModalLoading(true);
    try {
      await createLead(data);
      setModalOpen(false);
      fetchLeads();
      fetchDashboardStats();
    } catch (err) {
      throw new Error(getErrorMessage(err));
    } finally {
      setModalLoading(false);
    }
  };

  // Called after any inline activity log in the modal (view mode)
  const handleLeadUpdated = useCallback(() => {
    fetchLeads();
    fetchDashboardStats();
  }, [fetchLeads, fetchDashboardStats]);

  // Update lead
  const handleUpdateLead = async (id: string, data: Partial<CreateLeadData & { status: string }>) => {
    setModalLoading(true);
    try {
      await updateLead(id, data);
      setModalOpen(false);
      fetchLeads();
      fetchDashboardStats();
    } catch (err) {
      throw new Error(getErrorMessage(err));
    } finally {
      setModalLoading(false);
    }
  };

  // Use stats from backend dashboard, or compute simple fallback from local leads
  const stats = dashboardStats
    ? {
        total: dashboardStats.total_leads,
        cold: dashboardStats.cold_leads,
        rejected: dashboardStats.rejected_leads,
        successful: dashboardStats.successful_leads,
        conversionRate: Math.round(dashboardStats.conversion_rate * 100),
      }
    : {
        total: totalCount,
        cold: leads.filter((l) => l.predicted_outcome === 'cold').length,
        rejected: leads.filter((l) => l.predicted_outcome === 'rejected').length,
        successful: leads.filter((l) => l.predicted_outcome === 'successful').length,
        conversionRate: totalCount > 0
          ? Math.round((leads.filter((l) => l.predicted_outcome === 'successful').length / totalCount) * 100)
          : 0,
      };

  return (
    <Layout>
      <div className="page-container">
        {/* Welcome Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="page-title">
              Welcome back, {user?.name?.split(' ')[0] || 'User'}
              {user?.emp_id && (
                <span className="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 align-middle">
                  {user.emp_id}
                </span>
              )}
            </h1>
            <p className="page-subtitle">Here's an overview of your leads and predictions.</p>
          </div>
          <button className="btn-secondary" onClick={() => { fetchLeads(); fetchDashboardStats(); }}>
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-cold-50 border border-cold-200 text-sm text-cold-700 animate-fade-in">
            {error}
            <button className="ml-2 underline font-medium" onClick={fetchLeads}>Try again</button>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <StatCard
            icon={<Users className="w-5 h-5" />}
            label="Total Leads"
            value={stats.total}
            colorClass="text-primary-600 bg-primary-50"
          />
          <StatCard
            icon={<Snowflake className="w-5 h-5" />}
            label="Cold"
            value={stats.cold}
            colorClass="text-cold-500 bg-cold-50"
          />
          <StatCard
            icon={<XCircle className="w-5 h-5" />}
            label="Rejected"
            value={stats.rejected}
            colorClass="text-rejected-500 bg-rejected-50"
          />
          <StatCard
            icon={<CheckCircle className="w-5 h-5" />}
            label="Successful"
            value={stats.successful}
            colorClass="text-successful-500 bg-successful-50"
          />
          <StatCard
            icon={<TrendingUp className="w-5 h-5" />}
            label="Conversion Rate"
            value={`${stats.conversionRate}%`}
            colorClass="text-primary-500 bg-primary-50"
          />
        </div>

        {/* Salary Info Card */}
        {salaryInfo && (
          <div className="card p-5 mb-6 border-l-4 border-l-amber-500">
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp className="w-5 h-5 text-amber-600" />
              <h2 className="section-title text-amber-900">💰 Salary This Month</h2>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
              <div>
                <p className="text-xs text-gray-500">Target Revenue</p>
                <p className="text-lg font-bold text-gray-900">₹{salaryInfo.target_revenue.toLocaleString('en-IN')}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Actual Revenue</p>
                <p className="text-lg font-bold text-gray-900">₹{salaryInfo.actual_revenue.toLocaleString('en-IN')}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Progress</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(100, (salaryInfo.actual_revenue / salaryInfo.target_revenue) * 100)}%`,
                        backgroundColor: salaryInfo.actual_revenue >= salaryInfo.target_revenue ? '#10B981' : '#F59E0B'
                      }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-500">
                    {Math.min(100, Math.round((salaryInfo.actual_revenue / salaryInfo.target_revenue) * 100))}%
                  </span>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500">Deduction Rule</p>
                <p className="text-sm font-semibold text-amber-700">{salaryInfo.applicable_rule}</p>
                <p className="text-xs text-gray-400">-{salaryInfo.deduction_percent}% deduction</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Take-home</p>
                <p className={`text-lg font-bold ${salaryInfo.take_home_percent >= 100 ? 'text-successful-600' : salaryInfo.take_home_percent >= 50 ? 'text-rejected-500' : 'text-cold-500'}`}>
                  {salaryInfo.take_home_percent}%
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Lead Table */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-primary-600" />
            <h2 className="section-title">Your Leads</h2>
          </div>
          <LeadTable
            leads={leads}
            loading={loading}
            totalCount={totalCount}
            page={page}
            pageSize={pageSize}
            search={search}
            statusFilter={statusFilter}
            onSearchChange={handleSearchChange}
            onStatusFilterChange={handleStatusFilterChange}
            onPageChange={setPage}
            onSortChange={handleSortChange}
            sortField={sortField}
            sortOrder={sortOrder}
            onAddLead={handleAddLead}
            onLeadClick={handleLeadClick}
          />
        </div>
      </div>

      {/* Lead Modal */}
      <LeadModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={handleCreateLead}
        onUpdate={handleUpdateLead}
        onLeadUpdated={handleLeadUpdated}
        lead={selectedLead}
        mode={modalMode}
        loading={modalLoading}
      />
    </Layout>
  );
}
