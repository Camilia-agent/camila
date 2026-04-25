import HeroBanner from '../components/HeroBanner.jsx';
import KpiCard from '../components/KpiCard.jsx';
import Panel from '../components/Panel.jsx';
import InfoTip from '../components/InfoTip.jsx';
import WinRateChart from '../components/WinRateChart.jsx';

import { useApi } from '../hooks/useApi.js';

function PanelLoading({ message = 'Loading…' }) {
  return (
    <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--neutral-4)', fontSize: 12 }}>
      {message}
    </div>
  );
}

function PipelineTable({ rows }) {
  return (
    <table className="pipeline-table">
      <thead>
        <tr>
          <th>RFP / Issuer</th>
          <th>Model</th>
          <th>TCV (Base)</th>
          <th>Stage</th>
          <th>HIL Level</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            <td>
              <div className="rfp-name">{row.name}</div>
              <div className="rfp-org">{row.org}</div>
            </td>
            <td><span className="model-tag">{row.model}</span></td>
            <td><strong>{row.tcv}</strong></td>
            <td>
              <span className={`stage-pill stage-${row.stage.variant}`}>
                <span className="stage-dot"></span> {row.stage.label}
              </span>
            </td>
            <td><span className={`tag tag-${row.hil.variant}`}>{row.hil.label}</span></td>
            <td>
              <div className="action-row">
                {row.actions.map((a, j) => (
                  <button key={j} className={`act-btn ${a.primary ? 'primary' : ''}`}>
                    {a.label}
                  </button>
                ))}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ScenarioPanelBody({ payload }) {
  return (
    <>
      <div style={{ fontSize: 11, color: 'var(--neutral-4)', marginBottom: 14 }}>
        {payload.assumptions}
      </div>
      <div className="scenario-grid">
        {payload.scenarios.map(s => (
          <div key={s.variant} className={`scenario-card sc-${s.variant}`}>
            <div className="sc-label">{s.label}</div>
            <div className="sc-val">{s.val}</div>
            <div className="sc-sub">{s.sub}</div>
            <div className="sc-detail">
              {s.rows.map((r, i) => (
                <div key={i} className="sc-row">
                  <span>{r.label}</span><strong>{r.value}</strong>
                </div>
              ))}
            </div>
            {s.recommended ? (
              <div><div className="sc-base-badge">⭐ Recommended</div></div>
            ) : null}
          </div>
        ))}
      </div>
    </>
  );
}

function BenchmarkPanelBody({ payload }) {
  return (
    <>
      <div style={{ fontSize: 11, color: 'var(--neutral-4)', marginBottom: 12 }}>
        {payload.intro}
      </div>
      <div className="bm-chart">
        {payload.rows.map((row, i) => (
          <div key={i} className="bm-row">
            <div className="bm-label">{row.label}</div>
            <div className="bm-bar-wrap">
              <div className="bm-bar" style={{ width: row.width, background: row.color }}></div>
            </div>
            <div className="bm-val">{row.val}</div>
          </div>
        ))}
      </div>
      <div
        className="bm-note"
        dangerouslySetInnerHTML={{ __html: payload.note }}
      />
    </>
  );
}

function HilList({ items }) {
  return (
    <div className="hil-list">
      {items.map(item => (
        <div key={item.level} className="hil-item">
          <div className={`hil-level lvl-${item.level}`}>{item.level}</div>
          <div className="hil-content">
            <div className="hil-title">{item.title}</div>
            <div className="hil-desc">{item.desc}</div>
            <div className="hil-meta">
              <span className="hil-who">{item.who}</span>
              <span className={`hil-status hs-${item.status.variant}`}>
                {item.status.label}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function RiskList({ items }) {
  const labelByVariant = { low: 'Low', med: 'Medium', high: 'High' };
  return (
    <div className="risk-list">
      {items.map((r, i) => (
        <div key={i} className={`risk-item risk-${r.variant}`}>
          <div>
            <div className="risk-badge">{labelByVariant[r.variant] ?? r.variant}</div>
            <div className="risk-text">{r.text}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function DashboardPage({ onOpenApp, onMinimize, onClose }) {
  const { data: kpis }       = useApi('/api/dashboard/kpis');
  const { data: pipeline }   = useApi('/api/dashboard/pipeline');
  const { data: scenarios }  = useApi('/api/dashboard/scenarios');
  const { data: benchmarks } = useApi('/api/dashboard/benchmarks');
  const { data: hil }        = useApi('/api/dashboard/hil-checkpoints');
  const { data: risks }      = useApi('/api/dashboard/risks');

  const heroStats = [{
    value: kpis ? String(kpis.pending_approvals) : '…',
    label: 'Pending HIL Approvals'
  }];

  return (
    <div className="app-page">
      <HeroBanner
        title="Centific Pricing Intelligence"
        subtitle="From RFP to approval-ready pricing in minutes."
        stats={heroStats.map(s => ({ ...s, onClick: () => onOpenApp('approvals') }))}
        onMinimize={onMinimize}
        onClose={onClose}
      />

      <div className="kpi-grid">
        {kpis ? (
          <>
            <div onClick={() => onOpenApp('pipeline')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} className="kpi-click-wrapper">
              <KpiCard {...kpiProps(kpis.rfps_in_pipeline)} />
            </div>
            <div onClick={() => onOpenApp('analytics')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} className="kpi-click-wrapper">
              <KpiCard {...kpiProps(kpis.tcv_total)} />
            </div>
            <div onClick={() => onOpenApp('analytics')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} className="kpi-click-wrapper">
              <KpiCard {...kpiProps(kpis.win_rate)} />
            </div>
          </>
        ) : (
          <>
            <KpiCardPlaceholder />
            <KpiCardPlaceholder />
            <KpiCardPlaceholder />
          </>
        )}
      </div>

      <Panel
        title="Active RFP Pipeline"
        ptag={pipeline ? `${pipeline.length} ROWS` : '…'}
        action="View Pipeline →"
        onAction={() => onOpenApp('pipeline')}
        className="section-sep"
        bodyStyle={{ padding: '0 20px 8px' }}
      >
        {pipeline ? <PipelineTable rows={pipeline} /> : <PanelLoading />}
      </Panel>

      <div className="grid-3 section-sep">
        <Panel
          title="Scenario Pricing"
          ptag={scenarios ? `${scenarios.rfp_code}${scenarios.rfp_label ? ' · ' + scenarios.rfp_label : ''}` : '…'}
          action="Edit Assumptions →"
          onAction={() => onOpenApp('corpus')}
          withCornerTip
          headerExtra={scenarios ? <InfoTip title={scenarios.tooltip.title} rows={scenarios.tooltip.rows} /> : null}
        >
          {scenarios ? <ScenarioPanelBody payload={scenarios} /> : <PanelLoading />}
        </Panel>

        <Panel 
          title="Benchmarking — Historical Rates"
          action="View Analytics →"
          onAction={() => onOpenApp('analytics')}
        >
          {benchmarks ? <BenchmarkPanelBody payload={benchmarks} /> : <PanelLoading />}
        </Panel>
      </div>

      <div className="grid-2 section-sep">
        <Panel 
          title="HIL Checkpoints" 
          ptag="5 Levels" 
          action="Manage Approvals →"
          onAction={() => onOpenApp('approvals')}
        >
          {hil ? <HilList items={hil} /> : <PanelLoading />}
        </Panel>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <WinRateChart />

          <Panel 
            title="Contract Risk Analysis" 
            ptag="Tool 14"
            action="View Details →"
            onAction={() => onOpenApp('corpus')}
          >
            {risks ? <RiskList items={risks} /> : <PanelLoading />}
          </Panel>
        </div>
      </div>

      <div className="dashboard-footer">
        Centific Pricing Intelligence · BR-PI-001 to BR-PI-012 Active · All 19 Tools Operational · &lt; 5s SLA · 99.9% Reliability
      </div>
    </div>
  );
}

function kpiProps(card) {
  return {
    icon:         card.icon,
    iconVariant:  card.icon_variant,
    trend:        card.trend,
    trendVariant: card.trend_dir,
    value:        card.value,
    label:        card.label,
    sub:          card.sub
  };
}

function KpiCardPlaceholder() {
  return (
    <div className="kpi-card">
      <div className="kpi-top">
        <div className="kpi-icon purple">…</div>
      </div>
      <div className="kpi-val">—</div>
      <div className="kpi-lbl">Loading…</div>
      <div className="kpi-sub">&nbsp;</div>
    </div>
  );
}
