'use client';

import { useState, useEffect } from 'react';
import { Transaction, transactionAPI, TransactionCreate, TransactionUpdate } from '@/lib/api';
import { TransactionItem } from './TransactionItem';
import { TransactionForm } from './TransactionForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | undefined>();

  useEffect(() => {
    loadTransactions();
  }, []);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const data = await transactionAPI.getAll({ limit: 100 });
      setTransactions(data);
    } catch (error) {
      console.error('거래 내역 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: TransactionCreate | TransactionUpdate) => {
    try {
      if (editingTransaction) {
        await transactionAPI.update(editingTransaction.id, data as TransactionUpdate);
      } else {
        await transactionAPI.create(data as TransactionCreate);
      }
      await loadTransactions();
      setShowForm(false);
      setEditingTransaction(undefined);
    } catch (error) {
      console.error('거래 내역 저장 실패:', error);
      throw error;
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    try {
      await transactionAPI.delete(id);
      await loadTransactions();
    } catch (error) {
      console.error('거래 내역 삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTransaction(undefined);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">거래 내역</h2>
        <Button onClick={() => {
          setEditingTransaction(undefined);
          setShowForm(true);
        }}>
          거래 추가
        </Button>
      </div>

      {showForm && (
        <Card title={editingTransaction ? '거래 수정' : '거래 등록'}>
          <TransactionForm
            transaction={editingTransaction}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
          />
        </Card>
      )}

      <Card>
        {loading ? (
          <div className="text-center py-8 text-gray-500">로딩 중...</div>
        ) : transactions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">거래 내역이 없습니다.</div>
        ) : (
          <div className="divide-y">
            {transactions.map((transaction) => (
              <TransactionItem
                key={transaction.id}
                transaction={transaction}
                onEdit={handleEdit}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
