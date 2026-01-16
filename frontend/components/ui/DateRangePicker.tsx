'use client';

import React, { useState } from 'react';

interface DateRangePickerProps {
  startDate?: string;
  endDate?: string;
  onChange: (startDate: string | undefined, endDate: string | undefined) => void;
  className?: string;
}

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  startDate,
  endDate,
  onChange,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleStartDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value || undefined, endDate);
  };

  const handleEndDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(startDate, e.target.value || undefined);
  };

  const handleClear = () => {
    onChange(undefined, undefined);
    setIsOpen(false);
  };

  const formatDateRange = () => {
    if (!startDate && !endDate) return '날짜 선택';
    if (startDate && endDate) {
      return `${startDate} ~ ${endDate}`;
    }
    if (startDate) return `${startDate} ~`;
    if (endDate) return `~ ${endDate}`;
    return '날짜 선택';
  };

  return (
    <div className={`relative ${className}`}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2.5 border-2 border-gray-200 rounded-lg bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all w-full"
      >
        <svg
          className="w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <span>{formatDateRange()}</span>
        {(startDate || endDate) && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleClear();
            }}
            className="ml-2 text-gray-400 hover:text-gray-600"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        )}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute z-20 mt-2 bg-white border-2 border-gray-200 rounded-xl shadow-xl p-4 min-w-[320px]">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-2">
                  시작일
                </label>
                <input
                  type="date"
                  value={startDate || ''}
                  onChange={handleStartDateChange}
                  className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-2">
                  종료일
                </label>
                <input
                  type="date"
                  value={endDate || ''}
                  onChange={handleEndDateChange}
                  min={startDate}
                  className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleClear}
                  className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  초기화
                </button>
                <button
                  onClick={() => setIsOpen(false)}
                  className="flex-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  적용
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
