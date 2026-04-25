export default function InfoTip({ title, rows }) {
  return (
    <span className="info-tip info-tip-corner" tabIndex={0} aria-label={title}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
           strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8"  x2="12.01" y2="8"/>
      </svg>
      <div className="info-tip-panel">
        <div className="info-tip-title">{title}</div>
        {rows.map((row, i) => (
          <div className="info-tip-row" key={i}>
            <span className={`info-dot info-dot-${row.dot}`}></span>
            <div>
              <strong>{row.title}</strong>
              <p>{row.body}</p>
            </div>
          </div>
        ))}
      </div>
    </span>
  );
}
