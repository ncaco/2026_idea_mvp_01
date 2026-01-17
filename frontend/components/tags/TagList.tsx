'use client';

import { useState, useEffect } from 'react';
import {
  Tag,
  TagCreate,
  TagUpdate,
  tagAPI,
} from '@/lib/api';
import { Plus, Tag as TagIcon, Trash2, Edit2 } from 'lucide-react';
import { TagForm } from './TagForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';

export const TagList: React.FC = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTag, setEditingTag] = useState<Tag | undefined>();

  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    try {
      setLoading(true);
      const data = await tagAPI.getAll(true); // 거래 수 포함
      setTags(data);
    } catch (error) {
      console.error('태그 로드 실패:', error);
      alert('태그를 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: TagCreate | TagUpdate) => {
    try {
      if (editingTag) {
        await tagAPI.update(editingTag.id, data as TagUpdate);
      } else {
        await tagAPI.create(data as TagCreate);
      }
      await loadTags();
      setShowForm(false);
      setEditingTag(undefined);
    } catch (error: any) {
      console.error('저장 실패:', error);
      alert(`저장 실패: ${error.message}`);
      throw error;
    }
  };

  const handleEdit = (tag: Tag) => {
    setEditingTag(tag);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까? 이 태그가 붙은 거래에서도 태그가 제거됩니다.')) return;
    try {
      await tagAPI.delete(id);
      await loadTags();
    } catch (error: any) {
      console.error('삭제 실패:', error);
      alert(`삭제 실패: ${error.message}`);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTag(undefined);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">태그 관리</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">거래에 태그를 추가하여 분류하고 통계를 확인하세요</p>
        </div>
        <Button
          size="md"
          onClick={() => {
            setEditingTag(undefined);
            setShowForm(true);
          }}
        >
          <Plus className="w-4 h-4" />
          태그 추가
        </Button>
      </div>

      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        ) : tags.length === 0 ? (
          <div className="text-center py-12 text-gray-500 dark:text-gray-400 text-base">
            태그가 없습니다.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {tags.map((tag) => (
              <Card
                key={tag.id}
                compact
                className="interactive hover:shadow-xl transition-all duration-300 border-2 border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 hover:scale-105"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    {tag.color && (
                      <div
                        className="w-4 h-4 rounded-full flex-shrink-0"
                        style={{ backgroundColor: tag.color }}
                      />
                    )}
                    <TagIcon className={`w-4 h-4 flex-shrink-0 ${tag.color ? '' : 'text-gray-400'}`} />
                    <span className="font-bold text-sm truncate dark:text-gray-100">{tag.name}</span>
                  </div>
                </div>
                <div className="space-y-1 mb-3">
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    거래 수: <span className="font-medium">{tag.transaction_count || 0}건</span>
                  </div>
                </div>
                <div className="flex gap-2 pt-3 border-t-2 border-gray-200 dark:border-gray-700">
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => handleEdit(tag)}
                    className="flex-1 min-w-[70px]"
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => handleDelete(tag.id)}
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
        onClose={handleCancel}
        title={editingTag ? '태그 수정' : '태그 추가'}
        size="md"
      >
        <TagForm
          tag={editingTag}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};
