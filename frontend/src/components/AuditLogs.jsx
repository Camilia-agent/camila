import { useEffect, useState } from 'react';

const MOCK_LOGS = [
  "Agent initialized and ready.",
  "Checked internal cost databases for updates.",
  "Connected to historical rate database."
];

const NEW_LOGS = [
  "RFP ingestion sequence initiated for Global Services.",
  "Metadata extraction: 14 fields identified in PDF source.",
  "Internal cost database sync: 1,240 records verified.",
  "Pricing model 'Subscription' applied to project Alpha.",
  "Standardized locale mappings for EMEA region completed.",
  "Calculated margin variance: +2.4% above baseline.",
  "Scenario modeling: Conservative vs. Aggressive completed.",
  "Benchmarking: Proposed rates within 95th percentile.",
  "HIL Checkpoint triggered: Waiting for human approval.",
  "Contract risk scan: No critical violations detected.",
  "Template population: Client-facing document generated.",
  "System health check: All 19 micro-tools operational.",
  "Audit trail update: Traceability ID AG-PI-998 logged.",
  "Historical deal analysis: Similar RFP found (Win Prob: 78%).",
  "API endpoint /api/pipeline/kanban accessed by Agent."
];

export default function AuditLogs({ isOpen, onClose }) {
  const [logs, setLogs] = useState(() => {
    return MOCK_LOGS.map((msg, i) => ({
      id: `initial-${i}`,
      msg,
      time: new Date(Date.now() - (MOCK_LOGS.length - i) * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }));
  });

  useEffect(() => {
    // Add a new log every 10 seconds as requested
    const interval = setInterval(() => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      const randomIndex = Math.floor(Math.random() * NEW_LOGS.length);
      const msg = NEW_LOGS[randomIndex];
      
      setLogs(prev => [
        { id: `log-${Date.now()}`, msg, time: timeStr },
        ...prev.slice(0, 49) // Keep last 50 logs for performance
      ]);
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {isOpen && <div className="audit-overlay" onClick={onClose}></div>}
      <div className={`audit-drawer ${isOpen ? 'open' : ''}`}>
        <div className="audit-header">
          <div className="audit-title">
            <span className="audit-icon">🛡️</span>
            Live Audit Logs
          </div>
          <button className="audit-close" onClick={onClose} title="Close">×</button>
        </div>
        <div className="audit-content">
          {logs.map((log) => (
            <div key={log.id} className="audit-log-item">
              <div className="audit-log-time">{log.time}</div>
              <div className="audit-log-msg">{log.msg}</div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
