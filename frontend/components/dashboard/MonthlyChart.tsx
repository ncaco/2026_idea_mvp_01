'use client';

import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { statisticsAPI, MonthlyStatistics } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export const MonthlyChart: React.FC = () => {
  const [data, setData] = useState<MonthlyStatistics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const currentYear = new Date().getFullYear();
      const monthlyData: MonthlyStatistics[] = [];

      for (let month = 1; month <= 12; month++) {
        try {
          const stats = await statisticsAPI.getMonthly(currentYear, month);
          monthlyData.push({
            ...stats,
            year: currentYear,
            month,
          });
        } catch (error) {
          monthlyData.push({
            income: 0,
            expense: 0,
            balance: 0,
            year: currentYear,
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
  }));

  if (loading) {
    return (
      <Card title="월별 수입/지출 추이">
        <div className="h-64 flex items-center justify-center text-gray-500">
          로딩 중...
        </div>
      </Card>
    );
  }

  return (
    <Card title="월별 수입/지출 추이">
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value: number) => `₩${value.toLocaleString()}`} />
          <Legend />
          <Line type="monotone" dataKey="수입" stroke="#22c55e" strokeWidth={2} />
          <Line type="monotone" dataKey="지출" stroke="#ef4444" strokeWidth={2} />
          <Line type="monotone" dataKey="잔액" stroke="#3b82f6" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};
