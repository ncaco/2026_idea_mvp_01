'use client';

import { useState } from 'react';
import {
  TransactionTemplate,
  TransactionTemplateCreate,
  TransactionTemplateUpdate,
  Category,
} from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { CategorySelect } from '@/components/categories/CategorySelect';

interface TemplateFormProps {
  template?: TransactionTemplate;
  categories: Category[];
  onSubmit: (data: TransactionTemplateCreate | TransactionTemplateUpdate) => Promise<void>;
  onCancel: () => void;
}

export const TemplateForm: React.FC<TemplateFormProps> = ({
  template,
  categories,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState<string>(template?.name || '');
  const [categoryId, setCategoryId] = useState<number | undefined>(template?.category_id);
  const [type, setType] = useState<'income' | 'expense'>(template?.type || 'expense');
  const [amount, setAmount] = useState<string>(template?.amount?.toString() || '');
  const [description, setDescription] = useState<string>(template?.description || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!name.trim()) {
      setError('템플릿 이름을 입력해주세요.');
      setLoading(false);
      return;
    }

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
      const data: TransactionTemplateCreate | TransactionTemplateUpdate = {
        name: name.trim(),
        category_id: categoryId,
        type,
        amount: parseFloat(amount),
        description: description.trim() || undefined,
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
      <Input
        label="템플릿 이름"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">유형</label>
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
        type={type}
        value={categoryId}
        onChange={(id) => setCategoryId(id)}
        error={error && !categoryId ? error : undefined}
      />

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

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      <div className="flex gap-2 justify-end pt-2">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={loading} className="min-w-[80px]">
          {loading ? '저장 중...' : template ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
