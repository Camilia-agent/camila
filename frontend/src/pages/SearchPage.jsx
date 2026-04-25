import StubHero from '../components/StubHero.jsx';
import { useCorpusFilter } from '../hooks/useCorpusFilter.js';
import { fmtTCV, winProbColor } from '../lib/format.js';

export default function SearchPage() {
  const { meta, rows, count, loading, filters, setFilter } = useCorpusFilter();
  const topRows = rows.slice(0, 25);

  return (
    <div className="stub-page">
      <StubHero
        icon="🔍"
        title="Universal Search"
        subtitle="Search imported RFPs, curated deals, clients, pricing models, and risk tags"
      />

      <div className="corpus-toolbar">
        <div className="corpus-search-wrap">
          <input
            type="text"
            className="corpus-search"
            placeholder="Search by RFP ID, client, service, file name, or description..."
            value={filters.search}
            onChange={e => setFilter('search', e.target.value)}
            autoFocus
          />
        </div>
        <div className="corpus-count">
          {loading ? 'Searching...' : `${count} match${count === 1 ? '' : 'es'}`}
        </div>
      </div>

      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">Top Matches</div>
          <div className="panel-action">{meta ? 'Corpus + dataset' : 'Loading'}</div>
        </div>
        <div className="panel-body">
          <div className="corpus-table-wrap">
            <table className="corpus-table">
              <thead>
                <tr>
                  <th>RFP</th>
                  <th>Name</th>
                  <th>Client</th>
                  <th>Category</th>
                  <th>TCV</th>
                  <th>Win %</th>
                  <th>Risk</th>
                </tr>
              </thead>
              <tbody>
                {topRows.map(row => (
                  <tr key={row.id}>
                    <td className="col-id">{row.id}</td>
                    <td className="col-name">{row.name}</td>
                    <td>{row.client}</td>
                    <td>{row.category}</td>
                    <td className="col-tcv">{fmtTCV(row.tcv)}</td>
                    <td className="col-winprob" style={{ color: winProbColor(row.winprob) }}>
                      {row.winprob}%
                    </td>
                    <td><span className={`risk-pill risk-${row.risk}`}>{row.risk}</span></td>
                  </tr>
                ))}
                {!loading && topRows.length === 0 ? (
                  <tr>
                    <td colSpan="7">No matching records found.</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
