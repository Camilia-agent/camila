import StubHero from '../components/StubHero.jsx';

const sections = [
  {
    title: 'Run The System',
    rows: [
      ['Backend', 'python -m uvicorn app.main:app --reload --port 8000'],
      ['Frontend', 'npm run dev'],
      ['API docs', 'http://localhost:8000/docs']
    ]
  },
  {
    title: 'Data Flow',
    rows: [
      ['Curated seed', 'backend/db/ddl.sql + backend/db/dml.sql power the dashboard cards and approval workflows.'],
      ['CSV corpus', 'database/out/*.csv is imported into backend/local.db for searchable RFP history.'],
      ['Cloud mode', 'Set DATABASE_URL to a reachable PostgreSQL URI to use Aiven instead of SQLite.']
    ]
  },
  {
    title: 'Operational Checks',
    rows: [
      ['Health', 'GET /api/health returns the active database backend.'],
      ['Corpus', 'GET /api/corpus returns curated RFPs plus imported dataset rows.'],
      ['Approvals', 'Approve/reject actions persist to the active database.']
    ]
  }
];

export default function HelpPage() {
  return (
    <div className="stub-page">
      <StubHero
        icon="💬"
        title="Help & Documentation"
        subtitle="Quick operating reference for the Centific Pricing Intelligence workspace"
      />

      <div className="grid-2">
        {sections.map(section => (
          <div className="panel" key={section.title}>
            <div className="panel-header">
              <div className="panel-title">{section.title}</div>
            </div>
            <div className="panel-body">
              <div className="help-list">
                {section.rows.map(([label, value]) => (
                  <div className="help-row" key={label}>
                    <div className="help-label">{label}</div>
                    <div className="help-value">{value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
