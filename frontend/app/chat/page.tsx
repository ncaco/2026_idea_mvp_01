'use client';

import { useState, useEffect } from 'react';
import Layout from '@/components/layout/Layout';

export default function ChatPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Streamlit 서버 연결 확인
    const checkStreamlit = async () => {
      try {
        const response = await fetch('http://localhost:8501/_stcore/health', {
          method: 'GET',
          mode: 'no-cors',
        });
        setIsLoading(false);
      } catch (err) {
        setIsLoading(false);
        setError('Streamlit 서버에 연결할 수 없습니다. Streamlit 앱이 실행 중인지 확인하세요.');
      }
    };

    checkStreamlit();
  }, []);

  if (error) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-[calc(100vh-8rem)]">
          <div className="text-center max-w-md">
            <div className="text-red-600 mb-4">
              <svg
                className="w-16 h-16 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">연결 오류</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <div className="bg-gray-50 p-4 rounded-lg text-left">
              <p className="text-sm text-gray-700 mb-2">해결 방법:</p>
              <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1">
                <li>PowerShell에서 다음 명령어 실행:</li>
                <li className="ml-4 font-mono bg-gray-200 px-2 py-1 rounded">
                  cd ./streamlit-chat; .\run.ps1
                </li>
                <li>Streamlit 서버가 시작되면 페이지를 새로고침하세요.</li>
              </ol>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="w-full h-full relative bg-gray-50 flex flex-col">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Streamlit 앱을 로딩 중...</p>
            </div>
          </div>
        )}
        <div className="w-full h-full overflow-hidden bg-white flex flex-col">
          <iframe
            src="http://localhost:8501"
            className="w-full h-full border-0"
            allow="clipboard-read; clipboard-write"
            title="AI 가계부 채팅"
            onLoad={() => setIsLoading(false)}
            style={{ 
              height: '100%',
              width: '100%',
              display: 'block',
              border: 'none',
              overflow: 'hidden'
            }}
            scrolling="no"
          />
        </div>
      </div>
    </Layout>
  );
}
