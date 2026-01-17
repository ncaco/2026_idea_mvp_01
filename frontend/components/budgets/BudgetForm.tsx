'use client';

import { useState, useEffect } from 'react';
import { Budget, BudgetCreate, BudgetUpdate, Category } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface BudgetFormProps {
  budget?: Budget;
  defaultMonth?: string;
  categories: Category[];
  onSubmit: (data: BudgetCreate | BudgetUpdate) => Promise<void>;
  onCancel: () => void;
}

export const BudgetForm: React.FC<BudgetFormProps> = ({
  budget,
  defaultMonth,
  categories,
  onSubmit,
  onCancel,
}) => {
  const [categoryId, setCategoryId] = useState<number | undefined>(budget?.category_id);
  const [amount, setAmount] = useState<string>(budget?.amount.toString() || '');
  const [month, setMonth] = useState<string>(budget?.month || defaultMonth || '');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!amount || !month) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    const amountNum = parseFloat(amount);
    if (isNaN(amountNum) || amountNum <= 0) {
      alert('올바른 금액을 입력해주세요.');
      return;
    }

    try {
      setSubmitting(true);
      const data: BudgetCreate | BudgetUpdate = {
        category_id: categoryId || undefined,
        amount: amountNum,
        month,
      };
      await onSubmit(data);
    } catch (error: any) {
      alert(error.message || '예산 저장에 실패했습니다.');
    } finally {
      setSubmitting(false);
    }
  };

  const expenseCategories = categories.filter((c) => c.type === 'expense');

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          카테고리 (선택사항)
        </label>
        <select
          value={categoryId || ''}
          onChange={(e) => setCategoryId(e.target.value ? parseInt(e.target.value) : undefined)}
          className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">전체 예산</option>
          {expenseCategories.map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
        <p className="mt-1 text-xs text-gray-500">
          카테고리를 선택하지 않으면 전체 예산으로 설정됩니다.
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          예산 금액 <span className="text-red-500">*</span>
        </label>
        <Input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="예산 금액을 입력하세요"
          min="0"
          step="0.01"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          예산 월 <span className="text-red-500">*</span>
        </label>
        <Input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          required
        />
      </div>

      <div className="flex gap-2 justify-end pt-4">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={submitting} className="min-w-[80px]">
          {submitting ? '저장 중...' : '저장'}
        </Button>
      </div>
    </form>
  );
};
