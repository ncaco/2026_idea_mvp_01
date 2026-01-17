'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle } from 'lucide-react';
import { budgetAPI, BudgetStatus } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export const BudgetAlerts: React.FC = () => {
  const [alerts, setAlerts] = useState<BudgetStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      setLoading(true);
      const now = new Date();
      const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
      const statuses = await budgetAPI.getStatus(month);
      const overBudgets = statuses.filter(s => s.is_over_budget);
      setAlerts(overBudgets);
    } catch (error) {
      console.error('예산 알림 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || alerts.length === 0) return null;

  return (
    <Card compact className="border-2 border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20 mb-6">
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h3 className="font-semibold text-red-900 dark:text-red-300 mb-2">
            예산 초과 알림
          </h3>
          <div className="space-y-2">
            {alerts.map((alert) => (
              <div key={alert.budget_id} className="text-sm text-red-800 dark:text-red-400">
                <span className="font-medium">
                  {alert.category_name || '전체 예산'}
                </span>
                : 예산 {Number(alert.budget_amount).toLocaleString()}원 중{' '}
                {Number(alert.spent_amount).toLocaleString()}원 사용 (
                {alert.percentage.toFixed(1)}%)
              </div>
            ))}
          </div>
        </div>
        <Link href="/budgets">
          <Button variant="secondary" size="sm">예산 관리</Button>
        </Link>
      </div>
    </Card>
  );
};
