'use client';

import { useState, useEffect } from 'react';
import {
  RecurringTransaction,
  RecurringTransactionCreate,
  RecurringTransactionUpdate,
  Category,
} from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface RecurringTransactionFormProps {
  recurring?: RecurringTransaction;
  categories: Category[];
  onSubmit: (data: RecurringTransactionCreate | RecurringTransactionUpdate) => Promise<void>;
  onCancel: () => void;
}

export const RecurringTransactionForm: React.FC<RecurringTransactionFormProps> = ({
  recurring,
  categories,
  onSubmit,
  onCancel,
}) => {
  const [categoryId, setCategoryId] = useState<number | undefined>(recurring?.category_id);
  const [type, setType] = useState<'income' | 'expense'>(recurring?.type || 'expense');
  const [amount, setAmount] = useState<string>(recurring?.amount?.toString() || '');
  const [description, setDescription] = useState<string>(recurring?.description || '');
  const [frequency, setFrequency] = useState<'daily' | 'weekly' | 'monthly' | 'yearly'>(
    recurring?.frequency || 'monthly'
  );
  const [dayOfMonth, setDayOfMonth] = useState<string>(recurring?.day_of_month?.toString() || '');
  const [dayOfWeek, setDayOfWeek] = useState<string>(recurring?.day_of_week?.toString() || '');
  const [startDate, setStartDate] = useState<string>(
    recurring?.start_date ? new Date(recurring.start_date).toISOString().split('T')[0] : ''
  );
  const [endDate, setEndDate] = useState<string>(
    recurring?.end_date ? new Date(recurring.end_date).toISOString().split('T')[0] : ''
  );
  const [isActive, setIsActive] = useState<boolean>(recurring?.is_active ?? true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  // 타입 변경 시 카테고리 필터링
  useEffect(() => {
    if (categories.length > 0) {
      const filteredCategories = categories.filter((c) => c.type === type);
      if (filteredCategories.length > 0 && (!categoryId || !filteredCategories.find((c) => c.id === categoryId))) {
        setCategoryId(filteredCategories[0].id);
      }
    }
  }, [type, categories]);

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

    if (!startDate) {
      setError('시작일을 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const data: RecurringTransactionCreate | RecurringTransactionUpdate = {
        category_id: categoryId,
        type,
        amount: parseFloat(amount),
        description: description.trim() || undefined,
        frequency,
        day_of_month: frequency === 'monthly' && dayOfMonth ? parseInt(dayOfMonth) : undefined,
        day_of_week: frequency === 'weekly' && dayOfWeek ? parseInt(dayOfWeek) : undefined,
        start_date: startDate,
        end_date: endDate || undefined,
        is_active: isActive,
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
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">유형</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="income"
              checked={type === 'income'}
              onChange={(e) => setType(e.target.value as 'income' | 'expense')}
              className="mr-2"
            />
            수입
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              value="expense"
              checked={type === 'expense'}
              onChange={(e) => setType(e.target.value as 'income' | 'expense')}
              className="mr-2"
            />
            지출
          </label>
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          카테고리 <span className="text-red-500">*</span>
        </label>
        <select
          value={categoryId || ''}
          onChange={(e) => setCategoryId(Number(e.target.value))}
          className="w-full px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-all"
          required
        >
          <option value="">카테고리 선택</option>
          {categories.filter((c) => c.type === type).map((category) => (
            <option key={category.id} value={category.id}>
              {category.name}
            </option>
          ))}
        </select>
      </div>

      <Input
        label="금액"
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="금액을 입력하세요"
        min="0"
        step="0.01"
        required
      />

      <Input
        label="설명 (선택사항)"
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          반복 주기 <span className="text-red-500">*</span>
        </label>
        <select
          value={frequency}
          onChange={(e) => setFrequency(e.target.value as any)}
          className="w-full px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-all"
          required
        >
          <option value="daily">매일</option>
          <option value="weekly">매주</option>
          <option value="monthly">매월</option>
          <option value="yearly">매년</option>
        </select>
      </div>

      {frequency === 'weekly' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">요일</label>
          <select
            value={dayOfWeek}
            onChange={(e) => setDayOfWeek(e.target.value)}
            className="w-full px-4 py-2.5 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border-2 border-gray-200 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 transition-all"
          >
            <option value="">선택하세요</option>
            <option value="0">월요일</option>
            <option value="1">화요일</option>
            <option value="2">수요일</option>
            <option value="3">목요일</option>
            <option value="4">금요일</option>
            <option value="5">토요일</option>
            <option value="6">일요일</option>
          </select>
        </div>
      )}

      {frequency === 'monthly' && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">일자 (비워두면 매월 마지막 날)</label>
          <Input
            type="number"
            value={dayOfMonth}
            onChange={(e) => setDayOfMonth(e.target.value)}
            placeholder="1-31 (비워두면 마지막 날)"
            min="1"
            max="31"
          />
        </div>
      )}

      <Input
        label="시작일"
        type="date"
        value={startDate}
        onChange={(e) => setStartDate(e.target.value)}
        required
      />

      <Input
        label="종료일 (선택사항, 비워두면 무제한)"
        type="date"
        value={endDate}
        onChange={(e) => setEndDate(e.target.value)}
      />

      <div>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
            className="mr-2"
          />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">활성화</span>
        </label>
      </div>

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      <div className="flex gap-2 justify-end pt-2">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={loading} className="min-w-[80px]">
          {loading ? '저장 중...' : recurring ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
