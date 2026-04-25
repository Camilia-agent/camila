import StubHero from '../components/StubHero.jsx';
import Panel from '../components/Panel.jsx';
import { useApi } from '../hooks/useApi.js';
import { apiUrl } from '../lib/api.js';

export default function ApprovalsPage({ onMinimize, onClose }) {
  const { data: approvals, error, refetch } = useApi('/api/approvals');

  async function action(id, kind) {
    try {
      const res = await fetch(apiUrl(`/api/approvals/${id}/${kind}`), { method: 'POST' });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      refetch();
    } catch (e) {
      alert(`Failed to ${kind}: ${e.message}`);
    }
  }

  return (
    <div className="stub-page">
      <StubHero
        icon="✅"
        title="HIL Approvals Inbox"
        subtitle="All pending Human-in-Loop checkpoints awaiting your review"
        onMinimize={onMinimize}
        onClose={onClose}
      />

      <Panel
        title="Pending Your Action"
        ptag={approvals ? `${approvals.length} items` : '…'}
        bodyStyle={{ padding: 0 }}
      >
        {error ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--neutral-4)' }}>
            Unable to load approvals. Is the backend running?
          </div>
        ) : !approvals ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--neutral-4)' }}>
            Loading…
          </div>
        ) : approvals.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--neutral-4)' }}>
            No pending approvals.
          </div>
        ) : (
          <div className="approvals-list">
            {approvals.map(item => (
              <div className="approval-row" key={item.id}>
                <div className="approval-info">
                  <div className={`hil-level lvl-${item.level} approval-level`}>
                    L{item.level}
                  </div>
                  <div>
                    <div className="approval-title">{item.title}</div>
                    <div className="approval-meta">{item.meta}</div>
                  </div>
                </div>
                <div className="approval-actions">
                  <button className="act-btn" onClick={() => action(item.id, 'reject')}>
                    Reject
                  </button>
                  <button className="act-btn primary" onClick={() => action(item.id, 'approve')}>
                    Approve
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Panel>
    </div>
  );
}
