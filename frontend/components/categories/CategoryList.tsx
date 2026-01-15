'use client';

import { useState, useEffect } from 'react';
import { Category, categoryAPI, CategoryCreate, CategoryUpdate } from '@/lib/api';
import { CategoryForm } from './CategoryForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export const CategoryList: React.FC = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | undefined>();
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');

  useEffect(() => {
    loadCategories();
  }, [filterType]);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const type = filterType === 'all' ? undefined : filterType;
      const data = await categoryAPI.getAll(type);
      setCategories(data);
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

  const incomeCategories = categories.filter((c) => c.type === 'income');
  const expenseCategories = categories.filter((c) => c.type === 'expense');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">카테고리 관리</h2>
        <Button onClick={() => {
          setEditingCategory(undefined);
          setShowForm(true);
        }}>
          카테고리 추가
        </Button>
      </div>

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

      {showForm && (
        <Card title={editingCategory ? '카테고리 수정' : '카테고리 등록'}>
          <CategoryForm
            category={editingCategory}
            onSubmit={handleSubmit}
            onCancel={handleCancel}
          />
        </Card>
      )}

      {loading ? (
        <Card>
          <div className="text-center py-8 text-gray-500">로딩 중...</div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {incomeCategories.length > 0 && (
            <Card title="수입 카테고리">
              <div className="space-y-2">
                {incomeCategories.map((category) => (
                  <div
                    key={category.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      {category.color && (
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: category.color }}
                        />
                      )}
                      <span className="font-medium">{category.name}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => {
                          if (confirm('정말 삭제하시겠습니까?')) {
                            handleDelete(category.id);
                          }
                        }}
                      >
                        삭제
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {expenseCategories.length > 0 && (
            <Card title="지출 카테고리">
              <div className="space-y-2">
                {expenseCategories.map((category) => (
                  <div
                    key={category.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-2">
                      {category.color && (
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: category.color }}
                        />
                      )}
                      <span className="font-medium">{category.name}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => {
                          if (confirm('정말 삭제하시겠습니까?')) {
                            handleDelete(category.id);
                          }
                        }}
                      >
                        삭제
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {categories.length === 0 && (
            <Card>
              <div className="text-center py-8 text-gray-500">카테고리가 없습니다.</div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};
