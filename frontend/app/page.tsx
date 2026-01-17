import Layout from '@/components/layout/Layout';
import { SummaryCards } from '@/components/dashboard/SummaryCards';
import { MonthlyChart } from '@/components/dashboard/MonthlyChart';
import { CategoryPieChart } from '@/components/dashboard/CategoryPieChart';
import { RecentTransactions } from '@/components/dashboard/RecentTransactions';
import { PredictionChart } from '@/components/dashboard/PredictionChart';
import { Button } from '@/components/ui/Button';
import { Plus, Settings } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <Layout>
      <div className="space-y-6">
        {/* 헤더 섹션 */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-1">대시보드</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">가계부 현황을 한눈에 확인하세요</p>
          </div>
          <div className="flex gap-2">
            <Link href="/transactions">
              <Button size="sm" className="flex items-center gap-2">
                <Plus className="w-4 h-4" />
                거래 추가
              </Button>
            </Link>
            <Link href="/categories">
              <Button variant="secondary" size="sm" className="flex items-center gap-2">
                <Settings className="w-4 h-4" />
                카테고리 관리
              </Button>
            </Link>
          </div>
        </div>

        {/* 요약 카드 */}
        <SummaryCards />

        {/* 차트 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MonthlyChart />
          </div>
          <div>
            <CategoryPieChart />
          </div>
        </div>

        {/* 최근 거래 및 예측 섹션 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <RecentTransactions />
          </div>
          <div>
            <PredictionChart />
          </div>
        </div>
      </div>
    </Layout>
  );
}
