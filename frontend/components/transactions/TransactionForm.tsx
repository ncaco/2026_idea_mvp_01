'use client';

import { useState, useEffect } from 'react';
import { Transaction, TransactionCreate, TransactionUpdate, categoryAPI, Category } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { CategorySelect } from '@/components/categories/CategorySelect';

interface TransactionFormProps {
  transaction?: Transaction;
  onSubmit: (data: TransactionCreate | TransactionUpdate) => Promise<void>;
  onCancel: () => void;
}

export const TransactionForm: React.FC<TransactionFormProps> = ({
  transaction,
  onSubmit,
  onCancel,
}) => {
  const [type, setType] = useState<'income' | 'expense'>(transaction?.type || 'expense');
  const [categoryId, setCategoryId] = useState<number | undefined>(transaction?.category_id);
  const [amount, setAmount] = useState<string>(transaction?.amount.toString() || '');
  const [description, setDescription] = useState<string>(transaction?.description || '');
  const [transactionDate, setTransactionDate] = useState<string>(
    transaction?.transaction_date || new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!categoryId) {
      setError('카테고리를 선택해주세요.');
      setLoading(false);
      return;
    }

    if (!amount || parseFloat(amount) <= 0) {
      setError('금액을 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const data: TransactionCreate | TransactionUpdate = {
        category_id: categoryId,
        type,
        amount: parseFloat(amount),
        description: description || undefined,
        transaction_date: transactionDate,
      };

      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">유형</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="income"
              checked={type === 'income'}
              onChange={(e) => {
                setType(e.target.value as 'income' | 'expense');
                setCategoryId(undefined);
              }}
              className="mr-2"
            />
            수입
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="expense"
              checked={type === 'expense'}
              onChange={(e) => {
                setType(e.target.value as 'income' | 'expense');
                setCategoryId(undefined);
              }}
              className="mr-2"
            />
            지출
          </label>
        </div>
      </div>

      <CategorySelect
        value={categoryId}
        onChange={setCategoryId}
        type={type}
        error={error && !categoryId ? error : undefined}
      />

      <Input
        label="금액"
        type="number"
        step="0.01"
        min="0"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        required
        error={error && !amount ? error : undefined}
      />

      <Input
        label="거래일자"
        type="date"
        value={transactionDate}
        onChange={(e) => setTransactionDate(e.target.value)}
        required
      />

      <Input
        label="설명 (선택사항)"
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="secondary" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? '저장 중...' : transaction ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
