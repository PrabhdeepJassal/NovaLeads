// ============================================================
// NovaLeads — Lead Table Component
// ============================================================

import {
  Search,
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  ChevronLeft,
  ChevronRight,
  Plus,
} from 'lucide-react';
import type { Lead, LeadStatus } from '../types';
import PredictionBadge, { getStatusBadge } from './PredictionBadge';
import LoadingSpinner from './LoadingSpinner';
import EmptyState from './EmptyState';

interface LeadTableProps {
  leads: Lead[];
  loading: boolean;
  totalCount: number;
  page: number;
  pageSize: number;
  search: string;
  statusFilter: string;
  onSearchChange: (value: string) => void;
  onStatusFilterChange: (value: string) => void;
  onPageChange: (page: number) => void;
  onSortChange: (field: string) => void;
  sortField: string;
  sortOrder: 'asc' | 'desc';
  onAddLead: () => void;
  onLeadClick: (lead: Lead) => void;
}

const STATUS_TABS = [
  { value: '', label: 'All', color: 'bg-gray-100 text-gray-700' },
  { value: 'active', label: 'Active', color: 'bg-indigo-100 text-indigo-700' },
  { value: 'cold', label: 'Cold', color: 'bg-cold-50 text-cold-600' },
  { value: 'rejected', label: 'Rejected', color: 'bg-rejected-50 text-rejected-600' },
  { value: 'successful', label: 'Successful', color: 'bg-successful-50 text-successful-600' },
];

export default function LeadTable({
  leads,
  loading,
  totalCount,
  page,
  pageSize,
  search,
  statusFilter,
  onSearchChange,
  onStatusFilterChange,
  onPageChange,
  onSortChange,
  sortField,
  sortOrder,
  onAddLead,
  onLeadClick,
}: LeadTableProps) {
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  const getSortIcon = (field: string) => {
    if (sortField !== field) return <ChevronsUpDown className="w-3.5 h-3.5 text-gray-300" />;
    return sortOrder === 'asc' ? (
      <ChevronUp className="w-3.5 h-3.5 text-primary-600" />
    ) : (
      <ChevronDown className="w-3.5 h-3.5 text-primary-600" />
    );
  };

  const handleSort = (field: string) => {
    onSortChange(field);
  };

  return (
    <div className="space-y-4">
      {/* Toolbar: Search + Status Filters + Add Button */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            className="input-field pl-9 pr-3"
            placeholder="Search by company or contact..."
            value={search}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          {/* Status filter tabs (horizontal scroll on mobile) */}
          <div className="flex gap-1 overflow-x-auto flex-1 sm:flex-none">
            {STATUS_TABS.map((tab) => (
              <button
                key={tab.value}
                onClick={() => onStatusFilterChange(tab.value)}
                className={`tab-button whitespace-nowrap ${
                  statusFilter === tab.value ? 'tab-button-active' : 'tab-button-inactive'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <button className="btn-primary flex-shrink-0" onClick={onAddLead}>
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Add Lead</span>
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          {loading ? (
            <div className="py-16">
              <LoadingSpinner size="lg" text="Loading leads..." />
            </div>
          ) : leads.length === 0 ? (
            <EmptyState
              title="No leads found"
              description={
                search || statusFilter
                  ? 'Try adjusting your search or filter criteria.'
                  : 'Get started by adding your first lead.'
              }
              action={
                !search && !statusFilter ? (
                  <button className="btn-primary" onClick={onAddLead}>
                    <Plus className="w-4 h-4" />
                    Add Your First Lead
                  </button>
                ) : undefined
              }
            />
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {[
                    { field: 'company_name', label: 'Company' },
                    { field: 'contact_name', label: 'Contact' },
                    { field: 'lead_source', label: 'Source' },
                    { field: 'status', label: 'Status' },
                    { field: 'prediction', label: 'ML Prediction' },
                    { field: 'created_at', label: 'Created' },
                    { field: '', label: 'Actions' },
                  ].map((col) => (
                    <th
                      key={col.field || Math.random().toString()}
                      className="table-header"
                    >
                      {col.field ? (
                        <button
                          className="flex items-center gap-1 hover:text-gray-700 transition-colors"
                          onClick={() => handleSort(col.field)}
                        >
                          {col.label}
                          {getSortIcon(col.field)}
                        </button>
                      ) : (
                        col.label
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-100">
                {leads.map((lead) => (
                  <tr
                    key={lead.id}
                    onClick={() => onLeadClick(lead)}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <td className="table-cell font-medium text-gray-900">
                      {lead.company_name}
                    </td>
                    <td className="table-cell">{lead.contact_name}</td>
                    <td className="table-cell">
                      <span className="text-xs bg-gray-100 text-gray-600 rounded-full px-2.5 py-0.5 font-medium capitalize">
                        {(lead.lead_source || '').replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="table-cell">{getStatusBadge(lead.status)}</td>
                    <td className="table-cell">
                      {lead.predicted_outcome ? (
                        <PredictionBadge
                          predicted_outcome={lead.predicted_outcome}
                          confidence={lead.prediction_confidence}
                        />
                      ) : (
                        <span className="text-xs text-gray-400 italic">Pending</span>
                      )}
                    </td>
                    <td className="table-cell text-gray-500">
                      {new Date(lead.created_at).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="table-cell">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onLeadClick(lead);
                        }}
                        className="text-xs font-medium text-primary-600 hover:text-primary-700"
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Pagination */}
        {!loading && totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-sm text-gray-500">
              Showing{' '}
              <span className="font-medium text-gray-700">
                {(page - 1) * pageSize + 1}
              </span>{' '}
              to{' '}
              <span className="font-medium text-gray-700">
                {Math.min(page * pageSize, totalCount)}
              </span>{' '}
              of{' '}
              <span className="font-medium text-gray-700">{totalCount}</span> leads
            </p>
            <div className="flex items-center gap-1">
              <button
                className="btn-ghost p-1.5 disabled:opacity-30"
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(
                  (p) =>
                    p === 1 ||
                    p === totalPages ||
                    Math.abs(p - page) <= 1
                )
                .map((p, idx, arr) => (
                  <span key={p} className="flex items-center">
                    {idx > 0 && arr[idx - 1] !== p - 1 && (
                      <span className="px-1 text-gray-300">...</span>
                    )}
                    <button
                      className={`w-8 h-8 text-sm font-medium rounded-lg transition-colors ${
                        p === page
                          ? 'bg-primary-50 text-primary-700'
                          : 'text-gray-500 hover:bg-gray-100'
                      }`}
                      onClick={() => onPageChange(p)}
                    >
                      {p}
                    </button>
                  </span>
                ))}
              <button
                className="btn-ghost p-1.5 disabled:opacity-30"
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
