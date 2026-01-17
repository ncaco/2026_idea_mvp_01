'use client';

import Layout from '@/components/layout/Layout';
import { RecurringTransactionList } from '@/components/recurring-transactions/RecurringTransactionList';

export default function RecurringTransactionsPage() {
  return (
    <Layout>
      <RecurringTransactionList />
    </Layout>
  );
}
