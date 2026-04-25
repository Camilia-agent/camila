import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

import './styles/tokens.css';
import './styles/base.css';
import './styles/desktop.css';
import './styles/taskbar.css';
import './styles/shared.css';
import './styles/dashboard.css';
import './styles/pipeline.css';
import './styles/analytics.css';
import './styles/approvals.css';
import './styles/settings.css';
import './styles/corpus.css';
import './styles/audit.css';

createRoot(document.getElementById('root')).render(<App />);
