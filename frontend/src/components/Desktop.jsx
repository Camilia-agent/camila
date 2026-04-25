import { useState } from 'react';
import { useWeather } from '../hooks/useWeather.js';

const appIcons = [
  { id: 'dashboard', label: 'Pricing\nDashboard', icon: '📊', bg: 'linear-gradient(135deg, #00F0FF 0%, #B026FF 100%)' }
];

const staticIcons = [
  { id: 'pc',      label: 'My PC',       icon: '🖥️', bg: 'linear-gradient(135deg, #64748B 0%, #94A3B8 100%)' },
  { id: 'network', label: 'Network',     icon: '🌐', bg: 'linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%)' },
  { id: 'bin',     label: 'Recycle Bin', icon: '🗑️', bg: 'linear-gradient(135deg, #475569 0%, #6B7280 100%)' }
];

const weatherFallback = {
  location:     'Hyderabad, IN',
  localSubLine: '—',
  current: { temp: '—', condition: 'Loading…', icon: '🌤️', high: '—', low: '—' },
  forecast: []
};

export default function Desktop({ onOpenApp }) {
  const [selected, setSelected] = useState(null);
  const { data: weather, error } = useWeather();

  const w = weather || weatherFallback;
  const liveLabel = weather ? 'Live' : error ? 'Offline' : '…';

  function handleSingle(id) {
    setSelected(id);
  }

  function handleOpen(id) {
    onOpenApp(id);
  }

  function handleBackdrop(e) {
    if (e.target === e.currentTarget) setSelected(null);
  }

  return (
    <div className="desktop" onClick={handleBackdrop}>
      <div className="glow-orb o1"></div>
      <div className="glow-orb o2"></div>
      <div className="glow-orb o3"></div>

      <div className="system-status">
        <div className="sys-item">
          <span className="sys-dot"></span>
          <span className="sys-item-label">API</span> Online
        </div>
        <div className="sys-sep"></div>
        <div className="sys-item">
          <span className="sys-dot"></span>
          <span className="sys-item-label">HIL</span> 5 Active
        </div>
        <div className="sys-sep"></div>
        <div className="sys-item">
          <span className="sys-dot warn"></span>
          <span className="sys-item-label">Pipeline</span> 23 RFPs
        </div>
      </div>

      <div className="desktop-icons" onClick={handleBackdrop}>
        {appIcons.map(icon => (
          <div
            key={icon.id}
            className={`desktop-icon ${selected === icon.id ? 'selected' : ''}`}
            tabIndex={0}
            onClick={() => handleSingle(icon.id)}
            onDoubleClick={() => handleOpen(icon.id)}
            onKeyDown={e => { if (e.key === 'Enter') handleOpen(icon.id); }}
          >
            <div className="desktop-icon-img" style={{ background: icon.bg }}>{icon.icon}</div>
            <div className="desktop-icon-label">
              {icon.label.split('\n').map((line, i) => (
                <span key={i}>{line}{i === 0 ? <br/> : null}</span>
              ))}
            </div>
          </div>
        ))}
        {staticIcons.map(icon => (
          <div key={icon.id} className="desktop-icon desktop-icon-static">
            <div className="desktop-icon-img" style={{ background: icon.bg }}>{icon.icon}</div>
            <div className="desktop-icon-label">{icon.label}</div>
          </div>
        ))}
      </div>

      <div className="weather-widget">
        <div className="weather-top">
          <div>
            <div className="weather-loc">{w.location}</div>
            <div className="weather-loc-sub">{w.localSubLine}</div>
          </div>
          <div style={{ fontSize: 11, opacity: 0.75, textShadow: '0 1px 2px rgba(0,0,0,0.45)' }}>
            {liveLabel}
          </div>
        </div>
        <div className="weather-now">
          <div className="weather-icon-big">{w.current.icon}</div>
          <div>
            <div className="weather-temp">{w.current.temp}</div>
            <div className="weather-cond">{w.current.condition}</div>
            <div className="weather-hilo">H: {w.current.high}  ·  L: {w.current.low}</div>
          </div>
        </div>
        <div className="weather-forecast">
          {w.forecast.map(day => (
            <div className="forecast-day" key={day.label}>
              <span className="forecast-label">{day.label}</span>
              <span className="forecast-icon">{day.icon}</span>
              <span className="forecast-temp">{day.temp}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="desktop-welcome">
        <strong>CENTIFIC</strong>
        Pricing Intelligence
      </div>
    </div>
  );
}
