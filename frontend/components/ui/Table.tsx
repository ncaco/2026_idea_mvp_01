'use client';

import React from 'react';

interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export const Table: React.FC<TableProps> = ({ children, className = '' }) => {
  return (
    <div className={`overflow-x-auto custom-scrollbar ${className}`}>
      <table className="min-w-full divide-y divide-gray-200 rounded-lg">{children}</table>
    </div>
  );
};

interface TableHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export const TableHeader: React.FC<TableHeaderProps> = ({ children, className = '' }) => {
  return (
    <thead className={`bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 ${className}`}>
      <tr>{children}</tr>
    </thead>
  );
};

interface TableHeaderCellProps {
  children: React.ReactNode;
  sortable?: boolean;
  sortDirection?: 'asc' | 'desc' | null;
  onSort?: () => void;
  className?: string;
}

export const TableHeaderCell: React.FC<TableHeaderCellProps> = ({
  children,
  sortable = false,
  sortDirection = null,
  onSort,
  className = '',
}) => {
  return (
    <th
      className={`px-4 py-3.5 text-left text-xs font-bold text-gray-700 dark:text-gray-300 uppercase tracking-wider ${
        sortable ? 'cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 select-none transition-colors' : ''
      } ${className}`}
      onClick={sortable ? onSort : undefined}
    >
      <div className="flex items-center gap-2">
        <span>{children}</span>
        {sortable && (
          <span className="text-gray-500 text-sm">
            {sortDirection === 'asc' && '↑'}
            {sortDirection === 'desc' && '↓'}
            {!sortDirection && '⇅'}
          </span>
        )}
      </div>
    </th>
  );
};

interface TableBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const TableBody: React.FC<TableBodyProps> = ({ children, className = '' }) => {
  return <tbody className={`bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700 ${className}`}>{children}</tbody>;
};

interface TableRowProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  hover?: boolean;
}

export const TableRow: React.FC<TableRowProps> = ({
  children,
  onClick,
  className = '',
  hover = true,
}) => {
  return (
    <tr
      className={`${hover ? 'hover:bg-blue-50 transition-colors duration-200' : ''} ${
        onClick ? 'cursor-pointer' : ''
      } border-b border-gray-100 ${className}`}
      onClick={onClick}
    >
      {children}
    </tr>
  );
};

interface TableCellProps {
  children: React.ReactNode;
  className?: string;
}

export const TableCell: React.FC<TableCellProps> = ({ children, className = '' }) => {
  return <td className={`px-4 py-3.5 text-sm text-gray-900 dark:text-gray-100 ${className}`}>{children}</td>;
};
