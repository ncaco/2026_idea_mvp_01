'use client';

import { useState, useEffect } from 'react';
import { aiAPI, SpendingPatternsResponse } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658'];

export const SpendingPatterns: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [patterns, setPatterns] = useState<SpendingPatternsResponse | null>(null);
  const [startDate, setStartDate] = useState<string>(() => {
    const date = new Date();
    date.setMonth(date.getMonth() - 3);
    return date.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState<string>(() => {
    return new Date().toISOString().split('T')[0];
  });

  const loadPatterns = async () => {
    try {
      setLoading(true);
      const data = await aiAPI.getSpendingPatterns({
        start_date: startDate,
        end_date: endDate,
      });
      setPatterns(data);
    } catch (error) {
      console.error('패턴 분석 로드 실패:', error);
      alert('패턴 분석을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPatterns();
  }, []);

  const handleAnalyze = () => {
    loadPatterns();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">지출 패턴 분석</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">지출 패턴을 분석하고 이상치를 확인하세요</p>
        </div>
      </div>

      <Card compact className="border-2 border-gray-200 shadow-sm">
        <div className="p-4 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <Input
              type="date"
              label="시작 날짜"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
            <Input
              type="date"
              label="종료 날짜"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
            <Button size="md" onClick={handleAnalyze} className="w-full sm:w-auto whitespace-nowrap">분석하기</Button>
          </div>
        </div>
      </Card>

      {loading ? (
        <Card compact className="border-2 border-gray-200 shadow-sm">
          <div className="text-center py-12 text-gray-500">
            <div className="skeleton w-full h-64 rounded-xl" />
          </div>
        </Card>
      ) : patterns ? (
        <>
          {/* 월별 패턴 */}
          {patterns.monthly_pattern.length > 0 && (
            <Card compact className="border-2 border-gray-200 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
                월별 지출 패턴
              </h3>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={patterns.monthly_pattern}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="month"
                      tickFormatter={(value) => `${value}월`}
                    />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''}
                    />
                    <Legend />
                    <Bar dataKey="total" fill="#8884d8" name="지출 금액" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {/* 요일별 패턴 */}
          {patterns.weekday_pattern.length > 0 && (
            <Card compact className="border-2 border-gray-200 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
                요일별 지출 패턴
              </h3>
              <div className="p-4">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={patterns.weekday_pattern}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="weekday_name" />
                    <YAxis />
                    <Tooltip
                      formatter={(value: number | undefined) => value !== undefined ? `₩${value.toLocaleString()}` : ''}
                    />
                    <Legend />
                    <Bar dataKey="avg_amount" fill="#82ca9d" name="평균 지출" />
                    <Bar dataKey="count" fill="#ffc658" name="거래 건수" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}

          {/* 이상치 */}
          {patterns.outliers.length > 0 && (
            <Card compact className="border-2 border-gray-200 shadow-sm">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4 p-4 border-b-2 border-gray-200 dark:border-gray-700">
                이상치 감지 (평균 대비 2배 이상)
              </h3>
              <div className="p-4">
                <div className="space-y-2">
                  {patterns.outliers.map((outlier) => (
                      <div
                        key={outlier.id}
                        className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-700 rounded-lg"
                      >
                        <div>
                          <p className="font-semibold text-red-900 dark:text-red-300">
                            ₩{outlier.amount.toLocaleString()}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {new Date(outlier.date).toLocaleDateString('ko-KR')}
                          </p>
                          {outlier.description && (
                            <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">{outlier.description}</p>
                          )}
                        </div>
                      </div>
                  ))}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-4">
                  평균 지출: ₩{patterns.average_amount.toLocaleString()} | 
                  임계값: ₩{patterns.threshold.toLocaleString()}
                </p>
              </div>
            </Card>
          )}

          {patterns.monthly_pattern.length === 0 &&
            patterns.weekday_pattern.length === 0 &&
            patterns.outliers.length === 0 && (
              <Card compact className="border-2 border-gray-200 shadow-sm">
                <div className="text-center py-12 text-gray-500 text-base">
                  분석할 데이터가 없습니다.
                </div>
              </Card>
            )}
        </>
      ) : (
        <Card compact className="border-2 border-gray-200 shadow-sm">
          <div className="text-center py-12 text-gray-500 text-base">
            패턴 분석을 불러올 수 없습니다.
          </div>
        </Card>
      )}
    </div>
  );
};
