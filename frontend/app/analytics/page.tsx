'use client';

import Layout from '@/components/layout/Layout';
import { SpendingPatterns } from '@/components/analytics/SpendingPatterns';
import { AdvancedStatistics } from '@/components/analytics/AdvancedStatistics';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState<'patterns' | 'advanced'>('patterns');

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex gap-2 border-b-2 border-gray-200 dark:border-gray-700">
          <Button
            variant={activeTab === 'patterns' ? 'primary' : 'secondary'}
            size="md"
            onClick={() => setActiveTab('patterns')}
          >
            지출 패턴 분석
          </Button>
          <Button
            variant={activeTab === 'advanced' ? 'primary' : 'secondary'}
            size="md"
            onClick={() => setActiveTab('advanced')}
          >
            고급 통계
          </Button>
        </div>
        {activeTab === 'patterns' ? <SpendingPatterns /> : <AdvancedStatistics />}
      </div>
    </Layout>
  );
}
