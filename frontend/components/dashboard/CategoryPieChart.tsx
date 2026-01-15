'use client';

import { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { statisticsAPI, CategoryStatistics } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export const CategoryPieChart: React.FC = () => {
  const [data, setData] = useState<CategoryStatistics[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const currentYear = new Date().getFullYear();
      const currentMonth = new Date().getMonth() + 1;
      const stats = await statisticsAPI.getByCategory(currentYear, currentMonth, 'expense');
      setData(stats);
    } catch (error) {
      console.error('카테고리 통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = data.map((item) => ({
    name: item.category_name,
    value: item.total,
    color: item.color || '#3B82F6',
  }));

  const COLORS = chartData.map((item) => item.color);

  if (loading) {
    return (
      <Card title="카테고리별 지출">
        <div className="h-64 flex items-center justify-center text-gray-500">
          로딩 중...
        </div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card title="카테고리별 지출">
        <div className="h-64 flex items-center justify-center text-gray-500">
          데이터가 없습니다.
        </div>
      </Card>
    );
  }

  return (
    <Card title="카테고리별 지출">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `₩${value.toLocaleString()}`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
};
