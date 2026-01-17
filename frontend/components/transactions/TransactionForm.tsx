'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  Transaction, 
  TransactionCreate, 
  TransactionUpdate, 
  categoryAPI, 
  Category,
  aiAPI,
  CategoryClassificationResponse
} from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { CategorySelect } from '@/components/categories/CategorySelect';
import { Zap } from 'lucide-react';

interface TransactionFormProps {
  transaction?: Transaction;
  onSubmit: (data: TransactionCreate | TransactionUpdate) => Promise<void>;
  onCancel: () => void;
}

// 숫자 포맷팅 유틸리티 함수
const formatNumber = (value: string): string => {
  // 숫자와 소수점만 추출
  const numericValue = value.replace(/[^\d.]/g, '');
  if (!numericValue) return '';
  
  // 소수점이 여러 개인 경우 첫 번째만 유지
  const parts = numericValue.split('.');
  const integerPart = parts[0] || '';
  const decimalPart = parts.length > 1 ? '.' + parts.slice(1).join('') : '';
  
  // 정수 부분에 콤마 추가
  const formattedInteger = integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  
  return formattedInteger + decimalPart;
};

// 콤마 제거 후 숫자로 변환
const parseNumber = (value: string): number => {
  const numericValue = value.replace(/,/g, '');
  return parseFloat(numericValue) || 0;
};

export const TransactionForm: React.FC<TransactionFormProps> = ({
  transaction,
  onSubmit,
  onCancel,
}) => {
  const [type, setType] = useState<'income' | 'expense'>(transaction?.type || 'expense');
  const [categoryId, setCategoryId] = useState<number | undefined>(transaction?.category_id);
  const [amount, setAmount] = useState<string>(
    transaction?.amount ? formatNumber(transaction.amount.toString()) : ''
  );
  const [description, setDescription] = useState<string>(transaction?.description || '');
  const [transactionDate, setTransactionDate] = useState<string>(
    transaction?.transaction_date || new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [suggestedCategory, setSuggestedCategory] = useState<CategoryClassificationResponse | null>(null);
  const [naturalLanguageText, setNaturalLanguageText] = useState<string>('');
  const [showNaturalLanguage, setShowNaturalLanguage] = useState(false);

  // 자동 카테고리 제안
  const suggestCategory = useCallback(async (desc: string) => {
    if (!desc || desc.length < 2) {
      setSuggestedCategory(null);
      return;
    }

    try {
      const result = await aiAPI.classifyCategory({
        description: desc,
        transaction_type: type,
      });
      if (result.confidence > 0.3) {
        setSuggestedCategory(result);
      } else {
        setSuggestedCategory(null);
      }
    } catch (error) {
      console.error('카테고리 제안 실패:', error);
      setSuggestedCategory(null);
    }
  }, [type]);

  // 자연어 파싱
  const handleNaturalLanguageParse = async () => {
    if (!naturalLanguageText.trim()) return;

    try {
      const result = await aiAPI.parseNaturalLanguage({ text: naturalLanguageText });
      
      if (result.transaction_date) {
        setTransactionDate(result.transaction_date);
      }
      if (result.amount) {
        setAmount(formatNumber(result.amount.toString()));
      }
      if (result.category_id) {
        setCategoryId(result.category_id);
      }
      if (result.description) {
        setDescription(result.description);
      }
      if (result.type) {
        setType(result.type);
      }

      setNaturalLanguageText('');
      setShowNaturalLanguage(false);
    } catch (error) {
      console.error('자연어 파싱 실패:', error);
      alert('자연어 파싱에 실패했습니다. 다시 시도해주세요.');
    }
  };

  // 설명 변경 시 자동 카테고리 제안
  useEffect(() => {
    const timer = setTimeout(() => {
      if (description && !transaction) {
        suggestCategory(description);
      }
    }, 500); // 500ms 디바운스

    return () => clearTimeout(timer);
  }, [description, transaction, suggestCategory]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!categoryId) {
      setError('카테고리를 선택해주세요.');
      setLoading(false);
      return;
    }

    const numericAmount = parseNumber(amount);
    if (!amount || numericAmount < 0) {
      setError('금액을 입력해주세요. (0원 이상)');
      setLoading(false);
      return;
    }

    try {
      const data: TransactionCreate | TransactionUpdate = {
        category_id: categoryId,
        type,
        amount: numericAmount,
        description: description || undefined,
        transaction_date: transactionDate,
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
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">유형</label>
        <div className="flex gap-4">
          <label className="flex items-center">
            <input
              type="radio"
              value="income"
              checked={type === 'income'}
              onChange={(e) => {
                setType(e.target.value as 'income' | 'expense');
                setCategoryId(undefined);
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
                setType(e.target.value as 'income' | 'expense');
                setCategoryId(undefined);
              }}
              className="mr-2"
            />
            지출
          </label>
        </div>
      </div>

      <CategorySelect
        value={categoryId}
        onChange={setCategoryId}
        type={type}
        error={error && !categoryId ? error : undefined}
      />

      <Input
        label="금액"
        type="text"
        inputMode="decimal"
        value={amount}
        onChange={(e) => {
          const formatted = formatNumber(e.target.value);
          setAmount(formatted);
        }}
        placeholder="0"
        required
        error={error && !amount ? error : undefined}
      />

      <Input
        label="거래일자"
        type="date"
        value={transactionDate}
        onChange={(e) => setTransactionDate(e.target.value)}
        required
      />

      {/* 자연어 입력 */}
      {!transaction && (
        <div className="border-2 border-blue-200 dark:border-blue-700 rounded-lg p-3 bg-blue-50 dark:bg-blue-900/20">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <label className="text-sm font-medium text-blue-900 dark:text-blue-300">자연어로 입력하기</label>
            <button
              type="button"
              onClick={() => setShowNaturalLanguage(!showNaturalLanguage)}
              className="ml-auto text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
            >
              {showNaturalLanguage ? '숨기기' : '보이기'}
            </button>
          </div>
          {showNaturalLanguage && (
            <div className="space-y-2">
              <Input
                type="text"
                value={naturalLanguageText}
                onChange={(e) => setNaturalLanguageText(e.target.value)}
                placeholder='예: "어제 점심에 15000원 식비"'
                className="text-sm"
              />
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={handleNaturalLanguageParse}
                disabled={!naturalLanguageText.trim()}
                className="w-full"
              >
                파싱하기
              </Button>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                자연어로 입력하면 날짜, 금액, 카테고리를 자동으로 추출합니다.
              </p>
            </div>
          )}
        </div>
      )}

      <Input
        label="설명 (선택사항)"
        type="text"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />

      {/* 자동 카테고리 제안 */}
      {suggestedCategory && suggestedCategory.category_id && !transaction && (
        <div className="border-2 border-green-200 dark:border-green-700 rounded-lg p-3 bg-green-50 dark:bg-green-900/20">
          <div className="flex items-center justify-between gap-2">
            <div>
              <p className="text-sm font-medium text-green-900 dark:text-green-300">
                카테고리 제안: {suggestedCategory.category_name}
              </p>
              <p className="text-xs text-green-700 dark:text-green-400">
                신뢰도: {(suggestedCategory.confidence * 100).toFixed(0)}%
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => {
                  if (suggestedCategory.category_id) {
                    setCategoryId(suggestedCategory.category_id);
                    setSuggestedCategory(null);
                  }
                }}
                className="min-w-[60px]"
              >
                적용
              </Button>
              <Button
                type="button"
                variant="secondary"
                size="sm"
                onClick={() => setSuggestedCategory(null)}
                className="min-w-[60px]"
              >
                무시
              </Button>
            </div>
          </div>
        </div>
      )}

      {error && <p className="text-sm text-red-600">{error}</p>}

      <div className="flex gap-2 justify-end pt-2">
        <Button type="button" variant="secondary" size="md" onClick={onCancel} className="min-w-[80px]">
          취소
        </Button>
        <Button type="submit" size="md" disabled={loading} className="min-w-[80px]">
          {loading ? '저장 중...' : transaction ? '수정' : '등록'}
        </Button>
      </div>
    </form>
  );
};
