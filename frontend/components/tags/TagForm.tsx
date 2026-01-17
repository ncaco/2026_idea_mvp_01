'use client';

import { useState } from 'react';
import {
  Tag,
  TagCreate,
  TagUpdate,
} from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

interface TagFormProps {
  tag?: Tag;
  onSubmit: (data: TagCreate | TagUpdate) => Promise<void>;
  onCancel: () => void;
}

export const TagForm: React.FC<TagFormProps> = ({
  tag,
  onSubmit,
  onCancel,
}) => {
  const [name, setName] = useState<string>(tag?.name || '');
  const [color, setColor] = useState<string>(tag?.color || '#3B82F6');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!name.trim()) {
      setError('태그명을 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      const data: TagCreate | TagUpdate = {
        name: name.trim(),
        color: color || undefined,
      };

      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="태그명"
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        error={error && !name.trim() ? error : undefined}
      />

      <Input
        label="색상"
        type="color"
        value={color}
        onChange={(e) => setColor(e.target.value)}
      />

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      <div className="flex gap-2 justify-end pt-2">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={loading} className="min-w-[80px]">
          {loading ? '저장 중...' : tag ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
