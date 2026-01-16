'use client';

import { useEffect, useState } from 'react';
import { Transaction, transactionAPI } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import Link from 'next/link';

export const RecentTransactions: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await transactionAPI.getAll({ limit: 5 });
      setTransactions(data);
    } catch (error) {
      console.error('최근 거래 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card title="최근 거래" compact>
        <div className="space-y-2">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 skeleton rounded" />
          ))}
        </div>
      </Card>
    );
  }

  if (transactions.length === 0) {
    return (
      <Card title="최근 거래" compact>
        <div className="text-center py-8 text-gray-500 text-sm">
          거래 내역이 없습니다.
        </div>
      </Card>
    );
  }

  return (
    <Card title="최근 거래" compact>
      <div className="space-y-2">
        {transactions.map((transaction) => {
          const isIncome = transaction.type === 'income';
          const amountColor = isIncome ? 'text-green-600' : 'text-red-600';
          const amountPrefix = isIncome ? '+' : '-';

          return (
            <Link
              key={transaction.id}
              href="/transactions"
              className="flex items-center justify-between p-2 rounded-md hover:bg-gray-50 transition-colors group"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`font-semibold text-sm ${amountColor}`}>
                    {amountPrefix}₩{Number(transaction.amount).toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(transaction.transaction_date).toLocaleDateString('ko-KR', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </div>
                {transaction.description && (
                  <p className="text-xs text-gray-600 mt-0.5 truncate">
                    {transaction.description}
                  </p>
                )}
              </div>
              <svg
                className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </Link>
          );
        })}
      </div>
      <div className="mt-3 pt-3 border-t border-gray-200">
        <Link
          href="/transactions"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center justify-center gap-1"
        >
          전체 보기
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </Link>
      </div>
    </Card>
  );
};
