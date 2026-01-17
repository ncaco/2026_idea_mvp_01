'use client';

import { useState, useEffect, useMemo } from 'react';
import {
  Transaction,
  transactionAPI,
  TransactionCreate,
  TransactionUpdate,
  categoryAPI,
  Category,
  tagAPI,
} from '@/lib/api';
import { Download, Upload, Trash2, Plus, Copy, Edit2, CheckSquare, Square } from 'lucide-react';
import { TransactionForm } from './TransactionForm';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Modal } from '@/components/ui/Modal';
import { FilterBar } from '@/components/ui/FilterBar';
import {
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
} from '@/components/ui/Table';

type SortField = 'date' | 'amount' | 'category' | 'type';
type SortDirection = 'asc' | 'desc' | null;

export const TransactionList: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTransaction, setEditingTransaction] = useState<Transaction | undefined>();
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [bulkEditMode, setBulkEditMode] = useState(false);
  const [showBulkEditModal, setShowBulkEditModal] = useState(false);

  // 필터 상태
  const [searchValue, setSearchValue] = useState('');
  const [startDate, setStartDate] = useState<string | undefined>();
  const [endDate, setEndDate] = useState<string | undefined>();
  const [typeFilter, setTypeFilter] = useState<'income' | 'expense' | 'all'>('all');
  const [selectedCategoryIds, setSelectedCategoryIds] = useState<number[]>([]);

  // 정렬 상태
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  useEffect(() => {
    loadCategories();
    loadTransactions();
  }, []);

  const loadCategories = async () => {
    try {
      const data = await categoryAPI.getAll();
      setCategories(data);
    } catch (error) {
      console.error('카테고리 로드 실패:', error);
    }
  };

  const loadTransactions = async () => {
    try {
      setLoading(true);
      const params: any = {
        limit: 1000,
      };
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (typeFilter !== 'all') params.type = typeFilter;
      if (selectedCategoryIds.length === 1) {
        params.category_id = selectedCategoryIds[0];
      }
      if (searchValue) {
        params.search = searchValue;
      }

      const data = await transactionAPI.getAll(params);
      setTransactions(data);
    } catch (error) {
      console.error('거래 내역 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTransactions();
  }, [startDate, endDate, typeFilter, searchValue, selectedCategoryIds]);

  const handleSubmit = async (data: TransactionCreate | TransactionUpdate) => {
    try {
      if (editingTransaction) {
        await transactionAPI.update(editingTransaction.id, data as TransactionUpdate);
      } else {
        await transactionAPI.create(data as TransactionCreate);
      }
      await loadTransactions();
      setShowForm(false);
      setEditingTransaction(undefined);
    } catch (error) {
      console.error('거래 내역 저장 실패:', error);
      throw error;
    }
  };

  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setShowForm(true);
  };

  const handleDuplicate = (transaction: Transaction) => {
    // 거래를 복제하여 새로 생성 (거래일은 오늘로 설정)
    const duplicatedTransaction: Transaction = {
      ...transaction,
      id: 0, // 새로 생성될 거래이므로 ID는 0
      transaction_date: new Date().toISOString().split('T')[0], // 오늘 날짜
      created_at: '',
      updated_at: '',
    };
    setEditingTransaction(undefined); // 새 거래로 처리
    // 폼에 데이터 미리 채우기 위해 transaction 대신 duplicatedTransaction을 사용
    // 하지만 TransactionForm은 transaction이 있으면 수정 모드이므로, 
    // 복제된 데이터를 새로 생성하도록 처리
    const newTransaction: TransactionCreate = {
      category_id: transaction.category_id,
      type: transaction.type,
      amount: Number(transaction.amount),
      description: transaction.description ? `${transaction.description} (복제)` : undefined,
      transaction_date: new Date().toISOString().split('T')[0],
    };
    
    // 직접 API 호출하여 생성
    transactionAPI.create(newTransaction)
      .then(() => {
        loadTransactions();
        alert('거래가 복제되었습니다.');
      })
      .catch((error) => {
        console.error('거래 복제 실패:', error);
        alert(`거래 복제 실패: ${error.message}`);
      });
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    try {
      await transactionAPI.delete(id);
      await loadTransactions();
    } catch (error) {
      console.error('거래 내역 삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`선택한 ${selectedIds.size}개의 거래를 삭제하시겠습니까?`)) return;
    try {
      await Promise.all(Array.from(selectedIds).map(id => transactionAPI.delete(id)));
      await loadTransactions();
      setSelectedIds(new Set());
      setBulkEditMode(false);
      alert(`${selectedIds.size}개의 거래가 삭제되었습니다.`);
    } catch (error) {
      console.error('일괄 삭제 실패:', error);
      alert('일괄 삭제에 실패했습니다.');
    }
  };

  const handleBulkEdit = () => {
    // 일괄 수정 모달 표시
    setShowBulkEditModal(true);
  };

  const handleBulkEditSubmit = async (data: { category_id?: number; tag_ids?: number[] }) => {
    try {
      const updates = Array.from(selectedIds).map(id => 
        transactionAPI.update(id, data as any)
      );
      await Promise.all(updates);
      await loadTransactions();
      setSelectedIds(new Set());
      setBulkEditMode(false);
      setShowBulkEditModal(false);
      alert(`${selectedIds.size}개의 거래가 수정되었습니다.`);
    } catch (error) {
      console.error('일괄 수정 실패:', error);
      alert('일괄 수정에 실패했습니다.');
    }
  };

  const toggleSelect = (id: number) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredAndSortedTransactions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredAndSortedTransactions.map(t => t.id)));
    }
  };

  const handleDeleteAll = async () => {
    const filterInfo = [];
    if (startDate) filterInfo.push(`시작일: ${startDate}`);
    if (endDate) filterInfo.push(`종료일: ${endDate}`);
    if (typeFilter !== 'all') filterInfo.push(`유형: ${typeFilter === 'income' ? '수입' : '지출'}`);
    if (selectedCategoryIds.length > 0) {
      const categoryNames = selectedCategoryIds
        .map(id => categories.find(c => c.id === id)?.name)
        .filter(Boolean)
        .join(', ');
      filterInfo.push(`카테고리: ${categoryNames}`);
    }

    const filterText = filterInfo.length > 0 
      ? `\n\n현재 필터 조건:\n${filterInfo.join('\n')}`
      : '\n\n모든 거래 내역이 삭제됩니다.';

    if (!confirm(`정말 전체 삭제하시겠습니까?${filterText}\n\n이 작업은 되돌릴 수 없습니다.`)) {
      return;
    }

    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (typeFilter !== 'all') params.type = typeFilter;
      if (selectedCategoryIds.length === 1) {
        params.category_id = selectedCategoryIds[0];
      }

      const result = await transactionAPI.deleteAll(params);
      alert(result.message);
      await loadTransactions();
    } catch (error: any) {
      console.error('전체 삭제 실패:', error);
      alert(`전체 삭제 실패: ${error.message}`);
    }
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingTransaction(undefined);
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      if (sortDirection === 'asc') {
        setSortDirection('desc');
      } else if (sortDirection === 'desc') {
        setSortDirection(null);
        setSortField('date');
        setSortDirection('desc');
      } else {
        setSortDirection('asc');
      }
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleClearFilters = () => {
    setSearchValue('');
    setStartDate(undefined);
    setEndDate(undefined);
    setTypeFilter('all');
    setSelectedCategoryIds([]);
  };

  // 검색어 하이라이트 함수
  const highlightText = (text: string, searchTerm: string) => {
    if (!searchTerm || !text) return text;
    const regex = new RegExp(`(${searchTerm})`, 'gi');
    const parts = text.split(regex);
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  // 필터링 및 정렬된 거래 내역
  const filteredAndSortedTransactions = useMemo(() => {
    let filtered = [...transactions];

    // 카테고리 필터 (서버에서 처리하지 않은 경우)
    if (selectedCategoryIds.length > 1) {
      filtered = filtered.filter((t) => selectedCategoryIds.includes(t.category_id));
    }

    // 정렬
    if (sortDirection) {
      filtered.sort((a, b) => {
        let aValue: any;
        let bValue: any;

        switch (sortField) {
          case 'date':
            aValue = new Date(a.transaction_date).getTime();
            bValue = new Date(b.transaction_date).getTime();
            break;
          case 'amount':
            aValue = a.amount;
            bValue = b.amount;
            break;
          case 'category':
            const aCategory = categories.find((c) => c.id === a.category_id);
            const bCategory = categories.find((c) => c.id === b.category_id);
            aValue = aCategory?.name || '';
            bValue = bCategory?.name || '';
            break;
          case 'type':
            aValue = a.type;
            bValue = b.type;
            break;
          default:
            return 0;
        }

        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [transactions, searchValue, selectedCategoryIds, sortField, sortDirection, categories]);

  const getCategoryName = (categoryId: number) => {
    return categories.find((c) => c.id === categoryId)?.name || '알 수 없음';
  };

  const getCategoryColor = (categoryId: number) => {
    return categories.find((c) => c.id === categoryId)?.color || '#6b7280';
  };

  const handleExportExcel = async () => {
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (typeFilter !== 'all') params.type = typeFilter;
      if (selectedCategoryIds.length === 1) {
        params.category_id = selectedCategoryIds[0];
      }
      
      await transactionAPI.exportExcel(params);
    } catch (error: any) {
      console.error('엑셀 다운로드 실패:', error);
      alert(`엑셀 다운로드 실패: ${error.message}`);
    }
  };

  const handleExportCsv = async () => {
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (typeFilter !== 'all') params.type = typeFilter;
      if (selectedCategoryIds.length === 1) {
        params.category_id = selectedCategoryIds[0];
      }
      
      await transactionAPI.exportCsv(params);
    } catch (error: any) {
      console.error('CSV 다운로드 실패:', error);
      alert(`CSV 다운로드 실패: ${error.message}`);
    }
  };

  const handleImportExcel = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
      alert('엑셀 파일(.xlsx, .xls)만 업로드 가능합니다.');
      return;
    }
    
    if (!confirm('엑셀 파일을 업로드하시겠습니까? 기존 데이터는 유지되고 새 데이터가 추가됩니다.')) {
      return;
    }
    
    try {
      const result = await transactionAPI.importExcel(file);
      alert(
        `업로드 완료!\n성공: ${result.success}건\n실패: ${result.failed}건${
          result.errors && result.errors.length > 0
            ? `\n\n오류:\n${result.errors.slice(0, 5).join('\n')}`
            : ''
        }`
      );
      await loadTransactions();
      // 파일 입력 초기화
      event.target.value = '';
    } catch (error: any) {
      console.error('엑셀 업로드 실패:', error);
      alert(`엑셀 업로드 실패: ${error.message}`);
      event.target.value = '';
    }
  };

  const handleImportCsv = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    if (!file.name.endsWith('.csv')) {
      alert('CSV 파일(.csv)만 업로드 가능합니다.');
      return;
    }
    
    if (!confirm('CSV 파일을 업로드하시겠습니까? 기존 데이터는 유지되고 새 데이터가 추가됩니다.')) {
      return;
    }
    
    try {
      const result = await transactionAPI.importCsv(file);
      alert(
        `업로드 완료!\n성공: ${result.success}건\n실패: ${result.failed}건${
          result.errors && result.errors.length > 0
            ? `\n\n오류:\n${result.errors.slice(0, 5).join('\n')}`
            : ''
        }`
      );
      await loadTransactions();
      // 파일 입력 초기화
      event.target.value = '';
    } catch (error: any) {
      console.error('CSV 업로드 실패:', error);
      alert(`CSV 업로드 실패: ${error.message}`);
      event.target.value = '';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">거래 내역</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">모든 거래 내역을 확인하고 관리하세요</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <label htmlFor="excel-upload" className="cursor-pointer">
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
              id="excel-upload"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleImportExcel}
              className="hidden"
            />
          </label>
          <label htmlFor="csv-upload" className="cursor-pointer">
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
              id="csv-upload"
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
          {bulkEditMode ? (
            <>
              <Button
                variant="secondary"
                size="md"
                onClick={() => {
                  if (selectedIds.size === 0) {
                    alert('수정할 거래를 선택해주세요.');
                    return;
                  }
                  // 일괄 수정 모달 표시
                  handleBulkEdit();
                }}
                disabled={selectedIds.size === 0}
              >
                <Edit2 className="w-4 h-4" />
                일괄 수정 ({selectedIds.size})
              </Button>
              <Button
                variant="danger"
                size="md"
                onClick={() => {
                  if (selectedIds.size === 0) {
                    alert('삭제할 거래를 선택해주세요.');
                    return;
                  }
                  handleBulkDelete();
                }}
                disabled={selectedIds.size === 0}
              >
                <Trash2 className="w-4 h-4" />
                일괄 삭제 ({selectedIds.size})
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={() => {
                  setBulkEditMode(false);
                  setSelectedIds(new Set());
                }}
              >
                취소
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="secondary"
                size="md"
                onClick={() => setBulkEditMode(true)}
              >
                <CheckSquare className="w-4 h-4" />
                일괄 선택
              </Button>
              <Button
                size="md"
                onClick={() => {
                  setEditingTransaction(undefined);
                  setShowForm(true);
                }}
              >
                <Plus className="w-4 h-4" />
                거래 추가
              </Button>
            </>
          )}
        </div>
      </div>

      <FilterBar
        searchValue={searchValue}
        onSearchChange={setSearchValue}
        startDate={startDate}
        endDate={endDate}
        onDateRangeChange={(start, end) => {
          setStartDate(start);
          setEndDate(end);
        }}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
        categories={categories}
        selectedCategoryIds={selectedCategoryIds}
        onCategoryFilterChange={setSelectedCategoryIds}
        onClearFilters={handleClearFilters}
      />

      <Card 
        compact
        className="border-2 border-gray-200 shadow-sm"
      >
        {loading ? (
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        ) : filteredAndSortedTransactions.length === 0 ? (
          <div className="text-center py-12 text-gray-500 text-base">거래 내역이 없습니다.</div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
            <TableHeader>
              {bulkEditMode && (
                <TableHeaderCell>
                  <button
                    onClick={toggleSelectAll}
                    className="flex items-center justify-center"
                  >
                    {selectedIds.size === filteredAndSortedTransactions.length ? (
                      <CheckSquare className="w-4 h-4" />
                    ) : (
                      <Square className="w-4 h-4" />
                    )}
                  </button>
                </TableHeaderCell>
              )}
              <TableHeaderCell
                sortable
                sortDirection={sortField === 'date' ? sortDirection : null}
                onSort={() => handleSort('date')}
              >
                날짜
              </TableHeaderCell>
              <TableHeaderCell
                sortable
                sortDirection={sortField === 'type' ? sortDirection : null}
                onSort={() => handleSort('type')}
              >
                유형
              </TableHeaderCell>
              <TableHeaderCell
                sortable
                sortDirection={sortField === 'category' ? sortDirection : null}
                onSort={() => handleSort('category')}
              >
                카테고리
              </TableHeaderCell>
              <TableHeaderCell>설명</TableHeaderCell>
              <TableHeaderCell
                sortable
                sortDirection={sortField === 'amount' ? sortDirection : null}
                onSort={() => handleSort('amount')}
              >
                금액
              </TableHeaderCell>
              <TableHeaderCell>작업</TableHeaderCell>
            </TableHeader>
            <TableBody>
              {filteredAndSortedTransactions.map((transaction) => {
                const isIncome = transaction.type === 'income';
                const amountColor = isIncome ? 'text-green-600' : 'text-red-600';
                const amountPrefix = isIncome ? '+' : '-';

                return (
                  <TableRow key={transaction.id} hover>
                    {bulkEditMode && (
                      <TableCell>
                        <button
                          onClick={() => toggleSelect(transaction.id)}
                          className="flex items-center justify-center"
                        >
                          {selectedIds.has(transaction.id) ? (
                            <CheckSquare className="w-4 h-4 text-blue-600" />
                          ) : (
                            <Square className="w-4 h-4 text-gray-400" />
                          )}
                        </button>
                      </TableCell>
                    )}
                    <TableCell className="whitespace-nowrap dark:text-gray-300">
                      {new Date(transaction.transaction_date).toLocaleDateString('ko-KR', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                      })}
                    </TableCell>
                    <TableCell>
                      <span
                        className={`px-2 py-1 text-xs rounded-full font-medium ${
                          isIncome
                            ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                            : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                        }`}
                      >
                        {isIncome ? '수입' : '지출'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{ backgroundColor: getCategoryColor(transaction.category_id) }}
                          />
                          <span className="text-sm dark:text-gray-300">
                            {searchValue
                              ? highlightText(
                                  getCategoryName(transaction.category_id),
                                  searchValue
                                )
                              : getCategoryName(transaction.category_id)}
                          </span>
                        </div>
                        {transaction.tags && transaction.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-1">
                            {transaction.tags.map((tag) => (
                              <span
                                key={tag.id}
                                className="inline-flex items-center gap-1 px-1.5 py-0.5 text-xs rounded border"
                                style={{
                                  backgroundColor: tag.color ? `${tag.color}20` : 'transparent',
                                  borderColor: tag.color || '#e5e7eb',
                                  color: tag.color || '#6b7280',
                                }}
                              >
                                {tag.color && (
                                  <span
                                    className="w-1.5 h-1.5 rounded-full"
                                    style={{ backgroundColor: tag.color }}
                                  />
                                )}
                                {tag.name}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="max-w-xs dark:text-gray-300">
                      {transaction.description ? (
                        <span className="truncate block">
                          {searchValue
                            ? highlightText(transaction.description, searchValue)
                            : transaction.description}
                        </span>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell className={`font-semibold ${amountColor} dark:${isIncome ? 'text-green-400' : 'text-red-400'}`}>
                      {amountPrefix}₩{Number(transaction.amount).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleDuplicate(transaction)}
                          className="min-w-[40px]"
                          title="복제"
                        >
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handleEdit(transaction)}
                          className="min-w-[60px]"
                        >
                          수정
                        </Button>
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleDelete(transaction.id)}
                          className="min-w-[60px]"
                        >
                          삭제
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
          </div>
        )}
        {!loading && filteredAndSortedTransactions.length > 0 && (
          <div className="mt-4 pt-4 border-t-2 border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 text-center">
            총 {filteredAndSortedTransactions.length}건의 거래 내역
          </div>
        )}
      </Card>

      <Modal
        isOpen={showForm}
        onClose={handleCancel}
        title={editingTransaction ? '거래 수정' : '거래 등록'}
        size="md"
      >
        <TransactionForm
          transaction={editingTransaction}
          onSubmit={handleSubmit}
          onCancel={handleCancel}
        />
      </Modal>
    </div>
  );
};
