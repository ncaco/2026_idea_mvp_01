import Layout from '@/components/layout/Layout';
import { TransactionList } from '@/components/transactions/TransactionList';

export default function TransactionsPage() {
  return (
    <Layout>
      <TransactionList />
    </Layout>
  );
}
