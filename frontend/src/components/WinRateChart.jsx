import { useState } from 'react';
import { useApi } from '../hooks/useApi.js';

const pointColors = ['#22D3EE', '#6366F1', '#5929d0', '#CF008B', '#22D3EE', '#6366F1', '#5929d0'];

function geometry(data) {
  const xStart = 60, xEnd = 340;
  const yMin = 35, yMax = 80;
  const yTop = 40, yBottom = 190;
  const n = data.length;
  const step = n > 1 ? (xEnd - xStart) / (n - 1) : 0;

  return data.map((d, i) => ({
    x: xStart + i * step,
    y: yBottom - ((d.val - yMin) / (yMax - yMin)) * (yBottom - yTop),
    val: d.val,
    label: d.x
  }));
}

export default function WinRateChart() {
  const [rangeKey, setRangeKey] = useState('quarter');
  const { data: ds, error } = useApi(`/api/dashboard/winrate?range=${rangeKey}`);

  const points = ds ? geometry(ds.data) : [];

  const linePath = points.map((p, i) =>
    (i === 0 ? 'M ' : 'L ') + p.x.toFixed(1) + ' ' + p.y.toFixed(1)
  ).join(' ');

  const areaPath = points.length
    ? linePath +
      ` L ${points[points.length - 1].x.toFixed(1)} 190` +
      ` L ${points[0].x.toFixed(1)} 190 Z`
    : '';

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          Win Rate Trend
          <span className="ptag">{ds ? ds.label : '…'}</span>
        </div>
        <div className="wr-tabs" role="tablist">
          {['week', 'month', 'quarter'].map(r => (
            <button
              key={r}
              className={`wr-tab ${rangeKey === r ? 'active' : ''}`}
              role="tab"
              onClick={() => setRangeKey(r)}
            >
              {r.charAt(0).toUpperCase() + r.slice(1)}
            </button>
          ))}
        </div>
      </div>
      <div className="panel-body">
        <div className="wr-sub">
          {error ? 'Unable to load win-rate data.' : ds ? ds.sub : 'Loading…'}
        </div>

        <div className="wr-line-chart">
          <svg viewBox="0 0 380 220" width="100%" height="220">
            <defs>
              <linearGradient id="wrAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#5929d0" stopOpacity="0.30" />
                <stop offset="100%" stopColor="#5929d0" stopOpacity="0" />
              </linearGradient>
              <linearGradient id="wrLineGrad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%"   stopColor="#22D3EE" />
                <stop offset="50%"  stopColor="#5929d0" />
                <stop offset="100%" stopColor="#CF008B" />
              </linearGradient>
            </defs>

            <line x1="40" y1="40"  x2="360" y2="40"  stroke="#E2E8F0" strokeDasharray="3,4" />
            <line x1="40" y1="90"  x2="360" y2="90"  stroke="#E2E8F0" strokeDasharray="3,4" />
            <line x1="40" y1="140" x2="360" y2="140" stroke="#E2E8F0" strokeDasharray="3,4" />
            <line x1="40" y1="190" x2="360" y2="190" stroke="#E2E8F0" />

            <text x="32" y="44"  fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">80%</text>
            <text x="32" y="94"  fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">65%</text>
            <text x="32" y="144" fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">50%</text>
            <text x="32" y="194" fontSize="9" fill="#94A3B8" textAnchor="end" fontFamily="JetBrains Mono">35%</text>

            <path d={areaPath} fill="url(#wrAreaGrad)" style={{ transition: 'd 0.5s ease' }} />
            <path d={linePath} fill="none" stroke="url(#wrLineGrad)" strokeWidth="3"
                  strokeLinecap="round" strokeLinejoin="round"
                  filter="drop-shadow(0 2px 8px rgba(89,41,208,0.25))"
                  style={{ transition: 'd 0.5s ease' }} />

            <g>
              {points.map((p, i) => {
                const isLast = i === points.length - 1;
                const color = pointColors[i % pointColors.length];
                if (isLast) {
                  return (
                    <g key={i}>
                      <circle cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r="14" fill="#CF008B" opacity="0.18">
                        <animate attributeName="r" values="7;14;7" dur="2s" repeatCount="indefinite"/>
                      </circle>
                      <circle cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r="7"
                              fill="#CF008B" stroke="#fff" strokeWidth="3"
                              filter="drop-shadow(0 0 10px #CF008B)" />
                    </g>
                  );
                }
                return (
                  <circle key={i} cx={p.x.toFixed(1)} cy={p.y.toFixed(1)} r="5"
                          fill="#fff" stroke={color} strokeWidth="2.5" />
                );
              })}
            </g>

            <g>
              {points.map((p, i) => {
                const isLast = i === points.length - 1;
                return (
                  <text key={i} x={p.x.toFixed(1)} y="210"
                        fontSize="11"
                        fill={isLast ? '#CF008B' : '#64748B'}
                        fontWeight={isLast ? 700 : 400}
                        textAnchor="middle" fontFamily="JetBrains Mono">
                    {p.label}{isLast ? ' ★' : ''}
                  </text>
                );
              })}
            </g>

            <g>
              {points.map((p, i) => {
                const isLast = i === points.length - 1;
                return (
                  <text key={i}
                        x={p.x.toFixed(1)}
                        y={(p.y - 12).toFixed(1)}
                        fontSize={isLast ? 13 : 12}
                        fill={isLast ? '#CF008B' : '#0F172A'}
                        fontWeight={isLast ? 800 : 700}
                        textAnchor="middle"
                        fontFamily="Space Grotesk, Poppins">
                    {p.val}%
                  </text>
                );
              })}
            </g>
          </svg>
        </div>

        <div className="wr-insight">
          {(ds?.insights ?? [{}, {}, {}]).map((ins, i) => (
            <div className="wr-ins-row" key={i}>
              <div className="wr-ins-lbl">{ins.lbl ?? '—'}</div>
              <div className="wr-ins-val" style={{ color: ins.color || 'var(--neutral-0)' }}>
                {ins.val ?? '—'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
