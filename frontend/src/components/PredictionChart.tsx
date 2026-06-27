// ============================================================
// NovaLeads — Prediction Chart Component (3-bar probabilities)
// ============================================================

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LabelList } from 'recharts';
import type { LeadStatus } from '../types';

interface PredictionChartProps {
  coldProbability: number;
  rejectedProbability: number;
  successfulProbability: number;
  predictedStatus: LeadStatus;
  height?: number;
}

export default function PredictionChart({
  coldProbability,
  rejectedProbability,
  successfulProbability,
  predictedStatus,
  height = 200,
}: PredictionChartProps) {
  const data = [
    {
      name: 'Cold ❄️',
      value: Math.round(coldProbability * 100),
      fill: coldProbability >= 0.5 ? '#EF4444' : '#FCA5A5',
      isPredicted: predictedStatus === 'cold',
    },
    {
      name: 'Rejected ✋',
      value: Math.round(rejectedProbability * 100),
      fill: rejectedProbability >= 0.5 ? '#F59E0B' : '#FCD34D',
      isPredicted: predictedStatus === 'rejected',
    },
    {
      name: 'Successful ✅',
      value: Math.round(successfulProbability * 100),
      fill: successfulProbability >= 0.5 ? '#10B981' : '#6EE7B7',
      isPredicted: predictedStatus === 'successful',
    },
  ];

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg px-3 py-2 text-sm">
          <p className="font-medium text-gray-900">{item.name}</p>
          <p className="text-gray-600">{item.value}% probability</p>
          {item.isPredicted && (
            <span className="text-primary-600 font-medium text-xs">← Predicted</span>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 20, right: 10, left: 10, bottom: 5 }}>
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12, fill: '#6B7280' }}
            axisLine={{ stroke: '#E5E7EB' }}
            tickLine={false}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fontSize: 11, fill: '#9CA3AF' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'transparent' }} />
          <Bar
            dataKey="value"
            radius={[6, 6, 0, 0]}
            maxBarSize={60}
            animationDuration={800}
          >
            <LabelList
              dataKey="value"
              position="top"
              formatter={(v: number) => `${v}%`}
              style={{ fill: '#6B7280', fontSize: 11, fontWeight: 500 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
