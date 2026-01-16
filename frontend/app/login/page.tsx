'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authAPI.login({ username, password });
        // 토큰이 저장되었는지 확인
        if (response.access_token) {
          // 토큰 저장 확인을 위해 약간의 지연
          await new Promise(resolve => setTimeout(resolve, 50));
          // localStorage에서 토큰 확인
          const savedToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
          if (savedToken) {
            console.log('로그인 성공, 토큰 저장 확인됨. 페이지 이동합니다.');
            // 전체 페이지 리로드를 통해 모든 상태를 초기화
            window.location.href = '/';
          } else {
            console.error('토큰이 저장되지 않았습니다!');
            throw new Error('토큰 저장에 실패했습니다');
          }
        } else {
          throw new Error('로그인에 실패했습니다');
        }
      } else {
        await authAPI.register({ username, email: email || undefined, password });
        // 회원가입 후 자동 로그인
        const response = await authAPI.login({ username, password });
        // 토큰이 저장되었는지 확인
        if (response.access_token) {
          // 토큰 저장 확인을 위해 약간의 지연
          await new Promise(resolve => setTimeout(resolve, 50));
          // localStorage에서 토큰 확인
          const savedToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
          if (savedToken) {
            console.log('회원가입 및 로그인 성공, 토큰 저장 확인됨. 페이지 이동합니다.');
            // 전체 페이지 리로드를 통해 모든 상태를 초기화
            window.location.href = '/';
          } else {
            console.error('토큰이 저장되지 않았습니다!');
            throw new Error('토큰 저장에 실패했습니다');
          }
        } else {
          throw new Error('로그인에 실패했습니다');
        }
      }
    } catch (err: any) {
      setError(err.message || '오류가 발생했습니다');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <Card className="w-full max-w-md">
        <div className="p-6">
          <h1 className="text-2xl font-bold mb-6 text-center">
            {isLogin ? '로그인' : '회원가입'}
          </h1>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                사용자명
              </label>
              <Input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="사용자명을 입력하세요"
              />
            </div>

            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  이메일 (선택)
                </label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="이메일을 입력하세요"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                비밀번호
              </label>
              <Input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="비밀번호를 입력하세요"
              />
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center">{error}</div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={loading}
            >
              {loading ? '처리 중...' : isLogin ? '로그인' : '회원가입'}
            </Button>
          </form>

          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              {isLogin ? '계정이 없으신가요? 회원가입' : '이미 계정이 있으신가요? 로그인'}
            </button>
          </div>
        </div>
      </Card>
    </div>
  );
}
