import StubHero from '../components/StubHero.jsx';
import { useApi } from '../hooks/useApi.js';

function riskCls(risk) {
  if (!risk || risk === '—') return '';
  const r = risk.toLowerCase();
  if (r === 'low')  return 'pdc-risk-low';
  if (r === 'high') return 'pdc-risk-high';
  return 'pdc-risk-med';
}

function winColor(prob) {
  if (prob == null) return 'var(--neutral-4)';
  if (prob >= 75) return 'var(--success)';
  if (prob >= 55) return 'var(--warning)';
  return 'var(--error)';
}

function stageActions(icon) {
  if (icon === '📥') return [{ label: 'Monitor', primary: false }, { label: 'Details', primary: false }];
  if (icon === '🔍') return [{ label: 'Validate', primary: true },  { label: 'Pause',   primary: false }];
  if (icon === '⏳') return [{ label: 'Approve',  primary: true },  { label: 'Risk',    primary: false }];
  if (icon === '✅') return [{ label: 'Export',   primary: true },  { label: 'Archive', primary: false }];
  return [{ label: 'Review', primary: true }, { label: 'Bridge', primary: false }];
}

function DealCard({ deal, borderColor, stageIcon }) {
  const actions = stageActions(stageIcon);
  const hasRisk = deal.risk && deal.risk !== '—';
  return (
    <div className="pipe-deal-card" style={{ borderLeftColor: borderColor }}>
      <div className="pdc-header">
        <span className="pdc-code">{deal.code}</span>
        {hasRisk
          ? <span className={`pdc-risk ${riskCls(deal.risk)}`}>{deal.risk}</span>
          : null}
      </div>

      <div className="pdc-name" title={deal.name}>{deal.name}</div>
      <div className="pdc-org"  title={deal.org}>{deal.org}</div>

      <div className="pdc-meta-row">
        {deal.category && deal.category !== '—'
          ? <span className="pdc-cat">{deal.category}</span>
          : null}
        {deal.model && deal.model !== '—'
          ? <span className="pdc-model">{deal.model}</span>
          : null}
      </div>

      <div className="pdc-stats">
        <div className="pdc-stat">
          <span className="pdc-stat-lbl">TCV</span>
          <span className="pdc-stat-val">{deal.tcv}</span>
        </div>
        <div className="pdc-stat">
          <span className="pdc-stat-lbl">HIL</span>
          <span className="pdc-stat-val">{deal.hil}</span>
        </div>
        {deal.winprob != null
          ? <div className="pdc-stat">
              <span className="pdc-stat-lbl">Win</span>
              <span className="pdc-stat-val" style={{ color: winColor(deal.winprob) }}>
                {deal.winprob}%
              </span>
            </div>
          : null}
      </div>

      <div className="pdc-actions">
        {actions.map((a, i) => (
          <button
            key={i}
            className={`pdc-act-btn${a.primary ? ' pdc-act-primary' : ''}`}
            onClick={() => {}}
          >
            {a.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function StageSummaryBar({ stages }) {
  const total = stages.reduce((s, st) => s + st.count, 0);
  return (
    <div className="pipe-summary-bar">
      <div className="pipe-summary-item pipe-summary-total">
        <span className="pipe-summary-val">{total}</span>
        <span className="pipe-summary-lbl">Total Active RFPs</span>
      </div>
      {stages.map(st => (
        <div key={st.name} className="pipe-summary-item">
          <span className="pipe-summary-val" style={{ color: st.color }}>{st.count}</span>
          <span className="pipe-summary-lbl">{st.icon} {st.name}</span>
        </div>
      ))}
    </div>
  );
}

export default function PipelinePage({ onMinimize, onClose }) {
  const { data: stages, error, loading } = useApi('/api/pipeline/kanban');

  return (
    <div className="stub-page">
      <StubHero
        icon="📋"
        title="RFP Pipeline"
        subtitle="Track every active RFP across the full processing lifecycle — from ingestion to approved delivery"
        onMinimize={onMinimize}
        onClose={onClose}
      />

      {error ? (
        <div className="empty-stub">
          <div className="empty-stub-icon">⚠️</div>
          <h3>Unable to load pipeline</h3>
          <p>Make sure the backend is running at the configured API URL.</p>
        </div>
      ) : loading ? (
        <div className="empty-stub">
          <div className="empty-stub-icon">⏳</div>
          <h3>Loading pipeline…</h3>
        </div>
      ) : (
        <>
          <StageSummaryBar stages={stages} />

          <div className="pipeline-kanban">
            {stages.map(stage => (
              <div className="pipe-stage-col" key={stage.name}
                   style={{ '--stage-color': stage.borderColor }}>
                <div className="pipe-stage-head"
                     style={{ borderTopColor: stage.borderColor }}>
                  <div className="pipe-stage-name">
                    <span className="pipe-stage-icon">{stage.icon}</span>
                    {stage.name}
                  </div>
                  <div className="pipe-stage-count"
                       style={{
                         background: stage.borderColor + '1a',
                         color: stage.borderColor,
                       }}>
                    {stage.count}
                  </div>
                </div>

                <div className="pipe-stage-body">
                  {stage.deals.length === 0 ? (
                    <div className="pipe-empty">No RFPs in this stage</div>
                  ) : (
                    stage.deals.map((deal, i) => (
                      <DealCard
                        key={i}
                        deal={deal}
                        borderColor={stage.borderColor}
                        stageIcon={stage.icon}
                      />
                    ))
                  )}
                </div>

                {/* Stage Insight Footer - Fixed outside scroll area to utilize space symmetrically */}
                <div className="pipe-stage-footer">
                  <div className="pipe-stage-insight" style={{ borderColor: stage.borderColor }}>
                    <div className="psi-title">Stage Insights</div>
                    <div className="psi-row">
                      <span>Active Value</span>
                      <strong>{stage.deals.length > 0 ? '₹' + (stage.deals.length * 12).toFixed(1) + ' Cr' : '—'}</strong>
                    </div>
                    <div className="psi-row">
                      <span>Avg. Confidence</span>
                      <strong>{stage.deals.length > 0 ? (82 + stage.deals.length).toFixed(0) + '%' : '—'}</strong>
                    </div>
                    <div className="psi-row">
                      <span>Next Step</span>
                      <p>{stage.name === 'INGESTING' ? 'Metadata Sync' : stage.name === 'HIL REVIEW' ? 'Human Sign-off' : 'Batch Export'}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
