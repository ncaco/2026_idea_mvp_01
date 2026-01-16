'use client';

import { useEffect, useState } from 'react';
import { statisticsAPI, MonthlyStatistics, transactionAPI, Transaction } from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface TrendData {
  current: number;
  previous: number;
  change: number;
  changePercent: number;
}

export const SummaryCards: React.FC = () => {
  const [currentStats, setCurrentStats] = useState<MonthlyStatistics | null>(null);
  const [previousStats, setPreviousStats] = useState<MonthlyStatistics | null>(null);
  const [todayStats, setTodayStats] = useState<{ income: number; expense: number }>({
    income: 0,
    expense: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const currentYear = now.getFullYear();
      const currentMonth = now.getMonth() + 1;
      const previousMonth = currentMonth === 1 ? 12 : currentMonth - 1;
      const previousYear = currentMonth === 1 ? currentYear - 1 : currentYear;

      // 현재 월 통계
      const current = await statisticsAPI.getMonthly(currentYear, currentMonth);
      setCurrentStats(current);

      // 전월 통계
      const previous = await statisticsAPI.getMonthly(previousYear, previousMonth);
      setPreviousStats(previous);

      // 오늘 통계
      const today = new Date().toISOString().split('T')[0];
      const transactions = await transactionAPI.getAll({
        start_date: today,
        end_date: today,
        limit: 1000,
      });

      const todayIncome = transactions
        .filter((t) => t.type === 'income')
        .reduce((sum, t) => sum + t.amount, 0);
      const todayExpense = transactions
        .filter((t) => t.type === 'expense')
        .reduce((sum, t) => sum + t.amount, 0);

      setTodayStats({ income: todayIncome, expense: todayExpense });
    } catch (error) {
      console.error('통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateTrend = (current: number, previous: number): TrendData => {
    const change = current - previous;
    const changePercent = previous !== 0 ? (change / previous) * 100 : 0;
    return { current, previous, change, changePercent };
  };

  const formatTrend = (trend: TrendData) => {
    const isPositive = trend.change >= 0;
    const sign = isPositive ? '+' : '';
    return {
      value: `${sign}${trend.change.toLocaleString()}`,
      percent: `${sign}${trend.changePercent.toFixed(1)}%`,
      color: isPositive ? 'text-green-600' : 'text-red-600',
      icon: isPositive ? '↑' : '↓',
    };
  };

  if (loading || !currentStats) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} compact>
            <div className="h-20 skeleton rounded" />
          </Card>
        ))}
      </div>
    );
  }

  const incomeTrend = calculateTrend(currentStats.income, previousStats?.income || 0);
  const expenseTrend = calculateTrend(currentStats.expense, previousStats?.expense || 0);
  const balanceTrend = calculateTrend(currentStats.balance, previousStats?.balance || 0);

  const incomeTrendFormatted = formatTrend(incomeTrend);
  const expenseTrendFormatted = formatTrend(expenseTrend);
  const balanceTrendFormatted = formatTrend(balanceTrend);

  const cards = [
    {
      title: '이번 달 수입',
      value: currentStats.income,
      color: 'text-green-600',
      trend: incomeTrendFormatted,
      icon: '💰',
    },
    {
      title: '이번 달 지출',
      value: currentStats.expense,
      color: 'text-red-600',
      trend: expenseTrendFormatted,
      icon: '💸',
    },
    {
      title: '이번 달 잔액',
      value: currentStats.balance,
      color: currentStats.balance >= 0 ? 'text-green-600' : 'text-red-600',
      trend: balanceTrendFormatted,
      icon: '💵',
    },
    {
      title: '오늘 수입',
      value: todayStats.income,
      color: 'text-green-600',
      trend: null,
      icon: '📈',
    },
    {
      title: '오늘 지출',
      value: todayStats.expense,
      color: 'text-red-600',
      trend: null,
      icon: '📉',
    },
    {
      title: '오늘 잔액',
      value: todayStats.income - todayStats.expense,
      color: todayStats.income - todayStats.expense >= 0 ? 'text-green-600' : 'text-red-600',
      trend: null,
      icon: '📊',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {cards.map((card, index) => (
        <Card
          key={index}
          compact
          className="interactive hover:shadow-lg transition-all duration-200"
        >
          <div className="flex items-start justify-between mb-2">
            <div className="text-xs text-gray-600 font-medium">{card.title}</div>
            <span className="text-lg">{card.icon}</span>
          </div>
          <div className={`text-2xl font-bold ${card.color} mb-1`}>
            ₩{card.value.toLocaleString()}
          </div>
          {card.trend && (
            <div className="flex items-center gap-1 text-xs">
              <span className={card.trend.color}>{card.trend.icon}</span>
              <span className={card.trend.color}>
                {card.trend.value} ({card.trend.percent})
              </span>
              <span className="text-gray-500">전월 대비</span>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
};
