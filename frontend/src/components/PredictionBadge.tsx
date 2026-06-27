// ============================================================
// NovaLeads — Prediction Badge Component
// ============================================================

import type { LeadStatus } from '../types';
import { Zap, XCircle, CheckCircle, Snowflake } from 'lucide-react';

interface PredictionBadgeProps {
  predicted_outcome: string;
  confidence?: number;
  size?: 'sm' | 'md';
}

const statusConfig: Record<string, { bg: string; text: string; ring: string; icon: React.ReactNode; label: string }> = {
  new: {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    ring: 'ring-blue-600/20',
    icon: <Zap className="w-3.5 h-3.5" />,
    label: 'New',
  },
  active: {
    bg: 'bg-indigo-50',
    text: 'text-indigo-700',
    ring: 'ring-indigo-600/20',
    icon: <Zap className="w-3.5 h-3.5" />,
    label: 'Active',
  },
  cold: {
    bg: 'bg-cold-50',
    text: 'text-cold-600',
    ring: 'ring-cold-600/20',
    icon: <Snowflake className="w-3.5 h-3.5" />,
    label: 'Cold',
  },
  rejected: {
    bg: 'bg-rejected-50',
    text: 'text-rejected-600',
    ring: 'ring-rejected-600/20',
    icon: <XCircle className="w-3.5 h-3.5" />,
    label: 'Rejected',
  },
  successful: {
    bg: 'bg-successful-50',
    text: 'text-successful-600',
    ring: 'ring-successful-600/20',
    icon: <CheckCircle className="w-3.5 h-3.5" />,
    label: 'Successful',
  },
};

export default function PredictionBadge({ predicted_outcome, confidence, size = 'sm' }: PredictionBadgeProps) {
  const config = statusConfig[predicted_outcome] || statusConfig.new;
  const sizeClasses = size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1';

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ring-1 ring-inset ${config.bg} ${config.text} ${config.ring} ${sizeClasses}`}
    >
      {config.icon}
      {config.label}
      {confidence !== undefined && (
        <span className={`opacity-70 ${size === 'sm' ? 'text-[10px]' : 'text-xs'}`}>
          ({Math.round(confidence * 100)}%)
        </span>
      )}
    </span>
  );
}

// Also export status config for use in tables
export function getStatusBadge(status: LeadStatus) {
  const config = statusConfig[status] || statusConfig.new;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full text-xs font-medium px-2.5 py-0.5 ring-1 ring-inset ${config.bg} ${config.text} ${config.ring}`}
    >
      {config.icon}
      {config.label}
    </span>
  );
}
