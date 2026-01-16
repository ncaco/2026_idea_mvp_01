import Layout from '@/components/layout/Layout';
import { SummaryCards } from '@/components/dashboard/SummaryCards';
import { MonthlyChart } from '@/components/dashboard/MonthlyChart';
import { CategoryPieChart } from '@/components/dashboard/CategoryPieChart';
import { RecentTransactions } from '@/components/dashboard/RecentTransactions';
import { Button } from '@/components/ui/Button';
import Link from 'next/link';

export default function DashboardPage() {
  return (
    <Layout>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">대시보드</h1>
          <div className="flex gap-2">
            <Link href="/transactions">
              <Button size="sm">거래 추가</Button>
            </Link>
            <Link href="/categories">
              <Button variant="secondary" size="sm">
                카테고리 관리
              </Button>
            </Link>
          </div>
        </div>

        <SummaryCards />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <MonthlyChart />
          </div>
          <div>
            <CategoryPieChart />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <RecentTransactions />
          </div>
        </div>
      </div>
    </Layout>
  );
}
