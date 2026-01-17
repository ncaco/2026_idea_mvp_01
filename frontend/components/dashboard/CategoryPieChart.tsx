'use client';

import { useEffect, useState } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
  Sector,
} from 'recharts';
import { statisticsAPI, CategoryStatistics } from '@/lib/api';
import { Card } from '@/components/ui/Card';

interface ChartData {
  name: string;
  value: number;
  color: string;
  count: number;
  categoryId: number;
  [key: string]: string | number;
}

export const CategoryPieChart: React.FC = () => {
  const [data, setData] = useState<CategoryStatistics[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedYear, selectedMonth]);

  const loadData = async () => {
    try {
      setLoading(true);
      const stats = await statisticsAPI.getByCategory(selectedYear, selectedMonth, 'expense');
      setData(stats);
    } catch (error) {
      console.error('카테고리 통계 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  // 전체 데이터를 금액 기준으로 정렬
  const sortedData = [...data].sort((a, b) => b.total - a.total);
  
  // 전체 금액 계산
  const totalAmount = sortedData.reduce((sum, item) => sum + item.total, 0);
  
  // 비율 기준 설정 (3% 미만은 기타로 묶기)
  const MIN_PERCENTAGE = 3;
  const minAmount = (totalAmount * MIN_PERCENTAGE) / 100;
  
  // 상위 카테고리 개수 설정 (최대 7개)
  const MAX_CATEGORIES = 7;
  
  // 표시할 카테고리와 기타로 묶을 카테고리 분리
  const displayCategories: typeof sortedData = [];
  const otherCategories: typeof sortedData = [];
  
  sortedData.forEach((item, index) => {
    // 상위 MAX_CATEGORIES 개 이내이고 비율이 MIN_PERCENTAGE 이상인 경우만 표시
    if (index < MAX_CATEGORIES && item.total >= minAmount) {
      displayCategories.push(item);
    } else {
      otherCategories.push(item);
    }
  });
  
  // 기타 카테고리 합계 계산
  const otherTotal = otherCategories.reduce((sum, item) => sum + item.total, 0);
  const otherCount = otherCategories.reduce((sum, item) => sum + item.count, 0);
  
  // 차트 데이터 생성
  const chartData: ChartData[] = displayCategories.map((item) => ({
    name: item.category_name,
    value: item.total,
    color: item.color || '#3B82F6',
    count: item.count,
    categoryId: item.category_id,
  }));
  
  // 기타 카테고리가 있으면 추가
  if (otherCategories.length > 0 && otherTotal > 0) {
    chartData.push({
      name: `기타 (${otherCategories.length}개)`,
      value: otherTotal,
      color: '#94a3b8', // 회색
      count: otherCount,
      categoryId: -1, // 기타는 ID가 없음
    });
  }

  const COLORS = chartData.map((item) => item.color);

  const onPieEnter = (_: any, index: number) => {
    if (index !== undefined) {
      setActiveIndex(index);
    }
  };

  const onPieLeave = () => {
    setActiveIndex(null);
  };

  const renderActiveShape = (props: any) => {
    const RADIAN = Math.PI / 180;
    const {
      cx,
      cy,
      midAngle,
      innerRadius,
      outerRadius,
      startAngle,
      endAngle,
      fill,
      payload,
      percent,
      value,
    } = props;
    const sin = Math.sin(-RADIAN * midAngle);
    const cos = Math.cos(-RADIAN * midAngle);
    const sx = cx + (outerRadius + 10) * cos;
    const sy = cy + (outerRadius + 10) * sin;
    const mx = cx + (outerRadius + 20) * cos;
    const my = cy + (outerRadius + 20) * sin;
    const ex = mx + (cos >= 0 ? 1 : -1) * 22;
    const ey = my;
    const textAnchor = cos >= 0 ? 'start' : 'end';

    return (
      <g>
        <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill} className="text-sm font-semibold">
          {payload.name}
        </text>
        <Sector
          cx={cx}
          cy={cy}
          innerRadius={innerRadius}
          outerRadius={outerRadius + 5}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
        />
        <Sector
          cx={cx}
          cy={cy}
          startAngle={startAngle}
          endAngle={endAngle}
          innerRadius={outerRadius + 6}
          outerRadius={outerRadius + 10}
          fill={fill}
        />
        <path
          d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`}
          stroke={fill}
          fill="none"
          strokeWidth={2}
        />
        <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
        <text
          x={ex + (cos >= 0 ? 1 : -1) * 12}
          y={ey}
          textAnchor={textAnchor}
          fill="#333"
          className="text-xs font-medium"
        >
          {`₩${value.toLocaleString()}`}
        </text>
        <text
          x={ex + (cos >= 0 ? 1 : -1) * 12}
          y={ey}
          dy={18}
          textAnchor={textAnchor}
          fill="#999"
          className="text-xs"
        >
          {`${(percent * 100).toFixed(1)}%`}
        </text>
      </g>
    );
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload as ChartData;
      return (
        <div className="bg-white border-2 border-gray-200 rounded-xl shadow-xl p-4 backdrop-blur-sm">
          <div className="flex items-center gap-2 mb-3">
            <div 
              className="w-4 h-4 rounded-full" 
              style={{ backgroundColor: data.color }}
            />
            <p className="font-bold text-base" style={{ color: data.color }}>
              {data.name}
            </p>
          </div>
          <div className="space-y-1.5">
            <p className="text-sm font-semibold text-gray-700">
              금액: <span className="font-bold" style={{ color: data.color }}>₩{data.value.toLocaleString()}</span>
            </p>
            <p className="text-sm text-gray-600">
              거래 수: <span className="font-medium">{data.count}건</span>
            </p>
            <p className="text-sm text-gray-500">
              비율: <span className="font-semibold">{((data.value / chartData.reduce((sum, d) => sum + d.value, 0)) * 100).toFixed(1)}%</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  if (loading) {
    return (
      <Card title="카테고리별 지출" compact>
        <div className="h-48 flex items-center justify-center text-gray-500">
          <div className="skeleton w-full h-full rounded" />
        </div>
      </Card>
    );
  }

  if (chartData.length === 0) {
    return (
      <Card 
        title="카테고리별 지출" 
        compact
        className="border-2 border-gray-200 hover:border-blue-300 transition-colors shadow-sm hover:shadow-md"
      >
        <div className="h-48 flex items-center justify-center text-gray-500">
          데이터가 없습니다.
        </div>
      </Card>
    );
  }
  
  // 카테고리 개수가 많거나 기타로 묶인 경우 안내 메시지
  const showInfo = sortedData.length > MAX_CATEGORIES || otherCategories.length > 0;

  return (
    <Card 
      title="카테고리별 지출" 
      compact 
      className="interactive border-2 border-gray-200 hover:border-blue-300 transition-colors shadow-sm hover:shadow-md"
    >
      <div className="mb-4 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <select
            value={selectedYear}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            className="px-2 py-1.5 text-xs border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white font-medium"
          >
            {Array.from({ length: 5 }, (_, i) => new Date().getFullYear() - i).map((year) => (
              <option key={year} value={year}>
                {year}년
              </option>
            ))}
          </select>
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(Number(e.target.value))}
            className="px-2 py-1.5 text-xs border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white font-medium"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
              <option key={month} value={month}>
                {month}월
              </option>
            ))}
          </select>
        </div>
        {showInfo && (
          <div className="text-xs text-gray-500 bg-blue-50 px-2 py-1 rounded-md">
            {otherCategories.length > 0 
              ? `${MIN_PERCENTAGE}% 미만은 기타로 표시`
              : `상위 ${MAX_CATEGORIES}개 표시`}
          </div>
        )}
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie
            activeShape={renderActiveShape}
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey="value"
            onMouseEnter={onPieEnter}
            onMouseLeave={onPieLeave}
            animationDuration={300}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
            formatter={(value, entry: any) => (
              <span style={{ color: entry.color }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
      {showInfo && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            {otherCategories.length > 0 ? (
              <>
                총 {sortedData.length}개 카테고리 중 {displayCategories.length}개 표시, 
                {otherCategories.length}개는 기타로 묶음 ({MIN_PERCENTAGE}% 미만)
              </>
            ) : (
              <>총 {sortedData.length}개 카테고리 중 상위 {MAX_CATEGORIES}개만 표시됩니다</>
            )}
          </p>
        </div>
      )}
    </Card>
  );
};
