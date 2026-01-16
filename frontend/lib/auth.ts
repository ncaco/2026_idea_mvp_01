/**
 * 인증 관련 유틸리티
 */

export const isAuthenticated = (): boolean => {
  if (typeof window === 'undefined') {
    return false;
  }
  return !!localStorage.getItem('auth_token');
};

export const requireAuth = (): void => {
  if (typeof window !== 'undefined' && !isAuthenticated()) {
    window.location.href = '/login';
  }
};
