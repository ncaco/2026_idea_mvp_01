'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Wallet, ArrowUpCircle, ArrowDownCircle, BarChart3 } from 'lucide-react';
import { statisticsAPI, MonthlyStatistics, transactionAPI } from '@/lib/api';
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

      // 오늘 통계 (로컬 시간대 기준)
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const today = `${year}-${month}-${day}`;
      
      const transactions = await transactionAPI.getAll({
        start_date: today,
        end_date: today,
        limit: 1000,
      });

      const todayIncome = transactions
        .filter((t) => t.type === 'income')
        .reduce((sum, t) => sum + Number(t.amount || 0), 0);
      const todayExpense = transactions
        .filter((t) => t.type === 'expense')
        .reduce((sum, t) => sum + Number(t.amount || 0), 0);

      setTodayStats({ income: todayIncome, expense: todayExpense });
    } catch (error: any) {
      // 401 오류인 경우 (인증 실패)는 조용히 처리 (이미 리다이렉트됨)
      if (error?.message?.includes('401') || error?.message?.includes('인증')) {
        return;
      }
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

  const incomeTrend = calculateTrend(Number(currentStats.income || 0), Number(previousStats?.income || 0));
  const expenseTrend = calculateTrend(Number(currentStats.expense || 0), Number(previousStats?.expense || 0));
  const balanceTrend = calculateTrend(Number(currentStats.balance || 0), Number(previousStats?.balance || 0));

  const incomeTrendFormatted = formatTrend(incomeTrend);
  const expenseTrendFormatted = formatTrend(expenseTrend);
  const balanceTrendFormatted = formatTrend(balanceTrend);

  const cards = [
    {
      title: '이번 달 수입',
      value: Number(currentStats.income || 0),
      color: 'text-green-600',
      bgGradient: 'from-green-50 to-emerald-50',
      borderColor: 'border-green-200',
      trend: incomeTrendFormatted,
      icon: ArrowUpCircle,
      iconColor: 'text-green-600',
    },
    {
      title: '이번 달 지출',
      value: Number(currentStats.expense || 0),
      color: 'text-red-600',
      bgGradient: 'from-red-50 to-rose-50',
      borderColor: 'border-red-200',
      trend: expenseTrendFormatted,
      icon: ArrowDownCircle,
      iconColor: 'text-red-600',
    },
    {
      title: '이번 달 잔액',
      value: Number(currentStats.balance || 0),
      color: Number(currentStats.balance || 0) >= 0 ? 'text-green-600' : 'text-red-600',
      bgGradient: Number(currentStats.balance || 0) >= 0 ? 'from-blue-50 to-cyan-50' : 'from-orange-50 to-amber-50',
      borderColor: Number(currentStats.balance || 0) >= 0 ? 'border-blue-200' : 'border-orange-200',
      trend: balanceTrendFormatted,
      icon: Wallet,
      iconColor: Number(currentStats.balance || 0) >= 0 ? 'text-blue-600' : 'text-orange-600',
    },
    {
      title: '오늘 수입',
      value: Number(todayStats.income || 0),
      color: 'text-green-600',
      bgGradient: 'from-green-50 to-emerald-50',
      borderColor: 'border-green-200',
      trend: null,
      icon: TrendingUp,
      iconColor: 'text-green-600',
    },
    {
      title: '오늘 지출',
      value: Number(todayStats.expense || 0),
      color: 'text-red-600',
      bgGradient: 'from-red-50 to-rose-50',
      borderColor: 'border-red-200',
      trend: null,
      icon: TrendingDown,
      iconColor: 'text-red-600',
    },
    {
      title: '오늘 잔액',
      value: Number(todayStats.income || 0) - Number(todayStats.expense || 0),
      color: (Number(todayStats.income || 0) - Number(todayStats.expense || 0)) >= 0 ? 'text-green-600' : 'text-red-600',
      bgGradient: (Number(todayStats.income || 0) - Number(todayStats.expense || 0)) >= 0 ? 'from-blue-50 to-cyan-50' : 'from-orange-50 to-amber-50',
      borderColor: (Number(todayStats.income || 0) - Number(todayStats.expense || 0)) >= 0 ? 'border-blue-200' : 'border-orange-200',
      trend: null,
      icon: BarChart3,
      iconColor: (Number(todayStats.income || 0) - Number(todayStats.expense || 0)) >= 0 ? 'text-blue-600' : 'text-orange-600',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {cards.map((card, index) => {
        const Icon = card.icon;
        return (
          <Card
            key={index}
            compact
            className={`interactive hover:shadow-xl transition-all duration-300 border-2 ${card.borderColor} bg-gradient-to-br ${card.bgGradient} hover:scale-105`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="text-xs font-semibold text-gray-700 dark:text-gray-300">{card.title}</div>
              <div className={`p-1.5 rounded-lg bg-white/60 dark:bg-gray-800/60 ${card.iconColor}`}>
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div className={`text-2xl font-bold ${card.color} mb-2`}>
              ₩{Number(card.value || 0).toLocaleString()}
            </div>
            {card.trend && (
              <div className="flex items-center gap-1.5 text-xs pt-2 border-t border-white/50 dark:border-gray-700/50">
                <span className={card.trend.color}>
                  {card.trend.icon === '↑' ? <TrendingUp className="w-3 h-3 inline" /> : <TrendingDown className="w-3 h-3 inline" />}
                </span>
                <span className={`font-medium ${card.trend.color}`}>
                  {card.trend.value} ({card.trend.percent})
                </span>
                <span className="text-gray-500 dark:text-gray-400 text-[10px]">전월 대비</span>
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
};
