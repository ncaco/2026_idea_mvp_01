'use client';

import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  onClick?: () => void;
  compact?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  onClick,
  compact = false,
}) => {
  const paddingClass = compact ? 'p-4' : 'p-6';
  const interactiveClass = onClick
    ? 'cursor-pointer hover:shadow-lg transition-all duration-200 interactive'
    : 'transition-shadow duration-200';

  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm dark:shadow-gray-900/50 ${paddingClass} ${interactiveClass} animate-fade-in ${className}`}
      onClick={onClick}
    >
      {title && (
        <h3 className={`font-bold text-gray-900 dark:text-gray-100 ${compact ? 'text-lg mb-4' : 'text-xl mb-5'}`}>
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};
