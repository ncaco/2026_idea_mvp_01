'use client';

import { useEffect, useState } from 'react';
import { statisticsAPI, MonthlyStatistics } from '@/lib/api';
import { Card } from '@/components/ui/Card';

export const SummaryCards: React.FC = () => {
  const [stats, setStats] = useState<MonthlyStatistics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await statisticsAPI.getMonthly();
      setStats(data);
    } catch (error) {
      console.error('통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <div className="h-24 bg-gray-200 animate-pulse rounded" />
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card>
        <div className="text-sm text-gray-600 mb-1">총 수입</div>
        <div className="text-3xl font-bold text-green-600">
          ₩{stats.income.toLocaleString()}
        </div>
      </Card>
      <Card>
        <div className="text-sm text-gray-600 mb-1">총 지출</div>
        <div className="text-3xl font-bold text-red-600">
          ₩{stats.expense.toLocaleString()}
        </div>
      </Card>
      <Card>
        <div className="text-sm text-gray-600 mb-1">잔액</div>
        <div className={`text-3xl font-bold ${stats.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          ₩{stats.balance.toLocaleString()}
        </div>
      </Card>
    </div>
  );
};
