'use client';

import { useState, useEffect } from 'react';
import { statisticsAPI, categoryAPI, Category } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const AdvancedStatistics: React.FC = () => {
  const [startDate, setStartDate] = useState<string>(() => {
    const date = new Date();
    date.setMonth(date.getMonth() - 1);
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [selectedCategories, setSelectedCategories] = useState<number[]>([]);
  const [minAmount, setMinAmount] = useState<string>('');
  const [maxAmount, setMaxAmount] = useState<string>('');
  const [type, setType] = useState<'income' | 'expense'>('expense');
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoryStats, setCategoryStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    loadStatistics();
  }, [startDate, endDate, selectedCategories, minAmount, maxAmount, type]);

  const loadCategories = async () => {
    try {
      const data = await categoryAPI.getAll();
      setCategories(data.filter(c => c.type === type));
    } catch (error) {
      console.error('카테고리 로드 실패:', error);
    }
  };

  const loadStatistics = async () => {
    try {
      setLoading(true);
      const year = new Date(startDate).getFullYear();
      const month = new Date(startDate).getMonth() + 1;
      
      const stats = await statisticsAPI.getByCategory(year, month, type);
      
      // 필터 적용
      let filtered = stats;
      
      if (selectedCategories.length > 0) {
        filtered = filtered.filter(s => selectedCategories.includes(s.category_id));
      }
      
      if (minAmount) {
        filtered = filtered.filter(s => s.total >= parseFloat(minAmount));
      }
      
      if (maxAmount) {
        filtered = filtered.filter(s => s.total <= parseFloat(maxAmount));
      }
      
      setCategoryStats(filtered);
    } catch (error) {
      console.error('통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (categoryId: number) => {
    if (selectedCategories.includes(categoryId)) {
      setSelectedCategories(selectedCategories.filter(id => id !== categoryId));
    } else {
      setSelectedCategories([...selectedCategories, categoryId]);
    }
  };

  const totalAmount = categoryStats.reduce((sum, s) => sum + s.total, 0);

  const COLORS = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4'];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">고급 통계</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">기간별, 카테고리별, 금액대별 상세 통계</p>
      </div>

      {/* 필터 */}
      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="p-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="시작 날짜"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <Input
              label="종료 날짜"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>

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
                    setSelectedCategories([]);
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
                    setType(e.target.value as 'expense');
                    setSelectedCategories([]);
                  }}
                  className="mr-2"
                />
                지출
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="최소 금액"
              type="number"
              value={minAmount}
              onChange={(e) => setMinAmount(e.target.value)}
              placeholder="최소 금액"
            />
            <Input
              label="최대 금액"
              type="number"
              value={maxAmount}
              onChange={(e) => setMaxAmount(e.target.value)}
              placeholder="최대 금액"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">카테고리 필터</label>
            <div className="flex flex-wrap gap-2">
              {categories.map((category) => (
                <button
                  key={category.id}
                  type="button"
                  onClick={() => toggleCategory(category.id)}
                  className={`px-3 py-1.5 text-xs rounded-md border transition-colors ${
                    selectedCategories.includes(category.id)
                      ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-300 dark:border-blue-600 text-blue-700 dark:text-blue-300'
                      : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* 통계 결과 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
            카테고리별 통계
          </h3>
          <div className="p-4">
            {loading ? (
              <div className="text-center py-12">로딩 중...</div>
            ) : categoryStats.length === 0 ? (
              <div className="text-center py-12 text-gray-500">데이터가 없습니다.</div>
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={categoryStats}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category_name" />
                  <YAxis />
                  <Tooltip formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''} />
                  <Legend />
                  <Bar dataKey="total" fill="#3B82F6" name="금액" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>

        <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
            카테고리별 비율
          </h3>
          <div className="p-4">
            {loading ? (
              <div className="text-center py-12">로딩 중...</div>
            ) : categoryStats.length === 0 ? (
              <div className="text-center py-12 text-gray-500">데이터가 없습니다.</div>
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={categoryStats}
                    dataKey="total"
                    nameKey="category_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {categoryStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </Card>
      </div>

      {/* 요약 */}
      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
          통계 요약
        </h3>
        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">총 금액</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                ₩{totalAmount.toLocaleString()}
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">카테고리 수</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {categoryStats.length}개
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600 dark:text-gray-400">평균 금액</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                ₩{categoryStats.length > 0 ? (totalAmount / categoryStats.length).toLocaleString() : '0'}
              </div>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
