const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
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
