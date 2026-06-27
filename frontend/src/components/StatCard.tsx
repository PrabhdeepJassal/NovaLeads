// ============================================================
// NovaLeads — Stat Card Component
// ============================================================

import { TrendingUp, TrendingDown } from 'lucide-react';
import type { ReactNode } from 'react';

interface StatCardProps {
  icon: ReactNode;
  label: string;
  value: string | number;
  trend?: {
    value: number;
    isUp: boolean;
  };
  colorClass?: string;
  onClick?: () => void;
}

export default function StatCard({ icon, label, value, trend, colorClass = 'text-primary-600 bg-primary-50', onClick }: StatCardProps) {
  const Comp = onClick ? 'button' : 'div';
  return (
    <Comp
      onClick={onClick}
      className={`stat-card ${onClick ? 'cursor-pointer text-left w-full' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className={`p-2.5 rounded-xl ${colorClass}`}>
          {icon}
        </div>
        {trend && (
          <span
            className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${
              trend.isUp
                ? 'text-successful-600 bg-successful-50'
                : 'text-cold-600 bg-cold-50'
            }`}
          >
            {trend.isUp ? (
              <TrendingUp className="w-3 h-3" />
            ) : (
              <TrendingDown className="w-3 h-3" />
            )}
            {Math.abs(trend.value)}%
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </Comp>
  );
}
