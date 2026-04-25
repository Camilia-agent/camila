export default function HeroBanner({ title, subtitle, stats }) {
  return (
    <div className="hero-banner">
      <div className="hero-text">
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      <div className="hero-stats">
        {stats.map((stat, i) => (
          <div 
            className="hero-stat" 
            key={i} 
            onClick={stat.onClick}
            style={{ cursor: stat.onClick ? 'pointer' : 'default' }}
          >
            <div className="hero-stat-val">{stat.value}</div>
            <div className="hero-stat-lbl">{stat.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
