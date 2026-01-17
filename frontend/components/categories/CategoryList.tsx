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
import { Download, Upload, Trash2, Plus } from 'lucide-react';
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
            
            const totalAmount = filteredTransactions.reduce((sum, t) => {
              const amount = typeof t.amount === 'number' ? t.amount : parseFloat(String(t.amount)) || 0;
              return sum + amount;
            }, 0);
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

  const handleDeleteAll = async () => {
    const typeText = filterType === 'all' 
      ? '모든 카테고리' 
      : filterType === 'income' 
        ? '모든 수입 카테고리' 
        : '모든 지출 카테고리';

    if (!confirm(`정말 ${typeText}를 전체 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }

    try {
      const type = filterType !== 'all' ? filterType : undefined;
      const result = await categoryAPI.deleteAll(type);
      alert(result.message);
      await loadCategories();
    } catch (error: any) {
      console.error('전체 삭제 실패:', error);
      alert(`전체 삭제 실패: ${error.message}`);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingCategory(undefined);
  };

  const handleExportExcel = async () => {
    try {
      const type = filterType !== 'all' ? filterType : undefined;
      await categoryAPI.exportExcel(type);
    } catch (error: any) {
      console.error('엑셀 다운로드 실패:', error);
      alert(`엑셀 다운로드 실패: ${error.message}`);
    }
  };

  const handleImportExcel = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      alert('엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.');
      return;
    }
    
    if (!confirm('엑셀 파일을 업로드하시겠습니까? 기존 카테고리는 유지되고 새 카테고리가 추가됩니다.')) {
      return;
    }
    
    try {
      const result = await categoryAPI.importExcel(file);
      alert(
        `업로드 완료!\n성공: ${result.success}건\n실패: ${result.failed}건${
          result.errors && result.errors.length > 0
            ? `\n\n오류:\n${result.errors.slice(0, 5).join('\n')}`
            : ''
        }`
      );
      await loadCategories();
      // 파일 입력 초기화
      event.target.value = '';
    } catch (error: any) {
      console.error('엑셀 업로드 실패:', error);
      alert(`엑셀 업로드 실패: ${error.message}`);
      event.target.value = '';
    }
  };

  const handleExportCsv = async () => {
    try {
      const type = filterType !== 'all' ? filterType : undefined;
      await categoryAPI.exportCsv(type);
    } catch (error: any) {
      console.error('CSV 다운로드 실패:', error);
      alert(`CSV 다운로드 실패: ${error.message}`);
    }
  };

  const handleImportCsv = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
      alert('CSV 파일(.csv)만 업로드 가능합니다.');
      return;
    }
    
    if (!confirm('CSV 파일을 업로드하시겠습니까? 기존 카테고리는 유지되고 새 카테고리가 추가됩니다.')) {
      return;
    }
    
    try {
      const result = await categoryAPI.importCsv(file);
      alert(
        `업로드 완료!\n성공: ${result.success}건\n실패: ${result.failed}건${
          result.errors && result.errors.length > 0
            ? `\n\n오류:\n${result.errors.slice(0, 5).join('\n')}`
            : ''
        }`
      );
      await loadCategories();
      // 파일 입력 초기화
      event.target.value = '';
    } catch (error: any) {
      console.error('CSV 업로드 실패:', error);
      alert(`CSV 업로드 실패: ${error.message}`);
      event.target.value = '';
    }
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
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">카테고리 관리</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">수입/지출 카테고리를 관리하고 통계를 확인하세요</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label htmlFor="category-excel-upload" className="cursor-pointer">
            <Button
              variant="secondary"
              size="sm"
              as="span"
              className="min-w-[40px]"
              title="엑셀 업로드"
            >
              <Upload className="w-4 h-4" />
            </Button>
            <input
              id="category-excel-upload"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleImportExcel}
              className="hidden"
            />
          </label>
          <label htmlFor="category-csv-upload" className="cursor-pointer">
            <Button
              variant="secondary"
              size="sm"
              as="span"
              className="min-w-[40px]"
              title="CSV 업로드"
            >
              <Upload className="w-4 h-4" />
            </Button>
            <input
              id="category-csv-upload"
              type="file"
              accept=".csv"
              onChange={handleImportCsv}
              className="hidden"
            />
          </label>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExportExcel}
            className="min-w-[40px]"
            title="엑셀 다운로드"
          >
            <Download className="w-4 h-4" />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExportCsv}
            className="min-w-[40px]"
            title="CSV 다운로드"
          >
            <Download className="w-4 h-4" />
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={handleDeleteAll}
            className="min-w-[40px]"
            title="전체 삭제"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
          <Button
            size="md"
            onClick={() => {
              setEditingCategory(undefined);
              setShowForm(true);
            }}
          >
            <Plus className="w-4 h-4" />
            카테고리 추가
          </Button>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="flex gap-2">
          <Button
            variant={filterType === 'all' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('all')}
            className="min-w-[60px]"
          >
            전체
          </Button>
          <Button
            variant={filterType === 'income' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('income')}
            className="min-w-[60px]"
          >
            수입
          </Button>
          <Button
            variant={filterType === 'expense' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setFilterType('expense')}
            className="min-w-[60px]"
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Card key={i} compact className="border-2 border-gray-200">
              <div className="h-32 skeleton rounded-xl" />
            </Card>
          ))}
        </div>
      ) : (
        <>
          {incomeCategories.length > 0 && (
            <div>
              <h3 className="text-base font-bold text-gray-800 dark:text-gray-200 mb-3 flex items-center gap-2">
                <span className="w-1 h-5 bg-green-500 rounded-full"></span>
                수입 카테고리
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {incomeCategories.map((category) => (
                  <Card
                    key={category.id}
                    compact
                    className="interactive hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-700 hover:border-green-300 dark:hover:border-green-600 hover:scale-105"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {category.color && (
                          <div
                            className="w-4 h-4 rounded-full flex-shrink-0"
                            style={{ backgroundColor: category.color }}
                          />
                        )}
                        <span className="font-bold text-sm truncate dark:text-gray-100">{category.name}</span>
                      </div>
                    </div>
                    <div className="space-y-1.5 mb-3 bg-white/50 dark:bg-gray-800/50 rounded-lg p-2">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">거래 수</span>
                        <span className="font-bold text-gray-900 dark:text-gray-100">{category.transactionCount || 0}건</span>
                      </div>
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-gray-600 dark:text-gray-400 font-medium">총액</span>
                        <span className="font-bold text-green-600 dark:text-green-400">
                          ₩{Number(category.totalAmount || 0).toLocaleString('ko-KR')}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-3 border-t-2 border-gray-200 dark:border-gray-700">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                        className="flex-1 min-w-[70px]"
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(category.id)}
                        className="flex-1 min-w-[70px]"
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
              <h3 className="text-base font-bold text-gray-800 dark:text-gray-200 mb-3 mt-6 flex items-center gap-2">
                <span className="w-1 h-5 bg-red-500 rounded-full"></span>
                지출 카테고리
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {expenseCategories.map((category) => (
                  <Card
                    key={category.id}
                    compact
                    className="interactive hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-700 hover:border-red-300 dark:hover:border-red-600 hover:scale-105"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2 flex-1 min-w-0">
                        {category.color && (
                          <div
                            className="w-4 h-4 rounded-full flex-shrink-0"
                            style={{ backgroundColor: category.color }}
                          />
                        )}
                        <span className="font-bold text-sm truncate dark:text-gray-100">{category.name}</span>
                      </div>
                    </div>
                    <div className="space-y-1 mb-3">
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        거래 수: <span className="font-medium">{category.transactionCount || 0}건</span>
                      </div>
                      <div className="text-xs text-gray-600 dark:text-gray-400">
                        총액: <span className="font-medium text-red-600 dark:text-red-400">
                          ₩{Number(category.totalAmount || 0).toLocaleString('ko-KR')}
                        </span>
                      </div>
                    </div>
                    <div className="flex gap-2 pt-3 border-t-2 border-gray-200 dark:border-gray-700">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(category)}
                        className="flex-1 min-w-[70px]"
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(category.id)}
                        className="flex-1 min-w-[70px]"
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
            <Card className="border-2 border-gray-200">
              <div className="text-center py-12 text-gray-500 text-base">
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
