'use client';

import { useState } from 'react';
import { Category, CategoryCreate, CategoryUpdate } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface CategoryFormProps {
  category?: Category;
  onSubmit: (data: CategoryCreate | CategoryUpdate) => Promise<void>;
  onCancel: () => void;
}

export const CategoryForm: React.FC<CategoryFormProps> = ({
  category,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState<string>(category?.name || '');
  const [type, setType] = useState<'income' | 'expense'>(category?.type || 'expense');
  const [color, setColor] = useState<string>(category?.color || '#3B82F6');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!name.trim()) {
      setError('카테고리명을 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const data: CategoryCreate | CategoryUpdate = {
        name: name.trim(),
        type,
        color: color || undefined,
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

      <Input
        label="카테고리명"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        error={error && !name.trim() ? error : undefined}
      />

      <Input
        label="색상"
        type="color"
        value={color}
        onChange={(e) => setColor(e.target.value)}
      />

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2 justify-end pt-2">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={loading} className="min-w-[80px]">
          {loading ? '저장 중...' : category ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
