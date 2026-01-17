'use client';

import { useState } from 'react';
import { Download, Upload, Database } from 'lucide-react';
import { backupAPI } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

export const BackupRestore: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>('');

  const handleExport = async () => {
    try {
      setLoading(true);
      setMessage('');
      const blob = await backupAPI.export();
      
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `backup_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
      
      setMessage('백업 파일이 다운로드되었습니다.');
    } catch (error: any) {
      setMessage(`백업 실패: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!confirm('기존 데이터가 덮어씌워질 수 있습니다. 계속하시겠습니까?')) {
      return;
    }

    try {
      setLoading(true);
      setMessage('');
      const result = await backupAPI.import(file);
      
      const imported = result.imported;
      const summary = Object.entries(imported)
        .filter(([_, count]) => count > 0)
        .map(([key, count]) => `${key}: ${count}건`)
        .join(', ');
      
      setMessage(`복원 완료: ${summary}`);
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (error: any) {
      setMessage(`복원 실패: ${error.message}`);
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">데이터 백업/복원</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">데이터를 백업하고 복원하세요</p>
      </div>

      <Card compact className="border-2 border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="space-y-6">
          <div className="flex items-start gap-4">
            <Database className="w-6 h-6 text-blue-600 dark:text-blue-400 mt-1" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">백업</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                모든 거래 내역, 카테고리, 예산, 반복 거래, 태그를 JSON 파일로 백업합니다.
              </p>
              <Button
                onClick={handleExport}
                disabled={loading}
                size="md"
              >
                <Download className="w-4 h-4" />
                백업 다운로드
              </Button>
            </div>
          </div>

          <div className="border-t-2 border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex items-start gap-4">
              <Upload className="w-6 h-6 text-green-600 dark:text-green-400 mt-1" />
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">복원</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  백업 파일을 업로드하여 데이터를 복원합니다. 기존 데이터와 병합됩니다.
                </p>
                <label htmlFor="backup-file" className="cursor-pointer">
                  <Button
                    variant="secondary"
                    disabled={loading}
                    size="md"
                    as="span"
                  >
                    <Upload className="w-4 h-4" />
                    백업 파일 업로드
                  </Button>
                </label>
                <input
                  id="backup-file"
                  type="file"
                  accept=".json"
                  onChange={handleImport}
                  className="hidden"
                />
              </div>
            </div>
          </div>

          {message && (
            <div className={`p-3 rounded-lg ${
              message.includes('실패') 
                ? 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-300'
                : 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-300'
            }`}>
              {message}
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};
