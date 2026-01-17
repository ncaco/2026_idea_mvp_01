'use client';

import React from 'react';
import { SearchInput } from './SearchInput';
import { DateRangePicker } from './DateRangePicker';
import { Button } from './Button';
import { Card } from './Card';
import { Category } from '@/lib/api';

interface FilterBarProps {
  searchValue: string;
  onSearchChange: (value: string) => void;
  startDate?: string;
  endDate?: string;
  onDateRangeChange: (startDate: string | undefined, endDate: string | undefined) => void;
  typeFilter?: 'income' | 'expense' | 'all';
  onTypeFilterChange: (type: 'income' | 'expense' | 'all') => void;
  categories?: Category[];
  selectedCategoryIds: number[];
  onCategoryFilterChange: (categoryIds: number[]) => void;
  onClearFilters: () => void;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  searchValue,
  onSearchChange,
  startDate,
  endDate,
  onDateRangeChange,
  typeFilter = 'all',
  onTypeFilterChange,
  categories = [],
  selectedCategoryIds,
  onCategoryFilterChange,
  onClearFilters,
  className = '',
}) => {
  const hasActiveFilters =
    searchValue ||
    startDate ||
    endDate ||
    typeFilter !== 'all' ||
    selectedCategoryIds.length > 0;

  const handleCategoryToggle = (categoryId: number) => {
    if (selectedCategoryIds.includes(categoryId)) {
      onCategoryFilterChange(selectedCategoryIds.filter((id) => id !== categoryId));
    } else {
      onCategoryFilterChange([...selectedCategoryIds, categoryId]);
    }
  };

  return (
    <Card compact className={`border-2 border-gray-200 shadow-sm ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <SearchInput
          value={searchValue}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="설명, 금액 검색..."
          className="w-full"
        />

        <DateRangePicker
          startDate={startDate}
          endDate={endDate}
          onChange={onDateRangeChange}
          className="w-full"
        />

        <div className="flex gap-2">
          <Button
            variant={typeFilter === 'all' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => onTypeFilterChange('all')}
            className="flex-1"
          >
            전체
          </Button>
          <Button
            variant={typeFilter === 'income' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => onTypeFilterChange('income')}
            className="flex-1"
          >
            수입
          </Button>
          <Button
            variant={typeFilter === 'expense' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => onTypeFilterChange('expense')}
            className="flex-1"
          >
            지출
          </Button>
        </div>

        {hasActiveFilters && (
          <Button variant="secondary" size="sm" onClick={onClearFilters} className="w-full">
            필터 초기화
          </Button>
        )}
      </div>

      {categories.length > 0 && (
        <div>
          <div className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리 필터</div>
          <div className="flex flex-wrap gap-2">
            {categories.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategoryToggle(category.id)}
                className={`px-3 py-1.5 text-xs rounded-md border transition-colors min-h-[28px] ${
                  selectedCategoryIds.includes(category.id)
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
                    : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                {category.color && (
                  <span
                    className="inline-block w-2 h-2 rounded-full mr-1.5"
                    style={{ backgroundColor: category.color }}
                  />
                )}
                {category.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
};
