'use client';

import { useState, useEffect } from 'react';
import {
  RecurringTransaction,
  RecurringTransactionCreate,
  RecurringTransactionUpdate,
  recurringTransactionAPI,
  categoryAPI,
  Category,
} from '@/lib/api';
import { Plus, Repeat, Calendar, Trash2, Edit2, Play, Pause } from 'lucide-react';
import { RecurringTransactionForm } from './RecurringTransactionForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';

export const RecurringTransactionList: React.FC = () => {
  const [recurringTransactions, setRecurringTransactions] = useState<RecurringTransaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRecurring, setEditingRecurring] = useState<RecurringTransaction | undefined>();
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined);

  useEffect(() => {
    loadData();
  }, [filterActive]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [recurringData, categoryData] = await Promise.all([
        recurringTransactionAPI.getAll(filterActive),
        categoryAPI.getAll(),
      ]);
      setRecurringTransactions(recurringData);
      setCategories(categoryData);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      alert('데이터를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: RecurringTransactionCreate | RecurringTransactionUpdate) => {
    try {
      if (editingRecurring) {
        await recurringTransactionAPI.update(editingRecurring.id, data as RecurringTransactionUpdate);
      } else {
        await recurringTransactionAPI.create(data as RecurringTransactionCreate);
      }
      await loadData();
      setShowForm(false);
      setEditingRecurring(undefined);
    } catch (error: any) {
      console.error('저장 실패:', error);
      alert(`저장 실패: ${error.message}`);
      throw error;
    }
  };

  const handleEdit = (recurring: RecurringTransaction) => {
    setEditingRecurring(recurring);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await recurringTransactionAPI.delete(id);
      await loadData();
    } catch (error: any) {
      console.error('삭제 실패:', error);
      alert(`삭제 실패: ${error.message}`);
    }
  };

  const handleToggleActive = async (recurring: RecurringTransaction) => {
    try {
      await recurringTransactionAPI.update(recurring.id, { is_active: !recurring.is_active });
      await loadData();
    } catch (error: any) {
      console.error('상태 변경 실패:', error);
      alert(`상태 변경 실패: ${error.message}`);
    }
  };

  const handleGenerate = async () => {
    try {
      const result = await recurringTransactionAPI.generate();
      alert(result.message);
      // 거래 내역 페이지로 이동하거나 새로고침
      window.location.href = '/transactions';
    } catch (error: any) {
      console.error('거래 생성 실패:', error);
      alert(`거래 생성 실패: ${error.message}`);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingRecurring(undefined);
  };

  const getCategoryName = (categoryId: number) => {
    return categories.find((c) => c.id === categoryId)?.name || '알 수 없음';
  };

  const getFrequencyText = (frequency: string, dayOfMonth?: number, dayOfWeek?: number) => {
    switch (frequency) {
      case 'daily':
        return '매일';
      case 'weekly':
        const weekdays = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'];
        return dayOfWeek !== undefined ? `매주 ${weekdays[dayOfWeek]}` : '매주';
      case 'monthly':
        return dayOfMonth ? `매월 ${dayOfMonth}일` : '매월 마지막 날';
      case 'yearly':
        return '매년';
      default:
        return frequency;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">반복 거래 설정</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">정기 수입/지출을 자동으로 생성하세요</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="md"
            onClick={handleGenerate}
          >
            <Play className="w-4 h-4" />
            거래 생성
          </Button>
          <Button
            size="md"
            onClick={() => {
              setEditingRecurring(undefined);
              setShowForm(true);
            }}
          >
            <Plus className="w-4 h-4" />
            반복 거래 추가
          </Button>
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          variant={filterActive === undefined ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setFilterActive(undefined)}
          className="min-w-[60px]"
        >
          전체
        </Button>
        <Button
          variant={filterActive === true ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setFilterActive(true)}
          className="min-w-[60px]"
        >
          활성
        </Button>
        <Button
          variant={filterActive === false ? 'primary' : 'secondary'}
          size="sm"
          onClick={() => setFilterActive(false)}
          className="min-w-[60px]"
        >
          비활성
        </Button>
      </div>

      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        ) : recurringTransactions.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 text-base">
            반복 거래가 없습니다.
          </div>
        ) : (
          <div className="space-y-4">
            {recurringTransactions.map((recurring) => (
              <div
                key={recurring.id}
                className="p-4 border-2 border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors bg-white dark:bg-gray-800"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Repeat className={`w-5 h-5 ${recurring.is_active ? 'text-blue-600 dark:text-blue-400' : 'text-gray-400'}`} />
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {getCategoryName(recurring.category_id)}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs rounded-full font-medium ${
                          recurring.type === 'income'
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                            : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                        }`}
                      >
                        {recurring.type === 'income' ? '수입' : '지출'}
                      </span>
                      {!recurring.is_active && (
                        <span className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                          비활성
                        </span>
                      )}
                    </div>
                    <div className="space-y-1 text-sm text-gray-600 dark:text-gray-400">
                      <p>
                        <span className="font-semibold">금액:</span> ₩{Number(recurring.amount).toLocaleString()}
                      </p>
                      {recurring.description && (
                        <p>
                          <span className="font-semibold">설명:</span> {recurring.description}
                        </p>
                      )}
                      <p>
                        <span className="font-semibold">반복:</span> {getFrequencyText(recurring.frequency, recurring.day_of_month, recurring.day_of_week)}
                      </p>
                      <p>
                        <span className="font-semibold">시작일:</span> {new Date(recurring.start_date).toLocaleDateString('ko-KR')}
                        {recurring.end_date && (
                          <> ~ {new Date(recurring.end_date).toLocaleDateString('ko-KR')}</>
                        )}
                      </p>
                      {recurring.last_generated_date && (
                        <p>
                          <span className="font-semibold">마지막 생성:</span> {new Date(recurring.last_generated_date).toLocaleDateString('ko-KR')}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleToggleActive(recurring)}
                      className="min-w-[40px]"
                      title={recurring.is_active ? '비활성화' : '활성화'}
                    >
                      {recurring.is_active ? (
                        <Pause className="w-4 h-4" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleEdit(recurring)}
                      className="min-w-[60px]"
                    >
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDelete(recurring.id)}
                      className="min-w-[40px]"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Modal
        isOpen={showForm}
        onClose={handleCancel}
        title={editingRecurring ? '반복 거래 수정' : '반복 거래 추가'}
        size="md"
      >
        <RecurringTransactionForm
          recurring={editingRecurring}
          categories={categories}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};
