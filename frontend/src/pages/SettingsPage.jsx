import { useEffect, useState } from 'react';
import StubHero from '../components/StubHero.jsx';
import { useApi } from '../hooks/useApi.js';
import { apiUrl } from '../lib/api.js';

function Toggle({ on, onChange }) {
  return (
    <button
      type="button"
      className={`toggle ${on ? '' : 'off'}`}
      onClick={() => onChange(!on)}
      aria-pressed={on}
    />
  );
}

export default function SettingsPage() {
  const { data, error } = useApi('/api/settings/pricing-defaults');
  const [activeNav, setActiveNav] = useState('pricing');
  const [values, setValues]       = useState(null);

  useEffect(() => {
    if (!data) return;
    setValues(Object.fromEntries(data.rows.map(r => [r.id, r.control.defaultValue])));
  }, [data]);

  async function persist(key, value) {
    setValues(v => ({ ...v, [key]: value }));
    try {
      await fetch(apiUrl(`/api/settings/pricing-defaults/${key}`), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: typeof value === 'boolean' ? String(value) : value })
      });
    } catch {
      // optimistic update kept; show no UI noise for now
    }
  }

  if (error) {
    return (
      <div className="stub-page">
        <StubHero icon="⚙️" title="Settings" subtitle="Configure pricing defaults, business rules, integrations and user access" />
        <div className="empty-stub">
          <div className="empty-stub-icon">⚠️</div>
          <h3>Unable to load settings</h3>
          <p>Make sure the backend is running.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="stub-page">
      <StubHero
        icon="⚙️"
        title="Settings"
        subtitle="Configure pricing defaults, business rules, integrations and user access"
      />

      {!data || !values ? (
        <div className="empty-stub">
          <div className="empty-stub-icon">⏳</div>
          <h3>Loading settings…</h3>
        </div>
      ) : (
        <div className="settings-grid">
          <div className="settings-nav">
            {data.nav.map(item => (
              <button
                key={item.id}
                type="button"
                className={`settings-nav-item ${activeNav === item.id ? 'active' : ''}`}
                onClick={() => setActiveNav(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>

          <div className="settings-content">
            <h3>Pricing Defaults</h3>
            <p className="settings-intro">
              These defaults apply to all new RFPs unless overridden per deal.
            </p>

            {data.rows.map(row => (
              <div key={row.id} className="setting-row">
                <div className="setting-info">
                  <h4>{row.h4}</h4>
                  <p>{row.p}</p>
                </div>

                {row.control.kind === 'input' ? (
                  <input
                    className={`input-field ${row.control.wide ? 'wide' : ''}`}
                    value={values[row.id] ?? ''}
                    onChange={e => persist(row.id, e.target.value)}
                  />
                ) : (
                  <Toggle
                    on={!!values[row.id]}
                    onChange={v => persist(row.id, v)}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
