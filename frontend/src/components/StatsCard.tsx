import { ReactNode } from 'react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: ReactNode;
  trend?: { value: number; isPositive: boolean };
  color: 'blue' | 'green' | 'purple' | 'orange' | 'red' | 'yellow';
}

export default function StatsCard({ title, value, subtitle, icon, trend, color }: StatsCardProps) {
  const colorStyles = {
    blue: 'from-blue-500 to-blue-600 bg-blue-50',
    green: 'from-green-500 to-green-600 bg-green-50',
    purple: 'from-purple-500 to-purple-600 bg-purple-50',
    orange: 'from-orange-500 to-orange-600 bg-orange-50',
    red: 'from-red-500 to-red-600 bg-red-50',
    yellow: 'from-yellow-500 to-yellow-600 bg-yellow-50',
  };

  const iconColorStyles = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600',
    red: 'text-red-600',
    yellow: 'text-yellow-600',
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800">{value}</p>
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
          {trend && (
            <div className={`flex items-center mt-2 text-sm ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              <span>{trend.isPositive ? '↑' : '↓'}</span>
              <span className="ml-1">{Math.abs(trend.value)}%</span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-xl ${colorStyles[color].split(' ')[2]}`}>
          <div className={iconColorStyles[color]}>{icon}</div>
        </div>
      </div>
    </div>
  );
}