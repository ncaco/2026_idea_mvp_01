'use client';

import Layout from '@/components/layout/Layout';
import { BackupRestore } from '@/components/settings/BackupRestore';

export default function SettingsPage() {
  return (
    <Layout>
      <BackupRestore />
    </Layout>
  );
}
