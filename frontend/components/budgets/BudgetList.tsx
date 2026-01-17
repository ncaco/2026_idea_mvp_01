'use client';

import { useState, useEffect } from 'react';
import {
  Budget,
  BudgetCreate,
  BudgetUpdate,
  budgetAPI,
  categoryAPI,
  Category,
  BudgetStatus,
} from '@/lib/api';
import { Plus, Trash2, AlertTriangle } from 'lucide-react';
import { BudgetForm } from './BudgetForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';

export const BudgetList: React.FC = () => {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [budgetStatuses, setBudgetStatuses] = useState<BudgetStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingBudget, setEditingBudget] = useState<Budget | undefined>();
  const [selectedMonth, setSelectedMonth] = useState<string>(() => {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  });

  useEffect(() => {
    loadCategories();
    loadBudgets();
    loadBudgetStatus();
  }, [selectedMonth]);

  const loadCategories = async () => {
    try {
      const data = await categoryAPI.getAll();
      setCategories(data);
    } catch (error) {
      console.error('카테고리 로드 실패:', error);
    }
  };

  const loadBudgets = async () => {
    try {
      setLoading(true);
      const data = await budgetAPI.getAll({ month: selectedMonth });
      setBudgets(data);
    } catch (error) {
      console.error('예산 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadBudgetStatus = async () => {
    try {
      const data = await budgetAPI.getStatus(selectedMonth);
      setBudgetStatuses(data);
    } catch (error) {
      console.error('예산 현황 로드 실패:', error);
    }
  };

  const handleSubmit = async (data: BudgetCreate | BudgetUpdate) => {
    try {
      if (editingBudget) {
        await budgetAPI.update(editingBudget.id, data as BudgetUpdate);
      } else {
        await budgetAPI.create(data as BudgetCreate);
      }
      await loadBudgets();
      await loadBudgetStatus();
      setShowForm(false);
      setEditingBudget(undefined);
    } catch (error) {
      console.error('예산 저장 실패:', error);
      throw error;
    }
  };

  const handleEdit = (budget: Budget) => {
    setEditingBudget(budget);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await budgetAPI.delete(id);
      await loadBudgets();
      await loadBudgetStatus();
    } catch (error) {
      console.error('예산 삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingBudget(undefined);
  };

  const getCategoryName = (categoryId: number | undefined) => {
    if (!categoryId) return '전체 예산';
    return categories.find((c) => c.id === categoryId)?.name || '알 수 없음';
  };

  const getBudgetStatus = (budgetId: number) => {
    return budgetStatuses.find((s) => s.budget_id === budgetId);
  };

  const formatMonth = (month: string) => {
    const [year, monthNum] = month.split('-');
    return `${year}년 ${parseInt(monthNum)}월`;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">예산 관리</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">월별 예산을 설정하고 지출 현황을 확인하세요</p>
        </div>
        <div className="flex gap-2">
          <Input
            type="month"
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            className="w-40"
          />
          <Button
            size="sm"
            onClick={() => {
              setEditingBudget(undefined);
              setShowForm(true);
            }}
            className="min-w-[40px]"
            title="예산 추가"
          >
            <Plus className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* 예산 초과 알림 */}
      {budgetStatuses.filter(s => s.is_over_budget).length > 0 && (
        <Card compact className="border-2 border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20 mb-4">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400" />
            <span className="font-semibold text-red-900 dark:text-red-300">
              {budgetStatuses.filter(s => s.is_over_budget).length}개의 예산이 초과되었습니다.
            </span>
          </div>
        </Card>
      )}

      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        ) : budgets.length === 0 ? (
          <div className="text-center py-12 text-gray-500 text-base">
            {formatMonth(selectedMonth)} 예산이 없습니다.
          </div>
        ) : (
          <div className="space-y-4">
            {budgets.map((budget) => {
              const status = getBudgetStatus(budget.id);
              const percentage = status?.percentage || 0;
              const isOver = status?.is_over_budget || false;
              const spent = status?.spent_amount || 0;
              const remaining = status?.remaining_amount || budget.amount;

              return (
                <div
                  key={budget.id}
                  className={`p-4 border-2 rounded-lg transition-colors ${
                    isOver
                      ? 'border-red-300 dark:border-red-600 bg-red-50 dark:bg-red-900/20'
                      : 'border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 bg-white dark:bg-gray-800'
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                        {getCategoryName(budget.category_id)}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        예산: ₩{Number(budget.amount).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEdit(budget)}
                        className="min-w-[60px]"
                      >
                        수정
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDelete(budget.id)}
                        className="min-w-[40px]"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>

                  {status && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">사용 금액</span>
                        <span className={`font-semibold ${isOver ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}>
                          ₩{Number(spent).toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">잔여 금액</span>
                        <span className={`font-semibold ${remaining < 0 ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-gray-100'}`}>
                          ₩{Number(remaining).toLocaleString()}
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                        <div
                          className={`h-3 rounded-full transition-all ${
                            isOver
                              ? 'bg-red-500 dark:bg-red-600'
                              : percentage >= 80
                              ? 'bg-yellow-500 dark:bg-yellow-600'
                              : 'bg-blue-500 dark:bg-blue-600'
                          }`}
                          style={{ width: `${Math.min(percentage, 100)}%` }}
                        />
                      </div>
                      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>사용률</span>
                        <span className={isOver ? 'text-red-600 dark:text-red-400 font-semibold' : ''}>
                          {percentage.toFixed(1)}%
                          {isOver && ' (초과)'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>

      <Modal
        isOpen={showForm}
        onClose={handleCancel}
        title={editingBudget ? '예산 수정' : '예산 등록'}
        size="md"
      >
        <BudgetForm
          budget={editingBudget}
          defaultMonth={selectedMonth}
          categories={categories}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};
