'use client';

import { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from 'recharts';
import { statisticsAPI, MonthlyStatistics } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export const MonthlyChart: React.FC = () => {
  const [data, setData] = useState<MonthlyStatistics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [hiddenLines, setHiddenLines] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadData();
  }, [selectedYear]);

  const loadData = async () => {
    try {
      setLoading(true);
      const monthlyData: MonthlyStatistics[] = [];

      for (let month = 1; month <= 12; month++) {
        try {
          const stats = await statisticsAPI.getMonthly(selectedYear, month);
          monthlyData.push({
            ...stats,
            year: selectedYear,
            month,
          });
        } catch (error) {
          monthlyData.push({
            income: 0,
            expense: 0,
            balance: 0,
            year: selectedYear,
            month,
          });
        }
      }

      setData(monthlyData);
    } catch (error) {
      console.error('차트 데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = data.map((item) => ({
    name: `${item.month}월`,
    수입: item.income,
    지출: item.expense,
    잔액: item.balance,
    month: item.month,
  }));

  const handleLegendClick = (dataKey: string) => {
    const newHidden = new Set(hiddenLines);
    if (newHidden.has(dataKey)) {
      newHidden.delete(dataKey);
    } else {
      newHidden.add(dataKey);
    }
    setHiddenLines(newHidden);
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-3">
          <p className="font-semibold mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {entry.name}: ₩{entry.value.toLocaleString()}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card title="월별 수입/지출 추이" compact>
        <div className="h-48 flex items-center justify-center text-gray-500">
          <div className="skeleton w-full h-full rounded" />
        </div>
      </Card>
    );
  }

  return (
    <Card title="월별 수입/지출 추이" compact className="interactive">
      <div className="mb-3 flex items-center gap-2">
        <select
          value={selectedYear}
          onChange={(e) => setSelectedYear(Number(e.target.value))}
          className="px-3 py-1.5 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
            <option key={year} value={year}>
              {year}년
            </option>
          ))}
        </select>
      </div>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 10, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#6b7280"
            tickFormatter={(value) => `₩${(value / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            onClick={(e) => handleLegendClick(e.dataKey as string)}
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
          <Line
            type="monotone"
            dataKey="수입"
            stroke="#22c55e"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            hide={hiddenLines.has('수입')}
            animationDuration={300}
          />
          <Line
            type="monotone"
            dataKey="지출"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            hide={hiddenLines.has('지출')}
            animationDuration={300}
          />
          <Line
            type="monotone"
            dataKey="잔액"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
            hide={hiddenLines.has('잔액')}
            animationDuration={300}
          />
          <Brush dataKey="name" height={20} stroke="#94a3b8" />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};
