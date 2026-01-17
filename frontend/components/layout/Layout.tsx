'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { authAPI, removeToken } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';
import { Moon, Sun } from 'lucide-react';

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ username: string } | null>(null);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    // 로그인 페이지에서는 사용자 정보를 가져오지 않음
    if (pathname === '/login') {
      return;
    }
    
    // 약간의 지연을 두어 토큰이 저장될 시간을 줌
    const timer = setTimeout(() => {
      console.log('=== Layout 컴포넌트 - 사용자 정보 로드 시작 ===');
      console.log('현재 경로:', pathname);
      
      // 토큰이 있는지 먼저 확인
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      console.log('localStorage에서 토큰 확인:', token ? token.substring(0, 20) + '...' : '없음');
      
      if (!token) {
        console.warn('토큰이 없습니다. 로그인 페이지로 리다이렉트합니다');
        if (pathname !== '/login') {
          window.location.href = '/login';
        }
        return;
      }
      
      // 현재 사용자 정보 가져오기
      console.log('사용자 정보 API 호출 시작...');
      authAPI.getCurrentUser()
        .then((user) => {
          setCurrentUser(user);
          console.log('✅ 사용자 정보 로드 완료:', user.username);
        })
        .catch((error) => {
          console.error('❌ 사용자 정보 로드 실패:', error);
          console.error('에러 메시지:', error.message);
          // 토큰이 없거나 만료된 경우
          removeToken();
          if (pathname !== '/login') {
            window.location.href = '/login';
          }
        });
    }, 100); // 100ms 지연
    
    return () => clearTimeout(timer);
  }, [pathname]);

  const handleLogout = () => {
    removeToken();
    router.push('/login');
  };

  const navItems = [
    { href: '/', label: '대시보드' },
    { href: '/transactions', label: '거래 내역' },
    { href: '/categories', label: '카테고리' },
    { href: '/tags', label: '태그' },
    { href: '/budgets', label: '예산 관리' },
    { href: '/recurring-transactions', label: '반복 거래' },
    { href: '/templates', label: '템플릿' },
    { href: '/analytics', label: '패턴 분석' },
    { href: '/statistics/yearly', label: '연도별 통계' },
    { href: '/settings', label: '설정' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden">
      <nav className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-40">
        <div className="w-full px-3 sm:px-4 lg:px-6">
          <div className="flex justify-between h-12 items-center">
            <div className="flex items-center gap-4 sm:gap-6">
              <div className="flex-shrink-0">
                <h1 className="text-base sm:text-lg font-bold text-gray-900 dark:text-gray-100">가계부</h1>
              </div>
              <div className="hidden sm:flex sm:space-x-1">
                {navItems.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 ${
                      pathname === item.href
                        ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-100'
                    }`}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {currentUser && (
                <div className="hidden sm:flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300">
                  <span>{currentUser.username}</span>
                  <button
                    onClick={toggleTheme}
                    className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                    title={theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
                  >
                    {theme === 'dark' ? (
                      <Sun className="w-4 h-4" />
                    ) : (
                      <Moon className="w-4 h-4" />
                    )}
                  </button>
                  <button
                    onClick={handleLogout}
                    className="px-3 py-1 text-xs text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
                  >
                    로그아웃
                  </button>
                </div>
              )}
              <button
                className="sm:hidden p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                aria-label="메뉴"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  {mobileMenuOpen ? (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  ) : (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 12h16M4 18h16"
                    />
                  )}
                </svg>
              </button>
            </div>
          </div>
          {mobileMenuOpen && (
            <div className="sm:hidden pb-3 space-y-1 animate-slide-in">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    pathname === item.href
                      ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          )}
        </div>
      </nav>
      <main className="w-full px-3 sm:px-4 lg:px-6 py-4 max-w-[1920px] mx-auto">
        {children}
      </main>
    </div>
  );
}
