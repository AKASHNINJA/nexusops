import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'NexusOps | Enterprise FDE Control Plane',
  description: 'Production-Ready Forward Deployed Engineering Platform for Customer Data Integration & AI Agent Governance.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <header className="header-bar">
          <div className="logo-group">
            <span className="logo-badge">NEXUS</span>
            <div>
              <div className="logo-title">NexusOps Enterprise Control Plane</div>
              <span className="fde-badge">Forward Deployed Engineering Platform</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Environment: <strong style={{ color: '#10b981' }}>PRODUCTION READY</strong>
            </span>
          </div>
        </header>
        <main className="dashboard-container">
          {children}
        </main>
      </body>
    </html>
  );
}
