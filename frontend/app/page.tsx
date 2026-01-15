import Layout from '@/components/layout/Layout';
import { SummaryCards } from '@/components/dashboard/SummaryCards';
import { MonthlyChart } from '@/components/dashboard/MonthlyChart';
import { CategoryPieChart } from '@/components/dashboard/CategoryPieChart';

export default function DashboardPage() {
  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">대시보드</h1>
        <SummaryCards />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MonthlyChart />
          <CategoryPieChart />
        </div>
      </div>
    </Layout>
  );
}
