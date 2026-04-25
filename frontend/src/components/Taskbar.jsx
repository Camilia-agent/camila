import { useState } from 'react';
import { useClock } from '../hooks/useClock.js';

const taskbarItems = [
  { id: 'dashboard', icon: '📊', tip: 'Dashboard', sub: 'Pricing Overview' },
  { id: 'pipeline',  icon: '📋', tip: 'RFP Pipeline', sub: 'Active Kanban' },
  { id: 'analytics', icon: '📈', tip: 'Analytics', sub: 'Market Trends' },
  { id: 'approvals', icon: '✅', tip: 'HIL Approvals', sub: 'Pending Review' },
  { id: 'corpus',    icon: '📁', tip: 'RFP Corpus', sub: 'Knowledge Base' }
];

function TaskbarPreview({ item }) {
  return (
    <div className="taskbar-preview">
      <div className="preview-header">
        <span className="preview-icon">{item.icon}</span>
        <div className="preview-text">
          <div className="preview-title">{item.tip}</div>
          <div className="preview-sub">{item.sub}</div>
        </div>
      </div>
      <div className="preview-thumb">
        {/* A mock mini-UI representing the page */}
        <div className={`thumb-content thumb-${item.id}`}>
          <div className="thumb-header"></div>
          <div className="thumb-row"></div>
          <div className="thumb-row"></div>
          <div className="thumb-row half"></div>
        </div>
      </div>
    </div>
  );
}

export default function Taskbar({ currentPage, openApps, onOpenApp, onShowDesktop, onToggleAudit }) {
  const clock = useClock();
  const [hoveredId, setHoveredId] = useState(null);

  return (
    <div className="taskbar">
      <div className="taskbar-section"></div>

      <div className="taskbar-section center">
        <button className="start-btn" onClick={onShowDesktop}>
          <div className="start-btn-icon">
            <span></span><span></span>
            <span></span><span></span>
          </div>
          <span className="taskbar-tooltip">Start · Show Desktop</span>
        </button>

        <div className="taskbar-divider"></div>

        {taskbarItems.map(item => {
          const isActive = currentPage === item.id;
          const isOpen   = openApps.has(item.id);
          const isHovered = hoveredId === item.id;
          
          const cls = ['taskbar-item'];
          if (isActive) cls.push('active');
          if (isOpen)   cls.push('open');
          
          return (
            <div 
              key={item.id} 
              className="taskbar-item-wrapper"
              onMouseEnter={() => setHoveredId(item.id)}
              onMouseLeave={() => setHoveredId(null)}
            >
              {isHovered && <TaskbarPreview item={item} />}
              <button className={cls.join(' ')} onClick={() => onOpenApp(item.id)}>
                {item.icon}
                {!isHovered && <span className="taskbar-tooltip">{item.tip}</span>}
              </button>
            </div>
          );
        })}
      </div>

      <div className="taskbar-section right">
        <button className="tray-btn" onClick={onToggleAudit} title="Audit Logs">
          🛡️
        </button>
        <div className="tray-clock">
          <div className="clock-time">{clock.time}</div>
          <div className="clock-date">{clock.date}</div>
        </div>
      </div>
    </div>
  );
}
