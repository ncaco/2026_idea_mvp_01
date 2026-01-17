'use client';

import { useState, useEffect } from 'react';
import {
  TransactionTemplate,
  TransactionTemplateCreate,
  TransactionTemplateUpdate,
  transactionTemplateAPI,
  categoryAPI,
  Category,
} from '@/lib/api';
import { Plus, FileText, Trash2, Edit2, Copy } from 'lucide-react';
import { TemplateForm } from './TemplateForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';

export const TemplateList: React.FC = () => {
  const [templates, setTemplates] = useState<TransactionTemplate[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<TransactionTemplate | undefined>();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [templateData, categoryData] = await Promise.all([
        transactionTemplateAPI.getAll(),
        categoryAPI.getAll(),
      ]);
      setTemplates(templateData);
      setCategories(categoryData);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: TransactionTemplateCreate | TransactionTemplateUpdate) => {
    try {
      if (editingTemplate) {
        await transactionTemplateAPI.update(editingTemplate.id, data as TransactionTemplateUpdate);
      } else {
        await transactionTemplateAPI.create(data as TransactionTemplateCreate);
      }
      await loadData();
      setShowForm(false);
      setEditingTemplate(undefined);
    } catch (error: any) {
      alert(`저장 실패: ${error.message}`);
      throw error;
    }
  };

  const handleEdit = (template: TransactionTemplate) => {
    setEditingTemplate(template);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await transactionTemplateAPI.delete(id);
      await loadData();
    } catch (error: any) {
      alert(`삭제 실패: ${error.message}`);
    }
  };

  const handleUseTemplate = (template: TransactionTemplate) => {
    window.location.href = `/transactions?template=${template.id}`;
  };

  const getCategoryName = (categoryId: number) => {
    return categories.find((c) => c.id === categoryId)?.name || '알 수 없음';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">거래 템플릿</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">자주 사용하는 거래를 템플릿으로 저장하세요</p>
        </div>
        <Button
          size="md"
          onClick={() => {
            setEditingTemplate(undefined);
            setShowForm(true);
          }}
        >
          <Plus className="w-4 h-4" />
          템플릿 추가
        </Button>
      </div>

      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        ) : templates.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 text-base">
            템플릿이 없습니다.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card
                key={template.id}
                compact
                className="interactive hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                    <span className="font-bold text-sm truncate dark:text-gray-100">{template.name}</span>
                  </div>
                </div>
                <div className="space-y-1 mb-3 text-sm">
                  <div className="text-gray-600 dark:text-gray-400">
                    카테고리: <span className="font-medium">{getCategoryName(template.category_id)}</span>
                  </div>
                  <div className="text-gray-600 dark:text-gray-400">
                    유형: <span className={`font-medium ${template.type === 'income' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
                      {template.type === 'income' ? '수입' : '지출'}
                    </span>
                  </div>
                  <div className="text-gray-600 dark:text-gray-400">
                    금액: <span className="font-medium">₩{Number(template.amount).toLocaleString()}</span>
                  </div>
                  {template.description && (
                    <div className="text-gray-600 dark:text-gray-400 text-xs truncate">
                      {template.description}
                    </div>
                  )}
                </div>
                <div className="flex gap-2 pt-3 border-t-2 border-gray-200 dark:border-gray-700">
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => handleUseTemplate(template)}
                    className="flex-1 min-w-[70px]"
                  >
                    <Copy className="w-4 h-4" />
                    사용
                  </Button>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleEdit(template)}
                    className="flex-1 min-w-[70px]"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(template.id)}
                    className="flex-1 min-w-[70px]"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
      </Card>

      <Modal
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setEditingTemplate(undefined);
        }}
        title={editingTemplate ? '템플릿 수정' : '템플릿 추가'}
        size="md"
      >
        <TemplateForm
          template={editingTemplate}
          categories={categories}
          onSubmit={handleSubmit}
          onCancel={() => {
            setShowForm(false);
            setEditingTemplate(undefined);
          }}
        />
      </Modal>
    </div>
  );
};
