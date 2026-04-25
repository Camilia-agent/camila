import { useEffect, useState } from 'react';

import Desktop from './components/Desktop.jsx';
import Taskbar from './components/Taskbar.jsx';
import AuditLogs from './components/AuditLogs.jsx';

import DashboardPage from './pages/DashboardPage.jsx';
import PipelinePage  from './pages/PipelinePage.jsx';
import AnalyticsPage from './pages/AnalyticsPage.jsx';
import ApprovalsPage from './pages/ApprovalsPage.jsx';
import SettingsPage  from './pages/SettingsPage.jsx';
import CorpusPage    from './pages/CorpusPage.jsx';
import SearchPage    from './pages/SearchPage.jsx';
import HelpPage      from './pages/HelpPage.jsx';

const pages = {
  dashboard: DashboardPage,
  pipeline:  PipelinePage,
  analytics: AnalyticsPage,
  approvals: ApprovalsPage,
  settings:  SettingsPage,
  corpus:    CorpusPage,
  search:    SearchPage,
  help:      HelpPage
};

export default function App() {
  const [onDesktop, setOnDesktop] = useState(true);
  const [currentPage, setCurrentPage] = useState(null);
  const [openApps, setOpenApps] = useState(() => new Set());
  const [isAuditOpen, setAuditOpen] = useState(false);

  useEffect(() => {
    document.body.classList.toggle('desktop-mode', onDesktop);
  }, [onDesktop]);

  function openApp(id) {
    setOnDesktop(false);
    setCurrentPage(id);
    setOpenApps(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showDesktop() {
    setOnDesktop(true);
    setCurrentPage(null);
  }

  function closeApp(id) {
    setOpenApps(prev => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });
    showDesktop();
  }

  const PageComponent = currentPage ? pages[currentPage] : null;

  return (
    <>
      {onDesktop ? <Desktop onOpenApp={openApp} /> : (
        <div className="main">
          <div className="window-title-bar">
            <div className="wtb-info">
              <span className="wtb-icon">⚙️</span>
              <span className="wtb-title">{currentPage ? currentPage.toUpperCase() : 'AGENT OS'}</span>
            </div>
            <div className="window-controls">
              <button className="win-btn win-min" onClick={showDesktop} title="Minimize">
                <svg width="10" height="1" viewBox="0 0 10 1" fill="none"><path d="M0 0.5H10" stroke="white"/></svg>
              </button>
              <button className="win-btn win-close" onClick={() => closeApp(currentPage)} title="Close">
                <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="white"><path d="M1 1L9 9M9 1L1 9"/></svg>
              </button>
            </div>
          </div>
          {PageComponent ? (
            <PageComponent 
              onOpenApp={openApp} 
              onClose={() => closeApp(currentPage)}
              onMinimize={showDesktop}
            />
          ) : null}
        </div>
      )}
      <Taskbar
        currentPage={currentPage}
        openApps={openApps}
        onOpenApp={openApp}
        onShowDesktop={showDesktop}
        onToggleAudit={() => setAuditOpen(prev => !prev)}
      />
      <AuditLogs isOpen={isAuditOpen} onClose={() => setAuditOpen(false)} />
    </>
  );
}
