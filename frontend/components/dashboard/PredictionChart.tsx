'use client';

import { useState, useEffect } from 'react';
import { statisticsAPI } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const PredictionChart: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [prediction, setPrediction] = useState<any>(null);

  useEffect(() => {
    loadPrediction();
  }, []);

  const loadPrediction = async () => {
    try {
      setLoading(true);
      const data = await statisticsAPI.predictExpense(6);
      setPrediction(data);
    } catch (error) {
      console.error('예측 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card compact className="border-2 border-gray-200 shadow-sm">
        <div className="text-center py-12 text-gray-500">
          <div className="skeleton w-full h-64 rounded-xl" />
        </div>
      </Card>
    );
  }

  if (!prediction) {
    return (
      <Card compact className="border-2 border-gray-200 shadow-sm">
        <div className="text-center py-12 text-gray-500 text-base">
          예측 데이터를 불러올 수 없습니다.
        </div>
      </Card>
    );
  }

  return (
    <Card compact className="border-2 border-gray-200 shadow-sm">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
        다음 달 지출 예측
      </h3>
      <div className="p-4 space-y-4">
        <div className="text-center">
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">예상 총 지출</p>
          <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
            ₩{prediction.predicted_total.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            신뢰도: {(prediction.confidence * 100).toFixed(0)}% | 
            기준: 최근 {prediction.based_on_months}개월
          </p>
        </div>

        {prediction.predicted_by_category.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">카테고리별 예측</h4>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={prediction.predicted_by_category}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="category_name"
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip
                      formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''}
                />
                <Legend />
                <Bar dataKey="predicted_amount" fill="#8884d8" name="예상 지출" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </Card>
  );
};
