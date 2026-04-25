export default function KpiCard({ icon, iconVariant, trend, trendVariant = 'up', value, label, sub }) {
  function handleMove(e) {
    const rect = e.currentTarget.getBoundingClientRect();
    e.currentTarget.style.setProperty('--mx', `${e.clientX - rect.left}px`);
    e.currentTarget.style.setProperty('--my', `${e.clientY - rect.top}px`);
  }

  return (
    <div className="kpi-card" onMouseMove={handleMove}>
      <div className="kpi-top">
        <div className={`kpi-icon ${iconVariant}`}>{icon}</div>
        <div className={`kpi-trend trend-${trendVariant}`}>{trend}</div>
      </div>
      <div className="kpi-val">{value}</div>
      <div className="kpi-lbl">{label}</div>
      <div className="kpi-sub">{sub}</div>
    </div>
  );
}
