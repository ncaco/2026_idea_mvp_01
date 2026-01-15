'use client';

import { useEffect, useState } from 'react';
import { categoryAPI, Category } from '@/lib/api';

interface CategorySelectProps {
  value?: number;
  onChange: (categoryId: number) => void;
  type: 'income' | 'expense';
  error?: string;
}

export const CategorySelect: React.FC<CategorySelectProps> = ({
  value,
  onChange,
  type,
  error,
}) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    categoryAPI.getAll(type).then((data) => {
      setCategories(data);
      setLoading(false);
    });
  }, [type]);

  if (loading) {
    return <div className="text-gray-500">로딩 중...</div>;
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        카테고리
      </label>
      <select
        value={value || ''}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
          error ? 'border-red-500' : 'border-gray-300'
        }`}
      >
        <option value="">카테고리 선택</option>
        {categories.map((category) => (
          <option key={category.id} value={category.id}>
            {category.name}
          </option>
        ))}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
};
