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
    <Card 
      title="최근 거래" 
      compact
      className="border-2 border-gray-200 hover:border-blue-300 transition-colors shadow-sm hover:shadow-md"
    >
      <div className="space-y-2">
        {transactions.map((transaction) => {
          const isIncome = transaction.type === 'income';
          const amountColor = isIncome ? 'text-green-600' : 'text-red-600';
          const amountPrefix = isIncome ? '+' : '-';
          const bgColor = isIncome ? 'bg-green-50' : 'bg-red-50';

          return (
            <Link
              key={transaction.id}
              href="/transactions"
              className={`flex items-center justify-between p-3 rounded-lg ${bgColor} hover:shadow-md transition-all duration-200 group border border-transparent hover:border-gray-300`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-1">
                  <span className={`font-bold text-base ${amountColor}`}>
                    {amountPrefix}₩{Number(transaction.amount).toLocaleString()}
                  </span>
                  <span className="text-xs text-gray-600 bg-white px-2 py-0.5 rounded-full font-medium">
                    {new Date(transaction.transaction_date).toLocaleDateString('ko-KR', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </div>
                {transaction.description && (
                  <p className="text-sm text-gray-700 truncate font-medium">
                    {transaction.description}
                  </p>
                )}
              </div>
              <svg
                className="w-5 h-5 text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity"
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
      <div className="mt-4 pt-4 border-t-2 border-gray-200">
        <Link
          href="/transactions"
          className="text-sm text-blue-600 hover:text-blue-700 font-semibold flex items-center justify-center gap-2 hover:gap-3 transition-all"
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
