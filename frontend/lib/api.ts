const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// 토큰 관리
export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

export const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
};

export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
};

export interface Transaction {
  id: number;
  user_id: number;
  category_id: number;
  type: 'income' | 'expense';
  amount: number;
  description?: string;
  transaction_date: string;
  created_at: string;
  updated_at: string;
}

export interface Category {
  id: number;
  user_id: number;
  name: string;
  type: 'income' | 'expense';
  color?: string;
  icon?: string;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  category_id: number;
  type: 'income' | 'expense';
  amount: number;
  description?: string;
  transaction_date: string;
}

export interface TransactionUpdate {
  category_id?: number;
  type?: 'income' | 'expense';
  amount?: number;
  description?: string;
  transaction_date?: string;
}

export interface CategoryCreate {
  name: string;
  type: 'income' | 'expense';
  color?: string;
  icon?: string;
}

export interface CategoryUpdate {
  name?: string;
  type?: 'income' | 'expense';
  color?: string;
  icon?: string;
}

export interface MonthlyStatistics {
  income: number;
  expense: number;
  balance: number;
  year?: number;
  month?: number;
}

export interface CategoryStatistics {
  category_id: number;
  category_name: string;
  color?: string;
  total: number;
  count: number;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email?: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  console.log(`=== API 호출: ${endpoint} ===`);
  console.log('토큰 존재 여부:', token ? '있음' : '없음');
  if (token) {
    console.log('토큰 값 (처음 20자):', token.substring(0, 20) + '...');
    console.log('토큰 길이:', token.length);
  }
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('Authorization 헤더 추가됨');
  } else {
    console.warn('토큰이 없어 Authorization 헤더를 추가하지 않음');
  }
  
  console.log('요청 헤더:', JSON.stringify(headers, null, 2));
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    // 401 오류인 경우 상세 로그 출력
    if (response.status === 401) {
      const token = getToken();
      console.error('=== 401 Unauthorized 오류 ===');
      console.error('API 엔드포인트:', endpoint);
      console.error('토큰 존재 여부:', token ? '있음' : '없음');
      console.error('토큰 값 (처음 20자):', token ? token.substring(0, 20) + '...' : 'N/A');
      console.error('현재 경로:', typeof window !== 'undefined' ? window.location.pathname : 'N/A');
      console.error('요청 헤더:', headers);
      
      // 백엔드 응답 본문 확인
      try {
        const errorBody = await response.clone().json();
        console.error('백엔드 응답 본문:', errorBody);
      } catch (e) {
        console.error('백엔드 응답 본문 파싱 실패:', e);
      }
      
      // 토큰 제거는 하지만 리다이렉트는 하지 않음 (로그 확인용)
      removeToken();
      console.warn('토큰을 제거했습니다. (리다이렉트하지 않음 - 로그 확인용)');
    }
    
    // 422 오류인 경우 상세 로그 출력 (유효성 검증 오류)
    if (response.status === 422) {
      console.error('=== 422 Unprocessable Content 오류 ===');
      console.error('API 엔드포인트:', endpoint);
      console.error('요청 본문:', options.body);
    }
    
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    
    // 422 오류의 경우 FastAPI의 상세한 유효성 검증 오류 메시지 표시
    if (response.status === 422 && error.detail && Array.isArray(error.detail)) {
      const validationErrors = error.detail
        .map((err: any) => `${err.loc?.join('.')}: ${err.msg}`)
        .join(', ');
      throw new Error(`입력 데이터 오류: ${validationErrors}`);
    }
    
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Transaction API
export const transactionAPI = {
  getAll: (params?: {
    skip?: number;
    limit?: number;
    start_date?: string;
    end_date?: string;
    category_id?: number;
    type?: 'income' | 'expense';
  }) => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          queryParams.append(key, value.toString());
        }
      });
    }
    return fetchAPI<Transaction[]>(`/api/transactions?${queryParams.toString()}`);
  },

  getById: (id: number) => fetchAPI<Transaction>(`/api/transactions/${id}`),

  create: (data: TransactionCreate) => {
    // #region agent log
    fetch('http://127.0.0.1:7244/ingest/5dd89038-e302-4767-8ab6-a4bc08c49221',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'api.ts:create',message:'거래 생성 요청',data:data,timestamp:Date.now(),sessionId:'debug-session'})}).catch(()=>{});
    // #endregion
    return fetchAPI<Transaction>('/api/transactions', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  update: (id: number, data: TransactionUpdate) =>
    fetchAPI<Transaction>(`/api/transactions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI<void>(`/api/transactions/${id}`, {
      method: 'DELETE',
    }),
};

// Category API
export const categoryAPI = {
  getAll: (type?: 'income' | 'expense') => {
    const query = type ? `?type=${type}` : '';
    return fetchAPI<Category[]>(`/api/categories${query}`);
  },

  getById: (id: number) => fetchAPI<Category>(`/api/categories/${id}`),

  create: (data: CategoryCreate) =>
    fetchAPI<Category>('/api/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: CategoryUpdate) =>
    fetchAPI<Category>(`/api/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchAPI<void>(`/api/categories/${id}`, {
      method: 'DELETE',
    }),
};

// Statistics API
export const statisticsAPI = {
  getMonthly: (year?: number, month?: number) => {
    const queryParams = new URLSearchParams();
    if (year) queryParams.append('year', year.toString());
    if (month) queryParams.append('month', month.toString());
    const query = queryParams.toString() ? `?${queryParams.toString()}` : '';
    return fetchAPI<MonthlyStatistics>(`/api/statistics/monthly${query}`);
  },

  getByCategory: (year?: number, month?: number, type: 'income' | 'expense' = 'expense') => {
    const queryParams = new URLSearchParams();
    if (year) queryParams.append('year', year.toString());
    if (month) queryParams.append('month', month.toString());
    queryParams.append('type', type);
    return fetchAPI<CategoryStatistics[]>(`/api/statistics/by-category?${queryParams.toString()}`);
  },
};

// Auth API
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('=== 로그인 응답 ===');
    console.log('응답 데이터:', data);
    
    if (data.access_token) {
      setToken(data.access_token);
      console.log('토큰 저장 시도:', data.access_token.substring(0, 20) + '...');
      
      // 저장 후 즉시 확인
      await new Promise(resolve => setTimeout(resolve, 10)); // 약간의 지연
      const savedToken = getToken();
      console.log('저장된 토큰 확인:', savedToken ? savedToken.substring(0, 20) + '...' : '없음');
      console.log('토큰 길이:', savedToken ? savedToken.length : 0);
      console.log('localStorage 직접 확인:', typeof window !== 'undefined' ? localStorage.getItem('auth_token')?.substring(0, 20) + '...' : 'N/A');
    } else {
      console.error('로그인 응답에 access_token이 없습니다:', data);
    }
    return data;
  },

  register: async (userData: RegisterRequest): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  },

  getCurrentUser: async (): Promise<User> => {
    return fetchAPI<User>('/api/auth/me');
  },

  logout: (): void => {
    removeToken();
  },
};
