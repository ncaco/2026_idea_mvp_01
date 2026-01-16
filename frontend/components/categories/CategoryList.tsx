'use client';

import { useState, useEffect } from 'react';
import {
  Category,
  categoryAPI,
  CategoryCreate,
  CategoryUpdate,
  transactionAPI,
  Transaction,
  statisticsAPI,
  CategoryStatistics,
} from '@/lib/api';
import { CategoryForm } from './CategoryForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { SearchInput } from '@/components/ui/SearchInput';

interface CategoryWithStats extends Category {
  transactionCount?: number;
  totalAmount?: number;
}

export const CategoryList: React.FC = () => {
  const [categories, setCategories] = useState<CategoryWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | undefined>();
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');
  const [searchValue, setSearchValue] = useState('');

  useEffect(() => {
    loadCategories();
  }, [filterType]);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const type = filterType === 'all' ? undefined : filterType;
      const categoryData = await categoryAPI.getAll(type);
      
      // 통계 정보 로드
      const now = new Date();
      const currentYear = now.getFullYear();
      const currentMonth = now.getMonth() + 1;
      
      const categoriesWithStats = await Promise.all(
        categoryData.map(async (category) => {
          try {
            // 해당 카테고리의 거래 내역 가져오기
            const transactions = await transactionAPI.getAll({
              category_id: category.id,
              start_date: `${currentYear}-${String(currentMonth).padStart(2, '0')}-01`,
              limit: 1000,
            });
            
            const filteredTransactions = transactions.filter(
              (t) =>
                new Date(t.transaction_date).getFullYear() === currentYear &&
                new Date(t.transaction_date).getMonth() + 1 === currentMonth
            );
            
            const totalAmount = filteredTransactions.reduce((sum, t) => sum + t.amount, 0);
            const transactionCount = filteredTransactions.length;
            
            return {
              ...category,
              transactionCount,
              totalAmount,
            };
          } catch (error) {
            return {
              ...category,
              transactionCount: 0,
              totalAmount: 0,
            };
          }
        })
      );
      
      setCategories(categoriesWithStats);
    } catch (error) {
      console.error('카테고리 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: CategoryCreate | CategoryUpdate) => {
    try {
      if (editingCategory) {
        await categoryAPI.update(editingCategory.id, data as CategoryUpdate);
      } else {
        await categoryAPI.create(data as CategoryCreate);
      }
      await loadCategories();
      setShowForm(false);
      setEditingCategory(undefined);
    } catch (error) {
      console.error('카테고리 저장 실패:', error);
      throw error;
    }
  };

  const handleEdit = (category: Category) => {
    setEditingCategory(category);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await categoryAPI.delete(id);
      await loadCategories();
    } catch (error) {
      console.error('카테고리 삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingCategory(undefined);
  };

  const filteredCategories = categories.filter((category) => {
    if (searchValue) {
      return category.name.toLowerCase().includes(searchValue.toLowerCase());
    }
    return true;
  });

  const incomeCategories = filteredCategories.filter((c) => c.type === 'income');
  const expenseCategories = filteredCategories.filter((c) => c.type === 'expense');

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">카테고리 관리</h2>
        <Button
          onClick={() => {
            setEditingCategory(undefined);
            setShowForm(true);
          }}
        >
          카테고리 추가
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2">
          <Button
            variant={filterType === 'all' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('all')}
          >
            전체
          </Button>
          <Button
            variant={filterType === 'income' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('income')}
          >
            수입
          </Button>
          <Button
            variant={filterType === 'expense' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('expense')}
          >
            지출
          </Button>
        </div>
        <div className="flex-1 max-w-xs">
          <SearchInput
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="카테고리 검색..."
          />
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i} compact>
              <div className="h-32 skeleton rounded" />
            </Card>
          ))}
        </div>
      ) : (
        <>
          {incomeCategories.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">수입 카테고리</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {incomeCategories.map((category) => (
                  <Card
                    key={category.id}
                    compact
                    className="interactive hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {category.color && (
                          <div
                            className="w-4 h-4 rounded-full flex-shrink-0"
                            style={{ backgroundColor: category.color }}
                          />
                        )}
                        <span className="font-semibold text-sm truncate">{category.name}</span>
                      </div>
                    </div>
                    <div className="space-y-1 mb-3">
                      <div className="text-xs text-gray-600">
                        거래 수: <span className="font-medium">{category.transactionCount || 0}건</span>
                      </div>
                      <div className="text-xs text-gray-600">
                        총액: <span className="font-medium text-green-600">
                          ₩{(category.totalAmount || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-2 border-t border-gray-100">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                        className="flex-1 text-xs"
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(category.id)}
                        className="flex-1 text-xs"
                      >
                        삭제
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {expenseCategories.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2 mt-4">지출 카테고리</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                {expenseCategories.map((category) => (
                  <Card
                    key={category.id}
                    compact
                    className="interactive hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {category.color && (
                          <div
                            className="w-4 h-4 rounded-full flex-shrink-0"
                            style={{ backgroundColor: category.color }}
                          />
                        )}
                        <span className="font-semibold text-sm truncate">{category.name}</span>
                      </div>
                    </div>
                    <div className="space-y-1 mb-3">
                      <div className="text-xs text-gray-600">
                        거래 수: <span className="font-medium">{category.transactionCount || 0}건</span>
                      </div>
                      <div className="text-xs text-gray-600">
                        총액: <span className="font-medium text-red-600">
                          ₩{(category.totalAmount || 0).toLocaleString()}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-2 border-t border-gray-100">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                        className="flex-1 text-xs"
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(category.id)}
                        className="flex-1 text-xs"
                      >
                        삭제
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {filteredCategories.length === 0 && (
            <Card>
              <div className="text-center py-12 text-gray-500">
                {searchValue ? '검색 결과가 없습니다.' : '카테고리가 없습니다.'}
              </div>
            </Card>
          )}
        </>
      )}

      <Modal
        isOpen={showForm}
        onClose={handleCancel}
        title={editingCategory ? '카테고리 수정' : '카테고리 등록'}
        size="md"
      >
        <CategoryForm
          category={editingCategory}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};
