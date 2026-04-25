import { useEffect, useRef, useState } from 'react';
import StubHero from '../components/StubHero.jsx';
import { useCorpusFilter } from '../hooks/useCorpusFilter.js';
import { fmtTCV, winProbColor } from '../lib/format.js';

const FILTER_PILL_LABELS = {
  status:   { placeholder: 'All Status',     label: v => v },
  category: { placeholder: 'All Categories', label: v => v },
  model:    { placeholder: 'All Models',     label: v => v },
  risk:     { placeholder: 'All Risk',       label: v => `${v} Risk` }
};

function renderCell(row, key) {
  switch (key) {
    case 'status':
      return <span className={`status-pill status-${row.status}`}>{row.status}</span>;
    case 'tcv':
      return fmtTCV(row.tcv);
    case 'scenario':
      return <span className={`scen-pill scen-${row.scenario}`}>{row.scenario}</span>;
    case 'winprob':
      return <span style={{ color: winProbColor(row.winprob) }}>{row.winprob}%</span>;
    case 'risk':
      return <span className={`risk-pill risk-${row.risk}`}>{row.risk}</span>;
    default:
      return row[key];
  }
}

function cellClass(key) {
  switch (key) {
    case 'id':          return 'col-id';
    case 'name':        return 'col-name';
    case 'description': return 'col-desc';
    case 'tcv':         return 'col-tcv';
    case 'winprob':     return 'col-winprob';
    default:            return '';
  }
}

export default function CorpusPage({ onMinimize, onClose }) {
  const {
    meta, metaErr, rows, count, loading,
    filters, sort, cols,
    setFilter, toggleSort, toggleColumn, reset
  } = useCorpusFilter();

  const [colPanelOpen, setColPanelOpen] = useState(false);
  const colWrapRef = useRef(null);

  useEffect(() => {
    if (!colPanelOpen) return;
    function handleOutside(e) {
      if (colWrapRef.current && !colWrapRef.current.contains(e.target)) {
        setColPanelOpen(false);
      }
    }
    document.addEventListener('click', handleOutside);
    return () => document.removeEventListener('click', handleOutside);
  }, [colPanelOpen]);

  function handleAction(action, row) {
    if (action === 'view') {
      alert(
        `📄 View Details — ${row.name}\n\n` +
        `Client: ${row.client}\n` +
        `TCV: ${fmtTCV(row.tcv)}\n` +
        `Status: ${row.status}\n` +
        `Model: ${row.model}\n` +
        `Win Probability: ${row.winprob}%\n` +
        `Risk Level: ${row.risk}\n` +
        `HIL Stage: ${row.hil}\n\n` +
        `Description: ${row.description}`
      );
    } else if (action === 'download') {
      alert(`📥 Downloading pricing doc for ${row.id}...`);
    } else if (action === 'rerun') {
      alert(`🔁 Re-running ${row.id} with new assumptions...\n(Opens re-run modal with margin/overhead sliders)`);
    }
  }

  if (metaErr) {
    return (
      <div className="stub-page">
        <StubHero icon="📁" title="RFP Corpus Library" subtitle="—" onMinimize={onMinimize} onClose={onClose} />
        <div className="empty-stub">
          <div className="empty-stub-icon">⚠️</div>
          <h3>Unable to load corpus</h3>
          <p>Make sure the backend is running.</p>
        </div>
      </div>
    );
  }

  if (!meta) {
    return (
      <div className="stub-page">
        <StubHero icon="📁" title="RFP Corpus Library" subtitle="Loading…" />
      </div>
    );
  }

  const visibleCols = meta.columns.filter(c => cols[c.key]);

  return (
    <div className="stub-page">
      <StubHero
        icon="📁"
        title="RFP Corpus Library"
        subtitle="Manage and explore all verified RFPs — search, filter, sort, and re-run any deal"
        onMinimize={onMinimize}
        onClose={onClose}
      />

      <div className="corpus-toolbar">
        <div className="corpus-search-wrap">
          <svg className="corpus-search-icon" width="16" height="16" viewBox="0 0 24 24"
               fill="none" stroke="currentColor" strokeWidth="2"
               strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            className="corpus-search"
            placeholder="Search by RFP ID, name, client, or description..."
            value={filters.search}
            onChange={e => setFilter('search', e.target.value)}
          />
        </div>

        {Object.entries(FILTER_PILL_LABELS).map(([key, cfg]) => (
          <select
            key={key}
            className="corpus-filter"
            value={filters[key]}
            onChange={e => setFilter(key, e.target.value)}
          >
            <option value="">{cfg.placeholder}</option>
            {(meta.filterOptions[key] ?? []).map(opt => (
              <option key={opt} value={opt}>{cfg.label(opt)}</option>
            ))}
          </select>
        ))}

        <div className="col-toggle-wrap" ref={colWrapRef}>
          <button
            className="col-toggle-btn"
            onClick={e => { e.stopPropagation(); setColPanelOpen(o => !o); }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" strokeWidth="2"
                 strokeLinecap="round" strokeLinejoin="round">
              <line x1="3"  y1="6"  x2="21" y2="6"  />
              <line x1="3"  y1="12" x2="21" y2="12" />
              <line x1="3"  y1="18" x2="21" y2="18" />
            </svg>
            Columns
          </button>
          {colPanelOpen ? (
            <div className="col-toggle-panel">
              <div className="col-toggle-title">Show / Hide Columns</div>
              {meta.columns.map(col => (
                <label key={col.key}>
                  <input
                    type="checkbox"
                    checked={!!cols[col.key]}
                    onChange={() => toggleColumn(col.key)}
                  />
                  {col.label}
                </label>
              ))}
            </div>
          ) : null}
        </div>

        <div className="corpus-count">
          {loading ? '…' : `${count} result${count !== 1 ? 's' : ''}`}
        </div>
        <button className="corpus-reset" onClick={reset}>Reset</button>
      </div>

      <div className="corpus-table-wrap">
        <table className="corpus-table">
          <thead>
            <tr>
              {visibleCols.map(col => {
                const active = sort.key === col.key;
                const cls = active ? (sort.dir === 'asc' ? 'sort-asc' : 'sort-desc') : '';
                return (
                  <th
                    key={col.key}
                    className={cls}
                    onClick={col.sortable ? () => toggleSort(col.key) : undefined}
                    style={col.sortable ? undefined : { cursor: 'default' }}
                  >
                    {col.label}
                    {col.sortable ? <span className="sort-icon">⇅</span> : null}
                  </th>
                );
              })}
              <th className="col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(row => (
              <tr key={row.id}>
                {visibleCols.map(col => (
                  <td key={col.key} className={cellClass(col.key)}>
                    {renderCell(row, col.key)}
                  </td>
                ))}
                <td>
                  <div className="qa-row">
                    <button className="qa-btn" title="View Details"
                            onClick={() => handleAction('view', row)}>👁️</button>
                    <button className="qa-btn" title="Download Pricing Doc"
                            onClick={() => handleAction('download', row)}>📥</button>
                    <button className="qa-btn" title="Re-run with new assumptions"
                            onClick={() => handleAction('rerun', row)}>🔁</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
