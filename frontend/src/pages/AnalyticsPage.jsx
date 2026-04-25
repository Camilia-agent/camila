import StubHero from '../components/StubHero.jsx';
import { useApi } from '../hooks/useApi.js';

function AccuracyDistributionChart({ buckets }) {
  const yBottom = 180, yTop = 35;
  const xs = [42, 82, 122, 162, 202, 242, 282, 322, 362];
  const maxCount = Math.max(1, ...buckets.map(b => b.count));
  const scale = (yBottom - 35) / 16;

  return (
    <svg viewBox="0 0 420 220" width="100%" height="220" preserveAspectRatio="none">
      <defs>
        <linearGradient id="pdistGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#5929d0" stopOpacity="0.95" />
          <stop offset="100%" stopColor="#A855F7" stopOpacity="0.65" />
        </linearGradient>
        <linearGradient id="pdistSweet" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#16A34A" stopOpacity="0.95" />
          <stop offset="100%" stopColor="#4ADE80" stopOpacity="0.70" />
        </linearGradient>
        <linearGradient id="pdistCurve" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%"   stopColor="#22D3EE" />
          <stop offset="50%"  stopColor="#5929d0" />
          <stop offset="100%" stopColor="#CF008B" />
        </linearGradient>
      </defs>

      <line x1="35" y1="40"  x2="400" y2="40"  stroke="#E2E8F0" strokeDasharray="3,4"/>
      <line x1="35" y1="90"  x2="400" y2="90"  stroke="#E2E8F0" strokeDasharray="3,4"/>
      <line x1="35" y1="140" x2="400" y2="140" stroke="#E2E8F0" strokeDasharray="3,4"/>
      <line x1="35" y1="180" x2="400" y2="180" stroke="#CBD5E1"/>

      <text x="30" y="44"  fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">16</text>
      <text x="30" y="94"  fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">10</text>
      <text x="30" y="144" fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">5</text>
      <text x="30" y="184" fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">0</text>

      <rect x="122" y="35" width="152" height="145"
            fill="rgba(22, 163, 74, 0.06)"
            stroke="rgba(22, 163, 74, 0.3)"
            strokeDasharray="3,3" rx="3"/>
      <text x="198" y="30" textAnchor="middle" fontSize="9" fontWeight="700"
            fill="#16A34A" fontFamily="JetBrains Mono">SWEET SPOT · ±5%</text>

      {buckets.map((b, i) => {
        const height = b.count * scale;
        const y = yBottom - height;
        const x = xs[i];
        const fill = b.inSweet ? 'url(#pdistSweet)' : 'url(#pdistGrad)';
        return (
          <g key={b.label}>
            <rect x={x} y={y} width="33" height={Math.max(0, height)} rx="3" fill={fill} />
            <text x={x + 16} y={y - 4}
                  fontSize={i === 4 ? 13 : i === 3 || i === 5 ? 11 : i === 2 ? 10 : 9}
                  fill={b.inSweet ? '#166534' : '#0F172A'}
                  fontWeight={i === 3 || i === 4 || i === 5 ? 800 : 700}
                  textAnchor="middle"
                  fontFamily="Space Grotesk, Poppins">{b.count}</text>
          </g>
        );
      })}

      <path d="M 42 175 Q 82 165, 122 130 Q 162 82, 202 60 Q 242 82, 282 130 Q 322 165, 395 178"
            fill="none" stroke="url(#pdistCurve)" strokeWidth="2.5"
            strokeLinecap="round" strokeDasharray="5,3" opacity="0.85"
            filter="drop-shadow(0 2px 4px rgba(89,41,208,0.25))"/>

      {buckets.map((b, i) => (
        <text key={'lbl-' + b.label} x={xs[i] + 16} y="200"
              fontSize={i === 4 ? 11 : 10}
              fill={i === 4 ? '#16A34A' : '#64748B'}
              fontWeight={i === 4 ? 700 : 400}
              textAnchor="middle" fontFamily="JetBrains Mono">
          {b.label}{i === 4 ? ' ★' : ''}
        </text>
      ))}

      <text x="215" y="218" fontSize="10" fill="#94A3B8" textAnchor="middle"
            fontFamily="JetBrains Mono" fontStyle="italic">Deviation from Market Rate</text>
    </svg>
  );
}

export default function AnalyticsPage({ onMinimize, onClose }) {
  const { data: distribution } = useApi('/api/analytics/model-distribution');
  const { data: tcvBars }      = useApi('/api/analytics/tcv-by-category');
  const { data: activity }     = useApi('/api/analytics/activity');
  const { data: accuracy }     = useApi('/api/analytics/accuracy');

  return (
    <div className="stub-page">
      <StubHero
        icon="📊"
        title="Pricing Analytics"
        subtitle="Win rate, deal value distribution and pricing model performance trends"
        onMinimize={onMinimize}
        onClose={onClose}
      />

      <div className="analytics-grid">
        <div className="chart-panel">
          <h3>Pricing Model Distribution</h3>
          <div className="ch-sub">Active deals by pricing model</div>
          <div className="donut-wrap">
            <div className="donut">
              <div className="donut-center">
                <div className="donut-val">{distribution ? distribution.total : '…'}</div>
                <div className="donut-lbl">Active</div>
              </div>
            </div>
            <div className="donut-legend">
              {(distribution?.legend ?? []).map((row, i) => (
                <div className="legend-row" key={i}>
                  <div className="legend-sw" style={{ background: row.color }}></div>
                  {row.label}
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="chart-panel">
          <h3>TCV by Category (₹ Cr)</h3>
          <div className="ch-sub">Active deals across business lines</div>
          <div className="bar-chart-row">
            {(tcvBars ?? []).map((bar, i) => (
              <div className="bar-col" key={i}>
                <div className="bar-val">{bar.val}</div>
                <div className="bar-grow"
                     style={{ height: `${bar.heightPct}%`, background: bar.gradient }}></div>
                <div className="bar-lbl">{bar.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="chart-panel">
          <h3>Today's Activity Summary</h3>
          <div className="ch-sub">Live snapshot</div>

          <div className="activity-grid">
            {(activity?.tiles ?? []).map((tile, i) => (
              <div key={i} className={`activity-tile act-${tile.variant}`}>
                <div className="act-icon">{tile.icon}</div>
                <div className="act-value">{tile.value}</div>
                <div className="act-label">{tile.label}</div>
                <div className={`act-trend ${tile.trend.dir}`}>{tile.trend.text}</div>
              </div>
            ))}
          </div>

          {activity ? (
            <div className="activity-highlight">
              <div className="act-highlight-label">🏆 Today's Top Deal</div>
              <div className="act-highlight-value">{activity.topDeal}</div>
            </div>
          ) : null}
        </div>

        <div className="chart-panel">
          <h3>Pricing Accuracy Distribution</h3>
          <div className="ch-sub">Quoted price vs Final awarded price · last 44 deals</div>

          <div className="accuracy-dist-wrap">
            {accuracy ? <AccuracyDistributionChart buckets={accuracy.buckets} /> : null}
          </div>

          <div className="pdist-insight">
            {(accuracy?.insights ?? []).map((row, i) => (
              <div className="pdist-ins-row" key={i}>
                <div className="pdist-ins-lbl">{row.lbl}</div>
                <div className="pdist-ins-val" style={{ color: row.color || 'var(--neutral-0)' }}>
                  {row.val}
                </div>
                <div className="pdist-ins-sub">{row.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
