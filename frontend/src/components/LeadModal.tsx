// ============================================================
// NovaLeads — Lead Modal (Create / View / Edit)
// ============================================================

import { useState, useEffect } from 'react';
import {
  X,
  Building2,
  User,
  Mail,
  Phone,
  Globe,
  Briefcase,
  Users as UsersIcon,
  FileText,
  Save,
  Edit3,
  Loader2,
  Clock,
  Activity,
  PhoneCall,
  Calendar,
  Play,
  DollarSign,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import type { Lead, CreateLeadData, ActivityLog } from '../types';
import api, { getErrorMessage } from '../services/api';
import { getLeadActivity } from '../services/leads';
import PredictionBadge from './PredictionBadge';
import LoadingSpinner from './LoadingSpinner';

interface LeadModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit?: (data: CreateLeadData) => Promise<void>;
  onUpdate?: (id: string, data: Partial<CreateLeadData & { status: string }>) => Promise<void>;
  onLeadUpdated?: () => void;
  lead?: Lead | null;
  mode: 'create' | 'view' | 'edit';
  loading?: boolean;
}

const SOURCE_OPTIONS = [
  { value: 'Google Ads', label: 'Google Ads' },
  { value: 'Facebook', label: 'Facebook' },
  { value: 'LinkedIn', label: 'LinkedIn' },
  { value: 'Referral', label: 'Referral' },
  { value: 'Organic', label: 'Organic' },
  { value: 'Cold Call', label: 'Cold Call' },
  { value: 'Email Campaign', label: 'Email Campaign' },
];

const INDUSTRY_OPTIONS = [
  { value: 'Technology', label: 'Technology' },
  { value: 'Healthcare', label: 'Healthcare' },
  { value: 'Finance', label: 'Finance' },
  { value: 'Education', label: 'Education' },
  { value: 'Real Estate', label: 'Real Estate' },
  { value: 'E-Commerce', label: 'E-Commerce' },
  { value: 'Manufacturing', label: 'Manufacturing' },
  { value: 'Consulting', label: 'Consulting' },
  { value: 'Other', label: 'Other' },
];

const STATUS_OPTIONS = [
  { value: 'new', label: 'New' },
  { value: 'active', label: 'Active' },
  { value: 'cold', label: 'Cold' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'successful', label: 'Successful' },
];

const defaultForm: CreateLeadData = {
  company_name: '',
  contact_name: '',
  contact_email: '',
  contact_phone: '',
  lead_source: 'Referral',
  industry: 'Technology',
  company_size: 10,
  notes: '',
  website_visits: 0,
  emails_opened: 0,
  emails_clicked: 0,
  calls_made: 0,
  calls_connected: 0,
  call_duration_minutes: 0,
  meetings_scheduled: 0,
  meetings_done: 0,
  days_since_first_contact: 1,
  follow_ups_total: 0,
  demo_requested: false,
  budget_available: false,
  decision_maker_contacted: false,
  competitor_considering: false,
  revenue: 0,
};

export default function LeadModal({
  open,
  onClose,
  onSubmit,
  onUpdate,
  onLeadUpdated,
  lead,
  mode,
  loading = false,
}: LeadModalProps) {
  const [form, setForm] = useState<CreateLeadData>({ ...defaultForm });
  const [status, setStatus] = useState<string>('new');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [activityLog, setActivityLog] = useState<ActivityLog[]>([]);
  const [activityLoading, setActivityLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'details' | 'prediction' | 'activity'>('details');
  const [engagementOpen, setEngagementOpen] = useState(false);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const [refreshedLead, setRefreshedLead] = useState<Lead | null>(null);
  const [activityLogging, setActivityLogging] = useState(false);
  const [callDurationInput, setCallDurationInput] = useState<string>('');
  const [revenueInput, setRevenueInput] = useState<string>('');

  // Initialize form when lead changes
  useEffect(() => {
    if (lead && (mode === 'view' || mode === 'edit')) {
      setForm({
        company_name: lead.company_name,
        contact_name: lead.contact_name,
        contact_email: lead.contact_email,
        contact_phone: lead.contact_phone || '',
        lead_source: lead.lead_source,
        industry: lead.industry,
        company_size: lead.company_size || 10,
        notes: lead.notes || '',
        website_visits: lead.website_visits || 0,
        emails_opened: lead.emails_opened || 0,
        emails_clicked: lead.emails_clicked || 0,
        calls_made: lead.calls_made || 0,
        calls_connected: lead.calls_connected || 0,
        meetings_scheduled: lead.meetings_scheduled || 0,
        meetings_done: lead.meetings_done || 0,
        days_since_first_contact: lead.days_since_first_contact || 1,
        follow_ups_total: lead.follow_ups_total || 0,
        demo_requested: lead.demo_requested || false,
        budget_available: lead.budget_available || false,
        decision_maker_contacted: lead.decision_maker_contacted || false,
        competitor_considering: lead.competitor_considering || false,
        revenue: lead.revenue || 0,
      });
      setStatus(lead.status);
    } else {
      setForm({ ...defaultForm });
      setStatus('new');
    }
    setErrors({});
    setActiveTab('details');
    setActivityLog([]);
    setRefreshedLead(null);
    setEngagementOpen(false);
    setNotification(null);
    setCallDurationInput('');
  }, [lead, mode, open]);

  // Load activity log when viewing a lead
  useEffect(() => {
    if (open && lead && mode === 'view') {
      setActivityLoading(true);
      getLeadActivity(lead.id)
        .then(setActivityLog)
        .catch(() => setActivityLog([]))
        .finally(() => setActivityLoading(false));
    }
  }, [open, lead, mode]);

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!form.company_name.trim()) newErrors.company_name = 'Company name is required';
    if (!form.contact_name.trim()) newErrors.contact_name = 'Contact name is required';
    if (!form.contact_email.trim()) newErrors.contact_email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(form.contact_email)) newErrors.contact_email = 'Invalid email';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    if (mode === 'edit' && lead && onUpdate) {
      await onUpdate(lead.id, { ...form, status });
    } else if (onSubmit) {
      await onSubmit(form);
    }
  };

  const handleChange = (field: keyof CreateLeadData, value: string | number | boolean | undefined) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: '' }));
  };

  // Quick activity logging via PATCH — updates lead, refreshes prediction
  const handleLogActivity = async (payload: Partial<CreateLeadData>) => {
    if (!lead) return;
    setActivityLogging(true);
    try {
      const { data: updatedLead } = await api.patch<Lead>(`/leads/${lead.id}`, payload);
      setRefreshedLead(updatedLead);
      // Sync form state with the refreshed lead data
      setForm((prev) => ({
        ...prev,
        website_visits: updatedLead.website_visits,
        emails_opened: updatedLead.emails_opened,
        emails_clicked: updatedLead.emails_clicked,
        calls_made: updatedLead.calls_made,
        calls_connected: updatedLead.calls_connected,
        meetings_scheduled: updatedLead.meetings_scheduled,
        meetings_done: updatedLead.meetings_done,
        days_since_first_contact: updatedLead.days_since_first_contact,
        follow_ups_total: updatedLead.follow_ups_total,
        demo_requested: updatedLead.demo_requested,
        budget_available: updatedLead.budget_available,
        decision_maker_contacted: updatedLead.decision_maker_contacted,
        competitor_considering: updatedLead.competitor_considering,
        revenue: updatedLead.revenue,
      }));
      setNotification({ type: 'success', message: 'Activity logged — prediction updated!' });
      setTimeout(() => setNotification(null), 3000);
      onLeadUpdated?.();
    } catch (err) {
      setNotification({ type: 'error', message: getErrorMessage(err) });
      setTimeout(() => setNotification(null), 4000);
    } finally {
      setActivityLogging(false);
    }
  };

  if (!open) return null;

  const currentLead = refreshedLead || lead;

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-gray-200 animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 sticky top-0 bg-white z-10 rounded-t-2xl">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">
              {mode === 'create' ? 'New Lead' : mode === 'edit' ? 'Edit Lead' : currentLead?.company_name || 'Lead Details'}
            </h2>
            {mode === 'view' && currentLead && (
              <p className="text-sm text-gray-500 mt-0.5">
                Created {new Date(currentLead.created_at).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Notification banner */}
        {notification && (
          <div
            className={`mx-6 mt-4 px-4 py-3 rounded-lg text-sm flex items-center gap-2 animate-fade-in ${
              notification.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {notification.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 shrink-0" />
            )}
            {notification.message}
          </div>
        )}

        {/* View mode tabs */}
        {mode === 'view' && currentLead && (
          <div className="px-6 pt-4 border-b border-gray-200">
            <div className="flex gap-1">
              {(['details', 'prediction', 'activity'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`tab-button capitalize ${
                    activeTab === tab ? 'tab-button-active' : 'tab-button-inactive'
                  }`}
                >
                  {tab === 'details' && <Building2 className="w-4 h-4 mr-1.5 inline" />}
                  {tab === 'prediction' && <Loader2 className="w-4 h-4 mr-1.5 inline" />}
                  {tab === 'activity' && <Activity className="w-4 h-4 mr-1.5 inline" />}
                  {tab}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Body */}
        <div className="px-6 py-5">
          {/* View mode — prediction tab */}
          {mode === 'view' && activeTab === 'prediction' && currentLead && (
            <div className="space-y-6">
              <div>
                <h4 className="text-sm font-semibold text-gray-700 mb-3">ML Prediction</h4>
                <PredictionBadge predicted_outcome={currentLead.predicted_outcome} confidence={currentLead.prediction_confidence} size="md" />
              </div>
              {currentLead.predicted_at && (
                <p className="text-xs text-gray-400">
                  Predicted at {new Date(currentLead.predicted_at).toLocaleString()}
                </p>
              )}
              {refreshedLead && (
                <p className="text-xs text-green-600 font-medium flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Prediction refreshed after recent activity
                </p>
              )}
            </div>
          )}

          {/* View mode — activity tab */}
          {mode === 'view' && activeTab === 'activity' && (
            <div>
              {activityLoading ? (
                <LoadingSpinner text="Loading activity..." className="py-8" />
              ) : activityLog.length === 0 ? (
                <div className="text-center py-8 text-gray-500 text-sm">No activity recorded yet.</div>
              ) : (
                <div className="space-y-3">
                  {activityLog.map((log) => (
                    <div key={log.id} className="flex items-start gap-3 pb-3 border-b border-gray-100 last:border-0">
                      <div className="p-1.5 rounded-full bg-gray-100">
                        <Clock className="w-3.5 h-3.5 text-gray-500" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-700">
                          <span className="font-medium">{log.user_name}</span>{' '}
                          {log.description}
                        </p>
                        <p className="text-xs text-gray-400 mt-0.5">
                          {new Date(log.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Create / Edit form OR View details tab */}
          {(mode !== 'view' || activeTab === 'details') && (
            <form onSubmit={handleSubmit} className="space-y-5">
              {mode === 'view' && currentLead && (
                <div className="mb-2">
                  <span className="text-xs text-gray-500 uppercase tracking-wider font-medium">Lead Information</span>
                  <div className="mt-3 flex items-center gap-2">
                    <PredictionBadge predicted_outcome={currentLead.status} />
                    {currentLead.predicted_outcome && (
                      <PredictionBadge predicted_outcome={currentLead.predicted_outcome} confidence={currentLead.prediction_confidence} />
                    )}
                  </div>
                </div>
              )}

              {/* Quick Activity Logger — View mode only */}
              {mode === 'view' && currentLead && (
                <div className="border border-gray-200 rounded-xl p-4 bg-gray-50/50">
                  <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5" />
                    Log Activity
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {callDurationInput !== 'active' ? (
                      <button
                        type="button"
                        onClick={() => setCallDurationInput('active')}
                        disabled={activityLogging}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <PhoneCall className="w-3.5 h-3.5" />
                        Call
                      </button>
                    ) : (
                      <div className="flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-full px-3 py-1.5">
                        <span className="text-xs text-blue-700 font-medium">Call:</span>
                        <input
                          type="number"
                          className="w-16 text-xs border border-blue-200 rounded-md px-2 py-1 text-center"
                          placeholder="min"
                          min={1}
                          value={callDurationInput === 'active' ? '' : callDurationInput}
                          onChange={(e) => setCallDurationInput(e.target.value)}
                          autoFocus
                        />
                        <span className="text-xs text-gray-500">min</span>
                        <button
                          type="button"
                          onClick={() => {
                            const mins = parseInt(callDurationInput) || 5;
                            handleLogActivity({
                              calls_made: (form.calls_made || 0) + 1,
                              calls_connected: (form.calls_connected || 0) + 1,
                              call_duration_minutes: (form.call_duration_minutes || 0) + mins,
                            });
    setCallDurationInput('');
    setRevenueInput('');
                          }}
                          disabled={activityLogging}
                          className="text-xs font-semibold text-blue-700 hover:text-blue-800 ml-1"
                        >
                          Log
                        </button>
                        <button
                          type="button"
                          onClick={() => setCallDurationInput('')}
                          className="text-gray-400 hover:text-gray-600 ml-0.5"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                    <button
                      type="button"
                      onClick={() =>
                        handleLogActivity({
                          emails_opened: (form.emails_opened || 0) + 1,
                          emails_clicked: (form.emails_clicked || 0) + 1,
                        })
                      }
                      disabled={activityLogging}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-purple-50 text-purple-700 hover:bg-purple-100 border border-purple-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Mail className="w-3.5 h-3.5" />
                      Email
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        handleLogActivity({
                          meetings_scheduled: (form.meetings_scheduled || 0) + 1,
                          meetings_done: (form.meetings_done || 0) + 1,
                        })
                      }
                      disabled={activityLogging}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-amber-50 text-amber-700 hover:bg-amber-100 border border-amber-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Calendar className="w-3.5 h-3.5" />
                      Meeting
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLogActivity({ demo_requested: true })}
                      disabled={activityLogging || form.demo_requested}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-green-50 text-green-700 hover:bg-green-100 border border-green-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Play className="w-3.5 h-3.5" />
                      Demo
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLogActivity({ budget_available: true })}
                      disabled={activityLogging || form.budget_available}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <DollarSign className="w-3.5 h-3.5" />
                      Budget
                    </button>
                    {revenueInput !== 'active' ? (
                      <button
                        type="button"
                        onClick={() => setRevenueInput('active')}
                        disabled={activityLogging}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-full bg-yellow-50 text-yellow-700 hover:bg-yellow-100 border border-yellow-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <DollarSign className="w-3.5 h-3.5" />
                        Revenue
                      </button>
                    ) : (
                      <div className="flex items-center gap-1.5 bg-yellow-50 border border-yellow-200 rounded-full px-3 py-1.5">
                        <span className="text-xs text-yellow-700 font-medium">₹</span>
                        <input
                          type="number"
                          className="w-20 text-xs border border-yellow-200 rounded-md px-2 py-1 text-center"
                          placeholder="amount"
                          min={0}
                          value={revenueInput === 'active' ? '' : revenueInput}
                          onChange={(e) => setRevenueInput(e.target.value)}
                          autoFocus
                        />
                        <button
                          type="button"
                          onClick={() => {
                            const amt = parseFloat(revenueInput) || 0;
                            handleLogActivity({ revenue: (form.revenue || 0) + amt });
                            setRevenueInput('');
                          }}
                          disabled={activityLogging}
                          className="text-xs font-semibold text-yellow-700 hover:text-yellow-800 ml-1"
                        >
                          Log
                        </button>
                        <button
                          type="button"
                          onClick={() => setRevenueInput('')}
                          className="text-gray-400 hover:text-gray-600 ml-0.5"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    )}
                    {activityLogging && <Loader2 className="w-4 h-4 animate-spin text-gray-400 self-center" />}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Company Name */}
                <div>
                  <label className="input-label">
                    <Building2 className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Company Name
                  </label>
                  <input
                    className={`input-field ${errors.company_name ? 'border-cold-500 ring-cold-500' : ''}`}
                    placeholder="e.g. Acme Corp"
                    value={form.company_name}
                    onChange={(e) => handleChange('company_name', e.target.value)}
                    disabled={mode === 'view'}
                    readOnly={mode === 'view'}
                  />
                  {errors.company_name && <p className="input-error">{errors.company_name}</p>}
                </div>

                {/* Contact Name */}
                <div>
                  <label className="input-label">
                    <User className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Contact Name
                  </label>
                  <input
                    className={`input-field ${errors.contact_name ? 'border-cold-500 ring-cold-500' : ''}`}
                    placeholder="e.g. John Doe"
                    value={form.contact_name}
                    onChange={(e) => handleChange('contact_name', e.target.value)}
                    disabled={mode === 'view'}
                    readOnly={mode === 'view'}
                  />
                  {errors.contact_name && <p className="input-error">{errors.contact_name}</p>}
                </div>

                {/* Email */}
                <div>
                  <label className="input-label">
                    <Mail className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Contact Email
                  </label>
                  <input
                    type="email"
                    className={`input-field ${errors.contact_email ? 'border-cold-500 ring-cold-500' : ''}`}
                    placeholder="e.g. john@acme.com"
                    value={form.contact_email}
                    onChange={(e) => handleChange('contact_email', e.target.value)}
                    disabled={mode === 'view'}
                    readOnly={mode === 'view'}
                  />
                  {errors.contact_email && <p className="input-error">{errors.contact_email}</p>}
                </div>

                {/* Phone */}
                <div>
                  <label className="input-label">
                    <Phone className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Contact Phone
                  </label>
                  <input
                    className="input-field"
                    placeholder="e.g. +1 (555) 123-4567"
                    value={form.contact_phone || ''}
                    onChange={(e) => handleChange('contact_phone', e.target.value)}
                    disabled={mode === 'view'}
                    readOnly={mode === 'view'}
                  />
                </div>

                {/* Lead Source */}
                <div>
                  <label className="input-label">
                    <Globe className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Lead Source
                  </label>
                  <select
                    className="input-field"
                    value={form.lead_source}
                    onChange={(e) => handleChange('lead_source', e.target.value)}
                    disabled={mode === 'view'}
                  >
                    {SOURCE_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Industry */}
                <div>
                  <label className="input-label">
                    <Briefcase className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Industry
                  </label>
                  <select
                    className="input-field"
                    value={form.industry}
                    onChange={(e) => handleChange('industry', e.target.value)}
                    disabled={mode === 'view'}
                  >
                    {INDUSTRY_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Company Size */}
                <div>
                  <label className="input-label">
                    <UsersIcon className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                    Company Size
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    placeholder="e.g. 200"
                    value={form.company_size ?? ''}
                    onChange={(e) => handleChange('company_size', e.target.value ? Number(e.target.value) : 10)}
                    disabled={mode === 'view'}
                    readOnly={mode === 'view'}
                  />
                </div>

                {/* Call Duration — shown in create & edit mode */}
                {mode !== 'view' && (
                  <div>
                    <label className="input-label">
                      <PhoneCall className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                      Call Duration (min)
                    </label>
                    <input
                      type="number"
                      className="input-field"
                      placeholder="e.g. 15"
                      value={form.call_duration_minutes ?? 0}
                      onChange={(e) => handleChange('call_duration_minutes', Number(e.target.value))}
                      min={0}
                    />
                  </div>
                )}

                {/* Status (edit mode only) */}
                {mode === 'edit' && (
                  <div>
                    <label className="input-label">Status</label>
                    <select
                      className="input-field"
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                    >
                      {STATUS_OPTIONS.map((opt) => (
                        <option key={opt.value} value={opt.value}>
                          {opt.label}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>

              {/* Notes */}
              <div>
                <label className="input-label">
                  <FileText className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                  Notes
                </label>
                <textarea
                  className="input-field min-h-[80px] resize-y"
                  placeholder="Any additional notes about this lead..."
                  value={form.notes || ''}
                  onChange={(e) => handleChange('notes', e.target.value)}
                  disabled={mode === 'view'}
                  readOnly={mode === 'view'}
                />
              </div>

              {/* Engagement Details — Edit mode (collapsible) */}
              {mode === 'edit' && (
                <div className="border border-gray-200 rounded-xl overflow-hidden">
                  <button
                    type="button"
                    onClick={() => setEngagementOpen(!engagementOpen)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors text-left"
                  >
                    <span className="text-sm font-semibold text-gray-700 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-gray-500" />
                      Engagement Details
                    </span>
                    {engagementOpen ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                  {engagementOpen && (
                    <div className="p-4 border-t border-gray-200">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="input-label">Website Visits</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.website_visits ?? 0}
                            onChange={(e) => handleChange('website_visits', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Emails Opened</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.emails_opened ?? 0}
                            onChange={(e) => handleChange('emails_opened', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Emails Clicked</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.emails_clicked ?? 0}
                            onChange={(e) => handleChange('emails_clicked', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Calls Made</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.calls_made ?? 0}
                            onChange={(e) => handleChange('calls_made', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Calls Connected</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.calls_connected ?? 0}
                            onChange={(e) => handleChange('calls_connected', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Call Duration (min)</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.call_duration_minutes ?? 0}
                            onChange={(e) => handleChange('call_duration_minutes', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Meetings Scheduled</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.meetings_scheduled ?? 0}
                            onChange={(e) => handleChange('meetings_scheduled', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Meetings Done</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.meetings_done ?? 0}
                            onChange={(e) => handleChange('meetings_done', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                        <div>
                          <label className="input-label">Days Since First Contact</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.days_since_first_contact ?? 1}
                            onChange={(e) => handleChange('days_since_first_contact', Number(e.target.value))}
                            min={1}
                          />
                        </div>
                        <div>
                          <label className="input-label">Follow-ups Total</label>
                          <input
                            type="number"
                            className="input-field"
                            value={form.follow_ups_total ?? 0}
                            onChange={(e) => handleChange('follow_ups_total', Number(e.target.value))}
                            min={0}
                          />
                        </div>
                      </div>
                      {/* Checkboxes — full width */}
                      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2.5">
                        <label className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            checked={form.demo_requested ?? false}
                            onChange={(e) => handleChange('demo_requested', e.target.checked)}
                          />
                          <span>Demo Requested</span>
                        </label>
                        <label className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            checked={form.budget_available ?? false}
                            onChange={(e) => handleChange('budget_available', e.target.checked)}
                          />
                          <span>Budget Available</span>
                        </label>
                        <label className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            checked={form.decision_maker_contacted ?? false}
                            onChange={(e) => handleChange('decision_maker_contacted', e.target.checked)}
                          />
                          <span>Decision Maker Contacted</span>
                        </label>
                        <label className="flex items-center gap-2.5 text-sm text-gray-700 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            checked={form.competitor_considering ?? false}
                            onChange={(e) => handleChange('competitor_considering', e.target.checked)}
                          />
                          <span>Competitor Considering</span>
                        </label>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Actions */}
              {mode !== 'view' && (
                <div className="flex items-center justify-end gap-3 pt-2 border-t border-gray-100">
                  <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary" disabled={loading}>
                    {loading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <>{mode === 'edit' ? <Save className="w-4 h-4" /> : <Edit3 className="w-4 h-4" />}</>
                    )}
                    {mode === 'edit' ? 'Save Changes' : 'Create Lead'}
                  </button>
                </div>
              )}

              {mode === 'view' && (
                <div className="flex items-center justify-end pt-2 border-t border-gray-100">
                  <button type="button" className="btn-secondary" onClick={onClose}>
                    Close
                  </button>
                </div>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
