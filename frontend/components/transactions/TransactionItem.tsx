'use client';

import { Transaction } from '@/lib/api';
import { Button } from '@/components/ui/Button';

interface TransactionItemProps {
  transaction: Transaction;
  onEdit: (transaction: Transaction) => void;
  onDelete: (id: number) => void;
}

export const TransactionItem: React.FC<TransactionItemProps> = ({
  transaction,
  onEdit,
  onDelete,
}) => {
  const isIncome = transaction.type === 'income';
  const amountColor = isIncome ? 'text-green-600' : 'text-red-600';
  const amountPrefix = isIncome ? '+' : '-';

  return (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 hover:bg-gray-50">
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className={`font-semibold ${amountColor}`}>
            {amountPrefix}₩{Number(transaction.amount).toLocaleString()}
          </span>
          <span className="text-sm text-gray-500">
            {new Date(transaction.transaction_date).toLocaleDateString('ko-KR')}
          </span>
        </div>
        {transaction.description && (
          <p className="text-sm text-gray-600 mt-1">{transaction.description}</p>
        )}
      </div>
      <div className="flex gap-2">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => onEdit(transaction)}
        >
          수정
        </Button>
        <Button
          variant="danger"
          size="sm"
          onClick={() => {
            if (confirm('정말 삭제하시겠습니까?')) {
              onDelete(transaction.id);
            }
          }}
        >
          삭제
        </Button>
      </div>
    </div>
  );
};
