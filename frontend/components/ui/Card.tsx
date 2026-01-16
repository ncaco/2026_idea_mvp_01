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
      className={`bg-white rounded-lg shadow-md ${paddingClass} ${interactiveClass} animate-fade-in ${className}`}
      onClick={onClick}
    >
      {title && (
        <h3 className={`font-semibold text-gray-900 ${compact ? 'text-base mb-3' : 'text-lg mb-4'}`}>
          {title}
        </h3>
      )}
      {children}
    </div>
  );
};
