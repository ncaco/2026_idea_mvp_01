'use client';

import { useState, useEffect } from 'react';
import { statisticsAPI } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

export const YearlyStatistics: React.FC = () => {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [yearlyData, setYearlyData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadYearlyData();
  }, [selectedYear]);

  const loadYearlyData = async () => {
    try {
      setLoading(true);
      const months = [];
      for (let month = 1; month <= 12; month++) {
        const stats = await statisticsAPI.getMonthly(selectedYear, month);
        months.push({
          month,
          monthName: `${month}월`,
          income: stats.income,
          expense: stats.expense,
          balance: stats.balance,
        });
      }
      setYearlyData(months);
    } catch (error) {
      console.error('연도별 통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalIncome = yearlyData.reduce((sum, m) => sum + m.income, 0);
  const totalExpense = yearlyData.reduce((sum, m) => sum + m.expense, 0);
  const totalBalance = totalIncome - totalExpense;

  const COLORS = ['#3B82F6', '#EF4444', '#10B981'];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">연도별 통계</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">연도별 수입/지출 통계를 확인하세요</p>
        </div>
        <div className="flex gap-2">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-2 border-gray-200 dark:border-gray-600 rounded-lg"
          >
            {Array.from({ length: 10 }, (_, i) => new Date().getFullYear() - i).map(year => (
              <option key={year} value={year}>{year}년</option>
            ))}
          </select>
        </div>
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card compact className="border-2 border-green-200 dark:border-green-700">
          <div className="p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">총 수입</div>
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              ₩{totalIncome.toLocaleString()}
            </div>
          </div>
        </Card>
        <Card compact className="border-2 border-red-200 dark:border-red-700">
          <div className="p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">총 지출</div>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              ₩{totalExpense.toLocaleString()}
            </div>
          </div>
        </Card>
        <Card compact className="border-2 border-blue-200 dark:border-blue-700">
          <div className="p-4">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">순수익</div>
            <div className={`text-2xl font-bold ${totalBalance >= 0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
              ₩{totalBalance.toLocaleString()}
            </div>
          </div>
        </Card>
      </div>

      {/* 월별 차트 */}
      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
          월별 수입/지출 추이
        </h3>
        <div className="p-4">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={yearlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="monthName" />
              <YAxis />
              <Tooltip formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''} />
              <Legend />
              <Bar dataKey="income" fill="#10B981" name="수입" />
              <Bar dataKey="expense" fill="#EF4444" name="지출" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* 월별 순수익 차트 */}
      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
          월별 순수익 추이
        </h3>
        <div className="p-4">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={yearlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="monthName" />
              <YAxis />
              <Tooltip formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''} />
              <Legend />
              <Line type="monotone" dataKey="balance" stroke="#3B82F6" name="순수익" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};
